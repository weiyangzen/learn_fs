# sources/distributed-fs/openafs/src/util/work_queue_impl_types.h

Purpose: Defines private structures and enums backing the work queue implementation.

Important types: `afs_wq_work_state_t` covers init, scheduled, running, done, error, blocked, busy, and terminal states. `afs_work_queue_dep_node` links parent and child nodes. `afs_wq_node_list_id_t` identifies none, ready, blocked, and done lists. `afs_work_queue_node` stores queue linkage, dependencies, callback, rock/destructor, state, refcount, block/error counts, detach flag, retcode, mutex, and state condition. `afs_work_queue_node_list` wraps an rx queue with lock/CV/shutdown. `afs_work_queue` holds the lists, queue rock, options, drain/shutdown flags, counters, and CVs.

Control flow and state: This header defines the memory layout used by all private state transitions in `work_queue.c`; no executable control flow.

Dependencies and integration: Requires `__AFS_WORK_QUEUE_IMPL`, includes `work_queue_types.h`, and uses `<rx/rx_queue.h>`, pthread mutexes, and condition variables.

Risks and test signals: Layout changes affect all implementation logic and any accidental private consumers. The header has a typo in a comment (`signalled when th queue`) but no functional issue. Compile-time guard prevents normal external inclusion.
