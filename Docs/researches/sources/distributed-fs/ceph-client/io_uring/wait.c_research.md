# sources/distributed-fs/ceph-client/io_uring/wait.c

Purpose: implements `io_uring_enter()` completion waiting, including task_work flushing, timeouts, minimum wait time, signal masks, NAPI busy polling, and deferred-taskrun wakeups.

Important APIs/types/functions: `io_cqring_wait()`, `io_run_task_work_sig()`, `io_wake_function()`, hrtimer callbacks for normal and minimum timeout wakeups, and scheduling helpers around `struct io_wait_queue`/`struct ext_arg`.

Control flow: wait first runs local and normal task_work, flushes CQ overflow if needed, and returns immediately if enough CQEs are visible. Otherwise it prepares an exclusive waitqueue entry or deferred-taskrun wait count, applies optional signal mask, runs NAPI busy loop, and loops scheduling until enough events, work, signal, timeout, overflow/drop, or wake condition occurs. Timeout setup uses an on-stack hrtimer; a min-timeout can switch to a normal timeout only if no events/work arrived during the minimum interval.

State and persistence: transient wait state includes CQ target tail, CQ tail at min-wait start, timeout/min-timeout values, timeout hit flag, saved signal mask, current `in_iowait`, and `ctx->cq_wait_nr`. No persistent ring data is changed except wait counters and possible CQ overflow flushing.

Dependencies/integration: depends on task_work, local deferred task_work, CQ ring memory ordering, time namespaces, hrtimers, NAPI, signal masks, overflow flush helpers, and waitqueue wake logic.

Risks/test signals: risks include lost wakeups, timeout vs task_work ordering, deferred taskrun wait counts, CQ overflow/drop handling, and signal mask restoration. Test `min_complete`, relative/absolute waits, min-time waits, signal interruption, deferred taskrun, NAPI busy poll, CQ overflow flush, and empty/nonempty CQ races.
