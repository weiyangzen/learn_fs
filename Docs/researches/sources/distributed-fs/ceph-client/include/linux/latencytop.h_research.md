# sources/distributed-fs/ceph-client/include/linux/latencytop.h

Purpose: declares optional LatencyTOP scheduler-latency accounting hooks.

Important APIs and types: under `CONFIG_LATENCYTOP`, `struct latency_record` stores a backtrace, count, total time, and max latency; `latencytop_enabled` gates `account_scheduler_latency()`, which calls `__account_scheduler_latency()` only when enabled. `clear_tsk_latency_tracing()` clears per-task records. Without the config, helpers are no-ops.

Control flow: scheduler or blocking paths call `account_scheduler_latency()` with latency duration and interruptibility context; the inline fast path avoids overhead unless collection is enabled.

State and persistence: state is in-memory per-task latency records and a global enable flag. It is diagnostic and not persistent.

Dependencies and integration points: depends on `task_struct` and compiler branch prediction; integrates scheduler latency reporting with LatencyTOP userspace/debug interfaces.

Risks and test signals: risks are hot-path overhead, stale backtraces, and enabled/disabled semantic drift. Test compile with and without `CONFIG_LATENCYTOP`, runtime enabling, task record clearing, and scheduler latency reporting.
