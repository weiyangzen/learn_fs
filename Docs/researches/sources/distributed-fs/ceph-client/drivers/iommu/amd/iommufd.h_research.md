# sources/distributed-fs/ceph-client/drivers/iommu/amd/iommufd.h

Purpose: this header conditionally exposes AMD iommufd hooks to the main AMD IOMMU driver.

Important APIs, types, and functions: declares `amd_iommufd_hw_info()`, `amd_iommufd_get_viommu_size()`, and `amd_iommufd_viommu_init()` when `CONFIG_AMD_IOMMU_IOMMUFD` is enabled. When disabled, the same names are macros expanding to `NULL`, allowing `amd_iommu_ops` to be initialized without preprocessor branches.

Control flow: included by `amd/iommu.c` and `amd/iommufd.c`. The main ops table consumes these names directly; the IOMMU core sees absent callbacks as unsupported when the config is off.

State and persistence: no runtime state; it is purely a build-time interface boundary.

Dependencies and integration points: depends on the IOMMUFD config symbol and iommufd/IOMMU types visible through including translation units. It is the small compile-time bridge between generic AMD IOMMU support and optional iommufd nesting features.

Risks: the fallback macros must match callback pointer expectations exactly; changing callback signatures without this header would create either build failures or invalid ops-table initializers.

Test signals: build coverage with `CONFIG_AMD_IOMMU_IOMMUFD=y` and disabled is the key signal, plus runtime checking that iommufd callbacks are absent when disabled.
