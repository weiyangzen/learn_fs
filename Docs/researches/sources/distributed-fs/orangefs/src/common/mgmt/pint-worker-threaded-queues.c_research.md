<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-threaded-queues.c -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-threaded-queues.c

Purpose: active queue worker with a fixed set of service threads. It lets operations be posted to one or more queues while worker threads pull and service them asynchronously.

Important functions: `threaded_queues_init()` copies attributes, initializes queues/in-use lists, records the manager, allocates thread entries, and starts `thread_count` pthreads. `threaded_queues_destroy()` stops and joins each thread. Queue add/remove functions attach queues, manage producer/consumer refs, and coordinate with active threads through `remove_requested`. `threaded_queues_post()` validates queue ownership and pushes operations. `threaded_queues_cancel()` removes a queued operation. `PINT_worker_queues_thread_function()` is the core loop.

Thread control flow: each thread waits for an available queue, moves it to `inuse_queues`, timed-waits for up to `ops_per_queue` entries, returns the queue to the round-robin list, signals if more work remains, then services each operation with `PINT_manager_service_op()` and completes it with `PINT_manager_complete_op()`. Threads periodically wake when no queues exist so stop requests can be observed. Start/stop wrap `pthread_create()` and `pthread_join()`.

State is process-local and concurrent: worker mutex protects queue lists and removal state; each thread has its own mutex/running/error fields; queue locks protect entries. No persistence. Dependencies include pthreads, queue/manager/op APIs, locks, quicklist, and gossip.

Risks: several pointer/list checks look suspicious (`w->queues.next->next != NULL`, `qlist_entry(&w->queues.next, ...)`) and should be tested. `threaded_queues_cancel()` returns from `PINT_queue_remove()` while still holding `w->mutex`, likely leaking the mutex lock. Destroy has questionable extra unlocks. Thread descriptors and op-entry cleanup are split between context and worker paths, risking double or missed frees. Tests should stress posting/removing queues, cancellation, shutdown under load, timeout behavior, and race detection with thread sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-threaded-queues.c -->
