# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/module.h

## Purpose

defines MicroBlaze relocation constants used by loadable module relocation

## Important APIs, Types, and Functions

Source read size: 28 lines, 704 bytes. Includes: `asm-generic/module.h`. Key macros/defines:
`_ASM_MICROBLAZE_MODULE_H`, `R_MICROBLAZE_NONE`, `R_MICROBLAZE_32`, `R_MICROBLAZE_32_PCREL`,
`R_MICROBLAZE_64_PCREL`, `R_MICROBLAZE_32_PCREL_LO`, `R_MICROBLAZE_64`, `R_MICROBLAZE_32_LO`,
`R_MICROBLAZE_SRO32`, `R_MICROBLAZE_SRW32`, `R_MICROBLAZE_64_NONE`, `R_MICROBLAZE_32_SYM_OP_SYM`,
`R_MICROBLAZE_NUM`. Types visible in this file: `counter`.

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
