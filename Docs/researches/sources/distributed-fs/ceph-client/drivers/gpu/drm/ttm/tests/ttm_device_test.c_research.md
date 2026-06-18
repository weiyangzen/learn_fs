# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_device_test.c

Purpose: KUnit tests for `ttm_device_init()` and `ttm_device_fini()` device-level setup. It verifies that a TTM device is wired to DRM VMA mapping, global state, the system manager, the workqueue, and page pools.

Important APIs and control flow: `ttm_device_init_basic()` allocates a device, initializes it through `ttm_device_kunit_init()`, then checks `funcs`, `wq`, `man_drv[TTM_PL_SYSTEM]`, `sysman.use_tt`, `sysman.use_type`, manager `func`, and `dev_mapping`. `ttm_device_init_multiple()` creates three TTM devices and checks all are on the global device list. `ttm_device_fini_basic()` checks system-manager disabling, empty LRU, and removal from `man_drv`. `ttm_device_init_no_vma_man()` simulates a missing DRM VMA manager and expects `-EINVAL`. Parameterized pool tests verify that `TTM_ALLOCATION_POOL_USE_DMA_ALLOC` controls initialization of per-device DMA pool types.

State and persistence behavior: the tests observe global device-list membership, system-manager use bits, LRU emptiness, pool `dev`, `alloc_flags`, and per-cache/order pool-type fields. There is no durable persistence beyond kernel-global TTM state created and released in each case.

Dependencies and integration: depends on DRM KUnit helpers, `ttm_pool_internal.h`, and `ttm_kunit_helpers`. It tests the integration contract expected by all TTM BO, pool, VM, and swapout code: a valid `vma_manager`, workqueue, system manager, and pool.

Risks and test signals: catches invalid initialization ordering, missing VMA managers, global-list leaks, and pool flag regressions. It does not exercise teardown under live BO load.
