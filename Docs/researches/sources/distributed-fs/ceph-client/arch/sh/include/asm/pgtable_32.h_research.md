<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable_32.h

## Purpose
Defines SH32 PTE bit layout, page protection templates, cacheability/protection transformations, PTE constructors, and PTE/PMD predicates.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_PGTABLE_32_H`, `_PAGE_WT`, `_PAGE_HW_SHARED`, `_PAGE_DIRTY`, `_PAGE_CACHABLE`, `_PAGE_SZ0`, `_PAGE_RW`, `_PAGE_USER`, `_PAGE_SZ1`, `_PAGE_PRESENT`, `_PAGE_PROTNONE`, `_PAGE_ACCESSED`, `_PAGE_SPECIAL`, `_PAGE_SZ_MASK`, `_PAGE_PR_MASK`, `_PAGE_EXT_ESZ0`, `_PAGE_EXT_ESZ1`, `_PAGE_EXT_ESZ2`, plus 68 more.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization. The same API surface changes behavior across NOMMU, legacy MMU, and X2TLB builds, so Kconfig coverage matters.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_X2TLB`, `CONFIG_CPU_SH3`, `CONFIG_MMU`, `CONFIG_PAGE_SIZE_4KB`, `CONFIG_PAGE_SIZE_8KB`, `CONFIG_PAGE_SIZE_64KB`, `CONFIG_HUGETLB_PAGE_SIZE_64K`, `CONFIG_HUGETLB_PAGE_SIZE_256K`, `CONFIG_HUGETLB_PAGE_SIZE_1MB`, `CONFIG_HUGETLB_PAGE_SIZE_4MB`, `CONFIG_HUGETLB_PAGE_SIZE_64MB`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 482 lines, 16658 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable_32.h -->
