# sources/distributed-fs/ceph-client/arch/hexagon/kernel/signal.c

## Purpose

`signal.c` implements Hexagon real-time signal frame creation, signal-context save/restore, syscall restart handling, and `rt_sigreturn`. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs are `setup_sigcontext`, `restore_sigcontext`, `setup_rt_frame`, `do_signal`, and `SYSCALL_DEFINE0(rt_sigreturn)`. Concrete declarations observed in the file: Includes: `linux/linkage.h`, `linux/syscalls.h`, `linux/sched/task_stack.h`, `asm/registers.h`, `asm/thread_info.h`, `asm/unistd.h`, `linux/uaccess.h`, `asm/ucontext.h`, `asm/cacheflush.h`, `asm/signal.h`, `asm/vdso.h`. Types referenced or declared: `rt_sigframe`, `siginfo`, `ucontext`, `ksignal`, `pt_regs`, `sigcontext`, `hexagon_vdso`. Functions/syscalls: `setup_sigcontext`, `restore_sigcontext`, `setup_rt_frame`, `handle_signal`, `do_signal`, `rt_sigreturn`.

## Control Flow, State, And Persistence

Control flow runs on return to user mode: choose a signal, build `rt_sigframe` on the user or alt stack, redirect PC to the handler and LR to the VDSO trampoline, then restore context on `rt_sigreturn`.

## Dependencies And Integration Points

It integrates with `registers.h`, `ucontext`, `vdso.c`, syscall restart numbers, and uaccess helpers.

## Risks And Test Signals

Risks are corrupt user frames, incorrect PC/SP restore, signal mask loss, and syscall restart loops. Test signals are Linux signal selftests, altstack, sigreturn, interrupted syscall restart, and unwinder checks.
 A local static signal for this file is that it has 257 lines and 6708 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
