# sources/distributed-fs/ceph-client/arch/s390/kernel/signal.c

Purpose: implements s390 signal frame creation, signal return syscalls, register save/restore, alternate stack selection, and syscall restart handling during signal delivery.

Important APIs/types/functions: frame layouts are `struct sigframe` for old-style handlers and `struct rt_sigframe` for SA_SIGINFO handlers. Register helpers are `store_sigregs()`, `load_sigregs()`, `save_sigregs()`, `restore_sigregs()`, `save_sigregs_ext()`, and `restore_sigregs_ext()`. User ABI syscalls are `sigreturn` and `rt_sigreturn`. Delivery helpers are `get_sigframe()`, `setup_frame()`, `setup_rt_frame()`, `handle_signal()`, and `arch_do_signal_or_restart()`.

Control flow: delivery saves the current syscall number for ptrace visibility, obtains a signal, handles syscall restart return codes if interrupted by a handler, clears syscall state, notifies rseq, and builds either classic or RT frames. Frame setup chooses normal or alternate stack, writes a backchain, saves signal mask/context/FPU/access/vector state, selects the restorer from SA_RESTORER or vDSO, forces default user addressing mode/address-space control, sets handler arguments, and records synchronous-signal extras. Return syscalls read the saved mask and altstack state, save current FPU, restore PSW/GPR/access/FPU/vector state, clear syscall flag, and return the restored `%r2`; bad frames force SIGSEGV.

State and persistence: signal frames are transient userspace stack ABI. Kernel task state touched includes blocked signal mask, altstack state, access registers, FPU/vector state, restart block, `thread.system_call`, and `last_break`. No persistent storage is written.

Dependencies and integration points: depends on vDSO symbols for `sigreturn`, `rt_sigreturn`, and `restart_syscall`, access-register and FPU helpers, vector facility detection, rseq, generic signal core, syscall restart conventions, ptrace syscall flags, and user-copy helpers.

Risks: frame layout is ABI and includes variable extensions for VX registers. PSW restoration must reject unauthorized RI, avoid HOME address-space control, and force valid addressing mode. Restart handling must distinguish handler delivery from no-signal restart. Alternate-stack overflow returns `-EFAULT` and leads to forced signal behavior. Missing FPU save before frame creation or return would corrupt user context.

Test signals: classic and RT signal handlers, SA_ONSTACK overflow, SA_RESTORER and vDSO restorers, vector-register preservation, RI-enabled and RI-disabled tasks, syscall restart cases for `ERESTART*`, ptrace modification before delivery, rseq signal delivery, and bad-frame SIGSEGV paths.
