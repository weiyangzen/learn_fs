# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pgalloc.h

## Purpose

implements page-table page allocation and freeing helpers

## Important APIs, Types, and Functions

Source read size: 36 lines, 950 bytes. Includes: `linux/kernel.h`, `linux/highmem.h`,
`linux/pgtable.h`, `asm/setup.h`, `asm/io.h`, `asm/page.h`, `asm/cache.h`, `asm-generic/pgalloc.h`.
Declared functions: `Copyright`. Key macros/defines: `_ASM_MICROBLAZE_PGALLOC_H`,
`__HAVE_ARCH_PTE_ALLOC_ONE_KERNEL`, `pgd_alloc(mm)`, `__pte_free_tlb(tlb, pte, addr)`,
`pmd_populate(mm, pmd, pte)`, `pmd_populate_kernel(mm, pmd, pte)`. External symbols
referenced/declared: `__bad_pte`, `pte_alloc_one_kernel`.

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
