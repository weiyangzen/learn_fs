# sources/distributed-fs/ceph-client/arch/mips/include/asm/thread_info.h

## Purpose

`thread_info.h` defines low-level MIPS `thread_info`, stack sizing, thread flags, and fast current-thread access conventions.

## Important APIs, Types, And Functions

Important APIs are `struct thread_info`, `INIT_THREAD_INFO`, `current_thread_info()`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `STACK_WARN`, `TIF_*` and `_TIF_*` masks, syscall work masks, and SMP CPUID CP0 register constants. Includes: `asm/processor.h`. Macros/constants: `_ASM_THREAD_INFO_H`, `INIT_THREAD_INFO`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `THREAD_MASK`, `STACK_WARN`, `TIF_SIGPENDING`, `TIF_NEED_RESCHED`, `TIF_SYSCALL_AUDIT`, `TIF_SECCOMP`, `TIF_NOTIFY_RESUME`, `TIF_UPROBE`, `TIF_NOTIFY_SIGNAL`, `TIF_RESTORE_SIGMASK`, `TIF_USEDFPU`, `TIF_MEMDIE`, `TIF_NOHZ`, `TIF_FIXADE`, `TIF_LOGADE`, `TIF_32BIT_REGS`, `TIF_32BIT_ADDR`, `TIF_FPUBOUND`, `TIF_LOAD_WATCH`, `TIF_SYSCALL_TRACEPOINT`, `TIF_32BIT_FPREGS`, `TIF_HYBRID_FPREGS`, `TIF_USEDMSA`, `TIF_MSA_CTX_LIVE`, `TIF_SYSCALL_TRACE`, `_TIF_SYSCALL_TRACE`, `_TIF_SIGPENDING`, `_TIF_NEED_RESCHED`, `_TIF_SYSCALL_AUDIT`, `_TIF_SECCOMP`, and 26 more. Types/enums/unions: `should`, `shares`, `thread_info`, `task_struct`, `pt_regs`. Functions/prototypes/helpers: `current_thread_info`, `__asm__`.

## Control Flow

Entry assembly and C code find `thread_info` through `$28/$gp`, track preemption, pending work, syscall number, TLS, CPU, and saved regs, and use TIF masks to decide syscall-entry, syscall-exit, and return-to-user work.

## State And Persistence

State persists for each task on its kernel stack/supervisor stack area; flags and syscall fields change across scheduling, signal, syscall, FPU, watchpoint, and OOM paths.

## Dependencies And Integration Points

It integrates with exception entry, scheduler, syscall tracing, FPU/MSA state, watchpoints, CPU hotplug, VDSO build constraints, and generated assembly offsets.

## Risks

Risks are changing structure layout without regenerating offsets, flag-bit collisions, wrong stack size for page size/ABI, and `$gp` clobbering.

## Test Signals

Test signals are all MIPS builds, syscall/signal stress, preempt/debug builds, stack overflow warnings, and VDSO link checks.
Static review signal: this source currently has 198 lines and 6755 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
