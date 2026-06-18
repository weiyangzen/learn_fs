# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_test.c

Purpose: BMan self-test module entry point. It invokes configured BMan API tests at module initialization.

Important APIs and functions: `test_init()` conditionally calls `bman_test_api()` when `CONFIG_FSL_BMAN_TEST_API` is enabled. `test_exit()` is empty. The file declares module metadata and uses `module_init()`/`module_exit()`.

Control flow: loading the test module runs the API test once through a one-iteration loop. There is no runtime service after init.

State and persistence: no state is owned here beyond module lifetime. The called test allocates and frees BMan pool resources.

Dependencies and integration: depends on `bman_test.h` and optional `bman_test_api.c` linkage controlled by Kbuild.

Risks and test signals: risks include running destructive hardware API tests on systems where BMan is shared with active users. Test signals are module load logs from `bman_test_api()`, warning-free completion, and clean module unload.
