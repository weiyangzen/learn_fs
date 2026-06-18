<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/iommu.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/iommu.h

## Purpose
Public IOMMU abstraction for VFIO selftests supporting legacy VFIO type1, iommufd compatibility, and native iommufd modes.

## Important APIs, Types, and Functions
struct iommu_mode/dma_region/iommu, iommu_init/cleanup, map/unmap/unmap_all, hva2iova, iommu_iova_ranges, FIXTURE_VARIANT_ADD_ALL_IOMMU_MODES.

## Control Flow
Declares wrappers that map/unmap DMA regions and generate fixture variants over five IOMMU modes.

## State and Persistence
struct iommu owns container/iommufd fds, IOAS id, mode pointer, and list of mapped regions.

## Dependencies and Integration Points
Depends on linux/list.h/types.h and libvfio/assert.h; implemented in iommu.c.

## Risks and Edge Cases
Mapped region tracking is in-process only and must stay synchronized with kernel unmaps.

## Test Signals
VFIO DMA tests instantiate all variants through the fixture macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/iommu.h -->
