# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtsrmmu.h

Purpose: SRMMU register and PTE-bit header for SPARC32, with inline assembly accessors for context-table pointer, context id, fault status/address, whole-TLB flush, and raw PTE reads.

Important APIs/types/functions: functions/helpers `srmmu_get_mmureg`, `srmmu_set_mmureg`, `srmmu_set_ctable_ptr`, `srmmu_set_context`, `srmmu_get_context`, `srmmu_get_fstatus`, `srmmu_get_faddr`, `srmmu_flush_whole_tlb`, `srmmu_get_pte`; macros/constants `_SPARC_PGTSRMMU_H`, `SRMMU_MAX_CONTEXTS`, `SRMMU_PTE_TABLE_SIZE`, `SRMMU_PMD_TABLE_SIZE`, `SRMMU_PGD_TABLE_SIZE`, `SRMMU_ET_MASK`, `SRMMU_ET_INVALID`, `SRMMU_ET_PTD`, `SRMMU_ET_PTE`, `SRMMU_ET_REPTE`, `SRMMU_CTX_PMASK`, `SRMMU_PTD_PMASK`, `SRMMU_PTE_PMASK`, `SRMMU_CACHE`, `SRMMU_DIRTY`, `SRMMU_REF`, `SRMMU_NOREAD`, `SRMMU_EXEC`, plus 24 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC_PGTSRMMU_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU paths rather than through standalone functions.

State and persistence behavior: Architectural state is the SRMMU control/context registers, TLB contents, and fault registers addressed through alternate-space loads/stores.

Dependencies and integration points: Includes/dependencies: `asm/page.h`, `asm/thread_info.h`. Integration points include memory-management, TLB/MMU; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions. Test signals: SRMMU boot, context switch, page-fault decoding, TLB flush coverage, and CPU errata around ASI accesses should be tested.
