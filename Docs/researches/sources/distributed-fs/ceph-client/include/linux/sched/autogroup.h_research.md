# sources/distributed-fs/ceph-client/include/linux/sched/autogroup.h

Purpose: declares optional scheduler autogroup hooks that group interactive tasks by session for fair scheduling, plus root task-group exposure for cgroup scheduler builds.

Important APIs and types: `sched_autogroup_create_attach()`, `sched_autogroup_detach()`, `sched_autogroup_fork()`, `sched_autogroup_exit()`, `sched_autogroup_exit_task()`, proc show/set-nice helpers, and `root_task_group` are the exported contracts. Disabled configs compile to no-op stubs.

Control flow: fork/session/exit paths call these hooks to create, attach, detach, and release signal-struct autogroups; procfs can display or tune autogroup nice values.

State and persistence: autogroup state lives in scheduler and `signal_struct` fields, not in this header. It is runtime-only and tied to task/session lifetime.

Dependencies and integration points: integrates process lifetime, procfs, `signal_struct`, and CFS group scheduling. It relies on `CONFIG_SCHED_AUTOGROUP`, `CONFIG_PROC_FS`, and `CONFIG_CGROUP_SCHED`.

Risks and test signals: risks include missing no-op parity, lifecycle leaks on fork/exit failures, and proc tuning races. Test with autogroup enabled/disabled builds, session creation, task exit, proc reads/writes, and CFS group scheduling configs.
