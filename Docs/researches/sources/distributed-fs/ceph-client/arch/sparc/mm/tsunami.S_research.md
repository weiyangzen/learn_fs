# sources/distributed-fs/ceph-client/arch/sparc/mm/tsunami.S

Purpose: supplies MicroSPARC-I/Tsunami cache and TLB operations plus an optimized page-copy routine that can be patched into the generic SPARC32 block operation.

Important APIs/functions: exports `tsunami_flush_cache_all()`, `tsunami_flush_cache_mm()`, `tsunami_flush_cache_range()`, `tsunami_flush_cache_page()`, `tsunami_flush_page_to_ram()`, `tsunami_flush_page_for_dma()`, `tsunami_flush_sig_insns()`, `tsunami_flush_tlb_all()`, `tsunami_flush_tlb_mm()`, `tsunami_flush_tlb_range()`, `tsunami_flush_tlb_page()`, and `tsunami_setup_blockops()`.

Control flow: cache flushes check `mm->context` for mm/range/page variants and otherwise clear I-cache and D-cache via ASI flush-clear stores. TLB mm/range flushes perform a full probe flush; page flush temporarily switches the SRMMU context, flushes the selected page, and restores the old context. `tsunami_setup_blockops()` copies the local `tsunami_copy_1page` instruction sequence into `__copy_1page` and flushes caches.

State and persistence: no kernel data ownership beyond self-modifying the block-copy routine at setup. Hardware cache/TLB state is invalidated.

Dependencies and integration points: selected by `init_tsunami()` in `srmmu.c`; depends on SRMMU ASIs, `asm-offsets.h`, SPARC register windows, and `__copy_1page`.

Risks: context restore after page TLB flush is mandatory. The block-copy patch depends on exact instruction range and cache coherency. Broad cache flushing is simple but affects performance.

Test signals: boot Tsunami systems, run mmap/munmap and signal tests, verify DMA coherency, compare page-copy correctness under copy-on-write and fork stress, and check that patched `__copy_1page` executes after setup.
