# sources/distributed-fs/ceph-client/arch/mips/mm/dma-noncoherent.c

Purpose: architecture DMA synchronization for non-coherent MIPS systems.

Important APIs/functions: `arch_dma_prep_coherent()`, `arch_dma_set_uncached()`, `arch_sync_dma_for_device()`, `arch_sync_dma_for_cpu()`, and `arch_setup_dma_ops()` integrate with Linux DMA mapping. Internal helpers choose writeback, invalidate, or writeback-invalidate by DMA direction.

Control flow: `dma_sync_phys()` walks potentially highmem physical ranges page by page, maps each page with `kmap_atomic()`, and performs cache maintenance for device or CPU ownership. CPU-side post-DMA flush is conditional on `cpu_needs_post_dma_flush()` for CPUs that may speculatively fill stale lines or have MAARs.

State and persistence: only sets `dev->dma_coherent` during setup. No persistent per-mapping state.

Dependencies and integration: depends on cache hooks from `cache.c`/CPU-specific cache files, DMA mapping core, highmem, CPU type detection, and MIPS uncached address bases.

Risks and test signals: wrong direction handling causes data corruption. Test highmem scatterlist segments, each DMA direction, zero/invalid directions hitting BUG, post-DMA invalidate on affected CPUs, and coherent allocation preparation.
