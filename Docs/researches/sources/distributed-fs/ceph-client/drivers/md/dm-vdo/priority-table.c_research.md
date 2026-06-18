# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/priority-table.c

## Purpose
`priority-table.c` implements a bounded integer-priority queue with O(1) enqueue, dequeue, remove, reset, and empty checks. It is used where VDO needs fast scheduling among a small priority range.

## Important APIs, Types, and Functions
Public functions are `vdo_make_priority_table()`, `vdo_free_priority_table()`, `vdo_reset_priority_table()`, `vdo_priority_table_enqueue()`, `vdo_priority_table_dequeue()`, `vdo_priority_table_remove()`, and `vdo_is_priority_table_empty()`. Internals include `struct bucket` for one priority queue and `struct priority_table` with `max_priority`, `search_vector`, and flexible bucket array. `mark_bucket_empty()` updates the bit vector when a bucket drains.

## Control Flow
Creation validates `max_priority <= 63`, allocates a flexible bucket array, initializes each list head, and clears the search vector. Enqueue clamps too-high priorities to `max_priority`, appends to the bucket list, and sets the priority bit. Dequeue finds the highest non-empty priority using `ilog2(search_vector)`, removes the first entry from that bucket, clears the bit if the bucket is now empty, and returns the embedded list entry. Remove deletes an arbitrary entry and clears the bucket bit if that entry made its bucket empty. Reset reinitializes all lists and clears all bits.

## State and Persistence Behavior
All state is volatile. The table does not own queued objects; callers embed `list_head` entries in their own structures.

## Dependencies and Integration Points
It uses Linux lists/log2, VDO memory allocation, assertions, and status/error codes. Work queues and scheduling structures can use it for bounded-priority dispatch.

## Risks and Edge Cases
Priority range is limited by the 64-bit search vector. The implementation assumes a queued entry's list links are not used elsewhere while in the table. Removing an entry after reset or double-removing would corrupt lists. No locking is provided.

## Test Signals
Test max-priority validation, enqueue/dequeue ordering, FIFO behavior within the same priority, priority clamping, arbitrary remove from head/middle/tail buckets, reset with queued entries, empty checks, and caller-side locking where used concurrently.
