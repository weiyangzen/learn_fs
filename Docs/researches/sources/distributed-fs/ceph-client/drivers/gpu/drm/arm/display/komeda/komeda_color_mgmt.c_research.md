# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_color_mgmt.c

Purpose: converts DRM color-management properties into Komeda/D71 hardware coefficient tables.

Important APIs/types/functions: `komeda_select_yuv2rgb_coeffs()` selects fixed 10-bit YUV-to-RGB matrices for BT.601, BT.709, and BT.2020. `drm_lut_to_fgamma_coeffs()` samples a DRM gamma LUT into 65 foreground gamma coefficients. `drm_ctm_to_coeffs()` converts a 3x3 DRM CTM into Q3.12 coefficients.

Control flow: plane layer updates use selected YUV coefficients for YUV framebuffer input. CRTC/improc validation converts gamma/CTM blobs when color management changes; D71 improc update writes the resulting tables to DOU coefficient or IPS registers.

State and persistence: static coefficient tables are immutable. Generated coefficient arrays live in `komeda_improc_state` and persist only as DRM private atomic state until committed to registers.

Dependencies/integration: depends on DRM color-management helpers and `komeda_color_mgmt.h`. Integrated through `komeda_pipeline_state.c` and `d71_component.c`.

Risks: `komeda_select_yuv2rgb_coeffs()` can return NULL for unexpected encoding; callers write the returned pointer without explicit fallback. Gamma sampling assumes LUT size covers sector indexes up to 4095. Test signals: color-management atomic commits, null/invalid encoding handling, CTM conversion accuracy, gamma ramp conformance, and YUV limited/full range visual tests.
