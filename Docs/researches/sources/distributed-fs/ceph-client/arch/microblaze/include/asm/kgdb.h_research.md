# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/kgdb.h

## Purpose

defines KGDB breakpoint and register integration details

## Important APIs, Types, and Functions

Source read size: 32 lines, 741 bytes. Defined functions: `arch_kgdb_breakpoint`. Declared
functions: `__volatile__`, `microblaze_kgdb_break`. Key macros/defines: `__MICROBLAZE_KGDB_H__`,
`CACHE_FLUSH_IS_SAFE`, `BUFMAX`, `NUMREGBYTES`, `BREAK_INSTR_SIZE`. Types visible in this file:
`pt_regs`.

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
