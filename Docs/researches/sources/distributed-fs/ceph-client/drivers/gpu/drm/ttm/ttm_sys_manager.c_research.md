<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_sys_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_sys_manager.c

Purpose: Implements the minimal TTM system-memory manager. It provides resource objects for `TTM_PL_SYSTEM` without reserving an external address range.

Important APIs/types/functions: `ttm_sys_man_alloc()` allocates a plain `struct ttm_resource` and initializes it. `ttm_sys_man_free()` finalizes and frees it. `ttm_sys_manager_func` supplies the backend hooks. `ttm_sys_man_init()` configures `bdev->sysman`, sets `use_tt = true`, registers it for `TTM_PL_SYSTEM`, and marks it used.

Control flow: Device initialization calls `ttm_sys_man_init()`, which initializes core manager state with size `0` and installs it in the TTM manager table. Later allocations call the simple backend, which relies on `ttm_resource_init()` for common LRU/accounting behavior and carries no start-range allocation.

State and persistence: State lives in `bdev->sysman` and per-resource allocations. It does not maintain a range allocator or persistent metadata beyond common TTM manager usage and LRU lists.

Dependencies and integration points: Uses TTM device/resource/placement APIs and Linux slab allocation. It is the default system-memory path used by TTM BOs with translation tables.

Risks and test signals: The file is small; risk centers on pairing allocation/finalization and ensuring system resources are correctly treated as TT-backed. Tests should allocate/free system-placement BOs and verify manager registration, usage accounting, and LRU behavior through the common TTM resource code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_sys_manager.c -->
