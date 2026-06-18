<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/hugetlbpage.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/hugetlbpage.c

### Purpose
`hugetlbpage.c` supplies LoongArch hugepage page-table helpers and converts huge PMD encodings into TLB entrylo values.

### Important APIs, Types, And Functions
Functions are `huge_pte_alloc()`, `huge_pte_offset()`, and `pmd_to_entrylo()`. They operate on `struct mm_struct`, `struct vm_area_struct`, PGD/P4D/PUD/PMD levels, huge PMD bits, `_PAGE_HUGE`, `_PAGE_HGLOBAL`, and `_PAGE_GLOBAL`.

### Control Flow
Allocation walks PGD to PUD and allocates lower directories until it can return a PMD treated as `pte_t *`. Lookup follows only present levels and returns `NULL` for missing PMDs. `pmd_to_entrylo()` verifies the PMD is a leaf huge entry, clears the huge bit by xor, and maps the huge global bit into the normal TLB global bit.

### State, Persistence, And Dependencies
State is page-table memory in the target `mm`; no filesystem persistence exists. Dependencies include generic hugetlb, LoongArch PTE bit definitions, and TLB update code in `tlb.c`/`tlbex.S`.

### Integration Points
Generic hugetlb code calls allocation/lookup helpers. `tlb.c` and `tlbex.S` use `pmd_to_entrylo()` semantics when inserting hugepage TLB entries.

### Risks
Treating PMDs as PTEs is layout-sensitive. Incorrect huge/global bit conversion can create invalid TLB entries or wrong global sharing across ASIDs. The `panic()` on non-leaf PMDs is intentionally fatal.

### Test Signals
Run hugetlb mmap, fork, COW, unmap, and TLB invalidation tests; verify hugepage entrylo values under debug; cross-build with and without `CONFIG_HUGETLB_PAGE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/hugetlbpage.c -->
