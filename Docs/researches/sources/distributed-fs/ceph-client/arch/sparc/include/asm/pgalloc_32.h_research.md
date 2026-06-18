# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgalloc_32.h

Purpose: SPARC32 SRMMU page-table allocator interface using non-cacheable SRMMU table memory for PGD/PMD/PTE levels.

Important APIs/types/functions: types `page`; functions/helpers `srmmu_free_nocache`, `free_pgd_fast`, `pud_set`, `free_pmd_fast`, `pmd_set`, `pte_alloc_one`, `free_pte_fast`, `pte_free`; macros/constants `_SPARC_PGALLOC_H`, `pgd_free`, `pgd_alloc`, `pud_populate`, `pmd_free`, `__pmd_free_tlb`, `pmd_populate`, `pmd_populate_kernel`, `pte_free_kernel`, `__pte_free_tlb`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_PGALLOC_H`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU paths rather than through standalone functions.

State and persistence behavior: Page table state persists in nocache allocations from `srmmu_get_nocache`; freeing returns memory through `srmmu_free_nocache`, and `pud_set`/`pmd_set` encode SRMMU PTD physical pointers.

Dependencies and integration points: Includes/dependencies: `linux/kernel.h`, `linux/sched.h`, `linux/pgtable.h`, `asm/pgtsrmmu.h`, `asm/vaddrs.h`, `asm/page.h`. Integration points include memory-management, TLB/MMU; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions. Test signals: Fork/exit page-table allocation, TLB-gather freeing, nocache allocator exhaustion, and SRMMU page table alignment are test signals.
