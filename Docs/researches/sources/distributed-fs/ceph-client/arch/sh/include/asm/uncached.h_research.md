<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/uncached.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/uncached.h

## Purpose
Defines SH platform hooks for `uncached` memory, power, reset, or timekeeping integration.

## Important APIs, Types, And Functions
Includes `linux/bug.h`. Key macros/constants include `__ASM_SH_UNCACHED_H`, `jump_to_uncached()`, `back_to_cached()`, `virt_addr_uncached(kaddr)`, `uncached_init()`, `uncached_resize(size)`. Functions or extern declarations include `cached_to_uncached`, `uncached_size`, `uncached_end`, `virt_addr_uncached`, `uncached_init`, `uncached_resize`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `linux/bug.h`. Kconfig-sensitive paths mention `CONFIG_UNCACHED_MAPPING`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 59 lines, 1372 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/uncached.h -->
