# sources/distributed-fs/ceph-client/drivers/iommu/amd/Makefile

## Purpose

This Makefile defines the AMD IOMMU object set. Core AMD IOMMU support always builds `iommu.o`, `init.o`, `quirks.o`, `ppr.o`, and `pasid.o` when the parent directory is selected. Optional IOMMUFD support adds `iommufd.o` and `nested.o`; optional debugfs support adds `debugfs.o`.

## Integration, Risks, And Test Signals

The object set mirrors the Kconfig feature split: initialization, runtime IOMMU ops, quirks, page request handling, PASID/SVA, nested/IOMMUFD, and debugfs inspection. Risks are object omissions that produce unresolved symbols or disabled features, especially because headers declare functions conditionally used across these files. Test signals include `CONFIG_AMD_IOMMU=y` builds with and without `CONFIG_AMD_IOMMU_IOMMUFD` and `CONFIG_AMD_IOMMU_DEBUGFS`, plus module/builtin link checks for IRQ remapping and PPR/PASID paths.
