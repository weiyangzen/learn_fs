<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-queue.h -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-queue.h

Purpose: declares the generic queue data structures and APIs used by management workers and completion contexts.

Important types: `PINT_queue_id` is a generated id. `PINT_queue_entry_t` is an intrusive node containing a `qlist_head` and timestamp. `PINT_queue_entry_compare_callback` is defined but the active implementation does not visibly use the compare callback for ordering. `struct PINT_queue_stats` holds total queued count, average queued time, and variance. `struct PINT_queue_s` includes id, compare callback, entry list, mutex, condition variable, producer/consumer refs, count, triggers, stats, and a `link` used when workers place queues into their own round-robin lists.

Important macros and callbacks: `PINT_queue_entry_object()` computes a containing object pointer from an embedded queue entry. `enum PINT_queue_action` identifies POSTED, REMOVED, and EMPTIED triggers. Trigger and find callback typedefs shape the callback API.

State behavior is intrusive and shared: each queued object must own a `PINT_queue_entry_t`, and each queue object can also be linked into one worker list at a time using `queue->link`. APIs expose blocking and timed waits, explicit remove, search/remove, stats, and lifecycle.

Risks: because `struct PINT_queue_s` is exposed, callers can accidentally mutate internals or reuse `queue->link` incorrectly. Queue ids are opaque only by convention. Tests should validate container macro use, producer/consumer lifetime, wait APIs, and compatibility with both operation entries and context-completion entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-queue.h -->
