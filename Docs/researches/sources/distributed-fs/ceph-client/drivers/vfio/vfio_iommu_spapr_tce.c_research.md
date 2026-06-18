<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio_iommu_spapr_tce.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/vfio_iommu_spapr_tce.c

## Purpose
This file implements the POWER sPAPR TCE VFIO IOMMU backend. It manages TCE table ownership, DMA window creation/removal, v1 and v2 map/unmap behavior, optional preregistered memory, and EEH PE operations for VFIO containers.

## Important APIs, types, and functions
Key state types are `struct tce_container`, `struct tce_iommu_group`, and `struct tce_iommu_prereg`. The exported backend contract is `tce_iommu_driver_ops`, with `open`, `release`, `ioctl`, `attach_group`, and `detach_group`. Important functions include `tce_iommu_enable/disable`, `tce_iommu_register_pages`, `tce_iommu_build`, `tce_iommu_build_v2`, `tce_iommu_clear`, `tce_iommu_create_window`, `tce_iommu_remove_window`, `tce_iommu_take_ownership`, and `vfio_spapr_ioctl_eeh_pe_op`.

## Control flow
Open allocates a container for either `VFIO_SPAPR_TCE_IOMMU` or `VFIO_SPAPR_TCE_v2_IOMMU`. Attach validates table group data, v2 dynamic-window support, v1 single-group restrictions, compatibility with already attached groups, and takes ownership of any existing windows. V1 users enable the container before map/unmap; v2 users register memory and may create/remove dynamic windows. Map finds the TCE table for the IOVA, validates flags and alignment, translates userspace pages to HPAs, exchanges TCE entries, and flushes. Unmap clears TCE entries and releases pinned or preregistered memory references. Release detaches groups, frees VFIO-created tables, unregisters preregions, disables accounting, drops the mm, and frees the container.

## State and persistence behavior
State is per-container and in memory: attached groups, up to `IOMMU_TABLE_GROUP_MAX_TABLES` table pointers, preregistered memory list, owning mm, enabled flag, default-window pending flag, and locked page accounting. V1 accounts locked memory by worst-case DMA window size at enable/disable. V2 uses preregistered memory references and dynamic table allocation accounting.

## Dependencies and integration points
The backend depends on POWER IOMMU/TCE APIs, EEH, VFIO container IOMMU driver registration, user copy helpers, and mm IOMMU preregistration helpers. It integrates with userspace through VFIO sPAPR TCE ioctls and with platform firmware/hypervisor behavior through TCE table group operations.

## Risks and test signals
Risks include strict current-mm ownership, hot map/unmap paths with coarse locked-memory accounting, dynamic window compatibility across groups, and cleanup correctness for preregistered memory. Test signals include v1 enable/disable and single-group enforcement, v2 register/unregister memory, default window creation, dynamic window create/remove, map/unmap alignment failures, EEH operations, group detach while windows exist, and release cleanup with active preregions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio_iommu_spapr_tce.c -->
