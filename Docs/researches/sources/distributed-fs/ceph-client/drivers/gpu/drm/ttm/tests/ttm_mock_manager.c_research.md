# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_mock_manager.c

Purpose: KUnit-only resource managers for synthetic GPU memory domains. The main mock manager uses `gpu_buddy` to allocate address-space blocks, while bad and busy managers inject allocation failures.

Important APIs and functions: exports `ttm_mock_manager_init()`, `ttm_mock_manager_fini()`, `ttm_bad_manager_init()`, `ttm_busy_manager_init()`, and `ttm_bad_manager_fini()`. `ttm_mock_manager_alloc()` creates a `ttm_mock_resource`, initializes the embedded `ttm_resource`, translates placement flags into `GPU_BUDDY_TOPDOWN_ALLOCATION` or `GPU_BUDDY_CONTIGUOUS_ALLOCATION`, and allocates blocks from `gpu_buddy` under a mutex. `ttm_mock_manager_free()` frees buddy blocks, finalizes resource usage/LRU state, and releases memory.

Control flow: initialization allocates a manager, initializes `gpu_buddy`, sets `base->func`, `use_tt`, registers the manager in the TTM device with `ttm_set_driver_manager()`, and marks it used. Finalization evicts all resources, marks unused, destroys the buddy allocator, and unregisters the manager. Bad managers install `alloc` callbacks returning `-ENOSPC` or `-EBUSY` and a permissive `compatible` callback.

State and dependencies: state lives in `struct ttm_mock_manager` with a resource manager, buddy allocator, default page size, and lock. It depends on `gpu_buddy`, TTM resource manager APIs, and placement flags.

Risks and test signals: `ttm_mock_manager_fini()` returns early on eviction failure, which can intentionally expose cleanup issues. Error-injection managers are central to validation tests for fallback and eviction failure.
