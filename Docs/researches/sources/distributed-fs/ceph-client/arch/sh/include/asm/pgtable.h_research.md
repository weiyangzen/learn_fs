<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable.h

## Purpose
Connects SH two-level or X2 three-level page-table formats to generic MM, including physical masks, vmalloc bounds, TLB/cache updates, and PTE access checks.

## Important APIs, Types, And Functions
Includes `asm/pgtable-3level.h`, `asm/pgtable-2level.h`, `asm/page.h`, `asm/mmu.h`, `asm/addrspace.h`, `asm/fixmap.h`, `asm/pgtable_32.h`. Key macros/constants include `__ASM_SH_PGTABLE_H`, `NEFF`, `NEFF_SIGN`, `NEFF_MASK`, `NPHYS`, `NPHYS_SIGN`, `NPHYS_MASK`, `PGDIR_SIZE`, `PGDIR_MASK`, `PTRS_PER_PTE`, `PHYS_ADDR_MASK29`, `PHYS_ADDR_MASK32`, `PTE_PHYS_MASK`, `PTE_FLAGS_MASK`, `VMALLOC_START`, `VMALLOC_END`, `pte_pfn(x)`, `update_mmu_cache(vma, addr, ptep)`, plus 3 more. Structures include `vm_area_struct`, `mm_struct`. Functions or extern declarations include `__update_cache`, `__update_tlb`, `paging_init`, `page_table_range_init`. Register or hardware-address constants include `PHYS_ADDR_MASK29`, `PHYS_ADDR_MASK32`.

## Control Flow
Runtime flow is entered from generic MM, fault, copy-to-user, TLB, cache, and mapping paths. Inline helpers translate addresses, validate PTE state, update ASIDs or TTBs, and call implementation routines for cache/TLB synchronization.

## State And Persistence
State persists in `mm_struct`, page tables, ASIDs, fixed mappings, folios, TLB/cache hardware, and user-copy fault state. The header itself owns no durable storage but defines how those structures and hardware registers are interpreted.

## Dependencies And Integration Points
It directly depends on `asm/pgtable-3level.h`, `asm/pgtable-2level.h`, `asm/page.h`, `asm/mmu.h`, `asm/addrspace.h`, `asm/fixmap.h`, `asm/pgtable_32.h`. Kconfig-sensitive paths mention `CONFIG_X2TLB`, `CONFIG_29BIT`. Integration points are generic MM, TLB/cache maintenance, page-fault handling, user access, vmalloc/fixmap, and SH-specific assembly routines.

## Risks And Edge Cases
Risks include stale TLB/cache state, incorrect ASID reuse, wrong PTE flag masks, bad virtual/physical conversions, user-copy exception-table mistakes, and fixmap or vmalloc overlap.

## Test Signals
Useful signals are MM selftests, fork/exec/mmap/mprotect stress, user-copy fault injection, hugetlb tests, TLB shootdown tests, cacheflush paths, kexec/crash boots, and sparse builds across MMU/NOMMU/X2TLB options.

Source read size: 145 lines, 3745 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pgtable.h -->
