# sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal_32.c

Purpose: 32-bit PowerPC and 32-bit compat signal ABI implementation. It builds and restores legacy and real-time signal frames, saves/restores GPR/FPR/Altivec/VSX/SPE/TM state, implements `swapcontext`, `rt_sigreturn`, legacy `sigreturn`, and PPC32 `debug_setcontext`.

Important APIs/types/functions: `struct sigframe`, `struct rt_sigframe`, `get_min_sigframe_size_32()`, `prepare_save_user_regs()`, `__unsafe_save_user_regs()`, `prepare_save_tm_user_regs()`, `save_tm_user_regs_unsafe()`, `restore_user_regs()`, `restore_tm_user_regs()`, `handle_rt_signal32()`, `handle_signal32()`, `do_setcontext()`, `do_setcontext_tm()`, `swapcontext`, `rt_sigreturn`, `debug_setcontext`, and `sigreturn`.

Control flow: signal delivery computes a frame using `get_sigframe()`, prepares live FP/vector state, starts a user access block, writes `siginfo`/`ucontext` or legacy `sigcontext`, saves normal or TM register sets, installs a VDSO trampoline or inline `sigreturn` syscall instructions, updates LR/SP/GPR arguments, clears FP exceptions, and returns to the handler in native-endian mode. Return syscalls locate the frame relative to the current SP, restore blocked signal masks and altstack, optionally restore TM checkpoint/speculative state, set `TIF_RESTOREALL`, and force SIGSEGV on bad frames. `swapcontext` saves the old context and restores a new one, with compat size checks for VSX availability. `debug_setcontext` applies requested single-step/branch-trace state before restoring context on PPC32.

State and persistence: mutates current task register image, FP/vector/SPE/TM thread state, signal mask, altstack, debug registers, and restore flags. User-visible persistence is the exact 32-bit signal frame ABI on the user stack.

Dependencies and integration points: depends on common signal code, VDSO32 trampolines, uaccess unsafe regions, TM helpers, FP/Altivec/VSX/SPE flush/load routines, compat siginfo/sigset helpers on PPC64, syscall tables, and ptrace register layout.

Risks: signal-frame layout is ABI-critical and includes legacy gaps/padding. TM restore must not fault after setting MSR TS and must recheckpoint under preemption disable. Compat contexts may omit VSX; accepting MSR_VSX without a VSX region is rejected. Partial restore faults can corrupt registers, so some paths force SIGSEGV instead of returning `-EFAULT`. Endian bit restoration and r2/TLS preservation differ between signal and non-signal context restore.

Test signals: 32-bit native and compat signal selftests, legacy and RT handlers, VDSO and inline trampolines, `swapcontext()` with/without VSX-sized contexts, `sigreturn` bad-frame fault tests, FP/Altivec/VSX/SPE preservation, TM active/suspended delivery and return, endian-mode signal tests, and `debug_setcontext` stepping behavior.
