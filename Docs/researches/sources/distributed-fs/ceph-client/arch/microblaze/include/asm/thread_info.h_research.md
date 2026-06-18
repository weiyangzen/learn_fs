# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/thread_info.h

## Purpose

defines thread_info layout, flags, stack size, and current-thread helpers

## Important APIs, Types, and Functions

Source read size: 143 lines, 3844 bytes. Includes: `linux/types.h`, `asm/processor.h`. Declared
functions: `asm`. Key macros/defines: `_ASM_MICROBLAZE_THREAD_INFO_H`, `THREAD_SHIFT`,
`THREAD_SIZE`, `THREAD_SIZE_ORDER`, `INIT_THREAD_INFO(tsk)`, `TIF_SYSCALL_TRACE`,
`TIF_NOTIFY_RESUME`, `TIF_SIGPENDING`, `TIF_NEED_RESCHED`, `TIF_SINGLESTEP`, `TIF_NOTIFY_SIGNAL`,
`TIF_MEMDIE`, `TIF_SYSCALL_AUDIT`, `TIF_SECCOMP`, `TIF_POLLING_NRFLAG`, `_TIF_SYSCALL_TRACE`,
`_TIF_NOTIFY_RESUME`, `_TIF_SIGPENDING`, `_TIF_NEED_RESCHED`, `_TIF_SINGLESTEP`,
`_TIF_NOTIFY_SIGNAL`, `_TIF_POLLING_NRFLAG`, `_TIF_SYSCALL_AUDIT`, `_TIF_SECCOMP`; plus 4 more.
Types visible in this file: `cpu_context`, `thread_info`, `task_struct`.

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
