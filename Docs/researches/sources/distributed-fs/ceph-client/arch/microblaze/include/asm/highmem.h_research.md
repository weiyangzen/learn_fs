# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/highmem.h

## Purpose

defines highmem kmap bounds and helper declarations

## Important APIs, Types, and Functions

Source read size: 61 lines, 1800 bytes. Includes: `linux/init.h`, `linux/interrupt.h`,
`linux/uaccess.h`, `asm/fixmap.h`. Defined functions: `memory`. Key macros/defines:
`_ASM_HIGHMEM_H`, `PKMAP_ORDER`, `LAST_PKMAP`, `PKMAP_BASE`, `LAST_PKMAP_MASK`, `PKMAP_NR(virt)`,
`PKMAP_ADDR(nr)`, `flush_cache_kmaps()`, `arch_kmap_local_post_map(vaddr, pteval)`,
`arch_kmap_local_post_unmap(vaddr)`. External symbols referenced/declared: `pkmap_page_table`.

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
