# sources/distributed-fs/ceph-client/include/linux/sched/debug.h

Purpose: declares task, CPU, register, stack, proc-scheduler, and scheduler-text debugging interfaces.

Important APIs and types: `dump_cpu_task()`, `show_state_filter()`, `show_state()`, `show_regs()`, `show_stack()`, `sched_show_task()`, `proc_sched_show_task()`, `proc_sched_set_task()`, `__sched`, scheduler text section boundaries, and `in_sched_functions()` are exported.

Control flow: diagnostics call these helpers to dump task state or stack traces, procfs displays per-task scheduler details, and wchan logic filters addresses in scheduler text.

State and persistence: this header owns no state. It exposes debug output over live task/register/scheduler state.

Dependencies and integration points: integrates scheduler core with procfs, stack unwinding, register dump code, linker sections, and hang/debug paths.

Risks and test signals: risks include unsafe stack reads, misleading wchan filtering after section changes, proc output drift, and log noise in panic/hung-task paths. Test SysRq task dumps, hung-task output, proc scheduler files, stack traces on supported architectures, and linker section placement.
