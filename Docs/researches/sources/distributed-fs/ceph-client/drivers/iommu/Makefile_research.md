# sources/distributed-fs/ceph-client/drivers/iommu/Makefile

## Purpose

This Makefile maps IOMMU Kconfig symbols to built objects and subdirectories. It is the kbuild integration point for the generic IOMMU core, IOMMUFD, page-table formats, DMA helpers, debug facilities, IRQ remapping, and vendor/platform IOMMU drivers.

## Important Build Rules

Unconditional subdirectories include `arm/` and `iommufd/`. Vendor subdirectories are controlled by symbols such as `CONFIG_AMD_IOMMU`, `CONFIG_INTEL_IOMMU`, `CONFIG_RISCV_IOMMU`, and `CONFIG_GENERIC_PT`. Core objects are gated by `CONFIG_IOMMU_API` (`iommu.o`, `iommu-traces.o`, `iommu-sysfs.o`), `CONFIG_IOMMU_SUPPORT` (`iommu-pages.o`), `CONFIG_IOMMU_DEBUGFS`, `CONFIG_IOMMU_DMA`, page-table format symbols, and platform driver symbols.

## Control Flow And Integration

There is no runtime flow, but object ordering and symbol gating affect link composition. The Makefile must stay aligned with Kconfig symbols and file names; for example `CONFIG_AMD_IOMMU` descends into `amd/`, and `CONFIG_IRQ_REMAP` builds `irq_remapping.o`, which AMD code includes through shared headers.

## State, Risks, And Test Signals

State is limited to build inclusion. Risks are missing objects for selected Kconfig features, stale object names after source renames, and accidental omission of helper objects needed by builtin code. Test signals include `make drivers/iommu/`, architecture defconfigs, `allmodconfig`, module install packaging, and link checks for both builtin and modular driver combinations.
