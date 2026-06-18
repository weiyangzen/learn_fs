# sources/distributed-fs/ceph-client/io_uring/timeout.c

Purpose: implements timeout requests, linked timeouts, timeout cancellation/update, multishot timeouts, CQ-event-count timeouts, and timeout cleanup during cancellation.

Important APIs/types/functions: `struct io_timeout` and `struct io_timeout_rem` hold command state. Entry points include `io_timeout_prep()`, `io_link_timeout_prep()`, `io_timeout()`, `io_timeout_remove_prep()`, `io_timeout_remove()`, `io_timeout_cancel()`, `io_flush_timeouts()`, `io_kill_timeouts()`, `io_queue_linked_timeout()`, and `io_disarm_next()`.

Control flow: prep validates flags, parses timespec or immediate nanoseconds, handles absolute time namespaces, allocates `io_timeout_data`, and initializes hrtimer callbacks. Normal timeouts are inserted into `ctx->timeout_list`, sorted by CQ target sequence when `off` is nonzero, then hrtimer expiration queues task_work. Completion posts `-ETIME`, re-arms multishot timeouts if repeats remain and CQE posting succeeds, or completes the request. Linked timeouts arm after their head request and cancel the linked request on expiration. Remove requests either cancel a timeout by user_data or update normal/linked timeout hrtimers.

State and persistence: state lives in timeout and linked-timeout lists, hrtimers, `ctx->cq_timeouts`, `cq_last_tm_flush`, request refs, linked request chains, and timeout flags/time/mode. It is transient but controls completion ordering and cancellation.

Dependencies/integration: depends on hrtimers, time namespaces, completion locks, timeout locks, cancel matching, request refs, linked SQE chains, task_work, and CQ tail accounting.

Risks/test signals: risks are timer/cancel races, linked-chain ref handling, sequence wrap comparisons, multishot CQ overflow termination, absolute clock conversion, and lock ordering. Test relative/absolute clocks, CQ-count timeouts, multishot repeats, remove/update normal and linked timeouts, request cancellation, task exit kill, linked timeout racing with head completion, and time namespace behavior.
