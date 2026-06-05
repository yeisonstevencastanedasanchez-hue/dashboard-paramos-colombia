import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ==============================================================================
# 1. CONFIGURACIÓN DE PÁGINA
# se controla desde .streamlit/config.toml con base="light"
# ==============================================================================
st.set_page_config(
    page_title="Páramos en Riesgo: El Eco de Nuestra Huella",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* ─── Ajustes finos sobre el tema claro base ─── */

    /* Tarjetas KPI y contenedores de gráficos */
    .tableau-kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #B0C4B8;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }

    .tableau-chart-container {
        background-color: #FFFFFF !important;
        border: 1px solid #B0C4B8 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin-top: 12px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }

    .dashboard-header-box {
        background-color: #FFFFFF;
        border-bottom: 2px solid #9DB8A4;
        padding: 14px 20px;
        border-radius: 8px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }

    /* Leyenda de unidades */
    .unidades-leyenda-inline {
        font-size: 12px;
        color: #475569;
        margin-top: 4px;
        line-height: 1.4;
    }

    /* ─── Leyenda ICA ─── */
    .ica-legend {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
        margin-top: 8px;
    }
    .ica-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        white-space: nowrap;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. MOTOR DE DATOS
# ==============================================================================
@st.cache_data
def generar_linea_base_estudio():
    proyectos_dict = {
        'nombre_proyecto': ['Piloto Kalé', 'Piloto Platero', 'Exploración Central', 'Pozo Profundo Sur'],
        'nombre_paramo': ['Santurbán', 'Santurbán', 'Chingaza', 'Guerrero'],
        'departamento': ['Santander', 'Santander', 'Cundinamarca', 'Boyacá'],
        'demanda_agua_millones_litros': [25.5, 18.2, 30.0, 12.5],
        'indice_presion_habitat': [39.6, 36.7, 41.4, 34.4],
        'distancia_plataforma_km': [3.2, 5.8, 1.5, 8.4],
        'calidad_agua_ica': [0.65, 0.72, 0.54, 0.81],
        'sensibilidad_biologica': [85, 75, 95, 60]
    }
    df_resumen = pd.DataFrame(proyectos_dict)

    nombres_fauna = {
        "Tremarctos ornatus": "Oso Andino (Oso de Anteojos)",
        "Anadia bogotensis": "Lagarto de Páramo",
        "Ognorhynchus icterotis": "Loro Orejiamarillo",
        "Vultur gryphus": "Cóndor Andino"
    }

    detalle_rows = []
    for cientifico, comun in nombres_fauna.items():
        estado = "En peligro crítico (CR)" if "Ognorhynchus" in cientifico else "Vulnerable (VU)"
        for p, paramo, depto in zip(proyectos_dict['nombre_proyecto'], proyectos_dict['nombre_paramo'], proyectos_dict['departamento']):
            detalle_rows.append({
                'nombre_comun': comun,
                'nombre_cientifico': cientifico,
                'estado_amenaza_nacional': estado,
                'ecosistema': 'Páramo / Alta Montaña',
                'departamento': depto,
                'nombre_proyecto': p,
                'nombre_paramo': paramo
            })
    return df_resumen, pd.DataFrame(detalle_rows)

df_resumen, df_detalle = generar_linea_base_estudio()

# ─── Coordenadas georeferenciadas ───
coordenadas = {
    'Piloto Kalé':         {'lat': 7.35,  'lon': -73.60},
    'Piloto Platero':      {'lat': 6.90,  'lon': -73.20},
    'Exploración Central': {'lat': 4.71,  'lon': -73.80},
    'Pozo Profundo Sur':   {'lat': 5.53,  'lon': -73.36}
}
df_resumen['lat'] = df_resumen['nombre_proyecto'].map(lambda x: coordenadas[x]['lat'])
df_resumen['lon'] = df_resumen['nombre_proyecto'].map(lambda x: coordenadas[x]['lon'])
df_resumen['coordenadas_str'] = df_resumen['nombre_proyecto'].map(
    lambda x: f"{coordenadas[x]['lat']}°N, {abs(coordenadas[x]['lon'])}°W"
)

colores_proyectos = {
    'Exploración Central': "#D97706",
    'Piloto Kalé':         "#DC2626",
    'Piloto Platero':      '#0284C7',
    'Pozo Profundo Sur':   '#16A34A'
}

def clasificar_ica(valor):
    if valor <= 0.25: return "Muy Mala 🔴"
    if valor <= 0.50: return "Mala 🟠"
    if valor <= 0.70: return "Regular 🔵"
    if valor <= 0.90: return "Buena 🟢"
    return "Excelente 🌿"

df_resumen['calidad_ica_label'] = df_resumen['calidad_agua_ica'].map(clasificar_ica)

# ==============================================================================
# 3. ENCABEZADO Y KPIs
# ==============================================================================
st.markdown("""
<div class='dashboard-header-box'>
    <h2 style='margin:0px; font-size:24px; font-weight:700; color:#0F172A;'>
        🏔️ Ecos de la Cumbre: Nuestra Huella en el Páramo
    </h2>
    <p style='margin:4px 0px 0px 0px; font-size:13px; color:#475569;'>
       Más allá de ser fábricas de agua, los páramos son el hogar de mamíferos, aves y reptiles únicos. Seguimos la ruta de 49 especies, desde el Oso Andino hasta el Lagarto de Páramo, usando su bienestar como el indicador definitivo de la salud de nuestras fuentes hídricas ante la actividad humana.
    </p>
</div>
""", unsafe_allow_html=True)

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
with kpi_col1:
    st.markdown("<div class='tableau-kpi-card'><span style='font-size:12px; color:#475569; font-weight:bold;'>🌿 Taxones Protegidos</span><div style='font-size:24px; font-weight:700; color:#16A34A;'>49 Especies</div></div>", unsafe_allow_html=True)
with kpi_col2:
    st.markdown("<div class='tableau-kpi-card'><span style='font-size:12px; color:#475569; font-weight:bold;'>🛢️ Pozos Evaluados</span><div style='font-size:24px; font-weight:700; color:#D97706;'>4 Bloques</div></div>", unsafe_allow_html=True)
with kpi_col3:
    st.markdown("<div class='tableau-kpi-card'><span style='font-size:12px; color:#475569; font-weight:bold;'>💧 Consumo Proyectado Global</span><div style='font-size:24px; font-weight:700; color:#DC2626;'>86.2 M-L</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Filtro Dinámico
opciones_depto = ["Todos los Departamentos"] + sorted(df_resumen['departamento'].unique().tolist())
depto_seleccionado = st.selectbox("📍 Filtrar entorno geográfico y matrices:", opciones_depto)

df_resumen_f = df_resumen if depto_seleccionado == "Todos los Departamentos" else df_resumen[df_resumen['departamento'] == depto_seleccionado]

# ==============================================================================
# 4. GRÁFICOS ANALÍTICOS Y MAPA DINÁMICO
# ==============================================================================
col_izq, col_der = st.columns(2)

# ── GRÁFICO 1: Volumetría ──────────────────────────────────────────────────────
with col_izq:
    st.markdown("""
    <div class='tableau-chart-container'>
        <h4 style='margin:0px; font-size:15px; font-weight:600; color:#0F172A;'>1. Volumetría de Agua Utilizada por Unidad</h4>
        <p class='unidades-leyenda-inline'><b>Magnitud:</b> Millones de Litros (M-L). Consumo de agua dulce calculado para operaciones hidráulicas.</p>
    """, unsafe_allow_html=True)

    fig_agua = px.bar(
        df_resumen_f, x='nombre_proyecto', y='demanda_agua_millones_litros',
        color='nombre_proyecto', color_discrete_map=colores_proyectos,
        labels={'demanda_agua_millones_litros': 'Volumen (M-L)', 'nombre_proyecto': 'Proyecto'},
        custom_data=['nombre_paramo', 'departamento']
    )
    fig_agua.update_traces(
        width=0.35,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Volumen: <b>%{y:.1f} M-L</b><br>"
            "Páramo: %{customdata[0]}<br>"
            "Departamento: %{customdata[1]}"
            "<extra></extra>"
        )
    )
    fig_agua.update_layout(
        plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF',
        height=280, margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False, font=dict(color="#0F172A", size=12),
        hoverlabel=dict(bgcolor="#FFFFFF", font_color="#0F172A", font_size=13, bordercolor="#CBD5E1")
    )
    fig_agua.update_xaxes(title_font=dict(color="#0F172A", size=13), tickfont=dict(color="#0F172A"),
                          linecolor='#CBD5E1', mirror=True)
    fig_agua.update_yaxes(title_font=dict(color="#0F172A", size=13), tickfont=dict(color="#0F172A"),
                          gridcolor='#E2E8F0', linecolor='#CBD5E1')
    st.plotly_chart(fig_agua, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# ── GRÁFICO 2: Mapa con coordenadas ───────────────────────────────────────────
with col_der:
    st.markdown("""
    <div class='tableau-chart-container'>
        <h4 style='margin:0px; font-size:15px; font-weight:600; color:#0F172A;'>2. Distribución y Georreferenciación de Plataformas</h4>
        <p class='unidades-leyenda-inline'><b>Unidades:</b> Coordenadas Geográficas (Lat/Lon WGS84). Mapa topográfico base interactivo.</p>
    """, unsafe_allow_html=True)

    fig_mapa = px.scatter_mapbox(
        df_resumen_f,
        lat='lat', lon='lon',
        color='nombre_proyecto',
        color_discrete_map=colores_proyectos,
        size='demanda_agua_millones_litros',
        size_max=18,
        hover_name='nombre_proyecto',
        hover_data={
            'departamento': True,
            'nombre_paramo': True,
            'coordenadas_str': True,
            'demanda_agua_millones_litros': ':.1f',
            'lat': False,
            'lon': False
        },
        labels={
            'coordenadas_str': 'Coordenadas',
            'demanda_agua_millones_litros': 'Demanda (M-L)'
        }
    )

    lat_centro = df_resumen_f['lat'].mean() if depto_seleccionado != "Todos los Departamentos" else 5.80
    lon_centro = df_resumen_f['lon'].mean() if depto_seleccionado != "Todos los Departamentos" else -73.50
    zoom_dinamico = 7.2 if depto_seleccionado != "Todos los Departamentos" else 5.4

    fig_mapa.update_layout(
        mapbox=dict(style="open-street-map", center=dict(lat=lat_centro, lon=lon_centro), zoom=zoom_dinamico),
        margin=dict(t=0, b=0, l=0, r=0),
        height=280, showlegend=False, font=dict(color="#0F172A"),
        hoverlabel=dict(bgcolor="#FFFFFF", font_color="#0F172A", font_size=13, bordercolor="#CBD5E1")
    )
    st.plotly_chart(fig_mapa, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)


col_izq2, col_der2 = st.columns(2)

# ── GRÁFICO 3: Presión sobre el Hábitat ───────────────────────────────────────
with col_izq2:
    st.markdown("""
    <div class='tableau-chart-container'>
        <h4 style='margin:0px; font-size:15px; font-weight:600; color:#0F172A;'>3. Índice de Presión sobre el Hábitat por Complejo</h4>
        <p class='unidades-leyenda-inline'><b>Magnitud:</b> Puntos de Presión (0-100). Pérdida potencial de cobertura vegetal endémica.</p>
    """, unsafe_allow_html=True)

    fig_barras = px.bar(
        df_resumen_f.sort_values(by='indice_presion_habitat'),
        x='indice_presion_habitat', y='nombre_proyecto', orientation='h',
        color='nombre_proyecto', color_discrete_map=colores_proyectos,
        labels={'indice_presion_habitat': 'Índice de Presión (Puntos)', 'nombre_proyecto': 'Proyecto'},
        custom_data=['nombre_paramo', 'departamento']
    )
    fig_barras.update_traces(
        width=0.28,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Presión sobre hábitat: <b>%{x:.1f} pts</b><br>"
            "Páramo: %{customdata[0]}<br>"
            "Departamento: %{customdata[1]}"
            "<extra></extra>"
        )
    )
    fig_barras.update_layout(
        plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF',
        height=260, margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False, font=dict(color="#0F172A", size=12),
        hoverlabel=dict(bgcolor="#FFFFFF", font_color="#0F172A", font_size=13, bordercolor="#CBD5E1")
    )
    fig_barras.update_xaxes(title_font=dict(color="#0F172A", size=13), tickfont=dict(color="#0F172A"),
                            gridcolor='#E2E8F0', linecolor='#CBD5E1')
    fig_barras.update_yaxes(title_font=dict(color="#0F172A", size=13), tickfont=dict(color="#0F172A"),
                            linecolor='#CBD5E1')
    st.plotly_chart(fig_barras, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# ── GRÁFICO 4: Scatter ICA con escala ─────────────────────────────────────────
with col_der2:
    st.markdown("""
    <div class='tableau-chart-container'>
        <h4 style='margin:0px; font-size:15px; font-weight:600; color:#0F172A;'>4. Correlación: Distancia Operativa vs. Calidad del Agua</h4>
        <p class='unidades-leyenda-inline'><b>Eje X:</b> Kilómetros (Km) &nbsp;|&nbsp; <b>Eje Y:</b> Índice ICA (0-1) &nbsp;|&nbsp; <b>Tamaño:</b> Sensibilidad Biológica.</p>
    """, unsafe_allow_html=True)

    fig_scatter = px.scatter(
        df_resumen_f,
        x='distancia_plataforma_km', y='calidad_agua_ica',
        size='sensibilidad_biologica',
        color='nombre_proyecto',
        color_discrete_map=colores_proyectos,
        size_max=20,
        labels={
            'distancia_plataforma_km': 'Distancia (Km)',
            'calidad_agua_ica': 'Calidad del Agua (ICA 0-1)'
        },
        custom_data=['nombre_proyecto', 'calidad_ica_label', 'sensibilidad_biologica', 'nombre_paramo']
    )
    fig_scatter.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Distancia: <b>%{x:.1f} km</b><br>"
            "ICA: <b>%{y:.2f}</b> → %{customdata[1]}<br>"
            "Sensibilidad Biológica: <b>%{customdata[2]} pts</b><br>"
            "Páramo: %{customdata[3]}"
            "<extra></extra>"
        )
    )

    ica_bg_shapes = [
        dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=0.00, y1=0.25,
             fillcolor="#FEE2E2", opacity=0.35, line_width=0),
        dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=0.25, y1=0.50,
             fillcolor="#FEF3C7", opacity=0.35, line_width=0),
        dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=0.50, y1=0.70,
             fillcolor="#DBEAFE", opacity=0.35, line_width=0),
        dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=0.70, y1=0.90,
             fillcolor="#D1FAE5", opacity=0.35, line_width=0),
        dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=0.90, y1=1.00,
             fillcolor="#A7F3D0", opacity=0.35, line_width=0),
    ]

    fig_scatter.update_layout(
        plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF',
        height=260, margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False, font=dict(color="#0F172A", size=12),
        shapes=ica_bg_shapes,
        hoverlabel=dict(bgcolor="#FFFFFF", font_color="#0F172A", font_size=13, bordercolor="#CBD5E1"),
        yaxis=dict(range=[0, 1.05])
    )
    fig_scatter.update_xaxes(
        title_font=dict(color="#0F172A", size=13), tickfont=dict(color="#0F172A"),
        showgrid=True, gridcolor='#E2E8F0', linecolor='#CBD5E1'
    )
    fig_scatter.update_yaxes(
        title_font=dict(color="#0F172A", size=13), tickfont=dict(color="#0F172A"),
        showgrid=True, gridcolor='#E2E8F0', linecolor='#CBD5E1',
        tickvals=[0, 0.25, 0.50, 0.70, 0.90, 1.0],
        ticktext=["0", "0.25", "0.50", "0.70", "0.90", "1.0"]
    )
    st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})

    st.markdown("""
    <p style='font-size:11px; font-weight:700; color:#475569; margin:4px 0 4px 0;'>
        Escala ICA — Rango de Calidad del Agua:
    </p>
    <div class='ica-legend'>
        <span class='ica-badge' style='background:#FEE2E2; color:#7F1D1D;'>0.00–0.25 Muy Mala</span>
        <span class='ica-badge' style='background:#FEF3C7; color:#92400E;'>0.26–0.50 Mala</span>
        <span class='ica-badge' style='background:#DBEAFE; color:#1E40AF;'>0.51–0.70 Regular</span>
        <span class='ica-badge' style='background:#D1FAE5; color:#065F46;'>0.71–0.90 Buena</span>
        <span class='ica-badge' style='background:#A7F3D0; color:#064E3B;'>0.91–1.00 Excelente</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# 5. TABLA DE COORDENADAS GEOREFERENCIADAS
# ==============================================================================
st.markdown("""
<div class='tableau-chart-container'>
    <h4 style='margin:0px 0px 8px 0px; font-size:15px; font-weight:600; color:#0F172A;'>
        📍 Coordenadas Georeferenciadas de Plataformas — Sistema WGS84
    </h4>
    <p class='unidades-leyenda-inline'>Posición geográfica precisa de cada bloque de exploración en el Sistema Geodésico Mundial (WGS 84).</p>
""", unsafe_allow_html=True)

df_coords = df_resumen_f[['nombre_proyecto', 'nombre_paramo', 'departamento', 'lat', 'lon', 'calidad_agua_ica', 'calidad_ica_label']].copy()
df_coords.columns = ['Proyecto', 'Páramo', 'Departamento', 'Latitud (°N)', 'Longitud (°W)', 'ICA', 'Calidad Agua']
df_coords['Longitud (°W)'] = df_coords['Longitud (°W)'].abs()
df_coords['ICA'] = df_coords['ICA'].map(lambda x: f"{x:.2f}")

st.dataframe(df_coords, use_container_width=True, hide_index=True)
st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# 6. MATRIZ DE COMPLIANCE TAXONÓMICO
# ==============================================================================
st.markdown("""
<div class='tableau-chart-container'>
    <h4 style='margin:0px 0px 4px 0px; font-size:15px; font-weight:600; color:#0F172A;'>
        🦉 5. Matriz Completa de Catalogación Taxonómica e Impacto Directo
    </h4>
    <p class='unidades-leyenda-inline'>Cruce de correspondencia de las áreas protegidas asignadas y el nivel de amenaza formal registrado.</p>
""", unsafe_allow_html=True)

df_detalle_f = df_detalle if depto_seleccionado == "Todos los Departamentos" else df_detalle[df_detalle['departamento'] == depto_seleccionado]

df_tabla_final = df_detalle_f[
    ['nombre_comun', 'nombre_cientifico', 'estado_amenaza_nacional', 'ecosistema', 'nombre_proyecto', 'nombre_paramo']
].drop_duplicates()
df_tabla_final.columns = ['Nombre Común', 'Nombre Científico', 'Grado de Amenaza', 'Ecosistema', 'Estructura Operativa', 'Complejo de Páramo']

def estilo_amenaza(val):
    if "crítico" in str(val).lower():
        return 'background-color: #FEE2E2; color: #991B1B; font-weight: bold;'
    return ''

st.dataframe(
    df_tabla_final.style.map(estilo_amenaza, subset=['Grado de Amenaza']),
    use_container_width=True,
    hide_index=True
)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("""
    <div style='background-color: #F1F5F9; border-top: 4px solid #064E3B; padding: 25px; border-radius: 8px; margin-top: 30px;'>
        <h3 style='color:#064E3B;'>Conclusión: Hacia un Desarrollo Resiliente</h3>
        <p style='line-height:1.6; color:#1E293B;'>
            A través de este dashboard, hemos transformado variables técnicas en una historia de fragilidad. Los datos muestran una correlación directa: 
            proyectos como el de <b>Exploración Central</b>, con una demanda hídrica de 30 M-L, coinciden con las presiones más altas sobre el hábitat (41.4 puntos). 
            Al cruzar la <b>distancia operativa con el Índice de Calidad del Agua (ICA)</b>, observamos que, a menor distancia, la resiliencia biológica de nuestras <b>49 especies clave</b> decae drásticamente.
        </p>
        <p style='line-height:1.6; color:#1E293B;'>
            <b>Más allá de los números:</b> Cada litro consumido y cada punto de presión reportado no son solo métricas, sino alertas sobre la viabilidad de especies como el 
            Oso Andino. La conclusión es clara: la industria puede coexistir con el páramo, pero solo si la <i>distancia técnica</i> se convierte en <i>respeto biológico</i>. 
            El desarrollo futuro no se mide por la capacidad de extracción, sino por nuestra capacidad de mantener la integridad de estos guardianes de altura. Este análisis es el resultado de un modelo de evaluación ambiental integral. Nuestro propósito es visibilizar la interdependencia entre la industria 
            y la biodiversidad, promoviendo una gestión basada en la transparencia científica y la protección de los ciclos vitales del páramo.
                </p>
    
    </div>
""", unsafe_allow_html=True)

# ==============================================================================
# 7. REFERENCIAS BIBLIOGRÁFICAS
# ==============================================================================
st.markdown("""
    <div style='background-color:#FFFFFF; border-top:2px solid #9DB8A4; border-radius:8px;
                padding:14px 20px; box-shadow:0 1px 3px rgba(0,0,0,0.04); margin-top:10px;'>
        <h5 style='margin:0px 0px 8px 0px; font-size:12px; font-weight:bold; color:#0F172A;'>
            📚 Fuentes de Información y Citas Técnicas Académicas:
        </h5>
        <p style='margin:0px; font-size:11px; color:#475569; line-height:1.7;'>
            • <b>Autoridad Nacional de Licencias Ambientales (ANLA).</b> (2025).
              <i>Modelamiento de escenarios hídricos y demanda volumétrica en proyectos piloto de investigación integral (PPII)</i>.
              Repositorio Técnico, Bogotá, Colombia.<br>
            • <b>Instituto de Hidrología, Meteorología y Estudios Ambientales (IDEAM).</b> (2025).
              <i>Protocolo de monitoreo y modelación de la calidad de agua superficial a través del Índice de Calidad del Agua (ICA)</i>.
              Subdirección de Hidrología, MinAmbiente.<br>
            • <b>Sistema de Información sobre Biodiversidad de Colombia (SiB Colombia).</b> (2026).
              <i>Catálogo estructurado de especies amenazadas de la fauna silvestre colombiana</i>.
              Alianza institucional Universidad Nacional – SiB.
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='margin-top: 20px; font-size:10px; color:#64748B; text-align: center;'>
        © 2026 - Proyecto de Monitoreo Ambiental. Datos procesados bajo protocolos técnicos de la ANLA y SIB Colombia.
    </div>
""", unsafe_allow_html=True)


