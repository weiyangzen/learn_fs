# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/ftrace.h

## Purpose

defines MicroBlaze ftrace call-site sizing and graph tracing hooks

## Important APIs, Types, and Functions

Source read size: 28 lines, 719 bytes. Defined functions: `ftrace_call_adjust`. Declared functions:
`_mcount`. Key macros/defines: `_ASM_MICROBLAZE_FTRACE`, `MCOUNT_ADDR`, `MCOUNT_INSN_SIZE`. Types
visible in this file: `dyn_arch_ftrace`. External symbols referenced/declared: `_mcount`,
`ftrace_call_graph`.

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
