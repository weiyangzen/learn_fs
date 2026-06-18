# sources/distributed-fs/ceph-client/arch/sh/kernel/entry-common.S

Purpose: low-level SH exception, IRQ return, syscall, debug-trap, fork-return, and user-work dispatch code.

Important APIs and control flow: `exception_error` delegates to `do_exception_error`. `ret_from_irq` tests saved SR to choose kernel or user resume. `resume_kernel` handles preemptive rescheduling when safe; `resume_userspace` checks thread flags for schedule, signals, notify-resume, and syscall trace exit. `__restore_all` restores register state through `restore_all`. `debug_trap` indexes `debug_trap_table` from TRA. `system_call` builds the pt_regs frame, decodes trap ranges, handles syscall tracing/seccomp/audit hooks through C helpers, bounds `r3` by `NR_syscalls`, dispatches through `sys_call_table`, stores return values, and exits through work checks.

State, dependencies, and risks: state is the exact pt_regs stack layout, TRA/syscall number convention, and thread flags. Dependencies include generated offsets, `sys_call_table`, ptrace/signal code, scheduler, IRQ tracing, and trap handlers. Any layout drift breaks ptrace, signal restore, kgdb, and syscall tracing. Test signals are syscall ABI tests, ptrace syscall rewrite, signal delivery after syscalls/IRQs, preemption under interrupt, and debug trap handling.
