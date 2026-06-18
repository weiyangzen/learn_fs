<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_dma_mapping_mmio_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_dma_mapping_mmio_test.c

## Purpose
Tests whether VFIO can IOMMU-map PCI BAR MMIO mappings, including full, partial, and deliberately misaligned virtual mappings.

## Important APIs, Types, and Functions
largest_mapped_bar, do_mmio_map_test, map_full_bar, map_partial_bar, map_bar_misaligned fixtures over all IOMMU modes.

## Control Flow
Initializes IOMMU/device/allocator, selects largest readable+writable mappable BAR, maps BAR vaddr to an allocated IOVA for legacy VFIO type1 modes and expects failure for native/compat iommufd modes, then unmaps; misaligned case remaps BAR at a chosen offset.

## State and Persistence
Creates BAR mmaps and IOMMU mappings transiently; misaligned test reserves/remaps virtual address space.

## Dependencies and Integration Points
Depends on libvfio, VFIO PCI device, IOMMU modes, page size, and a device with a writable/readable mappable BAR.

## Risks and Edge Cases
Native iommufd expectation is documented as unsupported; future compat behavior may require test update.

## Test Signals
Pass is expected map/unmap success or failure per mode and no leaked mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/vfio_dma_mapping_mmio_test.c -->
