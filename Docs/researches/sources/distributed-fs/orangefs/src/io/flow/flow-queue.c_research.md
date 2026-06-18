# sources/distributed-fs/orangefs/src/io/flow/flow-queue.c

Purpose: small quicklist wrapper for queues of `flow_descriptor` objects.

Important APIs/functions: `flow_queue_new()` allocates and initializes a queue head; `flow_queue_add()` appends `flow_d->sched_queue_link`; `flow_queue_remove()` unlinks; `flow_queue_empty()` tests; `flow_queue_shownext()` returns first descriptor; `flow_queue_cleanup()` drains links then frees the head.

Control flow/state: all state is in caller-provided `flow_descriptor` queue links and heap queue head. Cleanup removes queued flows but explicitly does not release the flow descriptors.

Dependencies/integration: depends on `quicklist.h` and a `sched_queue_link` member in `flow_descriptor`; however the visible `flow.h` in this subset does not define `sched_queue_link`, and `module.mk.in` comments out this source. This suggests obsolete or disabled scheduler-era code.

Risks/test signals: compiling this against the current `flow_descriptor` would fail unless another build configuration adds the member. If re-enabled, tests should cover FIFO ordering, cleanup ownership semantics, double-remove safety, and null queue handling.
