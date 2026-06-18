# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-queue.c

## Purpose
`funnel-queue.c` implements the non-inline portions of VDO's multi-producer, single-consumer funnel queue. It provides allocation, teardown, polling, and idle/empty checks for a queue whose enqueue operation is inlined in the header.

## Important APIs, Types, And Functions
- `vdo_make_funnel_queue()` allocates and initializes the queue with a permanent stub node.
- `vdo_free_funnel_queue()` releases the queue object.
- `get_oldest()` is the core consumer-side algorithm for finding a retrievable non-stub entry while handling producer races.
- `vdo_funnel_queue_poll()` removes and returns the oldest available entry for the single consumer.
- `vdo_is_funnel_queue_empty()` reports no retrievable entries.
- `vdo_is_funnel_queue_idle()` reports neither retrievable entries nor in-progress producer enqueue state.

## Control Flow And Data Flow
The queue starts with `newest` and `oldest` pointing to a stub entry. Producers atomically swap `newest` and then link the previous node's `next` pointer. The consumer reads `oldest->next`; if the stub has a successor it advances past the stub. If the candidate entry has no successor, the consumer may reinsert the stub to preserve non-null invariants and force a future successor before dequeueing.

`vdo_funnel_queue_poll()` calls `get_oldest()`, advances `queue->oldest`, issues a read barrier so the caller sees producer-initialized entry contents, prefetches the next oldest entry, clears the removed link, and returns it. Only the consumer mutates `oldest`, so no consumer-side lock is used.

## State And Persistence Behavior
The queue is entirely transient memory state. Its key invariant is that `newest` and `oldest` are never NULL. The stub is a persistent in-memory sentinel that is sometimes reinserted to handle the race where a producer has swapped `newest` but not yet linked the previous node.

## Dependencies And Integration Points
The implementation uses VDO memory allocation, assertion helpers, `READ_ONCE`/`WRITE_ONCE`, `xchg()` from the inline put helper, `smp_rmb()`, and CPU prefetch helpers. It underpins `funnel-workqueue.c` and `indexer/funnel-requestqueue.c`.

## Risks
- The queue is safe only for one consumer; multiple consumers corrupt ordering and ownership.
- A preempted producer between `xchg()` and `previous->next = entry` temporarily hides later enqueued work.
- `vdo_is_funnel_queue_empty()` may return empty during an enqueue transition even though the queue is not idle; callers must choose the correct predicate.
- Entry lifetime is caller-owned; freeing before poll returns the entry would be unsafe.

## Test Signals
Concurrency tests should run many producers with one consumer, include forced preemption around enqueue, verify FIFO order among completed link chains, and distinguish empty versus idle behavior. Sanitizer or debug builds should assert that dequeued entries have `next == NULL` after poll.
