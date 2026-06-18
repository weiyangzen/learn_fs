<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/hugetlb-e500.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/hugetlb-e500.h

## Purpose
This header provides e500/Book3E-specific hugeTLB hooks for checking supported hugepage sizes, encoding huge PTE page-size fields, and flushing hugeTLB entries.

## Important APIs, Types, And Functions
It declares `flush_hugetlb_page()`, defines `check_and_get_huge_psize()`, and overrides `arch_make_huge_pte()`. The helper rejects shifts that are not powers of four in Book3E encoding terms and maps valid shifts through `shift_to_mmu_psize()`.

## Control Flow
HugeTLB setup calls the check helper before accepting a page size, then `arch_make_huge_pte()` clears and rewrites `_PAGE_PSIZE_MSK` in the PTE. Runtime invalidation goes through `flush_hugetlb_page()`.

## State And Persistence Behavior
The only persistent state is the hugepage size encoded in the PTE. No global state is owned by this header.

## Dependencies And Integration Points
It depends on e500 PTE size bit definitions and `shift_to_mmu_psize()` from the MMU header. It integrates with generic hugeTLB PTE construction and nohash TLB flushing.

## Risks And Edge Cases
The `shift & 1` test enforces the Book3E page-size sequence and can reject otherwise plausible Linux hugepage sizes. Incorrect `_PAGE_PSIZE_SHIFT_OFFSET` math produces wrong hardware TLB sizes.

## Test Signals
Configure e500 hugeTLB sizes, allocate and fault hugepages, test mprotect/unmap on huge mappings, and validate TLB invalidation for each accepted page size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/hugetlb-e500.h -->
