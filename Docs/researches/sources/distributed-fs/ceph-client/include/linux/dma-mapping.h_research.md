<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-mapping.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-mapping.h

## Purpose
Declares the public DMA mapping API used by drivers to map CPU memory, pages, scatterlists, resources, and coherent allocations for device DMA.

## Important APIs, Types, And Functions
The header defines DMA attributes, `DMA_MAPPING_ERROR`, `DMA_BIT_MASK()`, `struct dma_iova_state`, mapping-error and debug hooks, page/phys/SG/resource map/unmap APIs, coherent allocation APIs, mask APIs, mapping size queries, noncontiguous allocation/vmap/mmap helpers, optional IOVA APIs, cache sync APIs, page allocation helpers, single-buffer wrappers, sgtable sync/unmap helpers, coherent allocation wrappers, and per-structure `DEFINE_DMA_UNMAP_*` debug fields.

## Control Flow
Drivers map memory for a device with a direction and attributes, check `dma_mapping_error()`, hand the returned DMA address to hardware, synchronize ownership when required, and unmap after device use. Coherent allocation returns CPU and DMA addresses with a longer-lived ownership model. Noncontiguous and IOVA APIs separate address reservation/linking from mapping on IOMMU systems.

## State And Persistence
State is per-mapping DMA address, optional IOVA state, debug records, cache ownership, DMA masks, and allocated coherent/noncoherent pages. There is no persistence beyond live mappings and allocations.

## Dependencies And Integration Points
Depends on devices, pages, scatterlists, VMAs, DMA directions, cache alignment, IOMMU DMA, DMA API debug, and architecture DMA backends. It is used by almost all device drivers.

## Risks And Edge Cases
Mapping vmalloc memory through `dma_map_single_attrs()` is rejected. Attributes such as `SKIP_CPU_SYNC`, `MMIO`, `REQUIRE_COHERENT`, and `CC_SHARED` have strong platform constraints. Direction errors cause stale data or lost writes. SG unmap must use original nents. Noncoherent systems require correct sync calls unless the device can skip sync.

## Test Signals
DMA API debug, noncoherent platform tests, IOMMU and no-IOMMU builds, map/unmap leak checks, SG table round trips, resource/MMIO mappings, coherent mmap, noncontiguous vmap/mmap, mask boundary tests, and invalid vmalloc mapping warnings are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-mapping.h -->
