# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/viommu.c

## Purpose
`viommu.c` implements user-visible virtual IOMMU objects, virtual devices attached to a vIOMMU, and hardware queue objects backed by guest memory. It is the core glue between generic iommufd objects and IOMMU-driver-specific vIOMMU callbacks.

## Important APIs, Types, And Functions
Main entry points are `iommufd_viommu_alloc_ioctl()`, `iommufd_viommu_destroy()`, `iommufd_vdevice_alloc_ioctl()`, `iommufd_vdevice_abort()`, `iommufd_vdevice_destroy()`, `iommufd_hw_queue_alloc_ioctl()`, and `iommufd_hw_queue_destroy()`. Internal helpers include `iommufd_hw_queue_alloc_phys()` for pinning guest queue memory and verifying physical contiguity, and `iommufd_hw_queue_destroy_access()` for access cleanup.

## Control Flow
vIOMMU allocation validates type/flags, gets the physical device and paging HWPT, requires the HWPT to be a nesting parent, allocates a driver-sized object, initializes vdevice and veventq containers, records the IOMMU device, and calls `ops->viommu_init()`. Vdevice allocation validates the device belongs to the same physical IOMMU, serializes under the IOMMU group lock, inserts by virtual ID into the vIOMMU xarray, and calls optional driver init. Hardware queue allocation validates type/length, pins a physically contiguous range from the nesting parent IOAS through an internal access object, then calls the driver physical-queue init callback.

## State And Persistence
`struct iommufd_viommu` persists a reference to the parent paging HWPT, a vdevice xarray, veventq list, IOMMU device pointer, type, and driver ops. `struct iommufd_vdevice` links a physical iommufd device to a virtual ID. `struct iommufd_hw_queue` persists vIOMMU reference, internal access, base IOVA, length, type, and driver destroy callback.

## Dependencies And Integration Points
This file depends on IOMMU driver ops (`get_viommu_size`, `viommu_init`, optional vdevice and queue ops), iommufd access APIs, HWPT nesting state, IOMMU group locking, and object lifetime handling in `main.c`.

## Risks And Test Signals
High-risk areas are object-finalization error paths, group-lock lifetime of `idev->vdev`, stale vdevice xarray entries, hardware queue physical-contiguity assumptions, pinned queue cleanup on driver init failure, and driver-provided size/callback mismatches. Tests should cover unsupported/default types, non-nesting HWPT rejection, mismatched IOMMU devices, duplicate virtual IDs, vdevice destroy while device is pre-destroying, non-contiguous queue memory, queue dependency teardown, and vIOMMU driver init failure cleanup.
