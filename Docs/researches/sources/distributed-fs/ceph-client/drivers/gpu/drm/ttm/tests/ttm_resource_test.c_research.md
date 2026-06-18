# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_resource_test.c

Purpose: KUnit tests for `ttm_resource`, `ttm_resource_manager`, and the system manager allocation/free callbacks.

Important APIs and control flow: setup creates a full TTM test device and a mock BO/place. `ttm_resource_init_basic()` parameterizes system, VRAM, private memory type, and placement flags, optionally installs a test manager, and verifies resource fields, bus defaults, manager usage accounting, and LRU insertion. `ttm_resource_init_pinned()` verifies pinned resources move to the device `unevictable` list. `ttm_resource_fini_basic()` verifies LRU removal and usage decrement. Manager tests cover `ttm_resource_manager_init()`, `ttm_resource_manager_usage()`, and `ttm_resource_manager_set_used()`. System-manager tests call `man->func->alloc()` and `free()` for `TTM_PL_SYSTEM`.

State and dependencies: state includes `struct ttm_resource_test_priv`, mock resource managers, `bo->priority`, manager `usage`, LRU lists, the device `unevictable` list, placement flags, and resource bus fields. It depends on TTM resource APIs, KUnit helpers, and the system manager installed by `ttm_device_init()`.

Integration points: resource initialization is a foundational contract for BO validation, eviction, VM mappings, and pool accounting. The tests verify that resource manager accounting and LRU membership are consistent as BOs move.

Risks and test signals: assertions expose regressions in usage accounting, pinned/unevictable routing, resource bus defaults, and system manager free behavior. It does not cover full cursor or bulk-move iteration, which are mainly exercised by BO tests.
