# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/ptrace.h

## Purpose

defines kernel pt_regs helpers and register accessors

## Important APIs, Types, and Functions

Source read size: 24 lines, 593 bytes. Includes: `uapi/asm/ptrace.h`. Defined functions:
`Copyright`. Key macros/defines: `_ASM_MICROBLAZE_PTRACE_H`, `kernel_mode(regs)`, `user_mode(regs)`,
`instruction_pointer(regs)`, `profile_pc(regs)`, `user_stack_pointer(regs)`.

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
