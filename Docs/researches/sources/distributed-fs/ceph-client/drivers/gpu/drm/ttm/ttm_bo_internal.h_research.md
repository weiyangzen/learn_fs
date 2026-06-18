# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo_internal.h

Purpose: small private header for internal BO reference helpers used inside TTM implementation files.

Important APIs: defines inline `ttm_bo_get()` as `kref_get(&bo->kref)`, inline `ttm_bo_get_unless_zero()` as guarded `kref_get_unless_zero()`, and declares `ttm_bo_put()`.

Control flow and state: these helpers protect `struct ttm_buffer_object` lifetime during LRU walks, lookups, and asynchronous cleanup. `ttm_bo_get_unless_zero()` is specifically used where objects can be concurrently removed or destroyed, such as LRU eviction traversal and DMA mapping clearing.

Dependencies and integration: includes public `drm/ttm/ttm_bo.h` and is consumed by core files such as `ttm_bo.c` and `ttm_device.c`. The actual release path is implemented in `ttm_bo.c` through `kref_put(..., ttm_bo_release)`.

Risks and test signals: because these are lifetime primitives, misuse can cause use-after-free or leaked BOs. Tests that walk LRUs, delayed-delete BOs, or clear DMA mappings indirectly depend on this contract. The header intentionally exposes minimal API surface, reducing drift risk but making its semantics central to concurrency correctness.
