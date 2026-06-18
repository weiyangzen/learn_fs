# sources/distributed-fs/ceph-client/arch/sparc/mm/swift.S

Purpose: implements MicroSPARC-II/Swift cache, TLB, DMA, and signal-instruction flush routines for the SPARC32 SRMMU operation table.

Important APIs/functions: exports `swift_flush_cache_all()`, `swift_flush_cache_mm()`, `swift_flush_cache_range()`, `swift_flush_cache_page()`, `swift_flush_page_for_dma()`, `swift_flush_page_to_ram()`, `swift_flush_sig_insns()`, `swift_flush_tlb_all()`, `swift_flush_tlb_mm()`, `swift_flush_tlb_range()`, and `swift_flush_tlb_page()`.

Control flow: the active cache path aliases all cache flush variants to a conservative loop that clears data and instruction cache tags. Signal trampoline flushing issues two `flush` instructions. TLB range/mm operations fall back to whole-TLB probe flushes after checking `mm->context`, and page flushes also use a global probe flush in the compiled path.

State and persistence: no owned memory state; all effects are hardware cache/TLB invalidations. The routines observe `mm->context` and VMA `vm_mm` offsets from assembly constants.

Dependencies and integration points: selected by `init_swift()` in `srmmu.c` through `swift_ops`. Depends on SRMMU ASIs, PSR/window macros, page size constants, and `asm-offsets.h` structure offsets.

Risks: Swift has documented cache/TLB coherency errata, so this implementation chooses broad invalidation over fine-grained behavior. Overly narrow flushes could expose stale instructions, stale user mappings, or DMA incoherency; overly broad flushes are performance-costly but safer.

Test signals: run on MicroSPARC-II hardware or emulator with fork/exec, signal delivery, mmap permission changes, packet/DMA I/O, and page-table stress. Validate that no stale executable mappings remain after signal trampoline or text updates.
