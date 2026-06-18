<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-direct.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-direct.h

## Purpose
Declares internals of the direct DMA mapping implementation used by DMA core and IOMMU code.

## Important APIs, Types, And Functions
Defines `struct bus_dma_region`, `zone_dma_limit`, address translation helpers `translate_phys_to_dma()`, `translate_dma_to_phys()`, `dma_range_map_min()`, `dma_range_map_max()`, `phys_to_dma_unencrypted()`, `phys_to_dma()`, `dma_to_phys()`, `force_dma_unencrypted()`, `dma_capable()`, and direct allocation/support APIs such as `dma_direct_alloc()`, `dma_direct_free()`, page allocation/free, and `dma_direct_supported()`.

## Control Flow
Direct mapping converts CPU physical addresses to bus DMA addresses using an optional range map, memory encryption address transforms, and device masks. Allocation functions obtain CPU memory, produce a DMA handle, and free it through the paired direct path.

## State And Persistence
State is per-device DMA range maps, DMA masks, bus DMA limits, memory encryption mode, and global DMA zone limits. There is no durable persistence.

## Dependencies And Integration Points
Depends on DMA mapping core, DMA map ops internals, memblock low PFN, memory encryption helpers, SWIOTLB, and architecture overrides for `phys_to_dma`.

## Risks And Edge Cases
Missing range-map translation returns `DMA_MAPPING_ERROR` so `dma_capable()` fails. 32-bit DMA address limitations reject RAM below translated low memory. Encryption and unencrypted bounce buffers require correct address-bit handling. `addr + size - 1` needs valid nonzero sizes.

## Test Signals
Tests should cover devices with and without `dma_range_map`, mask and bus-limit boundaries, encrypted and unencrypted mappings, SWIOTLB fallback, 32-bit DMA address checks, allocation/free pairing, and required-mask computation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-direct.h -->
