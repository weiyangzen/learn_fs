# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_vram_helper.c

## Purpose
`drm_gem_vram_helper.c` implements GEM objects backed by a TTM-managed VRAM aperture for simple devices with dedicated video memory. It provides VRAM BO creation, pin/unpin, vmap/vunmap, dumb-buffer creation, plane prepare/cleanup helpers that pin scanout buffers to VRAM, a TTM device implementation for VRAM placement/moves, debugfs, managed VRAM MM initialization, and mode validation based on available VRAM.

## Important APIs, Types, And Functions
The main types are `struct drm_gem_vram_object` and `struct drm_vram_mm`. Public functions include `drm_gem_vram_create()`, `drm_gem_vram_put()`, `drm_gem_vram_offset()`, `drm_gem_vram_vmap()`, `drm_gem_vram_vunmap()`, `drm_gem_vram_fill_create_dumb()`, `drm_gem_vram_driver_dumb_create()`, `drm_gem_vram_plane_helper_prepare_fb()`, `drm_gem_vram_plane_helper_cleanup_fb()`, `drm_vram_mm_debugfs_init()`, `drmm_vram_helper_init()`, and `drm_vram_helper_mode_valid()`. It also defines TTM device funcs and default GEM object funcs using TTM mmap/print helpers.

## Control Flow
VRAM object creation requires `dev->vram_mm`, allocates or driver-creates a GEM/TTM object, initializes GEM shmem metadata, assigns the TTM device, starts placement in system memory, and calls `ttm_bo_init_validate()`. Pinning reserves the TTM BO, selects requested placement flags, validates placement, and increments the TTM pin count. Vmap requires the caller to hold the reservation lock, lazily calls `ttm_bo_vmap()` only when no cached map exists, increments `vmap_use_count`, and returns the cached map. Vunmap only decrements the use count; the actual unmap is delayed until move/delete notification. Plane prepare pins every framebuffer GEM object into VRAM, then calls GEM atomic `prepare_fb` for fencing; cleanup unpins all planes. TTM move callbacks unmap cached mappings before memcpy moves, choose system placement for eviction, reserve VRAM bus addresses, and initialize a range manager for the VRAM aperture.

## State And Persistence Behavior
`drm_vram_mm` persists on `drm_device.vram_mm` and is managed by `drmm_add_action_or_reset()`. Each VRAM BO persists current TTM resource placement, pin count, cached map, vmap use count, and placement arrays. Pinned scanout buffers have stable VRAM offsets returned by `drm_gem_vram_offset()`. Cached vmaps persist across vunmap calls until the BO moves or is deleted, reducing page-table churn.

## Dependencies And Integration Points
The helper integrates GEM with TTM resource managers, TTM TT, TTM move/mmap/vmap APIs, GEM framebuffer helpers, GEM atomic fence helpers, DRM managed cleanup, DRM debugfs, DRM mode validation, and PRIME/GEM object callback infrastructure. Drivers use it through `DRM_GEM_VRAM_DRIVER`, `DEFINE_DRM_GEM_FOPS`, dumb-create callbacks, and plane helper callbacks.

## Risks
VRAM helpers assume `dev->vram_mm` is initialized and warn otherwise. Pin/unpin must be balanced or scanout BOs will remain immovable. `drm_gem_vram_offset()` only makes sense for pinned non-system resources. Cached mappings must be unmapped before TTM moves; moving while `vmap_use_count` is nonzero is warned and unsafe. Plane prepare must unwind partial pins on failure. Mode validation uses a conservative half-VRAM and 32-bit-depth assumption, so it is a general admission check rather than a guarantee under heavy pinning.

## Test Signals
Relevant tests include VRAM MM initialization and cleanup, dumb-buffer create/map, pin/unpin balance through atomic plane updates, scanout offset correctness, TTM eviction from VRAM to system, vmap caching across moves, debugfs `vram-mm`, mode validation for large modes, and memory pressure scenarios where inactive BOs are evicted while active scanout remains pinned.
