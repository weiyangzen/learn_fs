# sources/distributed-fs/ceph-client/arch/microblaze/mm/consistent.c

Purpose: prepares coherent DMA allocations by flushing cache lines backing the allocated pages.

Important APIs and state: `arch_dma_prep_coherent(struct page *page, size_t size)` converts the page to a physical address and calls `flush_dcache_range()`.

Control flow: single straight-line operation over `[page_to_phys(page), +size)`.

State and persistence: no persistent state; cache side effects make memory coherent for device use.

Dependencies and integration: called by generic DMA allocation code; depends on `cache.c` implementation and valid page-to-phys mapping.

Risks and test signals: only flushes, not invalidates, so coherency assumptions must match DMA API expectations. Test coherent DMA allocations, write-back cache systems, and multi-page size ranges.
