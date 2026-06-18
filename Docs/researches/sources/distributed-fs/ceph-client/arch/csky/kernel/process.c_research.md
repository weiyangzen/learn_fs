# sources/distributed-fs/ceph-client/arch/csky/kernel/process.c

Purpose: thread creation, context-switch frame setup, idle/thread hooks, and task register inspection.

Important APIs/types/functions: functions: `copy_thread`, `elf_core_copy_task_fpregs`, `dump_task_regs`, `arch_cpu_idle`; types: `cpuinfo_csky`, `switch_stack`, `pt_regs`; exports: `__stack_chk_guard`

Control flow: Runtime flow is organized around `copy_thread`, `elf_core_copy_task_fpregs`, `dump_task_regs`, `arch_cpu_idle`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is stored in task_struct, thread_info, pt_regs, signal frames, and saved thread context rather than durable storage.

Dependencies and integration: Depends on `linux/module.h`, `linux/sched.h`, `linux/sched/task_stack.h`, `linux/sched/debug.h`, `linux/delay.h`, `linux/kallsyms.h`, `linux/uaccess.h`, `linux/ptrace.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Register layout and restart semantics are ABI-sensitive and must stay compatible with libc, debuggers, audit, seccomp, and core dumps.

Test signals: C-SKY cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.
