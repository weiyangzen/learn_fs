# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/fixmap.h

## Purpose

defines fixed virtual mapping slots used during early ioremap and highmem/fixmap operations

## Important APIs, Types, and Functions

Source read size: 66 lines, 1876 bytes. Includes: `linux/kernel.h`, `asm/page.h`, `linux/threads.h`,
`asm/kmap_size.h`, `asm-generic/fixmap.h`. Declared functions: `__set_fixmap`. Key macros/defines:
`_ASM_FIXMAP_H`, `FIXADDR_TOP`, `__FIXADDR_SIZE`, `FIXADDR_START`, `FIXMAP_PAGE_NOCACHE`. Types
visible in this file: `fixed_addresses`. External symbols referenced/declared: `__set_fixmap`.

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
