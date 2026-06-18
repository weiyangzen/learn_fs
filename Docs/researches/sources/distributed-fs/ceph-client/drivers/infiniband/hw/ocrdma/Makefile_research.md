# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/Makefile

Purpose: builds the ocrdma RoCE driver module and wires in its source objects.

Important APIs/types/functions: adds the be2net include path with `ccflags-y`, builds `ocrdma.o` when `CONFIG_INFINIBAND_OCRDMA` is enabled, and composes it from `ocrdma_main.o`, `ocrdma_verbs.o`, `ocrdma_hw.o`, `ocrdma_ah.o`, and `ocrdma_stats.o`.

Control flow: kernel kbuild evaluates `obj-$(CONFIG_INFINIBAND_OCRDMA)` and links the listed `ocrdma-y` objects into one module/built-in object.

State and persistence: build metadata only; no runtime state.

Dependencies and integration: depends on headers under `drivers/net/ethernet/emulex/benet`, especially `be_roce.h`, and integrates with the RDMA hw driver directory build.

Risks: include path drift between be2net and ocrdma can break builds. Adding a source file without updating `ocrdma-y` would omit it from the driver.

Test signals: kernel `M=drivers/infiniband/hw/ocrdma` builds, allmodconfig, and dependency builds after be2net header changes.
