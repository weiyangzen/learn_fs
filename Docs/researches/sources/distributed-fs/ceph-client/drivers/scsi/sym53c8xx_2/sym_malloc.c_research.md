# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_malloc.c

## Purpose

`sym_malloc.c` implements the private allocator used by the Symbios/LSI 53C8xx driver for naturally aligned memory, especially DMA-coherent script-visible objects. The allocator is intentionally simple: it obtains page-sized clusters, splits them into power-of-two chunks down to 16 bytes, merges buddies on free, and tracks virtual-to-bus translations for DMA pools.

## Important APIs, Types, And Functions

The internal allocator is `___sym_malloc()` and `___sym_mfree()`. `__sym_calloc2()` wraps allocation with zeroing and optional warnings, and `__sym_mfree()` adds debug logging. `mp0` is the non-DMA pool used to allocate allocator metadata such as `MPOOL` and `VTOB` records.

DMA-specific pool management is handled by `___get_dma_mem_cluster()`, `___free_dma_mem_cluster()`, `___get_dma_pool()`, `___cre_dma_pool()`, and `___del_dma_pool()`. The external functions declared in `sym_hipd.h` are implemented as `__sym_calloc_dma()`, `__sym_mfree_dma()`, and `__vtobus()`.

## Control Flow And State

Allocation rounds the requested size up to the next allocator bucket and searches the corresponding free list. If the bucket is empty, larger buckets are searched until a whole cluster must be obtained with the pool method. A larger block is then split downward by placing buddy halves into lower free lists. Freeing performs the reverse: it searches the current free list for the buddy address, merges when found, and repeats until either the buddy is absent or the full cluster size is reached.

DMA pools are keyed by `m_pool_ident_t`, which is a `struct device *` in this driver. Each DMA cluster allocation creates a `sym_m_vtob` record in `mp0`, fills it through `dma_alloc_coherent()`, hashes it by virtual cluster address, and links it into the pool. `__vtobus()` masks an arbitrary pointer down to the cluster base, finds the `VTOB` record, and returns the coherent DMA address plus the offset.

All public DMA allocation/free/translation operations are serialized by the global `sym53c8xx_lock` spinlock with IRQ save/restore. When `SYM_MEM_FREE_UNUSED` is enabled, completely free clusters are returned immediately and empty DMA pools are deleted.

## Dependencies And Integration Points

The file includes `sym_glue.h` and relies on allocator definitions from `sym_hipd.h`: `m_pool_p`, `m_vtob_p`, bucket sizes, cluster size/mask, `M_GET_MEM_CLUSTER()`, and DMA cluster helpers. It uses Linux `dma_alloc_coherent()`/`dma_free_coherent()` through inline helpers in the header, page allocation for the metadata pool, and `spin_lock_irqsave()` because callers can be in atomic SCSI paths.

Driver code consumes this allocator through macros such as `sym_calloc_dma()`, `sym_mfree_dma()`, and `vtobus()`. The allocator's alignment behavior supports SCRIPTS address arithmetic and table-layout assumptions described in `sym_hipd.h`.

## Risks And Test Signals

`__vtobus()` panics on failed lookup, so every translated pointer must originate from the matching DMA pool and remain inside an allocated cluster. Pointer arithmetic uses `m - a` on `void *`, which depends on compiler behavior accepted by this kernel codebase. The global lock is simple but serializes all sym DMA allocator users; deadlock risk comes from calling into it while holding locks that can be taken by DMA allocation reclaim paths, although allocations use atomic/GFP constraints.

Useful test signals are allocation failure warnings, `DEBUG_ALLOC` traces, stress with many CCB/LCB/table allocations, repeated attach/detach to verify pool deletion, DMA mapping under IOMMU/SWIOTLB, and fault injection around `dma_alloc_coherent()` and metadata allocation.
