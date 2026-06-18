# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_backend.h

## Purpose
`sun4i_backend.h` is the register map and public API for the original Allwinner Display Engine backend. It defines composition, layer, YUV, color-correction, sprite, pipe, and module-control registers plus the backend state structure consumed by backend, layer, CRTC, and frontend integration code.

## Important APIs, Types, and Functions
- Register macros for `MODCTL`, layer size/coordinate/line width/framebuffer address, attribute control, YUV input, output color correction, interrupts, and pipe offsets.
- Format macros such as `SUN4I_BACKEND_LAY_FBFMT_*` and YUV pixel-sequence fields.
- `SUN4I_BACKEND_NUM_LAYERS`, `SUN4I_BACKEND_NUM_FRONTEND_LAYERS`, and `SUN4I_BACKEND_NUM_YUV_PLANES`: hardware limits enforced in atomic check.
- `struct sun4i_backend`: embeds `struct sunxi_engine`, frontend pointer, clocks, resets, frontend teardown lock/flag, and quirks.
- Public layer update and format-support functions.

## Control Flow, State, and Persistence
The header itself has no control flow, but its constants define the register contract used by `sun4i_backend.c` and layer code. `struct sun4i_backend` persists for component lifetime and links the generic engine interface to backend-specific resources.

## Dependencies and Integration Points
It depends on Linux clock/list/OF/regmap/reset headers and `sunxi_engine.h`. It integrates with `sun4i_layer`, `sun4i_frontend`, `sun4i_crtc`, and the master `sun4i_drv` lists.

## Risks and Test Signals
Risks include register macro drift, bitfield mistakes in address high bits and layer priority/pipe selection, fixed four-layer assumptions, and exposing backend internals to multiple files. Tests should compile users after macro/API changes and exercise all public update calls against known register write expectations.
