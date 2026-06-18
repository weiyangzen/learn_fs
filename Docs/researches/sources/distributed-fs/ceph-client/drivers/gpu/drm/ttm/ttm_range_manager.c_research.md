<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_range_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_range_manager.c

Purpose: Implements TTM's generic `drm_mm` backed range resource manager for memory types such as VRAM or aperture ranges. It allocates page ranges, records them in `struct ttm_range_mgr_node`, and installs/removes a `struct ttm_resource_manager` into a `ttm_device` memory-type slot.

Important APIs/types/functions: `struct ttm_range_manager` wraps `ttm_resource_manager`, `drm_mm`, and a spinlock. `ttm_range_man_alloc()` allocates a flex node, initializes the resource, selects best-fit or top-down insertion, and inserts one `drm_mm_node`. `ttm_range_man_free()` removes the node and finalizes the TTM resource. `ttm_range_man_intersects()` and `ttm_range_man_compatible()` implement placement-range filtering for eviction and reuse. `ttm_range_man_init_nocheck()` and `ttm_range_man_fini_nocheck()` are exported setup/teardown helpers.

Control flow: initialization allocates the manager, initializes `drm_mm` over `[0, p_size)`, installs the manager with `ttm_set_driver_manager()`, and marks it used. Allocation computes `lpfn`, initializes TTM accounting/LRU state, inserts the DRM MM node under the range-manager spinlock, then publishes the resource. Teardown marks the manager unused, evicts all BOs, tears down `drm_mm`, removes the driver manager pointer, and frees the wrapper.

State and persistence: State is in-memory only: range occupancy lives in `drm_mm`, resource usage/LRU state in the embedded manager, and the node start becomes `res->start`. There is no on-disk persistence.

Dependencies and integration points: Depends on DRM MM, TTM placement/resource APIs, `ttm_bo_evict_first()` through manager teardown, and the device manager table. Backends use this for memory types where a contiguous page range must be reserved.

Risks and test signals: Fragmentation and spinlock hold time are called out in the source. Allocation error paths must pair `ttm_resource_fini()` with `kfree()`. Boundary tests should cover `fpfn/lpfn`, top-down placement, eviction filtering, teardown with live BOs, and `drm_mm_takedown()` after all objects are evicted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_range_manager.c -->
