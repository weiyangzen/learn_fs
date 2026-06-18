# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/Makefile

Purpose: This kbuild file lists the KUnit test objects for DRM TTM. It is entered from the parent TTM Makefile when `CONFIG_DRM_TTM_KUNIT_TEST` is enabled.

Important APIs, types, and functions: The only rule appends several objects to `obj-$(CONFIG_DRM_TTM_KUNIT_TEST)`: `ttm_device_test.o`, `ttm_pool_test.o`, `ttm_resource_test.o`, `ttm_tt_test.o`, `ttm_bo_test.o`, `ttm_bo_validate_test.o`, `ttm_mock_manager.o`, and `ttm_kunit_helpers.o`. The first six are test suites; the last two provide shared mock manager/helper infrastructure used by those suites.

Control flow: Kbuild compiles and links these test objects only when the KUnit config is selected. Because the parent directory already gates traversal on the same config, this file is doubly guarded by the config variable.

State and persistence: There is no runtime state. The durable effect is the test build manifest: adding/removing an object changes which TTM behavior receives KUnit coverage and which helper symbols are available to test suites.

Dependencies and integration points: Integrates with Linux kbuild and KUnit. The tests depend on the parent TTM core build products and local mock/helper objects. The SPDX line indicates GPL-2.0 and MIT licensing for the test build file.

Risks: Removing `ttm_mock_manager.o` or `ttm_kunit_helpers.o` can break multiple suites at link time. Adding a new test source without listing it here leaves it unbuilt. Because this file is config-gated, test failures may be invisible in non-KUnit build matrices.

Test signals: Enable `CONFIG_DRM_TTM_KUNIT_TEST` and run the KUnit suites for device, pool, resource, TT, BO, and BO validation. Also run a non-KUnit build to confirm the test directory contributes no objects.
