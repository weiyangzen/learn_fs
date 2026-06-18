# sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/adp_drv.c

## Purpose
`adp_drv.c` is the main Apple Display Pipe DRM/KMS driver. It creates a minimal atomic DRM device for the Apple touchbar display pipe, programs backend/frontend MMIO registers for a single XRGB8888 primary plane, handles vblank/page-flip events, builds an encoder/bridge/connector chain, and participates in component binding with the MIPI companion.

## Important APIs, types, and functions
The private state is `struct adp_drv_private`, embedding `struct drm_device`, one `drm_crtc`, encoder/connector/bridge pointers, backend/frontend MMIO bases, IRQs, a coherent mask buffer, and a pending vblank event. Important functions include `adp_open()`, `adp_drm_gem_dumb_create()`, `adp_plane_atomic_check/update/disable()`, `adp_crtc_atomic_enable/disable/flush()`, `adp_setup_crtc()`, `adp_setup_mode_config()`, `adp_parse_of()`, `adp_fe_irq()`, `adp_drm_bind()`, `adp_drm_unbind()`, `adp_probe()`, and `adp_remove()`.

## Control flow
Probe allocates a managed DRM device, maps named `be` and `fe` resources, reads `be`/`fe` IRQs, finds the remote OF graph node, and registers as a component master. Bind enables the FE FIFO, resolves the next bridge, initializes mode config, creates a primary plane and CRTC, allocates an encoder, attaches the bridge chain with `NO_CONNECTOR`, creates a bridge connector, initializes vblank, requests the FE IRQ, and registers the DRM device. Atomic plane updates program source/destination rectangles, stride, framebuffer DMA address, layer enables, scaling bypass, layer control, and pixel format. Atomic flush resizes/reallocates a coherent all-ones mask buffer for the current mode, writes its DMA address, triggers FIFO sync, and stores or sends page-flip events depending on vblank availability. FE IRQ handles vblank and sends deferred events once control bits indicate completion.

## State and persistence behavior
Runtime state is in `struct adp_drv_private` and hardware registers. GEM buffers are DMA-backed DRM objects; dumb buffers align height to 64 and compute size from pitch. The mask buffer is coherent DMA and is reallocated when mode dimensions change. No persistent storage exists.

## Dependencies and integration points
The file depends on DRM atomic/KMS helpers, GEM DMA helpers, framebuffer helpers, bridge connector APIs, OF graph/component framework, platform MMIO/IRQ resources, DMA coherent allocation, and MIPI/bridge devices supplied by `adp-mipi.c` and downstream panels. It exposes a DRM device named `adp`.

## Risks and edge cases
`adp_open()` refuses processes whose command starts with `X` to work around Xorg modesetting behavior, which is intentionally policy-like and brittle. `adp_crtc_atomic_flush()` does not check `dma_alloc_coherent()` failure before `memset()`, creating a potential null dereference. The mask buffer is not explicitly freed in unbind/remove except through resize paths. IRQ cleanup occurs after DRM shutdown, but request failure after setup needs managed state to unwind correctly. Only XRGB8888 and no scaling are supported, and MMIO programming assumes the hardware accepts the fixed register sequence.

## Test signals
Boot on matching `apple,h7-display-pipe` hardware, component bind with MIPI, modeset to the touchbar size, dumb-buffer creation with 64-line alignment, atomic page flips and vblank event delivery, open behavior from Xorg versus non-X clients, suspend/shutdown via `drm_atomic_helper_shutdown()`, IRQ handling, missing bridge/IRQ/resource probe failures, and DMA allocation fault injection for the mask buffer.
