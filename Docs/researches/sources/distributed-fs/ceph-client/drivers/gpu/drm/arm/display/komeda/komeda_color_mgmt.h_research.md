# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_color_mgmt.h

Purpose: declares Komeda color-management dimensions and conversion helpers.

Important APIs/types/functions: constants define coefficient counts and precision: 12 YUV2RGB/RGB2YUV coefficients, 12-bit precision, 65 gamma coefficients, 4096 LUT size, and 9 CTM coefficients. Function declarations are `drm_lut_to_fgamma_coeffs()`, `drm_ctm_to_coeffs()`, and `komeda_select_yuv2rgb_coeffs()`.

Control flow: header-only declarations used by pipeline-state validation and D71 hardware update code.

State and persistence: no state. Constants determine DRM color-management property sizes and hardware table write counts.

Dependencies/integration: includes `<drm/drm_color_mgmt.h>` and is included by `komeda_pipeline.h`, `d71_component.c`, and color conversion implementation.

Risks: changing coefficient counts without matching D71 register writes corrupts table programming. `KOMEDA_COLOR_LUT_SIZE` must match DRM CRTC color-management setup. Test signals: compile-time users of constants, CRTC gamma property size, and D71 register dump after gamma/CTM commits.
