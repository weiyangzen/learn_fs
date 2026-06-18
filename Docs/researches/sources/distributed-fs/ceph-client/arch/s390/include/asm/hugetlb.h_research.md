# sources/distributed-fs/ceph-client/arch/s390/include/asm/hugetlb.h

Purpose: This header provides s390-specific huge TLB page operations and declares the architecture overrides consumed by generic hugetlb code.

Important APIs/types/functions: `hugepages_supported()` maps support to `cpu_has_edat1()`. It declares `set_huge_pte_at()`, `__set_huge_pte_at()`, `huge_ptep_get()`, and `__huge_ptep_get_and_clear()`, and implements clear, get-and-clear, access-flag, write-protect, and userfaultfd-wp stubs.

Control flow: Hugepage operations inspect whether the entry is a region-3 or segment entry, clear it to the matching empty value, and update access flags by clearing and reinstalling a huge PTE. Write protection clears the current entry and writes a protected version.

State and persistence: The persistent state is the hugepage PTE/RSTE in the process page tables. Userfaultfd write-protect state is explicitly unsupported for huge PTEs here and always acts as no-op/false.

Dependencies and integration points: It depends on CPU EDAT1 capability, `pgtable.h` encodings, swap/swapops helpers, and generic hugetlb fallbacks.

Risks and test signals: Wrong region-vs-segment selection can corrupt hugepage mappings or fail TLB invalidation. Tests should include hugetlb mount/use, 1M and 2G mappings where supported, write-protect/accessed/dirty transitions, migration/swap markers, and no-EDAT1 fallback.
