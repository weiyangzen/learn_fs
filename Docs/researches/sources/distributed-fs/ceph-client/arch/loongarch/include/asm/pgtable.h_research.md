<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgtable.h

Purpose: implements LoongArch page-table geometry and PTE/PMD/PUD/P4D helper operations for Linux MM.
Important APIs and types: defines `PGDIR_SHIFT`, `PMD_SHIFT`, `PUD_SHIFT`, `PTRS_PER_*`, `VMALLOC_*`, `MODULES_*`, `vmemmap`, invalid page-table sentinel arrays, folded-level helpers, `pfn_pte`, `pte_pfn`, `pmd_pfn`, swap conversion macros, protection mutators such as `pte_mkdirty`, `pte_wrprotect`, `pte_modify`, THP helpers such as `pmd_trans_huge`, and MMU cache update hooks.
Control flow: most paths are inline transforms. Empty upper-level entries point at invalid tables rather than zero; `pmd_present` special-cases huge mappings; `set_pte` writes atomically and emits an SMP barrier for global mappings; `update_mmu_cache_range` iterates pages and calls `__update_tlb`.
State and persistence: page table entries persist memory permissions, PFNs, huge-page status, swap type/offset, exclusive swap state, and global bits. Clearing a PTE preserves `_PAGE_GLOBAL` while dropping other state.
Dependencies and integration: includes generic folded page-table headers based on `CONFIG_PGTABLE_LEVELS`, `asm/pgtable-bits.h`, sparsemem/fixmap definitions, and Linux MM types. It integrates with TLB refill/update code, vmalloc/module layout, KASAN/KFENCE placement, swap, THP, and highmem.
Risks and test signals: address-space layout math depends on `cpu_vabits`, `vm_map_base`, vmemmap size, and KASAN/KFENCE options. Bad invalid-table handling or swap bit layout breaks faults and reclaim. Signals include boot, `mm` selftests, swap stress, THP, KASAN/KFENCE builds, and TLB shootdown regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgtable.h -->
