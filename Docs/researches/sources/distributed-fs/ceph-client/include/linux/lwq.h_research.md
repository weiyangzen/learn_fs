<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lwq.h -->
# sources/distributed-fs/ceph-client/include/linux/lwq.h

## Purpose
This header declares a lightweight queue built on `llist` plus a spinlock for dequeue serialization. It supports fast lockless enqueue and ordered dequeue of batches.

## Important APIs, Types, and Functions
`struct lwq_node` wraps an `llist_node`; `struct lwq` contains an `llist_head`, spinlock, and dequeue cursor. APIs include `lwq_init`, `lwq_empty`, `__lwq_dequeue`, typed `lwq_dequeue`, `lwq_dequeue_all`, `lwq_for_each_safe`, `lwq_enqueue`, and `lwq_enqueue_batch`.

## Control Flow
Enqueue uses `llist_add` or batch add into the lockless head. Dequeue takes the queue lock, drains or advances the internal list, and typed macros convert nodes back to containing structures. Batch dequeue can return a chain for caller traversal.

## State and Persistence Behavior
Runtime state is queued node links, the llist head, the spinlock, and the current dequeue list. No persistence exists.

## Dependencies and Integration Points
It depends on `container_of`, spinlocks, and `llist.h`. It integrates with producer-heavy subsystems that want low-overhead enqueue but serialized consumer processing.

## Risks and Test Signals
Risks include enqueueing an already queued node, traversing live llist contents, failing to hold dequeue serialization, and order surprises from llist newest-first behavior. Test signals are concurrent producer stress, queue drain/order tests, lockdep on dequeue paths, and KCSAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lwq.h -->
