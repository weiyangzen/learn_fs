# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fb_dma_helper.c

## Purpose
`drm_fb_dma_helper.c` provides small KMS helpers for framebuffers backed by DMA GEM objects. It lets drivers derive DMA scanout addresses, synchronize non-coherent memory over damaged regions, and expose the active DMA-backed primary-plane buffer to DRM panic handling.

## Important APIs, Types, And Functions
The exported APIs are `drm_fb_dma_get_gem_obj()`, `drm_fb_dma_get_gem_addr()`, `drm_fb_dma_sync_non_coherent()`, and `drm_fb_dma_get_scanout_buffer()`. They operate on `struct drm_framebuffer`, `struct drm_plane_state`, `struct drm_gem_dma_object`, `struct drm_atomic_helper_damage_iter`, `struct drm_rect`, and `struct drm_scanout_buffer`.

## Control Flow
`drm_fb_dma_get_gem_obj()` fetches a framebuffer plane's GEM object through `drm_gem_fb_get_obj()` and casts it to DMA GEM. `drm_fb_dma_get_gem_addr()` starts at `obj->dma_addr + fb->offsets[plane]`, applies chroma subsampling for nonzero planes, rounds the source coordinate down to the containing format block, and adds pitch and block-size offsets. `drm_fb_dma_sync_non_coherent()` walks every format plane, skips coherent DMA objects, iterates damage clips, and calls `dma_sync_single_for_device()` for full affected scanlines. `drm_fb_dma_get_scanout_buffer()` validates that the current primary-plane framebuffer is linear, local, and already CPU-mapped before filling a panic scanout descriptor.

## State, Persistence, And Dependencies
The file keeps no persistent state. It reads immutable framebuffer metadata, current plane state, DMA GEM object addresses, and damage clips. It depends on GEM framebuffer helpers, DMA GEM helpers, DRM format block metadata, atomic damage iteration, DMA mapping sync, iosys maps, and DRM panic scanout types.

## Integration Points
DMA-backed KMS drivers call these helpers from plane update, CRTC, or panic paths. `drm_fb_dma_sync_non_coherent()` is intended for `.atomic_update` implementations that use damage clips with non-coherent DMA memory. `drm_fb_dma_get_scanout_buffer()` is a generic implementation for drivers that pre-vmap primary-plane buffers.

## Risks
The address calculation assumes framebuffer pitches, offsets, source coordinates, chroma subsampling, and block dimensions are already validated by KMS. Damage sync intentionally ignores clip x coordinates and syncs whole lines, which is conservative but can be expensive. `drm_fb_dma_get_scanout_buffer()` dereferences the plane's current state and DMA object and therefore only supports simple local linear CPU-visible buffers.

## Test Signals
Useful tests cover single-plane RGB and multi-plane YUV address derivation, block/tiled-like format block widths, nonzero source offsets, damage clips on non-coherent DMA objects, imported GEM rejection in panic scanout, non-linear modifier rejection, and unavailable `vaddr` handling.
