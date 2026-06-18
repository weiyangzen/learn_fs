# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/syscall.h

## Purpose

defines syscall number, argument, return-value, and rollback accessors

## Important APIs, Types, and Functions

Source read size: 86 lines, 1902 bytes. Includes: `uapi/linux/audit.h`, `linux/kernel.h`,
`linux/sched.h`, `asm/ptrace.h`. Defined functions: `syscall_get_nr`, `syscall_set_nr`,
`syscall_rollback`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`,
`microblaze_get_syscall_arg`, `syscall_get_arguments`, `syscall_get_arch`. Declared functions:
`BUG`, `do_syscall_trace_enter`. Key macros/defines: `__ASM_MICROBLAZE_SYSCALL_H`. Types visible in
this file: `pt_regs`.

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
