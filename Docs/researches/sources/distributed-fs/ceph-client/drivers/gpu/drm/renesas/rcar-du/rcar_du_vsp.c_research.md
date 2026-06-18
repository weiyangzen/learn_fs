# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_vsp.c

## Purpose

`rcar_du_vsp.c` implements the R-Car DU compositor path backed by a VSP1 device. It exposes DRM planes for VSP RPF inputs, maps GEM framebuffers into the VSP DMA domain, forwards atomic plane/pipe configuration to `vsp1_du_*()`, and converts VSP completion callbacks into vblank, page-flip, CRC, and writeback completion signals.

## Important APIs, Types, and Functions

Public entry points are `rcar_du_vsp_init()`, `rcar_du_vsp_enable()`, `rcar_du_vsp_disable()`, `rcar_du_vsp_atomic_begin()`, `rcar_du_vsp_atomic_flush()`, `rcar_du_vsp_map_fb()`, and `rcar_du_vsp_unmap_fb()`. The main internal helpers are `rcar_du_vsp_complete()`, `rcar_du_vsp_state_get_format()`, `rcar_du_vsp_plane_setup()`, and the DRM plane helper/state callbacks. Format arrays advertise Gen2/Gen3 formats and a Gen4 superset including 10-bit RGB and Y210/Y212.

## Control Flow

Initialization finds the VSP platform device from a DT node, adds a devm cleanup action, creates a device link from DU to VSP for suspend ordering, calls `vsp1_du_init()`, allocates one primary plane per connected CRTC and the remaining planes as overlays, and attaches alpha, zpos, and blend-mode properties. CRTC enable programs a dummy DU plane state for VSPD input selection and calls `vsp1_du_setup_lif()` with the active mode and completion callback. Atomic begin/flush wraps VSP atomic pipe transactions and passes CRC/writeback config. Plane updates translate DRM source/destination rectangles, alpha, zpos, blend mode, pitch, V4L2 pixel format, and SG DMA addresses into `vsp1_du_atomic_config`.

## State and Persistence Behavior

`struct rcar_du_vsp` stores the VSP device, device link, plane array, and plane count for the lifetime of the DRM device. Each `rcar_du_vsp_plane_state` stores the resolved `rcar_du_format_info` and mapped SG tables for the current framebuffer. Mapping is transient per visible plane state and must be released in cleanup. Hardware programming persists in the VSP pipeline until the next atomic update or LIF disable.

## Dependencies and Integration Points

This file depends on DRM atomic helpers, GEM DMA helpers, scatterlist/DMA APIs, `media/vsp1.h`, R-Car DU format helpers, CRTC state, and optional writeback support. It integrates tightly with `rcar_du_crtc.c` for enable/flush/page-flip sequencing and with VSP1 for all composition and DMA.

## Risks and Edge Cases

- Imported dma-bufs with non-contiguous SG tables are copied and mapped to VSP; failure unwinding must unmap only planes already mapped.
- The map/unmap helpers assume framebuffer plane count does not exceed the fixed three-table storage.
- `rcar_du_vsp_plane_atomic_update()` derives the old CRTC and must only dereference it when an old CRTC exists for disable updates.
- Format alpha-stripping for `DRM_MODE_BLEND_PIXEL_NONE` must stay synchronized with advertised formats and `rcar_du_format_info()`.
- Device-link ordering is state-less; runtime PM behavior still depends on the VSP and DU drivers honoring their PM contracts.

## Test Signals

Useful tests include KMS atomic plane updates for all advertised formats, imported dma-buf planes, multi-plane YUV buffers, alpha/blend-mode changes, zpos ordering, page-flip completion, CRC capture, writeback completion, suspend/resume with DU/VSP ordering, and fault injection for SG allocation/map failures.
