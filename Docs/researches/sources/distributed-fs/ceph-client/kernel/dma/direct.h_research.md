# sources/distributed-fs/ceph-client/kernel/dma/direct.h

## Purpose
This private header exposes the direct DMA backend interface and provides inline fast paths for single physical mappings, unmaps, and cache synchronization. It centralizes SWIOTLB, DMA attribute, device-capability, and non-coherent cache maintenance decisions used by the generic mapping layer.

## Important APIs, Types, And Functions
Declarations cover SG table creation, mmap support, sync need checks, SG map/unmap/sync, range coverage, and max mapping size. Inline functions include `dma_direct_sync_single_for_device()`, `dma_direct_sync_single_for_cpu()`, `dma_direct_map_phys()`, and `dma_direct_unmap_phys()`.

## Control Flow
`dma_direct_map_phys()` chooses between forced SWIOTLB bounce, rejecting incompatible `DMA_ATTR_CC_SHARED`, direct MMIO addresses, unencrypted translation, normal `phys_to_dma()`, or SWIOTLB fallback when the device cannot address the range or kmalloc bounce is needed. It performs device sync for non-coherent mappings unless skipped. `dma_direct_unmap_phys()` skips MMIO/required-coherent cases, syncs back for CPU unless requested otherwise, then asks SWIOTLB to unmap. Sync helpers translate DMA address to physical and call SWIOTLB and architecture cache hooks in the proper direction.

## State, Persistence, And Dependencies
The header holds no independent state. It depends on `linux/dma-direct.h`, `linux/memremap.h`, SWIOTLB APIs, device coherence and masks, DMA attributes, and architecture sync hooks.

## Integration Points
`direct.c` implements the declared non-inline functions. Generic DMA map ops and wrappers can use the inline helpers for low-overhead direct single mapping.

## Risks
Attribute combinations are subtle: MMIO, required coherent, skip CPU sync, and confidential-computing shared mappings change whether SWIOTLB or direct translation is legal. Incorrect flush argument use can miss cache maintenance. Overflow warning uses device mask and bus limit and must not dereference an unset mask in invalid device setup.

## Test Signals
Test direct map/unmap with coherent and non-coherent devices, `DMA_ATTR_SKIP_CPU_SYNC`, forced SWIOTLB, `DMA_ATTR_MMIO`, `DMA_ATTR_REQUIRE_COHERENT`, `DMA_ATTR_CC_SHARED`, kmalloc bounce thresholds, and cache sync calls in both directions.
