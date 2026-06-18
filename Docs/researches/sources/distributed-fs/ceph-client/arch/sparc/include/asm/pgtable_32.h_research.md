# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtable_32.h

Purpose: SPARC32 SRMMU page-table definition: address-space layout, PTE/PMD/PGD sizing, atomic PTE updates via `swap`, swap-entry encoding, IO-space PFN encoding, and SRMMU helper hooks.

Important APIs/types/functions: types `vm_area_struct`, `page`, `seq_file`; functions/helpers `load_mmu`, `calc_highpages`, `bootmem_init`, `paging_init`, `srmmu_swap`, `set_pte`, `srmmu_device_memory`, `pmd_pfn`, `__pmd_page`, `pmd_page_vaddr`, `pte_present`, `pte_none`, `__pte_clear`, `pte_clear`, `pmd_bad`, `pmd_present`, plus 33 more; macros/constants `_SPARC_PGTABLE_H`, `PMD_SHIFT`, `PMD_SIZE`, `PMD_MASK`, `PMD_ALIGN`, `PGDIR_SHIFT`, `PGDIR_SIZE`, `PGDIR_MASK`, `PGDIR_ALIGN`, `pte_ERROR`, `pmd_ERROR`, `pgd_ERROR`, `PTRS_PER_PTE`, `PTRS_PER_PMD`, `PTRS_PER_PGD`, `USER_PTRS_PER_PGD`, `PTE_SIZE`, `PAGE_NONE`, plus 28 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC_PGTABLE_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU, locking paths rather than through standalone functions.

State and persistence behavior: Persistent state includes `phys_base`, `pfn_base`, `ptr_in_current_pgd`, SRMMU PTE bits, and page-table entries updated atomically so hardware ref/mod bits stay coherent.

Dependencies and integration points: Includes/dependencies: `linux/const.h`, `asm-generic/pgtable-nopud.h`, `linux/spinlock.h`, `linux/mm_types.h`, `asm/types.h`, `asm/pgtsrmmu.h`, `asm/vaddrs.h`, `asm/oplib.h`, `asm/cpu_type.h`. Integration points include memory-management, TLB/MMU, locking; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions. Test signals: Fault handling, swap PTE round trips, `io_remap_pfn_range`, cache-disabled mappings, and `ptep_set_access_flags` TLB flush behavior are key signals.
