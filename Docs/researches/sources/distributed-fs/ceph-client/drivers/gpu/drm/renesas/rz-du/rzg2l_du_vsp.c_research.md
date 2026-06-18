# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_vsp.c

## Purpose

`rzg2l_du_vsp.c` implements the RZ/G2L DU compositor interface to VSP1. It creates DRM planes backed by VSP inputs, configures the VSP LIF for the CRTC, converts plane state to VSP atomic updates, and converts VSP completion callbacks into vblank/page-flip/CRC events.

## Important APIs, Types, and Functions

Public functions are `rzg2l_du_vsp_init()`, `rzg2l_du_vsp_enable()`, `rzg2l_du_vsp_disable()`, `rzg2l_du_vsp_atomic_flush()`, and `rzg2l_du_vsp_get_drm_plane()`. Internals include `rzg2l_du_vsp_complete()`, `rzg2l_du_vsp_plane_setup()`, `__rzg2l_du_vsp_plane_atomic_check()`, and DRM plane state callbacks.

## Control Flow

VSP init finds the VSP device from DT, registers cleanup, calls `vsp1_du_init()`, and allocates two managed universal planes: one primary for the connected CRTC and one overlay. CRTC enable calls `vsp1_du_setup_lif()` with mode size and completion callback. Atomic plane check validates no scaling and resolves format. Plane update converts source/destination rectangles, DMA addresses from GEM DMA objects, alpha, zpos, blend mode, and V4L2 pixel format into VSP config. Atomic flush sends the pipe config to VSP.

## State and Persistence Behavior

`rzg2l_du_vsp` stores only VSP index, supplier device, and DU pointer. Plane-private state stores the resolved format for the current atomic state. Unlike the R-Car version, this code uses contiguous GEM DMA addresses directly instead of SG map/unmap state.

## Dependencies and Integration Points

It depends on DRM atomic/GEM DMA helpers, VSP1 media API, RZ/G2L KMS format metadata, and CRTC page-flip functions.

## Risks and Edge Cases

- Direct `gem->dma_addr` use assumes buffers are contiguous and mapped for the VSP/DMA domain.
- Only ARGB1555/4444/8888 are converted to XRGB variants for pixel-none blending; other alpha-capable formats are not listed here.
- `rzg2l_du_vsp_get_drm_plane()` iterates all planes and returns `ERR_PTR(-EINVAL)` if no index matches; CRTC creation depends on VSP planes already being initialized.
- There is no explicit device link to enforce DU/VSP suspend ordering, unlike the R-Car VSP path.

## Test Signals

Plane updates for all supported formats, primary/overlay selection by VSP pipe, page-flip/vblank completion, CRC events, contiguous DMA buffer assumptions, and suspend/resume with VSP are key signals.
