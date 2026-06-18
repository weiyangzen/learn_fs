# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/buddy.c

## Purpose
`buddy.c` implements a compact buddy allocator used by HWS pools to allocate power-of-two chunks from firmware object ranges. It tracks free segments by order using Linux bitmaps.

## Important APIs, Types, And Functions
`mlx5hws_buddy_create()` allocates the object and initializes per-order bitmaps and free counters through `hws_buddy_init()`. `mlx5hws_buddy_alloc_mem()` finds the smallest available segment at or above the requested order, splits larger segments down to the requested order, and returns the segment offset. `mlx5hws_buddy_free_mem()` coalesces with free buddies while possible, then marks the final segment free. `mlx5hws_buddy_cleanup()` frees the bitmap arrays.

## Control Flow And State
Initialization creates `max_order + 1` bitmaps. Order `max_order` starts with a single free segment. Allocation scans upward from the requested order, clears the selected bit, decrements its free count, then repeatedly splits by shifting the segment and setting the sibling bit at lower orders. Freeing shifts the segment by order, repeatedly merges while the sibling bit is set, and sets the merged segment in the final order.

The allocator has no internal locking; callers must serialize access. It stores only in-memory bitmap state and does not persist across pool destruction.

## Dependencies And Integration Points
It relies on kernel bitmap allocation, `find_first_bit()`, `test_bit()`, and HWS pool code that translates pool chunks into firmware object offsets. `buddy.h` exposes the state shape and API.

## Risks And Test Signals
Risks are invalid order/segment inputs, lack of locking in direct callers, integer shifts at large `max_order`, and double-free corruption because `free_mem()` does not validate that the target segment is currently allocated. Test signals include exhaustive allocate/free cycles, fragmentation/coalescing patterns, invalid allocation exhaustion returning `-ENOMEM`, and running under lockdep/KASAN with pool users.
