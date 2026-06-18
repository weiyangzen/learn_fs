# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_sys_mgr.c

Purpose: Implements Xe's TTM system-memory manager for TT placement (`XE_PL_TT`), providing simple resource allocation objects for system-backed buffer objects.

Important APIs/types/functions: Internal `struct xe_ttm_sys_node` wraps a `ttm_range_mgr_node` and tracks the TTM BO. Manager callbacks are `xe_ttm_sys_mgr_new`, `xe_ttm_sys_mgr_del`, and `xe_ttm_sys_mgr_debug`, collected in `xe_ttm_sys_mgr_func`. Public API is `xe_ttm_sys_mgr_init`; managed cleanup is `xe_ttm_sys_mgr_fini`.

Control flow: Init computes total RAM via `si_meminfo`, initializes `xe->mem.sys_mgr` with `use_tt = true`, registers it as `XE_PL_TT`, marks it used, and registers a DRM managed cleanup action. Allocation creates a flexible node with one range, initializes the TTM resource, refuses non-temporary allocations when manager usage exceeds size, sets `start` to `XE_BO_INVALID_OFFSET`, and returns the resource. Free finalizes and frees the node. Fini disables the manager, evicts all resources, cleans up, and unregisters the driver manager.

State and persistence behavior: Persistent state lives in `xe->mem.sys_mgr` and TTM accounting. Per-resource state is dynamically allocated and freed with BO resource lifetime. No debug state is emitted because runtime-PM wrapping would be required.

Dependencies and integration points: Depends on TTM placement/range/TT APIs, DRM managed cleanup, system memory info, and Xe BO definitions. Integrated with TTM memory placement and eviction as the system memory backend.

Risks: Usage check compares TTM usage against `man->size << PAGE_SHIFT`; unit consistency depends on TTM manager accounting. Cleanup returns early on eviction failure, which leaves manager cleanup deferred/unfinished. Debug hook is intentionally empty to avoid PM issues.

Test signals: Allocate/free TT-backed BOs, trigger temporary and non-temporary placement paths, force memory pressure/eviction, and unload/remove the driver to verify managed cleanup and no leaks.
