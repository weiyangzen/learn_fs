<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/uaccess.h

## Purpose
Implements SH user-memory access policy and copy helpers, including access-limit checks, address validation, and clear/copy/string entry points.

## Important APIs, Types, And Functions
Includes `asm/extable.h`, `asm-generic/access_ok.h`, `asm/uaccess_32.h`. Key macros/constants include `__ASM_SH_UACCESS_H`, `put_user(x,ptr)`, `get_user(x,ptr)`, `__put_user(x,ptr)`, `__get_user(x,ptr)`, `__m(x)`, `__get_user_nocheck(x,ptr,size)`, `__get_user_check(x,ptr,size)`, `__put_user_nocheck(x,ptr,size)`, `__put_user_check(x,ptr,size)`, `INLINE_COPY_FROM_USER`, `INLINE_COPY_TO_USER`, `clear_user(addr,n)`. Structures include `__large_struct`, `mem_access`. Functions or extern declarations include `long`, `handle_unaligned_access`, `strncpy_from_user`, `strnlen_user`, `set_exception_table_vec`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `asm/extable.h`, `asm-generic/access_ok.h`, `asm/uaccess_32.h`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 133 lines, 4145 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/uaccess.h -->
