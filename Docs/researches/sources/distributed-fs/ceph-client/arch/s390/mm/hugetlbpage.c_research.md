## sources/distributed-fs/ceph-client/arch/s390/mm/hugetlbpage.c

Purpose: implements s390 huge TLB page table operations, converting between Linux PTE encodings and s390 segment/region-table large-entry encodings for 1 MiB PMD and 2 GiB PUD huge pages.

Important APIs, types, and functions: `__pte_to_rste()` and `__rste_to_pte()` convert present, empty, prot-none, dirty/young, soft-dirty, noexec, and swap encodings. `__set_huge_pte_at()`, `set_huge_pte_at()`, `huge_ptep_get()`, `__huge_ptep_get_and_clear()`, `huge_pte_alloc()`, `huge_pte_offset()`, `arch_hugetlb_valid_size()`, and `arch_hugetlb_cma_order()` implement the arch hugetlb interface.

Control flow: setting a huge PTE converts the Linux PTE to an RSTE and sets PMD large or PUD region3-large bits based on the existing table slot type. Getting reverses the encoding. Clearing uses `pudp_xchg_direct()` for region3 entries or `pmdp_xchg_direct()` for segment entries to perform architecture-correct invalidation. Allocation walks PGD/P4D/PUD and returns either the PUD slot for 2 GiB huge pages or a PMD slot for 1 MiB huge pages.

State and persistence: no private persistent state. It mutates page tables through standard mm structures and depends on direct TLB invalidation helpers in `pgtable.c`.

Dependencies and integration points: integrates with generic hugetlb, swap encoding helpers, s390 EDAT1/EDAT2 CPU feature detection, and page-table allocation. CMA hugepage order is only provided for EDAT2/PUD hugepages.

Risks: conversion tables are bit-sensitive; missing a software or hardware bit corrupts hugepage permissions or swap entries. `__set_huge_pte_at()` infers PUD vs PMD from the current slot value, so callers must pass the correct slot. Hugepage sizes are feature-gated; tests on machines without EDAT should reject unsupported sizes.

Test signals: hugetlb mmap/fault/unmap tests for 1 MiB and 2 GiB sizes, swap/migration entries, soft-dirty if enabled, NX and write-protect transitions, and TLB shootdown after clear.
