# sources/distributed-fs/ceph-client/drivers/iommu/amd/iommufd.c

Purpose: AMD-specific iommufd glue. It reports AMD hardware capability data to userspace and initializes per-vIOMMU state used by nested translation.

Important APIs, types, and functions: `amd_iommufd_hw_info()` allocates `struct iommu_hw_info_amd` and fills `efr`/`efr2`; `amd_iommufd_get_viommu_size()` returns the embedding size for `struct amd_iommu_viommu`; `amd_iommufd_viommu_init()` initializes the guest-domain xarray and links the vIOMMU to the parent `protection_domain`; `amd_iommufd_viommu_destroy()` removes that link and destroys the xarray. The local `amd_viommu_ops` currently only supplies `.destroy`.

Control flow: `amd_iommu_ops.hw_info`, `.get_viommu_size`, and `.viommu_init` call into this file. Init converts the parent `iommu_domain` to a `protection_domain`, stores it in the AMD vIOMMU wrapper, initializes `gdomid_array`, publishes ops, and adds the vIOMMU to the parent's `viommu_list` under the parent spinlock. Destroy performs the inverse.

State and persistence: the persistent runtime state is the `gdomid_array` that nested domains use to map guest domain IDs to host domain IDs, plus the list membership in the parent protection domain. The file does not store userspace data itself beyond these in-kernel objects.

Dependencies and integration points: depends on `iommufd_viommu`, UAPI `IOMMU_HW_INFO_TYPE_AMD`, AMD feature globals from init code, and nested allocation in `nested.c`, which relies on `viommu->ops.alloc_domain_nested` being provided elsewhere through AMD iommufd integration.

Risks: lifecycle ordering matters because nested domains may reference `gdomid_array`; destroying a vIOMMU while nested domains still exist would make those references invalid. Hardware-info reporting must stay ABI-compatible with UAPI sizes and feature-bit meanings.

Test signals: useful tests create/destroy AMD vIOMMUs through iommufd, read hardware info with default and AMD-specific types, reject unsupported types, and exercise nested domain allocation/free after vIOMMU init.
