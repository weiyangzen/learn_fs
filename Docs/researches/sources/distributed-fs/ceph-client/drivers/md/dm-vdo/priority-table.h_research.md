# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/priority-table.h

## Purpose
`priority-table.h` declares a compact bounded-priority queue abstraction for entries with embedded Linux `list_head` links.

## Important APIs, Types, and Functions
It forward-declares `struct priority_table` and declares make/free, enqueue, reset, dequeue, remove, and empty-check functions. The file-level comments define the design: an array of priority buckets plus a bit-vector hint for non-empty buckets.

## Control Flow
Callers create a table with a maximum priority, enqueue embedded list entries with integer priorities, dequeue the highest-priority available entry, optionally remove arbitrary entries, reset, and free.

## State and Persistence Behavior
No persistent state is involved. The table owns bucket/list heads but not queued objects.

## Dependencies and Integration Points
It includes Linux list support. It can be used by VDO work queues or other bounded scheduler paths.

## Risks and Edge Cases
Callers must ensure an embedded list entry is not simultaneously in another list and must serialize access if multiple threads operate on the same table. Priorities above the configured maximum are clamped by the implementation.

## Test Signals
Compile coverage plus queue ordering, removal, and reset tests validate the declared contract.
