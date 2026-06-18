# File Research: sources/block-storage/kvdo/vdo/priority-table.h

Read completely: 53 lines.

This header documents and declares the bounded integer-priority queue API. It exposes the opaque `struct priority_table` and operations to allocate, free, reset, enqueue, dequeue, remove arbitrary entries, and test for emptiness.

The header emphasizes that queued objects provide their own embedded `struct list_head`, that priorities are small non-negative integers, and that changing an entry's priority is a remove plus enqueue operation.

Dependencies: Linux list API and `__must_check`.

Security/reliability notes: ownership of queued entries remains with callers; freeing/resetting the table does not free entries.
