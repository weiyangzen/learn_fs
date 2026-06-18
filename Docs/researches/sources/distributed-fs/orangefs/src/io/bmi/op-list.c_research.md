# sources/distributed-fs/orangefs/src/io/bmi/op-list.c

## Purpose
Provides a quicklist-backed container for BMI method operation records. Network method implementations use it to queue, count, search, inspect, and remove pending `method_op` objects.

## Important APIs, Types, And Functions
Public functions are `op_list_new`, `op_list_add`, `op_list_cleanup`, `op_list_remove`, `op_list_empty`, `op_list_count`, `op_list_dump`, `op_list_search`, and `op_list_shownext`. Private helpers are `op_list_cmp_key` and `gossip_print_op`.

## Control Flow
`op_list_new` allocates and initializes a list head. `op_list_add` appends operations to the tail to preserve FIFO behavior. `op_list_search` scans until all enabled fields in `op_list_search_key` match. `op_list_cleanup` walks safely through the list and deallocates each `method_op`, then frees the list head. `op_list_remove` unlinks an op but leaves destruction to the caller.

## State And Persistence
The list owns only in-memory queue membership. No locking is performed; comments state callers must serialize access around operation structures. Cleanup frees queued operations, so ownership must be clear before calling it.

## Dependencies And Integration Points
Depends on `quicklist`, `bmi-method-support`, `gossip`, and `method_op` layout. `bmi_zoid` uses it to retain deferred client operations, and other BMI methods can use it for pending send/recv queues.

## Risks And Test Signals
Risks include no internal synchronization, cleanup deallocating operations still referenced elsewhere, and debug output relying on `method_op` fields that may evolve. Unit tests should cover FIFO order, empty/non-empty behavior, search by address/tag/id combinations, remove without free, and cleanup under multiple entries.
