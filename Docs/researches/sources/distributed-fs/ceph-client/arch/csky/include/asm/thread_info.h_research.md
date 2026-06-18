# sources/distributed-fs/ceph-client/arch/csky/include/asm/thread_info.h

## Purpose

defines C-SKY thread_info flags, layout, and current-thread access

## Important APIs, Types, and Functions

Source read size: 89 lines, 2808 bytes. Includes: `asm/types.h`, `asm/page.h`, `asm/processor.h`,
`abi/switch_context.h`. Key macros/defines: `_ASM_CSKY_THREAD_INFO_H`, `INIT_THREAD_INFO(tsk)`,
`THREAD_SIZE_ORDER`, `thread_saved_fp(tsk)`, `thread_saved_sp(tsk)`, `thread_saved_lr(tsk)`,
`TIF_SIGPENDING`, `TIF_NOTIFY_RESUME`, `TIF_NEED_RESCHED`, `TIF_UPROBE`, `TIF_SYSCALL_TRACE`,
`TIF_SYSCALL_TRACEPOINT`, `TIF_SYSCALL_AUDIT`, `TIF_NOTIFY_SIGNAL`, `TIF_POLLING_NRFLAG`,
`TIF_MEMDIE`, `TIF_RESTORE_SIGMASK`, `TIF_SECCOMP`; plus 14 more. Local structs: `thread_info`,
`task_struct`, `restart_block`, `pt_regs`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
