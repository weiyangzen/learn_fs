<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_resource.c

Purpose: Provides the common TTM resource-management core: resource initialization/finalization, allocation/free dispatch, LRU and bulk-move maintenance, resource-manager iteration, usage/debug output, cgroup device-memory charging, and kmap iterators for IO memory.

Important APIs/types/functions: `ttm_resource_init()` and `ttm_resource_fini()` maintain resource fields, LRU membership, and manager usage. `ttm_resource_alloc()` and `ttm_resource_free()` dispatch to backend `man->func` hooks and integrate `dmem_cgroup` charging. `ttm_lru_bulk_move_*()` manages bulk LRU tail moves by memory type and BO priority. `ttm_resource_cursor_*()` and `ttm_resource_manager_first()/next()` implement robust LRU iteration around hitch entries and bulk-move cursor tracking. `ttm_resource_manager_init()`, `ttm_resource_manager_evict_all()`, `ttm_resource_manager_usage()`, and `ttm_resource_manager_debug()` provide manager lifecycle and diagnostics. Kmap helpers include `ttm_kmap_iter_iomap_init()` and `ttm_kmap_iter_linear_io_init()/fini()`.

Control flow: Allocation first charges a dmem pool if configured, invokes the concrete manager allocator, stores the returned pool in `res->css`, and attaches eligible resources to the BO's bulk move under `bdev->lru_lock`. Free removes bulk tracking, calls the backend free hook, clears the caller pointer, and uncharges. LRU moves route pinned or swapped resources to `bdev->unevictable`, otherwise to a priority LRU or bulk tail. Manager eviction repeatedly calls `ttm_bo_evict_first()` until no entries remain, then waits for outstanding move fences.

State and persistence: Persistent runtime state includes manager usage, per-priority LRU lists, unevictable list entries, bulk-move ranges, cursor hitch positions, eviction fences, resource bus mappings, and optional dmem cgroup charge handles. All state is in kernel memory and protected by `lru_lock`, manager locks, or reservation assertions.

Dependencies and integration points: Integrates TTM BO/resource/placement APIs, DRM reservation fences, DRM printer/debugfs, scatter-gather DMA, `io_mapping`, `iosys_map`, and Linux cgroup device-memory accounting. Resource backends such as range and system managers rely on this common code.

Risks and test signals: Main risks are LRU corruption, usage underflow, cursor invalidation during bulk moves, missing dmem uncharge on allocation failure, IO mapping leaks, and misuse of reservation/lru locks. Test signals include KUnit/exported-test coverage for allocation/free, eviction, iteration across priority lists, bulk move add/delete, cgroup charge failure, and linear IO map fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_resource.c -->
