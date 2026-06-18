# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/Kconfig

## Purpose

`Kconfig` declares the Amazon Elastic Fabric Adapter RDMA driver configuration symbol `INFINIBAND_EFA`. It controls whether the EFA provider is built into the kernel, built as `efa.ko`, or omitted.

## Important APIs, Types, and Functions

- `config INFINIBAND_EFA`: tristate user-visible option labelled "Amazon Elastic Fabric Adapter (EFA) support".
- Dependencies: `PCI_MSI`, `64BIT`, little-endian CPU, and `INFINIBAND_USER_ACCESS`.
- Help text: documents that the module name is `efa`.

## Control Flow

There is no runtime control flow. During kernel configuration, this symbol is available only when MSI-capable PCI, 64-bit little-endian architecture, and RDMA userspace access support are enabled. Kbuild then uses the symbol in the EFA Makefile to include or exclude the driver object.

## State and Persistence Behavior

The selected tristate value persists in the kernel `.config` and determines build artifacts. It does not create runtime state by itself.

## Dependencies and Integration Points

This file integrates with the RDMA subsystem Kconfig tree and `drivers/infiniband/hw/efa/Makefile`. The architecture constraints match EFA's userspace/DMA ABI expectations and the generated admin headers' little-endian bitfield use.

## Risks and Edge Cases

- The `!CPU_BIG_ENDIAN` dependency prevents accidental builds on big-endian systems where admin and queue formats are not supported.
- Missing `INFINIBAND_USER_ACCESS` disables the driver even if kernel-only users might exist, reflecting EFA's uverbs-oriented design.
- Kconfig does not explicitly depend on PCI itself here; it relies on `PCI_MSI` implying the needed PCI infrastructure in normal kernel configs.

## Test Signals

Build matrix checks should cover `n`, `m`, and `y` where dependencies are available, verify `efa.ko` is produced for module builds, and confirm the option is hidden on big-endian, non-64-bit, or no-PCI-MSI configs.
