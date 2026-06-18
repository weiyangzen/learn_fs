# sources/distributed-fs/ceph-client/arch/sparc/kernel/signal_32.c

Purpose: implements native SPARC32 signal delivery and return, including old and RT signal frames, FPU/register-window save areas, syscall restart, legacy `sigstack`, and notify-resume integration.

Important APIs/functions: entry points are `do_sigreturn()`, `do_rt_sigreturn()`, `do_notify_resume()`, and `do_sys_sigstack()`. Internal helpers include `invalid_frame_pointer()`, `get_sigframe()`, `setup_frame()`, `setup_rt_frame()`, `handle_signal()`, `syscall_restart()`, and `do_signal()`.

Control flow: sigreturn validates frame alignment/access, saved FP, PC/NPC alignment, restores `pt_regs` or selected RT fields, limits PSR changes to condition codes/FPU enable, clears syscall restart state, restores optional FPU and saved register-window buffers, restores signal mask and altstack, and returns to user. Signal setup synchronizes user windows, computes extra space for FPU/window state, builds an aligned frame on normal or alternate stack, copies current regs and mask, saves FPU/windows if present, copies the current register window into the signal frame, sets handler arguments, points PC/NPC at the handler, and installs either a user restorer or a sigreturn trap trampoline flushed with `flush_sig_insns()`. `do_signal()` handles `%g6` orig-arg preservation and SPARC restart PC rewinding.

State and persistence: modifies current task `pt_regs`, blocked signal mask, altstack state, thread FPU/window buffers, and user stack frames. No external persistence.

Dependencies and integration points: depends on generic signal core, SPARC32 `pt_regs`/PSR/register-window layout, `sigutil` FPU/window helpers, `flush_sig_insns()`, `resume_user_mode_work()`, and syscall restart markers in PSR.

Risks: signal-frame ABI and trampoline instruction encodings are fixed. Register-window save/restore can fault and must synchronize with return-from-trap window handling. `sigstack` is lossy because it guesses stack extent. Incorrect orig `%i0` handling breaks restarted syscalls under ptrace/libc expectations.

Test signals: native SPARC32 signal/RT signal delivery, sigreturn/rt_sigreturn, SA_RESTART and non-restart syscalls, sigaltstack and old sigstack, FPU-using signal handlers, saved register windows, handler restorer and kernel trampoline paths, and malformed user frames.
