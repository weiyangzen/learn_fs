<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/iommu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/iommu.c

## Purpose
Implements the VFIO/IOMMU abstraction across legacy VFIO containers and native/compat iommufd.

## Important APIs, Types, and Functions
lookup_iommu_mode, __iommu_map/unmap/unmap_all, __iommu_hva2iova, iommu_iova_ranges, iommu_init/cleanup, vfio_iommu_get_info, iommufd_ioas_alloc.

## Control Flow
Initializes mode-specific fds, maps/unmaps regions with VFIO_IOMMU_MAP_DMA or IOMMU_IOAS_MAP, tracks mappings in a list, queries allowed IOVA ranges from VFIO capability chains or iommufd, sorts/validates ranges, and closes fds on cleanup.

## State and Persistence
Owns container_fd or iommufd, IOAS id, and in-process dma_regions list; kernel owns actual mappings.

## Dependencies and Integration Points
Depends on /dev/vfio/vfio, /dev/iommu, linux/vfio.h, linux/iommufd.h, list helpers, and libvfio assertions.

## Risks and Edge Cases
Mode detection uses nonzero iommufd as native indicator; unmap_all clears in-process list only after ioctl success; capability-chain parsing asserts on malformed/cyclic chains.

## Test Signals
DMA mapping tests cover map/unmap, unmap_all, overflow, and IOVA range allocation across modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/iommu.c -->
