# sources/distributed-fs/ceph-client/arch/sparc/mm/hugetlbpage.c

Purpose: SPARC64 huge TLB page support, converting Linux hugepage sizes to SPARC TTE encodings and implementing huge PTE allocation, lookup, set, and clear operations.

Important APIs/functions: `arch_make_huge_pte`, `pud_leaf_size`, `pmd_leaf_size`, `pte_leaf_size`, `huge_pte_alloc`, `huge_pte_offset`, `__set_huge_pte_at`, `set_huge_pte_at`, and `huge_ptep_get_and_clear`. Static helpers translate shifts to sun4u/sun4v TTE size bits and back.

Control flow: `arch_make_huge_pte` marks the entry huge, selects sun4u or sun4v encoding by `tlb_type`, and applies ADI MCD bit handling for `VM_SPARC_ADI`. Allocation walks PGD/P4D/PUD/PMD and returns a PUD/PMD leaf slot for large sizes or a huge PTE page for smaller huge pages. Set/clear compute the hardware-backed size, derive how many page-table slots are covered, update `mm->context.hugetlb_pte_count`, fill or zero consecutive entries, and enqueue TLB batch invalidations, including the second real 4MB half of an 8MB Linux HPAGE.

State and persistence: mutates page-table entries and `mm->context.hugetlb_pte_count`. No private persistent state.

Dependencies/integration: depends on SPARC page bits, `tlb_type`, `maybe_tlb_batch_add`, core hugetlb APIs, pgalloc, TLB/cache headers, and ADI flags.

Risks: size translation differs between sun4u and sun4v; unsupported shifts only warn and can fall back to default 4MB encoding. Count accounting must match the number of page-table slots populated. 8MB Linux HPAGE backed by two 4MB hardware pages requires duplicate TLB batching.

Test signals: hugetlb allocation/mapping/unmapping for 64K, 4MB/HPAGE, 256MB, 2GB, and 16GB where supported; ADI huge mappings; page-table count accounting; and TLB invalidation after clear/change.
