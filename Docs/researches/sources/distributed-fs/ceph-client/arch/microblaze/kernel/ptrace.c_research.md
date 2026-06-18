# sources/distributed-fs/ceph-client/arch/microblaze/kernel/ptrace.c

Purpose: implements MicroBlaze-specific ptrace register access and syscall tracing hooks.

Important APIs and state: `arch_ptrace()` handles `PTRACE_PEEKUSR`/`PTRACE_POKEUSR` for `pt_regs` offsets and text/data pseudo-offsets. `do_syscall_trace_enter()` handles seccomp, ptrace syscall-entry notification, and audit entry. `do_syscall_trace_leave()` handles audit exit and syscall-exit tracing. `ptrace_disable()` is a no-op.

Control flow: register offsets below `PT_SIZE` map directly into `task_pt_regs()`. Invalid or unaligned offsets return `-EIO`. Syscall entry can return `-1` to force ENOSYS dispatch while preserving original number in saved regs.

State and persistence: ptrace writes mutate saved user registers. Syscall tracing interacts with audit and seccomp state.

Dependencies and integration: entry.S calls tracing hooks on `_TIF_WORK_SYSCALL_MASK`; signal and fork paths depend on compatible `pt_regs`.

Risks and test signals: no validation prevents changing sensitive MSR/PC values beyond offset bounds. The disabled cache-maintenance alternative hints at write-back concerns. Test PEEK/POKE of every register, syscall tracing, seccomp strict, audit records, and single-step exit notification.
