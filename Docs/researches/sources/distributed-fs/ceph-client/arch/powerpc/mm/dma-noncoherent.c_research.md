# sources/distributed-fs/ceph-client/arch/powerpc/mm/dma-noncoherent.c

Purpose: provides cache synchronization hooks for non-coherent DMA on PowerPC.

Important APIs and control flow: `arch_sync_dma_for_device()` and `arch_sync_dma_for_cpu()` delegate to `__dma_sync_page()`, which converts physical addresses to pages, handles offsets, and synchronizes the requested buffer. `__dma_sync()` chooses invalidate, clean, or flush according to DMA direction and preserves dirty neighboring bytes by falling back to full flush when FROM_DEVICE buffers are not cache-line aligned. `arch_dma_prep_coherent()` flushes newly allocated coherent pages.

State and dependencies: no persistent state; it depends on page-to-virtual mapping, highmem `kmap_atomic()` when required, D-cache range primitives, DMA direction semantics, and local IRQ protection for highmem mappings. Risks are data corruption from invalidating unaligned dirty cache lines, missing highmem segments across page boundaries, and unnecessary cache churn on bidirectional mappings. Test signals include non-coherent DMA drivers, unaligned buffer DMA tests, highmem multi-page buffers, and DMA API debug instrumentation.
