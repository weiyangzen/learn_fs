<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timerqueue_types.h -->
# sources/distributed-fs/ceph-client/include/linux/timerqueue_types.h

## Purpose
defines timerqueue node and head storage types without pulling in the full helper API.

## Important APIs, Types, and Functions
The file is 27 lines and exports these visible symbol families: types/enums `timerqueue_node`, `timerqueue_head`, `timerqueue_linked_node`, `timerqueue_linked_head`; macros/constants none; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Code embeds `timerqueue_node` or `timerqueue_linked_node` in timer objects, initializes heads, and uses `timerqueue.h` functions to manipulate the rb-tree and list linkage.

## State and Persistence Behavior
Nodes store rb linkage and expiry; linked nodes add a list head. Heads store rb roots, cached next node, and optional duplicate-order list.

## Dependencies and Integration Points
It depends on rbtree and list types. Direct includes are `linux/rbtree_types.h`, `linux/types.h`.

## Risks and Edge Cases
The types contain live intrusive linkage, so object lifetime and single-queue ownership must be enforced by callers.

## Test Signals
Compile embedding users and run timerqueue ordering/lifetime tests with debug list/rbtree enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timerqueue_types.h -->
