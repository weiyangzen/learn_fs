# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_region_ttm.c

Purpose: connects i915 memory regions to DRM TTM device/resource-manager infrastructure and converts TTM allocations to i915 scatter-gather tables.

Important APIs/functions: exports `intel_region_ttm_device_init/fini`, `intel_region_to_ttm_type`, `intel_region_ttm_init/fini`, `intel_region_ttm_resource_to_rsgt`, and `intel_region_ttm_resource_free`; selftest builds also expose `intel_region_ttm_resource_alloc`.

Control flow: device init creates `dev_priv->bdev` with i915 TTM funcs. Region init maps i915 memory type/instance to TTM placement type and initializes a buddy manager sized by region and IO aperture. Fini cleans manager move fences, repeatedly flushes free objects and drains workqueues until the region object list empties, then tears down the buddy manager. Resource conversion chooses range-manager or buddy-resource SG table construction.

State and persistence: TTM state lives in `dev_priv->bdev` and `mem->region_private` as a `ttm_resource_manager`. Allocated resources remain until explicitly freed or manager teardown.

Dependencies and integration: depends on TTM device/range manager, i915 TTM buddy manager, GEM TTM driver funcs, memory-region abstraction, and i915 refcounted SG table helpers.

Risks: teardown can return `-EBUSY` and intentionally leave region memory allocated if objects leaked. Mapping instance to `TTM_PL_PRIV + instance` must stay below `TTM_NUM_MEM_TYPES`. Selftest allocation deliberately detaches `res->bo` to expose misuse.

Test signals: TTM-backed local memory tests, mock-region selftests, object leak detection during region fini, SG-table conversion validation, and eviction/migration workloads.
