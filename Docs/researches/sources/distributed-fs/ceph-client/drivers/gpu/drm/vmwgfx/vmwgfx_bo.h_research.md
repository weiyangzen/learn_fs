# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_bo.h

## Purpose
Declares the vmwgfx buffer-object abstraction built on top of TTM and GEM. It defines placement domains, creation parameters, the `struct vmw_bo` layout, and helper functions used throughout resource, command, framebuffer, and user-handle code.

## Important APIs, Types, And Functions
- `enum vmw_bo_domain` models system, waitable system, VRAM, GMR, and MOB placement preferences.
- `struct vmw_bo_params` supplies domain, busy-domain, TTM type, pin/keep-reservation flags, size, external reservation object, and scatter-gather table.
- `struct vmw_bo` embeds `ttm_buffer_object`, placement arrays, cached kmap state, resource rb-tree, eviction priority counters, detached-resource xarray, map/cpu-writer atomics, DX query context pointer, dirty tracking pointer, and dumb-surface association.
- Public functions cover placement, creation, user unref/synccpu ioctls, pin/unpin, guest pointer extraction, fencing, map/unmap, move/swap notify, detached-resource tracking, attached-surface discovery, user handle lookup, and MOB id extraction.
- Inline helpers adjust eviction priority and wrap GEM get/put for vmwgfx references.

## Control Flow
Callers construct `vmw_bo_params`, create a BO, then use placement helpers before TTM validation. Resource code attaches/detaches resources and updates priority counts. User code gets a ref via `vmw_user_bo_lookup()` and drops it with `vmw_user_bo_unref()`. Move/swap callbacks must be wired into TTM device functions to preserve mapping and resource invariants.

## State, Persistence, Dependencies, And Integration
The header describes in-memory BO state and depends on SVGA registers, DRM/TTM BO and placement APIs, Linux rb-tree types, xarray, and vmwgfx resource/fence forward declarations. There is no persistence. It is the common BO contract for command buffers, resources, dirty tracking, dumb surfaces, query MOBs, CPU blits, and DRM GEM handle lookup.

## Risks And Test Signals
Risks are incorrect domain combinations, priority counter imbalance, misuse of non-refcounted `dx_query_ctx`, stale `dumb_surface`, and forgetting that cached maps are protected by reservation/pinning. Test signals include reference get/put leak checks, priority add/del ordering, map/unmap counts, attached-surface lookup through all three paths, and MOB id use only when the resource is in MOB placement.
