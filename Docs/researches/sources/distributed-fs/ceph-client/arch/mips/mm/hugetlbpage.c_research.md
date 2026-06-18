# sources/distributed-fs/ceph-client/arch/mips/mm/hugetlbpage.c

Purpose: architecture helpers for locating and allocating hugepage PTE storage on MIPS.

Important APIs/functions: `huge_pte_alloc()` walks PGD/P4D/PUD levels and allocates a PMD entry cast as `pte_t *`. `huge_pte_offset()` walks existing levels and returns the PMD-backed huge PTE pointer if present.

Control flow: both functions are straightforward page-table walks. Allocation uses generic `p4d_alloc`, `pud_alloc`, and `pmd_alloc`.

State and persistence: mutates page tables only when allocating. No global state.

Dependencies and integration: used by Linux hugetlb core for MIPS hugepage mappings. Depends on folded/non-folded page-table abstractions and TLB flush semantics elsewhere.

Risks and test signals: casting PMD to PTE is architecture contract-sensitive. Test hugepage mmap, fault, unmap, fork, and page table teardown across folded page table configurations.
