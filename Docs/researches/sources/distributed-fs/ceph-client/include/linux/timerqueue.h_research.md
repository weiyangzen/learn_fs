<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timerqueue.h -->
# sources/distributed-fs/ceph-client/include/linux/timerqueue.h

## Purpose
declares red-black-tree timerqueue helpers used by hrtimers and other ordered-by-expiry queues, plus linked-list variants for duplicate expiry ordering.

## Important APIs, Types, and Functions
The file is 85 lines and exports these visible symbol families: types/enums `timerqueue_node`, `timerqueue_linked_node`; macros/constants none; function-like macros none; inline helpers `timerqueue_init`, `timerqueue_node_queued`, `timerqueue_init_head`; external prototypes `timerqueue_add`, `timerqueue_del`, `timerqueue_linked_add`, `rb_entry_safe`, `rb_erase_linked`.

## Control Flow
Users initialize a head and nodes, add nodes by expiry, read the earliest node with `timerqueue_getnext()` or linked first, iterate/delete nodes, and test queued state through rb linkage.

## State and Persistence Behavior
`timerqueue_head` stores an rb root and cached next pointer; linked heads also keep a list for nodes sharing or ordering expiry. Nodes store expiry values in `timerqueue_types.h`.

## Dependencies and Integration Points
It depends on rbtrees/lists through the types header and integrates with hrtimer internals and scheduler/time code needing ordered timers. Direct includes are `linux/rbtree.h`, `linux/timerqueue_types.h`.

## Risks and Edge Cases
Nodes must not be added twice, and callers own locking. Cached leftmost pointers must stay consistent with rb mutations; linked variants need list/rbtree synchronization.

## Test Signals
Unit-test insertion/deletion ordering, duplicate expiry ordering, queued-state checks, iteration after deletion, and randomized add/delete sequences under debug rbtree checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timerqueue.h -->
