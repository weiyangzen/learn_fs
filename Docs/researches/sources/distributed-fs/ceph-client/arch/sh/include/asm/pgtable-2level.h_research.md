<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable-2level.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable-2level.h

## Purpose
Defines SH page-table level geometry and index helpers selected by the main page-table header.

## Important APIs, Types, And Functions
Includes `asm-generic/pgtable-nopmd.h`. Key macros/constants include `__ASM_SH_PGTABLE_2LEVEL_H`, `PAGETABLE_LEVELS`, `PTE_MAGNITUDE`, `PTE_SHIFT`, `PTE_BITS`, `PGDIR_SHIFT`, `PTRS_PER_PGD`, `USER_PTRS_PER_PGD`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `asm-generic/pgtable-nopmd.h`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 24 lines, 567 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable-2level.h -->
