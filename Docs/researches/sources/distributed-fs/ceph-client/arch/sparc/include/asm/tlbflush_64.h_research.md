# sources/distributed-fs/ceph-client/arch/sparc/include/asm/tlbflush_64.h

Purpose: sparc64 TLB/TSB flush declarations and lazy batch structure, including per-CPU `tlb_batch`, kernel/user TSB flushes, page/range/mm flushes, and SMP shootdowns.

Important APIs/types/functions: types `tlb_batch`; functions/helpers `flush_tsb_kernel_range`, `flush_tsb_user`, `flush_tsb_user_page`, `flush_tlb_mm`, `flush_tlb_page`, `flush_tlb_range`, `flush_tlb_kernel_range`, `flush_tlb_pending`, `arch_enter_lazy_mmu_mode`, `arch_flush_lazy_mmu_mode`, `arch_leave_lazy_mmu_mode`, `__flush_tlb_all`, `__flush_tlb_page`, `__flush_tlb_kernel_range`, `global_flush_tlb_page`, `smp_flush_tlb_kernel_range`, plus 1 more; macros/constants `_SPARC64_TLBFLUSH_H`, `TLB_BATCH_NR`, `global_flush_tlb_page`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_TLBFLUSH_H`, `CONFIG_SMP`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU, SMP paths rather than through standalone functions.

State and persistence behavior: State persists in per-CPU `tlb_batch`, mm context IDs, TSB entries, and lazy MMU mode batching until `flush_tlb_pending`.

Dependencies and integration points: Includes/dependencies: `asm/mmu_context.h`. Integration points include memory-management, TLB/MMU, SMP; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: TLB shootdown races, huge-page flushes, context recycle, kernel vmalloc flushes, and SMP page invalidation are signals.
