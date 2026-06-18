# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/Kconfig

## Purpose

This Kconfig entry controls whether the InfiniBand SCSI RDMA Protocol target driver is built. It exposes `CONFIG_INFINIBAND_SRPT` as a tristate option for built-in, module, or disabled SRPT target support.

## Important APIs, Types, and Functions

The symbol is `INFINIBAND_SRPT`, prompted as "InfiniBand SCSI RDMA Protocol target support". It depends on `INFINIBAND`, `INFINIBAND_ADDR_TRANS`, and `TARGET_CORE`.

## Control Flow

There is no runtime control flow. During configuration, the option is visible only when RDMA core address translation and LIO target core are available. Kbuild then uses the symbol to include `ib_srpt.o`.

## State and Persistence Behavior

The only persisted state is kernel build configuration. If enabled as a module, the resulting module is the SRPT target driver; if built in, it links into the kernel image.

## Dependencies and Integration Points

The dependency list matches `ib_srpt.c` integrations with RDMA/IB core, RDMA address management, and target-core fabric APIs. The help text documents SRP target behavior and notes RDMA transport coverage.

## Risks and Edge Cases

Dependency drift is the main risk: if `ib_srpt.c` starts requiring additional kernel subsystems, the Kconfig gate must be updated or build failures will appear in partial configurations. The help text mentions iWARP even though device-management MAD behavior is InfiniBand-specific and RDMA CM support is controlled at runtime/configfs.

## Test Signals

Build matrix checks should cover `CONFIG_INFINIBAND_SRPT=y`, `=m`, and disabled, plus dependency-disabled combinations for `INFINIBAND`, `INFINIBAND_ADDR_TRANS`, and `TARGET_CORE`.
