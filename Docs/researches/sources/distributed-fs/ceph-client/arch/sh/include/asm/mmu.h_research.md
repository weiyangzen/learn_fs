<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/mmu.h

## Purpose
Defines SH architecture declarations and macros for `mmu` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/errno.h`, `linux/threads.h`, `asm/page.h`. Key macros/constants include `__MMU_H`, `PMB_PASCR`, `PMB_IRMCR`, `PASCR_SE`, `PMB_ADDR`, `PMB_DATA`, `NR_PMB_ENTRIES`, `PMB_E_MASK`, `PMB_E_SHIFT`, `PMB_PFN_MASK`, `PMB_SZ_16M`, `PMB_SZ_64M`, `PMB_SZ_128M`, `PMB_SZ_512M`, `PMB_SZ_MASK`, `PMB_C`, `PMB_WT`, `PMB_UB`, plus 5 more. Typedefs include `mm_context_id_t[NR_CPUS]`. Functions or extern declarations include `__in_29bit_mode`, `pmb_init`, `pmb_bolt_mapping`, `pmb_unmap`. Register or hardware-address constants include `__MMU_H`, `PMB_PASCR`, `PMB_IRMCR`, `PMB_ADDR`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization. MMU and NOMMU builds take different paths, usually replacing fault-tolerant or page-table behavior with direct stubs.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `linux/errno.h`, `linux/threads.h`, `asm/page.h`. Kconfig-sensitive paths mention `CONFIG_MMU`, `CONFIG_BINFMT_ELF_FDPIC`, `CONFIG_PMB`, `CONFIG_29BIT`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 107 lines, 2233 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/mmu.h -->
