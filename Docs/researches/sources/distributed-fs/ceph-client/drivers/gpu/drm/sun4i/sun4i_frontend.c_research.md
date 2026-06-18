# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_frontend.c

## Purpose
`sun4i_frontend.c` implements the original Allwinner Display Engine frontend scaler and colorspace-conversion block. It supports format/modifier validation, buffer/stride programming, scaling factors, YUV-to-RGB CSC coefficients, runtime PM clock/reset management, component binding, and exported helper APIs used by the backend.

## Important APIs, Types, and Functions
- Exported APIs: `sun4i_frontend_init`, `sun4i_frontend_exit`, `sun4i_frontend_enable`, `sun4i_frontend_update_buffer`, `sun4i_frontend_update_coord`, `sun4i_frontend_update_formats`, and `sun4i_frontend_format_is_supported`.
- Format helpers translate DRM input format, memory layout, pixel sequence, output format, tiling support, and chroma swapping.
- `sun4i_frontend_scaler_init`: loads horizontal/vertical FIR coefficients and marks coefficients ready when supported.
- Runtime PM callbacks enable clocks, reset hardware, enable the frontend, initialize scaler coefficients, then disable clocks/assert reset on suspend.
- `sun4i_frontend_of_table`: exposes compatible data for A10/A20 and A23/A33 variants.

## Control Flow, State, and Persistence
Component bind allocates state, maps registers, gets reset and bus/mod/ram clocks, records variant data, adds the frontend to `sun4i_drv.frontend_list`, and enables runtime PM. The backend calls `sun4i_frontend_init` when a plane needs scaling or unsupported-backend format conversion, then programs buffers, formats, and coordinates before starting processing. Buffer update handles linear and Allwinner tiled modifiers, sets per-plane strides and DMA addresses, and swaps chroma planes for YVU formats. Format update writes input mode/sequence, output RGB format, CSC bypass or BT.601 YUV-to-RGB coefficients, and phase registers. Coordinate update writes input/output sizes and fixed-point scale factors.

Persistent state includes clocks, reset, regmap, OF node, variant phase/coefficient flags, and list membership. Hardware state persists while runtime PM keeps the frontend active.

## Dependencies and Integration Points
The file depends on component framework, runtime PM, regmap, reset, clocks, DRM framebuffer/DMA helpers, format helpers, and `sun4i_backend.c` through exported symbols and shared BT.601 coefficients.

## Risks and Test Signals
Risks include limited RGB output choices, tiling only for selected YUV formats, possible divide-by-zero if CRTC size is invalid, undocumented phase settings, fixed BT.601 CSC, and frontend lifetime coordination with backend vblank teardown. Tests should cover all supported formats/modifiers, planar chroma swaps, scaling up/down, runtime PM cycles, coefficient initialization variants, backend handoff, and invalid format/modifier rejection.
