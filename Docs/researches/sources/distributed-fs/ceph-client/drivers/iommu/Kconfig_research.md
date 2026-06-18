# sources/distributed-fs/ceph-client/drivers/iommu/Kconfig

## Purpose

This Kconfig file is the main configuration surface for the Linux IOMMU subsystem. It defines generic IOMMU support, page-table format options, debugfs and debug-pagealloc options, default domain policy, common DMA/SVA/IOPF support, and a broad set of architecture/vendor IOMMU drivers.

## Important Symbols And Dependencies

Core symbols include `IOMMU_IOVA`, `IOMMU_API`, `IOMMUFD_DRIVER`, and `IOMMU_SUPPORT`. Generic page-table support is selected through `IOMMU_IO_PGTABLE`, with concrete formats such as `IOMMU_IO_PGTABLE_LPAE`, `IOMMU_IO_PGTABLE_ARMV7S`, and `IOMMU_IO_PGTABLE_DART`; LPAE KUnit and ARMv7s selftests provide validation hooks. `IOMMU_DEBUGFS` depends on `DEBUG_FS`.

The default-domain `choice` selects strict translated DMA, lazy translated DMA, or passthrough, with architecture-specific defaults. `IOMMU_DMA` selects DMA helper dependencies and the IOVA allocator on ARM64, X86, and S390. `IOMMU_SVA` and `IOMMU_IOPF` provide shared virtual addressing and page-fault support selected by drivers such as AMD IOMMU.

The file sources vendor submenus for AMD, ARM, Intel, IOMMUFD, and RISC-V, then defines platform drivers such as IRQ remapping, OMAP, Rockchip, Sun50i, Tegra SMMU, Exynos, Renesas IPMMU, Apple DART, s390, MediaTek, Hyper-V, virtio-iommu, Unisoc, and debug-pagealloc.

## Control Flow And Integration

Kconfig controls compilation and selected capabilities. Many symbols are selected by platform drivers rather than directly by users, so dependency correctness determines whether the IOMMU core, DMA mapping layer, page-table allocators, debugfs support, IRQ remapping, and vendor drivers are built together. The final `source "drivers/iommu/generic_pt/Kconfig"` exposes generic page-table infrastructure outside the `IOMMU_SUPPORT` block.

## State, Risks, And Test Signals

There is no runtime state in this file, but its symbols shape boot-time DMA isolation and security posture. The default-domain choice has direct security/performance tradeoffs: lazy invalidation and passthrough can improve performance while reducing isolation. Dependency errors can create build failures, missing DMA ops, absent page-table formats, or runtime feature gaps. Test signals include broad `allyesconfig`, `allmodconfig`, `randconfig`, architecture defconfigs, KUnit page-table tests, boot tests for strict/lazy/passthrough defaults, and verification that selected drivers pull in required core symbols.
