# sources/distributed-fs/ceph-client/arch/sparc/mm/hypersparc.S

Purpose: high-speed HyperSPARC-specific MMU, cache, TLB, page clear, and page copy routines for SPARC32 SRMMU systems.

Important APIs/functions: exports cache flush operations (`hypersparc_flush_cache_all/mm/range/page`, `hypersparc_flush_page_to_ram`, `hypersparc_flush_page_for_dma`, `hypersparc_flush_sig_insns`), TLB flush operations (`hypersparc_flush_tlb_all/mm/range/page`), and `hypersparc_setup_blockops`. Init-only routines `hypersparc_bzero_1page` and `hypersparc_copy_1page` are copied over generic page clear/copy implementations.

Control flow: cache routines flush register windows, read global VAC line/cache size variables, choose whole-user-space flushing for large ranges or page-by-page flushing for smaller ranges, temporarily switch SRMMU context registers, probe mappings, issue ASI_M flush stores, and restore context. TLB routines write SRMMU flush probe addresses at all/mm/range/page granularity. Blockops use HyperSPARC block fill/copy ASIs and `hypersparc_setup_blockops` patches generic routines then flushes the whole I-cache.

State and persistence: mutates hardware cache/TLB/MMU state and, during init, overwrites generic `bzero_1page`/`__copy_1page` code with HyperSPARC-specific implementations. It temporarily changes SRMMU context registers and restores them.

Dependencies/integration: includes SPARC ptrace/PSR/ASI/page/pgtable/SRMMU headers and asm offsets for `mm_context`/`vma->vm_mm`. Selected by HyperSPARC CPU setup as cache/TLB ops.

Risks: ASI operations are hardware-specific and can corrupt active contexts if restore paths fail. Some routines skip work when `mm_context == -1` on non-SMP builds. Self-modifying blockops require exact instruction count limits and I-cache flush. Comments note HyperSPARC flushes require valid mappings for physical tag match.

Test signals: HyperSPARC boot, context-switch stress, mmap/munmap cache coherency, signal trampoline flush, DMA coherency, page clear/copy memory tests, and TLB shootdown tests. Disassembly should confirm copied blockops stay within documented instruction-size limits.
