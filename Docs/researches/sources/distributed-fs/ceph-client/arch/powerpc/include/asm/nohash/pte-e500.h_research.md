<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pte-e500.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pte-e500.h

## Purpose
This header defines Book3E/e500 PTE bits and helper predicates for PTE, PMD, and PUD leaf mappings.

## Important APIs, Types, And Functions
It defines `_PAGE_PRESENT`, BookE BAP read/write/execute bits, `_PAGE_PSIZE_MSK`, `_PAGE_TSIZE_4K`, dirty/accessed/cache/endian/guarded bits, `_PAGE_EXEC`, `_PAGE_READ`, `_PAGE_WRITE`, kernel/user protection masks, `_PAGE_SPECIAL`, `PTE_RPN_SHIFT`, `PTE_WIMGE_SHIFT`, `PTE_BAP_SHIFT`, `_PTE_NONE_MASK`, `_PAGE_BASE*`, `pte_mkexec()`, `pte_huge_size()`, `pmd_leaf()`, `pmd_leaf_size()`, and 64-bit `pud_leaf()`/`pud_leaf_size()`.

## Control Flow
Generic PTE helpers call these inline functions when constructing executable mappings or detecting huge PMD/PUD leaves. `pte_huge_size()` decodes the hardware page-size field into a byte size.

## State And Persistence Behavior
The PTE stores software presence plus hardware permission, page-size, cacheability, and RPN fields. On 32-bit, `_PTE_NONE_MASK` preserves upper PTE bits when testing none entries.

## Dependencies And Integration Points
It is selected for 32-bit 85xx and 64-bit nohash Book3E. It integrates with hugeTLB, nohash pgtable mutation, TLB refill, and `pgtable-masks.h`.

## Risks And Edge Cases
`pte_mkexec()` deliberately clears supervisor execute while setting user execute, matching nohash semantics. Leaf detection on 64-bit treats positive entry values as leaves. Incorrect page-size decode breaks hugepage TLB programming.

## Test Signals
Exercise executable user mappings, huge PMD/PUD mappings, mprotect write-protect paths, swap/none detection, and cache-inhibited IO mappings on e500/Book3E hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pte-e500.h -->
