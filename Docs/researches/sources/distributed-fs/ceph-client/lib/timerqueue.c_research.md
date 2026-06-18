<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/timerqueue.c -->
# sources/distributed-fs/ceph-client/lib/timerqueue.c

## Purpose
Generic timer queue implementation using cached rbtrees to maintain timers ordered by expiration time.

## APIs, Types, and Functions
Exports `timerqueue_add()`, `timerqueue_del()`, `timerqueue_iterate_next()`, and `timerqueue_linked_add()`. Helpers `__timerqueue_less()` and `__tq_linked_less()` compare `expires` values for ordinary and linked timerqueue node wrappers.

## Control Flow, State, and Persistence
`timerqueue_add()` warns if the node is already linked, then calls `rb_add_cached()` and returns whether the inserted node is the leftmost/earliest timer. `timerqueue_del()` warns if the node is empty, erases it with `rb_erase_cached()`, clears the node, and returns whether the queue remains non-empty. `timerqueue_iterate_next()` wraps `rb_next()` to move forward without mutation. `timerqueue_linked_add()` inserts a linked-node variant. All queue state is caller-owned; this file performs no locking.

## Dependencies and Integration
Depends on `linux/timerqueue.h`, rbtree helpers, warnings, and GPL exports. It integrates with timer users that need ordered expiration queues and must provide external serialization.

## Risks and Test Signals
Risks include caller failure to serialize operations, adding an already-linked node, deleting an unlinked node, duplicate expiration ordering not being stable beyond rbtree behavior, and misuse of the linked-node container layout. Test signals include earliest-node return values, delete-last behavior, iteration order, duplicate expiration cases, and lockdep or race tests in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/timerqueue.c -->
