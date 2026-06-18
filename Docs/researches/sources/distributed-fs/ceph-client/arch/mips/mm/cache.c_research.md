# sources/distributed-fs/ceph-client/arch/mips/mm/cache.c

Purpose: common MIPS cache abstraction layer. It declares global cache operation function pointers, implements generic user cacheflush syscall glue, folio/page D-cache maintenance, protection map setup, and selects CPU-family cache initialization.

Important APIs/functions: global pointers such as `flush_cache_all`, `flush_cache_page`, `flush_icache_range`, `flush_data_cache_page`, DMA cache hooks, and vmap flush hooks are assigned by CPU-specific files. `SYSCALL_DEFINE3(cacheflush)` flushes user I-cache ranges. `__flush_dcache_folio_pages()`, `__flush_anon_page()`, and `__update_cache()` handle aliasing and executable mappings. `cpu_cache_init()` dispatches to R3K/R4K/Octeon initializers.

Control flow: folio flushes defer by marking dcache dirty if unmapped, otherwise map pages locally and call selected cache ops. `__update_cache()` clears dirty folios when PTEs enter the TLB and flushes aliases or executable pages.

State and persistence: global function pointers and `_page_cachable_default` are boot-persistent. Folio dcache-dirty flags are runtime page state.

Dependencies and integration: bridges Linux MM core, syscall layer, MIPS CPU feature detection, and CPU-specific cache implementations.

Risks and test signals: uninitialized function pointers or alias mistakes can corrupt user/kernel memory. Test cacheflush syscall access checks, mmap executable writes, anonymous page aliasing, folio dirty clearing, CPU family boot selection, and protection map permission bits.
