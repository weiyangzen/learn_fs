<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/iova_allocator.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/iova_allocator.h

## Purpose
Public sequential IOVA allocator interface for VFIO tests.

## Important APIs, Types, and Functions
struct iova_allocator, iova_allocator_init/cleanup/alloc.

## Control Flow
Allocates power-of-two sized IOVAs from sorted ranges returned by iommu_iova_ranges.

## State and Persistence
Allocator stores owned range array, current range index, and offset cursor.

## Dependencies and Integration Points
Depends on iommu.h and linux/iommufd.h range type.

## Risks and Edge Cases
No free/reuse support and asserts on exhaustion; size must be power of two.

## Test Signals
DMA mapping tests use returned IOVA values for map/unmap coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/iova_allocator.h -->
