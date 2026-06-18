# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/Kconfig

## Purpose
`Kconfig` exposes the mthca low-level InfiniBand HCA driver and its optional verbose debug output in the kernel configuration tree.

## Important APIs, types, and functions
`CONFIG_INFINIBAND_MTHCA` is a tristate depending on PCI and describes support for Mellanox InfiniHost Tavor and Arbel adapters. `CONFIG_INFINIBAND_MTHCA_DEBUG` is a boolean depending on the driver, visible for `EXPERT`, defaulting to enabled, and controls compilation of debug tracing.

## Control flow
The selected config controls whether `ib_mthca.o` is built by the Makefile and whether `mthca_debug_level` and `mthca_dbg()` dynamic debug-style output are compiled in.

## State and persistence
Kconfig state persists in the kernel build configuration. At runtime, the debug option enables a `debug_level` module parameter/sysfs setting used by logging macros.

## Dependencies and integration points
It integrates with the kernel RDMA driver menu, PCI dependency resolution, and `mthca_dev.h` debug macro definitions.

## Risks
Defaulting debug support to `y` under the driver increases code size and leaves verbose paths present unless distributions override it. Missing the PCI dependency would allow invalid builds, but this file declares it.

## Test signals
Build test the driver as `y`, `m`, and disabled; build with and without `CONFIG_INFINIBAND_MTHCA_DEBUG`; verify `debug_level` is present only in debug builds and that `ib_mthca.o` is not built when the tristate is off.
