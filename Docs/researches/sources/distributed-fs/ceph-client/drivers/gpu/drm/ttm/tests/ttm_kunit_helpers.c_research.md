# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_kunit_helpers.c

Purpose: shared KUnit scaffolding for TTM tests. It constructs DRM devices, TTM devices, mock BOs, placements, TT objects, and device callback tables so test files can exercise TTM core code without a real GPU driver.

Important APIs and functions: exported helpers include `ttm_device_kunit_init()`, `ttm_device_kunit_init_bad_evict()`, `ttm_bo_kunit_init()`, `ttm_place_kunit_init()`, `dummy_ttm_bo_destroy()`, `ttm_test_devices_basic()`, `ttm_test_devices_all()`, `ttm_test_devices_put()`, `ttm_test_devices_init()`, `ttm_test_devices_all_init()`, and `ttm_test_devices_fini()`. `ttm_dev_funcs` supplies `ttm_tt_simple_create`, `ttm_tt_simple_destroy`, `mock_move`, `ttm_bo_eviction_valuable`, and `mock_evict_flags`; `ttm_dev_funcs_bad_evict` swaps in `bad_evict_flags`.

Control flow: `mock_move()` performs null moves when possible, requests a TT bounce for VRAM to system by returning `-EMULTIHOP`, handles system-to-TT and TT-to-system with null moves, and otherwise delegates to `ttm_bo_move_memcpy()`. `mock_evict_flags()` maps VRAM and system objects to system, TT objects to `TTM_PL_MOCK2`, and MOCK1 to no placement so eviction purges. Device helpers allocate a platform device, DRM device, optional TTM device, and clean it up via KUnit suite hooks.

State and dependencies: maintains `struct ttm_test_devices`, static placement templates, and exported callback tables. It depends on DRM KUnit helpers, GEM object init/release, TTM BO/TT/resource APIs, and KUnit-managed allocations.

Risks and test signals: because it defines the fake driver semantics, changes here can alter many tests. The multihop and eviction callbacks intentionally model edge cases that production drivers must handle.
