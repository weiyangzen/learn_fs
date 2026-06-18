# sources/distributed-fs/ceph-client/io_uring/wait.h

Purpose: declares completion-wait helpers and CQ event counting utilities.

Important APIs/types/functions: `IO_CQ_WAKE_INIT` and `IO_CQ_WAKE_FORCE` encode waiter thresholds. `struct ext_arg` stores wait timeout, signal mask, minimum wait time, and iowait flag. Prototypes include `io_cqring_wait()`, `io_run_task_work_sig()`, `io_cqring_do_overflow_flush()`, and `io_cqring_overflow_flush_locked()`. Inlines count kernel/user-visible CQ events with required memory ordering.

Control flow: `io_cqring_events()` issues `smp_rmb()` before reading cached events to match CQ ring ordering rules.

State and persistence: no owned state; observes `ctx->cached_cq_tail` and shared ring CQ head/tail.

Dependencies/integration: used by enter/wait paths, task-work wakeup code, and overflow handling.

Risks/test signals: memory-ordering regressions can expose stale CQEs. Litmus-style CQ visibility tests and enter wait stress are important signals.
