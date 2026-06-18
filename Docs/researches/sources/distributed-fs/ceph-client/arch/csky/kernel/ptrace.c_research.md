# sources/distributed-fs/ceph-client/arch/csky/kernel/ptrace.c

Purpose: ptrace regsets, single-step control, syscall trace/audit hooks, and diagnostic register dumps.

Important APIs/types/functions: functions: `singlestep_disable`, `singlestep_enable`, `user_enable_single_step`, `user_disable_single_step`, `gpr_get`, `gpr_set`, `fpr_get`, `fpr_set`, `USER_REGSET_NOTE_TYPE`, `task_user_regset_view`, `regs_query_register_offset`, `regs_within_kernel_stack`, `regs_get_kernel_stack_nth`, `ptrace_disable`, `arch_ptrace`, `syscall_trace_enter`, `syscall_trace_exit`, `show_iutlb`; types: `pt_regs`, `csky_regset`, `membuf`, `user_fp`, `pt_regs_offset`; macros: `CREATE_TRACE_POINTS`, `TRACE_MODE_SI`, `TRACE_MODE_RUN`, `TRACE_MODE_MASK`, `REG_OFFSET_NAME(r)`, `REG_OFFSET_END`

Control flow: Ptrace and syscall-trace entry points toggle single-step bits, expose GPR/FPR regsets, sanitize status-register writes, emit audit/tracepoint records, and print diagnostic register/TLB state.

State and persistence: State is stored in task_struct, thread_info, pt_regs, signal frames, and saved thread context rather than durable storage.

Dependencies and integration: Depends on `linux/audit.h`, `linux/elf.h`, `linux/errno.h`, `linux/kernel.h`, `linux/mm.h`, `linux/ptrace.h`, `linux/regset.h`, `linux/sched.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Register layout and restart semantics are ABI-sensitive and must stay compatible with libc, debuggers, audit, seccomp, and core dumps.

Test signals: C-SKY cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.
