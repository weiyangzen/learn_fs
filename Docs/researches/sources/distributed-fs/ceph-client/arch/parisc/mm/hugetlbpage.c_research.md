# sources/distributed-fs/ceph-client/arch/parisc/mm/hugetlbpage.c

Purpose: implements PA-RISC huge TLB page-table operations for Linux hugetlb.

Important APIs and functions: `huge_pte_alloc()` allocates the first base PTE for a hugepage-aligned address; `huge_pte_offset()` locates an existing one; `set_huge_pte_at()`, `huge_ptep_get_and_clear()`, `huge_ptep_set_wrprotect()`, and `huge_ptep_set_access_flags()` update the range. `purge_tlb_entries_huge()` flushes all real hugepage-sized hardware TLB entries represented by a Linux hugepage.

Control flow: allocation and lookup align addresses to `HPAGE_MASK` and walk PGD/P4D/PUD/PMD levels to huge PTEs. Setting a huge PTE writes `1 << HUGETLB_PAGE_ORDER` contiguous base PTEs, incrementing the physical address by `PAGE_SIZE` for each sub-PTE, then purges huge TLB entries. Clear and write-protect reuse the same helper with zero or protected entries.

State and persistence: mutates per-mm page tables and TLB state. The code assumes callers hold the PA TLB lock for the internal helper.

Dependencies and integration: used by generic hugetlb MM when `CONFIG_HUGETLB_PAGE` is enabled. Depends on PA-RISC TLB flush encoding, `REAL_HPAGE_SHIFT`, `HPAGE_SHIFT`, and page-table allocation helpers.

Risks: hugepage alignment is critical because callers expect the first sub-PTE. Physical address increments must not cross unintended ranges. Missing lock discipline or incomplete purge loops can leave stale huge translations.

Test signals: allocate, fault, write-protect, clear, and change access flags for hugepages; test configurations where Linux hugepage size spans multiple hardware hugepage entries; verify TLB shootdown and COW/protection behavior.
