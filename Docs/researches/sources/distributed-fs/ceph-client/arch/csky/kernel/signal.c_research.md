# sources/distributed-fs/ceph-client/arch/csky/kernel/signal.c

Purpose: real-time signal frame setup, rt_sigreturn restore, syscall restart, and user-resume work.

Important APIs/types/functions: functions: `restore_fpu_state`, `save_fpu_state`, `restore_sigcontext`, `SYSCALL_DEFINE0`, `setup_sigcontext`, `get_sigframe`, `setup_rt_frame`, `handle_signal`, `do_signal`, `do_notify_resume`; types: `user_fp`, `rt_sigframe`, `siginfo`, `ucontext`, `sigcontext`, `pt_regs`, `ksignal`; macros: `restore_fpu_state(sigcontext)`, `save_fpu_state(sigcontext)`; syscalls: `rt_sigreturn`

Control flow: Signal delivery saves pt_regs/FPU state into an rt signal frame, points LR at the VDSO sigreturn stub, sets handler arguments, and adjusts syscall restart state; sigreturn validates the frame and restores masks, altstack, and registers.

State and persistence: State is stored in task_struct, thread_info, pt_regs, signal frames, and saved thread context rather than durable storage.

Dependencies and integration: Depends on `linux/signal.h`, `linux/uaccess.h`, `linux/syscalls.h`, `linux/resume_user_mode.h`, `asm/traps.h`, `asm/ucontext.h`, `asm/vdso.h`, `abi/regdef.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Register layout and restart semantics are ABI-sensitive and must stay compatible with libc, debuggers, audit, seccomp, and core dumps.

Test signals: C-SKY cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.
