<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-queue.c -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-queue.c

Purpose: generic intrusive, mutex-protected queue implementation for management operations and completion entries. It provides producer/consumer reference tracking, condition-variable waits, triggers, removal/search helpers, and queue-time statistics.

Important APIs: `PINT_queue_create()` allocates/registers a queue and initializes locks/lists. `PINT_queue_destroy()` requires zero producer/consumer refs and an empty queue. Producer/consumer add/remove functions maintain reference counters. `PINT_queue_add_trigger()` registers callbacks for posted/removed/emptied events. `PINT_queue_push()`, `PINT_queue_push_front()`, `PINT_queue_pull()`, `PINT_queue_remove()`, `PINT_queue_search_and_remove()`, `PINT_queue_wait_for_entry()`, `PINT_queue_timedwait()`, and `PINT_queue_wait()` are the core data-flow functions. `PINT_queue_get_stats()` and `PINT_queue_reset_stats()` expose aggregate queue latency metrics.

Control flow: insert asserts the embedded link is not already used, links front/back, timestamps, increments count, signals waiters, and runs POSTED triggers. Pull/remove unlink entries, zero links in most paths, decrement count, update stats from enqueue timestamp, and run REMOVED/EMPTIED triggers. Timed wait converts microseconds to an absolute timespec via `PINT_util_get_abs_timespec()`, handles spurious wakeups, and maps pthread/errno values to PVFS errors.

State is heap-resident per queue, registered by generated id, protected by queue mutex and condition variable. Dependencies include quicklist, generated ids, locks, `pint-util`, `pvfs2-internal`, and gossip.

Risks: `PINT_queue_search_and_remove()` does not zero the removed entry's link, unlike pull/remove. `PINT_queue_get_stats()` divides variance by `total_queued - 1`, unsafe when fewer than two samples exist. `PINT_queue_update_stats()` appears to assign average to `diff / total` rather than adding to the previous average. Tests should cover destruction preconditions, trigger order, spurious/timeouts, specific-entry waits, stats with 0/1/N samples, and intrusive link reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-queue.c -->
