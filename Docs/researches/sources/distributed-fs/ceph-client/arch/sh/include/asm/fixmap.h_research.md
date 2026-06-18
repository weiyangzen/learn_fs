<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/fixmap.h

## Purpose
Defines SH fixed virtual-address slots and fixmap address bounds for per-CPU temporary mappings, boot-time console mappings, and fixed ioremap windows.

## Important APIs, Types, And Functions
Includes `linux/kernel.h`, `linux/threads.h`, `asm/page.h`, `asm-generic/fixmap.h`. Key macros/constants include `_ASM_FIXMAP_H`, `FIX_N_COLOURS`, `FIX_N_IOREMAPS`, `FIXADDR_TOP`, `FIXADDR_SIZE`, `FIXADDR_START`, `FIXMAP_PAGE_NOCACHE`. Enums include `fixed_addresses`. Functions or extern declarations include `__set_fixmap`, `__clear_fixmap`. Register or hardware-address constants include `FIXADDR_TOP`, `FIXADDR_SIZE`, `FIXADDR_START`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `linux/kernel.h`, `linux/threads.h`, `asm/page.h`, `asm-generic/fixmap.h`. Kconfig-sensitive paths mention `CONFIG_IOREMAP_FIXED`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 86 lines, 2543 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/fixmap.h -->
