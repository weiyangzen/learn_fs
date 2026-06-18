# sources/distributed-fs/ceph-client/drivers/edac/wq.c

Purpose: `wq.c` provides the EDAC subsystem shared ordered workqueue for delayed polling work.

Important APIs/types/functions: static `wq` stores the queue. `edac_queue_work()` queues delayed work, `edac_mod_work()` modifies it, `edac_stop_work()` cancels synchronously and flushes, `edac_workqueue_setup()` allocates `edac-poller` with `WQ_MEM_RECLAIM`, and `edac_workqueue_teardown()` destroys it.

Control flow: EDAC setup creates the queue, drivers schedule or modify delayed poll work, removal paths stop work, and subsystem teardown destroys the queue.

State and persistence: queue state is in memory only. The implementation assumes setup before helper use and no outstanding users at teardown.

Dependencies/integration: Linux workqueue APIs and EDAC module exports. `WQ_MEM_RECLAIM` supports operation under memory pressure.

Risks: no null checks around `wq`; stopping one work item flushes the whole ordered queue; lifecycle ordering is critical.

Test signals: setup failure injection, queue/mod/stop cycles, poll-driver unload, teardown after work cancellation, and memory-pressure polling.
