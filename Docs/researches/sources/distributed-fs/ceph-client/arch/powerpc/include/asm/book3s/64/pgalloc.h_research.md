# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pgalloc.h

Purpose: implements Book3S64 page-table allocation/free helpers, including different PGD allocation sizes for radix and hash, page-table fragments, and vmemmap backing tracking.

Important APIs/types/functions: defines `struct vmemmap_backing`, `vmemmap_list`, `pmd_fragment_alloc/free`, `pgtable_free_tlb()`, `__tlb_remove_table()`, `pte_frag_destroy()`, `radix__pgd_alloc/free()`, `pgd_alloc()`, `pgd_free()`, PUD/PMD/PTE allocation and populate helpers, and fragment-aware free paths.

Control flow: allocation chooses radix or hash sizing and may use pages, page fragments, or slab caches depending on table level and page size. Free paths encode table index/shift for TLB-deferred release and use fragment destructors where applicable.

State and persistence: allocated tables are tied to an `mm_struct`; per-mm `pte_frag` and `pmd_frag` cache fragments. `vmemmap_list` tracks physical backing for vmemmap mappings.

Dependencies and integration points: depends on slab, cpumask, kmemleak, percpu, mmu_gather, and Book3S64 page-table geometry. It integrates with process lifecycle, memory hotplug, vmemmap, and RCU/TLB table freeing.

Risks: radix 4K PGDs allocate higher-order pages, so allocation failure handling matters. Fragment accounting must be exact to avoid leaks or double frees. TLB-deferred low-bit encoding depends on table alignment and index-size bounds.

Test signals: fork/exit stress, page-table allocation fault injection, memory hotplug, kmemleak scans, THP split/collapse, and both 4K/64K page-size builds.
