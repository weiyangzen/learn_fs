# sources/distributed-fs/ceph-client/drivers/iommu/amd/Kconfig

## Purpose

This fragment configures AMD IOMMU support and optional AMD-specific IOMMUFD and debugfs functionality. The main `AMD_IOMMU` symbol enables AMD-Vi DMA remapping, interrupt-remapping dependencies, PCI ATS/PRI/PASID support, SVA/IOPF, generic page-table infrastructure, and AMD-specific page-table formats.

## Important Symbols And Dependencies

`AMD_IOMMU` is a boolean depending on `X86_64`, `PCI`, `ACPI`, and `HAVE_CMPXCHG_DOUBLE`. It selects `SWIOTLB`, `PCI_MSI`, `PCI_ATS`, `PCI_PRI`, `PCI_PASID`, `IRQ_MSI_LIB`, `MMU_NOTIFIER`, `IOMMU_API`, `IOMMU_IOVA`, `IOMMU_SVA`, `IOMMU_IOPF`, `GENERIC_PT`, `IOMMU_PT`, `IOMMU_PT_AMDV1`, and `IOMMU_PT_X86_64`, plus `IOMMUFD_DRIVER` when `IOMMUFD` is enabled. `AMD_IOMMU_IOMMUFD` depends on both `IOMMUFD` and `AMD_IOMMU` and enables experimental vIOMMU/nested support. `AMD_IOMMU_DEBUGFS` depends on `AMD_IOMMU` and generic `IOMMU_DEBUGFS`.

## Control Flow, Risks, And Test Signals

Kconfig selection determines whether the AMD subdirectory is entered and whether optional nested/debugfs objects are built. The debugfs option is intentionally warning-heavy because it exposes low-level device internals. Risks include under-selecting required core features for PASID/PRI/SVA/IOPF paths, accidentally enabling experimental IOMMUFD features in production configs, and enabling debugfs on hardened systems. Test signals include x86_64 AMD defconfig builds, `CONFIG_AMD_IOMMU=y` boot with IVRS hardware, `CONFIG_AMD_IOMMU_IOMMUFD` compile coverage, and debugfs object inclusion only when both AMD and generic IOMMU debugfs are enabled.
