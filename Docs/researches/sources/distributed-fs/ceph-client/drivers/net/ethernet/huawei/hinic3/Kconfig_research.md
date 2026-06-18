# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/Kconfig

## Purpose
Adds the kernel configuration symbol for Huawei third-generation HiNIC adapters. It controls whether the `hinic3` driver is built and documents the supported architecture and module name.

## Important Settings
`config HINIC3` is a tristate option named "Huawei 3rd generation network adapters (HINIC3) support". It depends on little-endian CPUs, `X86 || ARM64 || COMPILE_TEST`, `PCI_MSI`, and `64BIT`. It selects `AUXILIARY_BUS`, `DIMLIB`, and `PAGE_POOL`, signaling that the driver integrates with auxiliary-device infrastructure, dynamic interrupt moderation, and page-pool-backed Rx buffering elsewhere in the hinic3 tree.

## Control Flow And State
Kconfig has no runtime flow, but it gates all object compilation in the hinic3 Makefile. The explicit `!CPU_BIG_ENDIAN` dependency is important because hardware and management structures in this driver are little endian and currently not converted comprehensively.

## Dependencies And Integration Points
The symbol is consumed by the local `Makefile` through `obj-$(CONFIG_HINIC3) += hinic3.o`. Kernel builders and distro configs use this file to expose the driver as built-in, module, or disabled.

## Risks And Test Signals
Risks are mostly build-configuration drift: missing dependencies cause link or runtime failures, while overly strict dependencies reduce test coverage. Test signals include `allmodconfig`, `COMPILE_TEST` on non-target architectures allowed by dependencies, module build/loading, and ensuring selected subsystems are still required by the actual source set.
