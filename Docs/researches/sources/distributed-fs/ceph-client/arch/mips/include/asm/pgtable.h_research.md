# sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable.h

### Purpose
`pgtable.h` is the main MIPS page-table API used by generic Linux MM. It combines the 32-bit or 64-bit geometry with bit definitions, defines kernel/user page protections, PTE/PMD mutation helpers, hardware table-walker control, cache/TLB update hooks, hugepage/THP support, noncached/write-combine protections, and GUP/vmalloc aliasing policy.

### Important APIs, Types, And Functions
Important exports include `PAGE_SHARED`, `PAGE_KERNEL`, `PAGE_KERNEL_NC`, `PAGE_KERNEL_UNCACHED`, `_page_cachable_default`, `__update_cache`, `ZERO_PAGE`, `pagetable_init`, `pmd_phys`, `pmd_pfn`, `pmd_page`, `htw_stop`, `htw_start`, `pte_none`, `pte_present`, `pte_no_exec`, `set_pte`, `pte_clear`, `set_ptes`, `pte_write`, `pte_dirty`, `pte_young`, `pte_wrprotect`, `pte_mkclean`, `pte_mkold`, `pte_mkwrite_novma`, `pte_mkdirty`, `pte_mkyoung`, `pte_modify`, swap-exclusive helpers, `pgprot_noncached`, `pgprot_writecombine`, `ptep_set_access_flags`, `__update_tlb`, `update_mmu_cache_range`, THP `pmd_*` helpers, `fixup_bigphys_addr`, and `gup_fast_permitted`.

### Control Flow
Fault handling and mmap paths call PTE mutators that preserve MIPS buddy/global semantics and update software valid/dirty/accessed bits. `set_ptes` checks whether cache updates are needed before installing a range. TLB update hooks feed the hardware TLB after faults. `htw_stop`/`htw_start` disable and re-enable the hardware table walker around destructive PTE clears.

### State, Persistence, Dependencies, And Integration
State includes page-table entries, zero-page coloring, hardware walker sequence counters in CPU data, CP0 PWCTL, cache state, TLB entries, and VMA/MM metadata. Dependencies include generic MM types, `pgtable-32.h` or `pgtable-64.h`, `cmpxchg`, I/O/cache/cpu-feature headers, and TLB/cache implementation functions. Integration points are all generic MM operations, hugepage/THP, swap, soft-dirty, cache aliasing, GUP-fast, and device memory remapping.

### Risks
The global-bit buddy rule is MIPS-specific and can create stale global translations if mishandled. Missing memory barriers in split 64-bit PTE writes can expose half-written entries. Cache update decisions affect VIPT alias correctness. Hardware-table-walker sequencing must be balanced or page walks can run on transient invalid entries.

### Test Signals
Run cross-architecture MIPS MM build matrices plus runtime fork/exec/mmap, COW, mprotect, swap, soft-dirty, hugepage/THP, aliasing-cache, GUP, and device-mmap tests. Fault-injection around TLB/cache update paths is especially useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pgtable.h -->
