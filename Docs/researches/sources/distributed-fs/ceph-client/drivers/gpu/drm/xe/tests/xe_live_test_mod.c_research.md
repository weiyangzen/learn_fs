# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_live_test_mod.c

## Purpose

`xe_live_test_mod.c` is the module glue that registers live Xe KUnit suites requiring real hardware or live driver devices.

## Important APIs, Types, and Functions

- External suite declarations: `xe_bo_test_suite`, `xe_bo_shrink_test_suite`, `xe_dma_buf_test_suite`, `xe_migrate_test_suite`, `xe_mocs_test_suite`, and `xe_guc_g2g_test_suite`.
- `kunit_test_suite(...)` registrations for each live suite.
- Module metadata and `MODULE_IMPORT_NS("EXPORTED_FOR_KUNIT_TESTING")`.

## Control Flow

When the live test module is loaded, KUnit sees the registered suites and runs their parameterized live-device tests according to KUnit selection.

## State and Persistence Behavior

The file owns no test state. It affects module-level suite registration and imports the namespace needed to access exported-for-KUnit symbols.

## Dependencies and Integration Points

It depends on the live suites being linked/exported and on KUnit/module infrastructure. It is built through the tests `Makefile` as `xe_live_test.o`.

## Risks and Edge Cases

- Missing externs or suite exports cause link failures.
- Registering live suites in the wrong module can make hardware-affecting tests run unexpectedly.
- Suite discovery depends on this file staying aligned with live test sources.

## Test Signals

Signals include module load success, KUnit discovery of all live suites, and no missing namespace/link errors.
