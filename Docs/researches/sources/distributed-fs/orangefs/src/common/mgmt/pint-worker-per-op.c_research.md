<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-per-op.c -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-per-op.c

Purpose: implements a worker backend that creates one detached pthread per posted operation. It favors immediate independent execution over queueing.

Important functions: `per_op_init()` copies attributes and resets `service_count`. `per_op_destroy()` returns `-PVFS_EBUSY` if any operations are still running. `per_op_post()` allocates a small thread descriptor, initializes detached pthread attributes, creates a detached thread, and returns `PINT_MGMT_OP_POSTED`. `PINT_worker_per_op_thread_function()` increments `service_count`, calls `PINT_manager_service_op()`, then `PINT_manager_complete_op()`, decrements `service_count`, and exits.

Control flow has no queue support and asserts `queue_id == 0`. The exported `PINT_worker_per_op_impl` provides init/destroy/post only; work happens asynchronously in detached threads, so no `do_work` callback is needed.

State is process-local in `struct PINT_worker_per_op_s`, mainly attributes and `service_count`. There is no locking around `service_count` in the visible implementation, and no persistence.

Dependencies include pthreads, manager service/complete helpers, OrangeFS errors, and gossip logging. Integration is via `PINT_WORKER_TYPE_PER_OP` in manager worker addition.

Risks: `max_threads` is documented in the header but not enforced, so unlimited thread creation is possible. The allocated thread descriptor is not freed in the thread function, suggesting a leak per post. Detached threads make shutdown synchronization limited to the unsynchronized `service_count`. Tests should cover high post counts, destroy while running, callback errors, memory/thread sanitizer checks, and enforcement or documentation of `max_threads`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-per-op.c -->
