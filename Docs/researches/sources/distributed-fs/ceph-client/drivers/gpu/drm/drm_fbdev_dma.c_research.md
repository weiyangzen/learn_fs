# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fbdev_dma.c

## Purpose
`drm_fbdev_dma.c` implements fbdev emulation for drivers whose dumb buffers are backed by DMA GEM memory. It creates a dumb client framebuffer, maps it for fbdev access, and chooses between direct fbdev access or a shadow system-memory buffer when framebuffer dirty callbacks require deferred flushing.

## Important APIs, Types, And Functions
The exported entry point is `drm_fbdev_dma_driver_fbdev_probe()`. It defines two `fb_ops` tables: `drm_fbdev_dma_fb_ops` for direct DMA memory and `drm_fbdev_dma_shadowed_fb_ops` for a deferred shadow buffer. Important helpers include open/release/module refcount handling, GEM mmap, destroy callbacks, `drm_fbdev_dma_damage_blit_real()`, `drm_fbdev_dma_damage_blit()`, `drm_fbdev_dma_helper_fb_dirty()`, and probe-tail setup functions.

## Control Flow
Probe computes a legacy fb format, allocates a dumb `drm_client_buffer`, vmaps it, rejects I/O memory mappings, stores `fb_helper->buffer` and `fb_helper->fb`, and fills generic fbdev info. If the framebuffer has a dirty callback, it allocates a vmalloc shadow buffer and enables deferred I/O; otherwise it points `info->screen_buffer` directly at the DMA mapping and exposes smem metadata when permitted. Dirty handling copies only the damaged clip from the shadow buffer into the client buffer, then calls the framebuffer `dirty` callback.

## State, Persistence, And Dependencies
Persistent state is held by `fb_helper->buffer`, `fb_helper->fb`, `fb_helper->info`, optional `fbdefio`, and optional vmalloc shadow storage. Direct mode stores the client buffer vmap in `info->screen_buffer`; shadow mode stores a separate `vzalloc()` buffer. Dependencies include fbdev DMA memory ops, DRM client buffer allocation and vmap, DMA GEM object fields such as `map_noncoherent`, GEM PRIME mmap, DRM fb helper damage callbacks, and iosys map copying.

## Integration Points
DMA memory-manager drivers can use this as their `drm_driver.fbdev_probe` callback. The fb_ops integrate with fbcon, userspace fbdev opens, mmap, drawing operations, and deferred I/O. The dirty callback path integrates with manual-update display drivers by blitting shadow damage into the actual DRM framebuffer and then invoking `fb->funcs->dirty`.

## Risks
Direct mode assumes the vmap is normal CPU memory, not I/O memory. Shadow mode must keep clip byte math correct for sub-byte fbdev formats and bytes-per-pixel formats. Destroy paths must clean deferred I/O, finish fb helper state, unmap/delete the client buffer, free the shadow buffer if used, and release the DRM client in the right order. Non-coherent DMA buffers rely on flags and later synchronization by the driver.

## Test Signals
Tests should cover direct and shadowed probe paths, failure after buffer allocation or vmap, dirty clips for 1/2/4 bpp and normal packed formats, fb_mmap through GEM PRIME, non-coherent map flags, destroy after partial setup, and driver dirty callback failures preserving error returns.
