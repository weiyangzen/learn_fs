# sources/distributed-fs/ceph-client/arch/nios2/kernel/signal.c

Purpose: constructs and restores Nios II rt signal frames, restarts interrupted syscalls, and handles return-
to-user signal/resume work.

Important APIs/types/functions: functions: `rt_restore_ucontext`, `do_rt_sigreturn`, `rt_setup_ucontext`, `setup_rt_frame`,
`handle_signal`, `do_signal`, `do_notify_resume`; prototypes: `signal_setup_done`, `handle_signal`,
`resume_user_mode_work`; types: `rt_sigframe`, `siginfo`, `ucontext`, `switch_stack`, `pt_regs`,
`ksignal`; macros: `_BLOCKABLE`.

Control flow: Signal delivery builds a rt frame on the user stack, saves register and sigmask state, points
execution at the handler/trampoline, and sigreturn validates/restores the ucontext before returning
through the syscall epilogue.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `linux/signal.h`, `linux/errno.h`, `linux/ptrace.h`, `linux/uaccess.h`,
`linux/unistd.h`, `linux/personality.h`, `linux/resume_user_mode.h`, `asm/ucontext.h`,
`asm/cacheflush.h`. Integration points include generic Linux MM, irq, signal, ptrace, module,
timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-register assembly.
This source is part of the Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
