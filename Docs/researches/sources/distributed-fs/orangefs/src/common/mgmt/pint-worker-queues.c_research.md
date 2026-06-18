<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-queues.c -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-queues.c

Purpose: active non-threaded queue worker. It stores operations in one or more queues and only makes progress when the manager's test/wait path calls the worker `do_work()` callback.

Important functions: `queues_init()` copies attributes, initializes queue list/locks/condition variable, and allocates an array for pulled queue entries. `queues_queue_add()`/`remove()` manage queue membership and producer/consumer refs. `queues_post()` chooses a queue by explicit id or, if only one queue exists, by default, then pushes the operation's embedded queue entry. `queues_do_work()` services a specific op by searching all queues or services batches round-robin across queues until timeout.

Control flow: for general work, the worker removes a queue from its round-robin list, waits or timed-waits for up to `ops_per_queue` entries, services each with `PINT_manager_service_op()`, completes each with `PINT_manager_complete_op()`, and returns the queue to the tail. If timeout expires mid-batch, unserviced entries are pushed back to the front in reverse order.

State is in-memory worker instance state plus shared queue objects. There is no persistence. Dependencies include `pint-queue`, `pint-op`, `pint-mgmt`, locks, generated ids, and gossip.

Risks: the code registers a worker id in `queues_post()` but does not use it. `queues_do_work()` assumes `op` is non-NULL before checking `op->id`; manager call sites sometimes pass `0`, which would be unsafe unless guarded elsewhere. The endless `while(1)` relies on timeout/break/error paths to exit. Tests should cover single/multiple queue posting, explicit op service, timeout push-back ordering, empty queue behavior, and manager test paths that pass null op pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-queues.c -->
