# sources/distributed-fs/ceph-client/include/linux/ioprio.h

Purpose: This header defines kernel helpers for deriving and validating block I/O priority values for tasks.

Important APIs, types, and functions: It imports UAPI priority encoding, defines `IOPRIO_DEFAULT`, `ioprio_valid`, `task_nice_ioprio`, `task_nice_ioclass`, `__get_task_ioprio`, `get_current_ioprio`, `set_task_ioprio`, and `ioprio_check_cap`.

Control flow: If a task has an `io_context` with an explicit class, `__get_task_ioprio` returns it. Otherwise it derives best-effort/idle/realtime class from scheduler policy and derives priority from nice value. For non-current tasks, block builds assert `task_lock` via `alloc_lock`. Non-block builds return defaults or `-ENOTBLK`.

State and persistence: Explicit priority is stored in the task's `io_context`. Derived priorities are computed on demand from task scheduling state.

Dependencies and integration points: Integrates with scheduler policy, realtime/deadline detection, block I/O context, and UAPI ioprio encoding.

Risks: Callers reading another task's priority must hold the expected task lock to keep `io_context` stable. Class validation rejects `IOPRIO_CLASS_NONE` as an explicit class. Non-block configurations cannot enforce or set real I/O priority.

Test signals: Test explicit and derived priority, idle and RT/DL policies, nice-to-priority mapping, capability checks, concurrent task priority reads under lockdep, and `CONFIG_BLOCK` stubs.
