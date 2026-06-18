# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/page.h

## Purpose

defines page table scalar types, virt/phys conversion, pfn helpers, and kernel address layout

## Important APIs, Types, and Functions

Source read size: 141 lines, 3715 bytes. Includes: `linux/pfn.h`, `asm/setup.h`, `asm/asm-compat.h`,
`linux/const.h`, `vdso/page.h`, `asm-generic/memory_model.h`, `asm-generic/getorder.h`. Defined
functions: `virt_to_pfn`. Declared functions: `page_is_ram`, `phys_to_pfn`, `__va`. Key
macros/defines: `_ASM_MICROBLAZE_PAGE_H`, `LOAD_OFFSET`, `PTE_SHIFT`, `PAGE_OFFSET`, `PTE_FMT`,
`copy_page(to, from)`, `clear_page(pgaddr)`, `copy_user_page(vto, vfrom, vaddr, topg)`,
`pte_val(x)`, `pgprot_val(x)`, `pgd_val(x)`, `__pte(x)`, `__pgd(x)`, `__pgprot(x)`,
`phys_to_pfn(phys)`, `pfn_to_phys(pfn)`, `virt_to_page(kaddr)`, `page_to_virt(page)`,
`ARCH_PFN_OFFSET`, `__virt_to_phys(addr)`, `__phys_to_virt(addr)`, `tophys(rd, rs)`, `tovirt(rd,
rs)`, `__pa(x)`; plus 3 more. Types visible in this file: `pte_basic_t`, `pgtable_t`, `pte`,
`pgprot`, `pgd`. External symbols referenced/declared: `max_low_pfn`, `min_low_pfn`, `max_pfn`,
`memory_start`, `memory_size`, `lowmem_size`, `kernel_tlb`, `page_is_ram`.

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
