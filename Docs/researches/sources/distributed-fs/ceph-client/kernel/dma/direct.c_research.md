# sources/distributed-fs/ceph-client/kernel/dma/direct.c

## Purpose
This file implements the generic direct DMA mapping backend for systems that can translate CPU physical addresses directly to device DMA addresses, with fallbacks for SWIOTLB bounce buffering, CMA, coherent atomic pools, non-coherent remapping, encryption/decryption, and PCI P2PDMA.

## Important APIs, Types, And Functions
Important APIs include `dma_direct_get_required_mask()`, `dma_coherent_ok()`, `dma_direct_alloc()`, `dma_direct_free()`, `dma_direct_alloc_pages()`, `dma_direct_free_pages()`, `dma_direct_map_sg()`, `dma_direct_unmap_sg()`, sync helpers, `dma_direct_get_sgtable()`, `dma_direct_can_mmap()`, `dma_direct_mmap()`, `dma_direct_supported()`, `dma_direct_all_ram_mapped()`, `dma_direct_max_mapping_size()`, `dma_direct_need_sync()`, and `dma_direct_set_offset()`. Helpers choose GFP zones, allocate pages, use SWIOTLB, and encrypt/decrypt memory for confidential-computing shared DMA.

## Control Flow
Allocation aligns size, handles `DMA_ATTR_NO_KERNEL_MAPPING`, delegates to arch allocation for non-coherent devices when configured, tries global coherent pools, decides whether to remap or mark memory uncached, uses atomic pools when blocking is not allowed, then allocates pages from SWIOTLB/CMA/buddy and prepares them for coherent DMA. Free reverses those choices, including pool release, vunmap, clearing uncached mappings, re-encryption, and freeing pages. SG mapping handles PCI P2PDMA bus-address cases, direct physical mappings, SWIOTLB fallback, and unwind on failure. Mmap first tries per-device/global coherent pools, then remaps PFNs. Range-map helpers validate whether all RAM is covered by a device DMA range map.

## State, Persistence, And Dependencies
Global state is `zone_dma_limit` and optional device `dma_range_map` allocated by `dma_direct_set_offset()`. Most behavior is derived from `struct device` masks, coherence, bus limits, ranges, SWIOTLB state, and attributes. Dependencies include CMA, SWIOTLB, DMA pools, arch cache sync hooks, memory encryption helpers, vmalloc/remap APIs, scatterlists, PCI P2PDMA, and system RAM walking.

## Integration Points
The generic DMA ops layer calls these routines for direct mapping. `direct.h` exposes inline single-map/unmap/sync helpers. `coherent.c` and `contiguous.c` provide pool/CMA services used here. SWIOTLB and arch hooks provide bounce and cache maintenance behavior.

## Risks
Mask and bus-limit checks are security- and data-integrity-critical. Non-coherent cache sync ordering must match map/unmap direction. Error paths can intentionally leak pages if memory cannot be re-encrypted. `DMA_ATTR_NO_KERNEL_MAPPING` returns a page cookie rather than a CPU pointer. P2PDMA cases must not be bounced or translated incorrectly.

## Test Signals
Test coherent and non-coherent allocation/free, atomic pool allocation, SWIOTLB forced bounce, DMA mask overflow warnings, CMA fallback, highmem remap, encryption/decryption paths, `NO_KERNEL_MAPPING`, SG mapping unwind, PCI P2PDMA modes, mmap bounds, range-map coverage, and `dma_direct_need_sync()`.
