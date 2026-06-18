# sources/distributed-fs/ceph-client/arch/csky/kernel/stacktrace.c

Purpose: frame-pointer-based stack unwinding for stack traces and perf.

Important APIs/types/functions: functions: `walk_stackframe`, `if`, `print_trace_address`, `show_stack`, `save_wchan`, `__get_wchan`, `__save_trace`, `save_trace`, `save_stack_trace_tsk`, `save_stack_trace`; types: `stackframe`, `pt_regs`, `stack_trace`; exports: `save_stack_trace_tsk`, `save_stack_trace`

Control flow: Runtime flow is organized around `walk_stackframe`, `if`, `print_trace_address`, `show_stack`, `save_wchan`, `__get_wchan`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/sched/debug.h`, `linux/sched/task_stack.h`, `linux/stacktrace.h`, `linux/ftrace.h`, `linux/ptrace.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.
