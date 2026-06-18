<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/iova_allocator.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/iova_allocator.c

## Purpose
Implements a simple monotonic IOVA allocator over kernel-reported allowed ranges.

## Important APIs, Types, and Functions
iova_allocator_init, cleanup, alloc, check_add_overflow.

## Control Flow
Copies sorted ranges, then for each allocation aligns within the current range, advances offset or range index, and asserts if no range has space.

## State and Persistence
Allocator owns the ranges array and cursor; no kernel state is changed until caller maps.

## Dependencies and Integration Points
Depends on iommu_iova_ranges and linux/overflow.h.

## Risks and Edge Cases
No deallocation or fragmentation handling; power-of-two assertion rejects arbitrary sizes.

## Test Signals
Used by DMA mapping and MMIO mapping tests to choose legal IOVAs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/iova_allocator.c -->
