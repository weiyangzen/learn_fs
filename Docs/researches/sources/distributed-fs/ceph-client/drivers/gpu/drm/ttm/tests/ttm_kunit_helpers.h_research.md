# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_kunit_helpers.h

Purpose: header for the TTM KUnit support layer. It exposes test-only memory type constants, callback tables, device bundles, and helper constructors used across the TTM test suite.

Important APIs and types: defines `TTM_PL_MOCK1` and `TTM_PL_MOCK2` as private memory types after `TTM_PL_PRIV`. Declares `ttm_dev_funcs` and `ttm_dev_funcs_bad_evict`. Defines `struct ttm_test_devices` containing the DRM device, backing kernel `struct device`, and optional `struct ttm_device`. Declares helpers for initializing TTM devices, BOs, placements, test device bundles, and KUnit init/fini hooks.

Control flow and dependencies: this header does not implement behavior, but it defines the coupling between test cases and `ttm_kunit_helpers.c`. Consumers include BO, validation, device, resource, pool, and TT tests. It includes DRM driver, TTM device/BO/placement, DRM KUnit helper, and KUnit test headers.

State and integration points: the key state contract is that a `ttm_test_devices` instance may represent only DRM/basic device state or a fully initialized TTM device. Test suites choose `ttm_test_devices_init()` or `ttm_test_devices_all_init()` depending on whether they need a live TTM device before each test.

Risks and test signals: the private memory type values must remain outside core TTM memory type collisions. Prototype drift here breaks all KUnit files at build time, making it an immediate signal for helper API changes.
