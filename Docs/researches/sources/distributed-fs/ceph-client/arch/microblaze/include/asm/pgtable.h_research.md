# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pgtable.h

## Purpose

defines MicroBlaze page-table layout, PTE bits, protection values, and PTE/PMD/PGD accessors

## Important APIs, Types, and Functions

Source read size: 437 lines, 14059 bytes. Includes: `asm/setup.h`, `asm-generic/pgtable-nopmd.h`,
`linux/sched.h`, `linux/threads.h`, `asm/processor.h`, `asm/mmu.h`, `asm/page.h`. Defined functions:
`pte_present`, `pte_write`, `pte_exec`, `pte_dirty`, `pte_young`, `pte_uncache`, `pte_cache`,
`mk_pte_phys`, `pte_modify`, `The`, `set_pte`, `ptep_test_and_clear_young`,
`ptep_test_and_clear_dirty`, `ptep_get_and_clear`, `ptep_mkdirty`, `pmd_page_vaddr`,
`pte_swp_exclusive`, `pte_swp_mkexclusive`, `pte_swp_clear_exclusive`. Declared functions:
`Copyright`, `raw_local_irq_save`, `__pte`, `iopa`. Key macros/defines: `_ASM_MICROBLAZE_PGTABLE_H`,
`VMALLOC_START`, `VMALLOC_END`, `_PAGE_CACHE_CTL`, `pgprot_noncached(prot)`,
`pgprot_noncached_wc(prot)`, `PGDIR_SHIFT`, `PGDIR_SIZE`, `PGDIR_MASK`, `PTRS_PER_PTE`,
`PTRS_PER_PMD`, `PTRS_PER_PGD`, `USER_PTRS_PER_PGD`, `USER_PGD_PTRS`, `KERNEL_PGD_PTRS`,
`pte_ERROR(e)`, `pgd_ERROR(e)`, `_PAGE_GUARDED`, `_PAGE_PRESENT`, `_PAGE_NO_CACHE`,
`_PAGE_WRITETHRU`, `_PAGE_USER`, `_PAGE_RW`, `_PAGE_DIRTY`; plus 48 more. Types visible in this
file: `vm_area_struct`. External symbols referenced/declared: `mem_init_done`, `va_to_phys`,
`va_to_pte`, `swapper_pg_dir`, `iopa`, `ioremap_base`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
