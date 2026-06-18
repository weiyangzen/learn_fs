# sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlb_64.h

Purpose: sparc64 TLB-gather integration that triggers pending TLB flush batches for `mmu_gather`, choosing SMP-aware or local flush paths.

Important APIs/types/functions: functions/helpers `smp_flush_tlb_pending`, `smp_flush_tlb_mm`, `__flush_tlb_pending`, `flush_tlb_pending`; macros/constants `_SPARC64_TLB_H`, `do_flush_tlb_mm`, `tlb_flush`, `tlb_needs_table_invalidate`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_TLB_H`, `CONFIG_SMP`, `CONFIG_MMU_GATHER_RCU_TABLE_FREE`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU, SMP paths rather than through standalone functions.

State and persistence behavior: State is pending per-mm TLB batch data and mm context; `tlb_flush` bridges generic MM teardown to sparc64 flush code.

Dependencies and integration points: Includes/dependencies: `linux/swap.h`, `linux/pagemap.h`, `asm/tlbflush.h`, `asm/mmu_context.h`, `asm-generic/tlb.h`. Integration points include memory-management, TLB/MMU, SMP; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: munmap/exit under SMP, batched flush ordering, table invalidation, and lazy MMU mode interactions are key tests.
