# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_bo.c

## Purpose
Implements vmwgfx's TTM/GEM buffer-object wrapper. It handles allocation, placement, pinning, cached kernel mappings, CPU synchronization ioctls, move/swap notifications, resource detachment, dumb-surface cleanup, fencing, and helper lookup/reference operations for user BO handles.

## Important APIs, Types, And Functions
- `vmw_bo_create()` and internal `vmw_bo_init()` allocate a `struct vmw_bo`, initialize GEM private storage, set placement, and call `ttm_bo_init_reserved()`.
- `vmw_bo_pin_in_vram_or_gmr()`, `vmw_bo_pin_in_vram()`, `vmw_bo_pin_in_start_of_vram()`, `vmw_bo_unpin()`, and `vmw_bo_pin_reserved()` manage fixed placement.
- `vmw_bo_map_and_cache_size()`, `vmw_bo_map_and_cache()`, and `vmw_bo_unmap()` implement refcounted cached kernel maps.
- `vmw_user_bo_synccpu_ioctl()` implements CPU access grab/release and optional command-submission blocking.
- `vmw_bo_move_notify()` and `vmw_bo_swap_notify()` tear down mappings and detach resources before incompatible moves.
- `vmw_bo_fence_single()` adds a vmwgfx fence to one BO reservation object.
- `vmw_bo_surface()` discovers an attached or detached surface using dumb-surface, xarray, and rb-tree relationships.

## Control Flow
Creation aligns size, initializes GEM/TTM, sets placement from requested domains, optionally pins, and optionally leaves the BO reserved. Pinning reserves the BO, validates placement, and pins without changing placement afterward. Move notification unmaps VRAM transitions and unbinds resources when moving backup MOBs out of MOB placement. Destruction unmaps, tears down detached resources, detaches dumb-surface MOBs under command-buffer mutex, releases dirty/coherent tracking, releases GEM, and frees the wrapper.

## State, Persistence, Dependencies, And Integration
State is in the TTM BO plus vmwgfx fields: placement arrays, cached kmap, resource rb-tree, detached-resource xarray, eviction priority counters, map and CPU-writer atomics, DX query context pointer, dirty tracking pointer, and dumb-surface link. Dependencies include DRM GEM, TTM placement/reservation/fence APIs, vmwgfx resource binding, and dma-resv. It is used by resource backing MOB management, command buffers, query MOBs, dumb buffers, PRIME/imported BOs, and user ioctls.

## Risks And Test Signals
Risks include leaked cached maps, pin-count mismatches, invalid resource detachment ordering, CPU writer underflow, and BO destruction while dumb-surface/resource links remain. Test signals include placement fallback behavior, pin/unpin across VRAM/GMR/MOB/system, synccpu grab/release with busy fences and `allow_cs`, move-notify detaching MOB-backed resources, dumb BO teardown, and priority adjustment as resources attach/detach.
