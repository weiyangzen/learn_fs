<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_dma_mapping_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_dma_mapping_test.c

## Purpose
Tests VFIO DMA map/unmap behavior for anonymous and hugepage memory, IOVA range limits, unmap_all, overflow, and optional Intel debugfs page-table validation.

## Important APIs, Types, and Functions
parse_next_value, intel_iommu_mapping_get, iommu_mapping_get, dma_map_unmap, unmap_range, unmap_all, overflow.

## Control Flow
For each IOMMU mode and memory size, mmaps memory, allocates IOVA, maps it, verifies hva2iova, optionally reads Intel debugfs domain_translation_struct to confirm page-table level, unmaps and checks removal; limit fixture maps near last IOVA and tests overflow handling.

## State and Persistence
Creates anonymous/hugetlb mappings and IOMMU mappings; reads debugfs but does not persist data.

## Dependencies and Integration Points
Depends on libvfio, VFIO device, /sys/kernel/debug/iommu/intel for page-size introspection when available, and HugeTLB availability for huge variants.

## Risks and Edge Cases
Hugepage variants skip if pages are unavailable; debugfs parser is Intel-specific and format-sensitive.

## Test Signals
Pass means map/unmap sizes match, IOVA translation is tracked/removed, overflow returns -EOVERFLOW, and page-table level matches mapping size when checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_dma_mapping_test.c -->
