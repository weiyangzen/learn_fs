# sources/distributed-fs/ceph-client/arch/sh/kernel/dma-coherent.c

Purpose: implements SH cache maintenance hooks for coherent DMA allocation and DMA synchronization.

Important APIs and control flow: `arch_dma_prep_coherent()` purges the cache range backing a page allocation. `arch_sync_dma_for_device()` converts a physical address through SH cache-operation virtual addressing and selects invalidate, writeback, or purge based on DMA direction; invalid directions call `BUG()`.

State, dependencies, and risks: there is no persistent state. Dependencies include SH cacheflush primitives, `phys_to_virt()`, `sh_cacheop_vaddr()`, and Linux DMA API direction semantics. Risks are aliasing mistakes on cached/uncached mappings, over/under-flushing for device-visible buffers, and fatal BUGs on bad callers. Test signals are DMA map/unmap stress, bidirectional transfers with cacheline sharing, and driver data-corruption checks.
