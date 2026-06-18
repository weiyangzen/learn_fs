# File Research: sources/block-storage/kvdo/vdo/priority-table.c

Read completely: 240 lines.

This file implements a bounded-height priority queue for small integer priorities. The table stores one circular Linux list per priority bucket and a 64-bit `search_vector` indicating which buckets are non-empty. The highest-priority non-empty bucket is found with `ilog2(search_vector)`, so enqueue, dequeue, remove, reset, and empty checks are O(1) for priorities 0 through 63.

`make_priority_table()` allocates a flexible-array table with `max_priority + 1` buckets and initializes each list head. `priority_table_enqueue()` moves an embedded `list_head` to the selected bucket tail and sets the bucket bit. `priority_table_dequeue()` removes the oldest entry from the highest priority bucket and clears the bit if the bucket becomes empty. `priority_table_remove()` removes an arbitrary entry and clears the corresponding bucket bit when it removed the last item.

Dependencies: Linux lists, `ilog2`, VDO/UDS allocation and status codes, and assertion helpers.

Security/reliability notes: the implementation asserts but does not hard-fail invalid enqueue priorities in production paths. `priority_table_remove()` cannot prove that an entry belongs to the supplied table; misuse with an entry from another list can corrupt the table state.
