# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/flat.h

## Purpose

implements FLAT binary relocation access helpers for no-MMU style binary support

## Important APIs, Types, and Functions

Source read size: 81 lines, 1984 bytes. Includes: `linux/unaligned.h`. Defined functions:
`Copyright`, `flat_put_addr_at_rp`. Declared functions: `put_unaligned`. Key macros/defines:
`_ASM_MICROBLAZE_FLAT_H`, `flat_get_relocate_addr(rel)`.

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
