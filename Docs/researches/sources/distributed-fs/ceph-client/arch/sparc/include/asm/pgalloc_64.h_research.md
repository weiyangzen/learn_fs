# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgalloc_64.h

Purpose: sparc64 page-table allocator using `pgtable_cache`, page-backed PTE allocations, deferred frees, and SMP-safe TLB table removal.

Important APIs/types/functions: types `mmu_gather`; functions/helpers `__p4d_populate`, `pgd_free`, `__pud_populate`, `pud_free`, `pmd_free`, `pte_alloc_one`, `pte_free_kernel`, `pte_free`, `pte_free_defer`, `pgtable_free`, `tlb_remove_table`, `pgtable_free_tlb`, `__tlb_remove_table`, `__pte_free_tlb`; macros/constants `_SPARC64_PGALLOC_H`, `p4d_populate`, `pud_populate`, `pte_free_defer`, `pmd_populate_kernel`, `pmd_populate`, `__pmd_free_tlb`, `__pud_free_tlb`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_PGALLOC_H`, `CONFIG_SMP`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU, SMP paths rather than through standalone functions.

State and persistence behavior: State is split between slab-backed upper tables, page-backed PTE tables, and `mmu_gather` deferred-free entries with a low-bit tag identifying page tables.

Dependencies and integration points: Includes/dependencies: `linux/kernel.h`, `linux/sched.h`, `linux/mm.h`, `linux/slab.h`, `asm/spitfire.h`, `asm/cpudata.h`, `asm/cacheflush.h`, `asm/page.h`. Integration points include memory-management, TLB/MMU, SMP; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: MM teardown under SMP, THP split/free, RCU/deferred PTE free, and pgtable cache lifetime should be covered.
