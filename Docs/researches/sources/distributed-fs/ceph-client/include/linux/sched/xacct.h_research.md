# sources/distributed-fs/ceph-client/include/linux/sched/xacct.h

Purpose: declares optional extended task I/O accounting helpers.

Important APIs and types: `add_rchar()`, `add_wchar()`, `inc_syscr()`, and `inc_syscw()` update `task_struct.ioac` when `CONFIG_TASK_XACCT` is enabled, and compile to no-ops otherwise.

Control flow: read/write syscall and filesystem paths call these helpers to accumulate byte and syscall counters for the task.

State and persistence: accounting state lives in `task_struct.ioac` and is folded into process/task accounting outputs. It persists for task lifetime.

Dependencies and integration points: depends on `sched.h` and task I/O accounting fields. Integrates syscall/file I/O paths with taskstats/proc accounting.

Risks and test signals: risks include disabled-config no-op assumptions, counter overflow in long-lived tasks, and missing accounting at new I/O paths. Test taskstats/proc I/O counters, read/write workloads, and builds with and without TASK_XACCT.
