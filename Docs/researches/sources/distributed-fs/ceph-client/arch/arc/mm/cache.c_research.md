# sources/distributed-fs/ceph-client/arch/arc/mm/cache.c

Purpose: implements ARC cache discovery, cache maintenance, DMA cache hooks, I-cache/D-cache synchronization, user cacheflush syscall, SLC and IOC setup.

Important APIs/functions: exposes cache geometry reporting through `arc_cache_mumbojumbo()`, runtime init via `arc_cache_init()`, DMA cache functions `dma_cache_wback_inv()`, `dma_cache_inv()`, `dma_cache_wback()`, icache sync APIs `flush_icache_range()`, `__sync_icache_dcache()`, `__inv_icache_pages()`, `__flush_dcache_pages()`, `flush_cache_all()`, and page helpers `copy_user_highpage()`/`clear_user_page()`.

Control flow: boot reads BCRs into `ic_info`, `dc_info`, `slc_info`, detects IOC and peripheral aperture, validates line sizes, chooses I-cache line-loop implementation, configures IOC if available/enabled, and assigns DMA cache function pointers to L1-only or SLC-aware implementations. Runtime cache ops choose entire, region, or line operations; D-cache ops bracket hardware commands with IRQ disable and status polling; SLC ops serialize with a spinlock.

State and persistence: persistent state includes cache geometry structs, `l2_line_sz`, `ioc_exists`, policy globals `slc_enable`/`ioc_enable`, peripheral aperture `perip_base`/`perip_end`, `_cache_line_loop_ic_fn`, and DMA cache function pointers. Page/folio `PG_dc_clean` tracks delayed D-cache cleanliness for executable mappings.

Dependencies and integration: depends on ARC aux registers, PAE40 state, SLC/IOC registers, `arc_get_mem_sz()`, DMA mapping hooks in `dma.c`, TLB/MMU init, SMP I-cache invalidation, vmalloc-to-physical translation, and the `cacheflush` syscall.

Risks: cache maintenance is hardware-sensitive. Wrong line size, PAE high-tag handling, region end semantics, SLC serialization, or IOC aperture setup can cause data corruption. `cacheflush` currently flushes all caches, which is correct but expensive. IOC is disabled with highmem/PAE constraints.

Test signals: boot cache capability logs, DMA coherency tests with coherent and noncoherent devices, module/kprobe code patching, userspace JIT cacheflush, SMP icache invalidation, highmem/PAE builds, and SLC/IOC platform tests.
