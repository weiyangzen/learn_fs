# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test.c

## Purpose
Small loadable QMan test module wrapper. It conditionally runs the stash test and API test at module initialization based on `CONFIG_FSL_QMAN_TEST_STASH` and `CONFIG_FSL_QMAN_TEST_API`.

## Important APIs, types, and functions
`test_init` is the module entry point. It runs one iteration, calling `qman_test_stash()` first when enabled and `qman_test_api()` second when enabled, stopping on the first error. `test_exit` is empty because the individual tests perform their own cleanup before returning. The file declares module metadata and uses `module_init`/`module_exit`.

## Control flow and state behavior
State is limited to local `loop` and `err` variables. No persistent module state is retained after tests finish. A nonzero return from either test fails module load, making failures visible to kmod and boot logs.

## Dependencies and integration points
Includes `qman_test.h`, which brings in QMan private definitions and the two test declarations. It depends on the QMan platform and portal drivers having successfully initialized before the module is loaded.

## Risks and test signals
Because tests execute during module load and can call `WARN_ON`, they are intrusive and hardware-dependent. The main signal is whether module insertion succeeds. Kernel logs from the underlying tests provide detail on failed enqueue/dequeue, retirement, DMA mapping, or stash behavior.
