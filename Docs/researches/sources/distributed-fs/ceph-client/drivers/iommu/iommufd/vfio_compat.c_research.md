# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/vfio_compat.c

## Purpose
`vfio_compat.c` emulates the legacy VFIO type1 container ioctl ABI on top of iommufd. It provides a compatibility IOAS for ABI calls that do not carry an IOAS ID and translates VFIO map/unmap/info/extension operations to iommufd IOAS and `io_pagetable` primitives.

## Important APIs, Types, And Functions
Exported compatibility helpers are `iommufd_vfio_compat_ioas_get_id()`, `iommufd_vfio_compat_set_no_iommu()`, and `iommufd_vfio_compat_ioas_create()`. The iommufd ioctl handler is `iommufd_vfio_ioas()`, and the fallback VFIO dispatcher is `iommufd_vfio_ioctl()`. Internal handlers implement DMA map/unmap, cache-coherency extension checks, `VFIO_SET_IOMMU`, page-size reporting, IOVA capability construction, and DMA availability capability construction.

## Control Flow
Group attach paths create or retrieve a compat IOAS. `IOMMU_VFIO_IOAS_GET/SET/CLEAR` exposes or changes the compat IOAS pointer. `VFIO_IOMMU_MAP_DMA` validates legacy flags, converts them to IOMMU protections, and maps user pages into the compat IOAS. `VFIO_IOMMU_UNMAP_DMA` handles full unmap or range unmap, with extra IOVA cuts when large pages are disabled. `VFIO_IOMMU_GET_INFO` reports page sizes and chained capabilities.

## State And Persistence
The persistent state is `ictx->vfio_ioas` and `ictx->no_iommu_mode`, guarded by the context object xarray lock. The compat IOAS is a normal user-visible IOAS object and is destroyed by regular object release if userspace does not destroy it.

## Dependencies And Integration Points
This file integrates Linux VFIO uapi structures, iommufd IOAS lookup/allocation, `io_pagetable` mapping, reserved IOVA interval traversal, and attached domain page-size discovery. It is called from `main.c` for unknown iommufd ioctls and from VFIO-facing attach paths.

## Risks And Test Signals
Risks include imperfect no-IOMMU emulation, legacy TYPE1 large-page splitting behavior, divergence from VFIO capability sizing, stale compat IOAS pointers, and unsupported dirty-page legacy ABI. Tests should cover VFIO API version, set/check extension combinations, map/unmap all, TYPE1 disabling of large pages, cap buffer truncation/resizing, no-IOMMU exclusion from normal IOAS, and cache-coherency reporting across HWPTs.
