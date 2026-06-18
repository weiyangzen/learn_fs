# sources/distributed-fs/orangefs/src/io/flow/flow-queue.h

Purpose: declares the quicklist-backed flow queue API.

Important APIs/types: `flow_queue_p` aliases `struct qlist_head *`; prototypes expose create, cleanup, add, remove, empty, and show-next operations.

Integration: includes `flow.h` and expects `flow_descriptor` to carry a queue link used by `flow-queue.c`. The top-level flow build currently comments out the implementation.

Risks/test signals: header/API drift with `flow.h` is the primary risk. Any attempt to revive this module should first reconcile the missing queue-link field and then add queue lifecycle tests.
