# sources/distributed-fs/ceph-client/arch/csky/include/asm/pgtable.h

## Purpose

defines C-SKY page table layout, PTE/PMD helpers, protection macros, and cacheability
transformations

## Important APIs, Types, and Functions

Source read size: 263 lines, 6420 bytes. Includes: `asm/fixmap.h`, `asm/memory.h`,
`asm/addrspace.h`, `abi/pgtable-bits.h`, `asm-generic/pgtable-nopmd.h`. Functions: `set_pte`,
`set_pmd`, `pmd_none`, `pmd_present`, `pmd_clear`, `pte_present`, `pte_write`, `pte_dirty`,
`pte_young`, `pte_wrprotect`, `pte_mkclean`, `pte_mkold`, `pte_mkwrite_novma`, `pte_mkdirty`,
`pte_mkyoung`, `pte_swp_exclusive`, `pte_swp_mkexclusive`, `pte_swp_clear_exclusive`; plus 3 more.
Key macros/defines: `__ASM_CSKY_PGTABLE_H`, `PGDIR_SHIFT`, `PGDIR_SIZE`, `PGDIR_MASK`,
`USER_PTRS_PER_PGD`, `PTRS_PER_PGD`, `PTRS_PER_PMD`, `PTRS_PER_PTE`, `pte_ERROR(e)`, `pgd_ERROR(e)`,
`PFN_PTE_SHIFT`, `pmd_pfn(pmd)`, `pmd_page(pmd)`, `pte_clear(mm, addr, ptep)`, `pte_none(pte)`,
`pte_present(pte)`, `pte_pfn(x)`, `pfn_pte(pfn, prot)`; plus 19 more. Local structs: `file`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
