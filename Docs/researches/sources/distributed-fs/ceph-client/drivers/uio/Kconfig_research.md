# sources/distributed-fs/ceph-client/drivers/uio/Kconfig

## Purpose
`drivers/uio/Kconfig` declares the Userspace I/O subsystem menu and the build-time configuration options for UIO core and in-tree UIO drivers. It controls whether `/dev/uioN` support and specific PCI, platform, Hyper-V, DFL, and eLBC/GPCM wrappers are built.

## Important Options
`UIO` is the top-level tristate and depends on `MMU`. Child options include `UIO_CIF`, `UIO_PDRV_GENIRQ`, `UIO_DMEM_GENIRQ`, `UIO_AEC`, `UIO_SERCOS3`, `UIO_PCI_GENERIC`, `UIO_NETX`, `UIO_FSL_ELBC_GPCM`, optional `UIO_FSL_ELBC_GPCM_NETX5152`, `UIO_MF624`, `UIO_HV_GENERIC`, `UIO_DFL`, and `UIO_PCI_GENERIC_SVA`. Dependencies gate bus or feature availability, such as `PCI`, `HAS_DMA`, `FSL_LBC`, `HYPERV_VMBUS`, `FPGA_DFL`, and `IOMMU_SVA`.

## Control Flow And State
Kconfig has no runtime flow. Its state is the kernel configuration, which drives compilation and module availability. Help text documents the userspace responsibility common to UIO: kernel code exposes interrupts and memory, while device-specific policy and acknowledgement are typically handled by userspace.

## Dependencies And Integration Points
The options feed `drivers/uio/Makefile` through `CONFIG_*` symbols. They integrate with broader kernel subsystems by depending on bus and hardware framework symbols.

## Risks And Edge Cases
Because UIO exposes device memory and interrupt control to userspace, enabling generic options can be a security and stability decision rather than a pure driver selection. Some help URLs are historical. `UIO_PCI_GENERIC_SVA` advertises Shared Virtual Addressing and should be enabled only when IOMMU SVA support and the target security model are understood.

## Test Signals
Use `olddefconfig`/`allyesconfig` style compile coverage for dependency correctness, module-name checks against `Makefile`, and boot/module-load tests for selected drivers. Configuration tests should verify unavailable dependencies hide or disable the corresponding driver options.
