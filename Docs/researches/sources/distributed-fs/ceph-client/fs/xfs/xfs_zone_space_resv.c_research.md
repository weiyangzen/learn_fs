# sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_space_resv.c

## Purpose
`xfs_zone_space_resv.c` manages zoned realtime free-space reservations. It separates total user-fillable realtime extents from immediately writable extents so user writers cannot consume the GC and reset reserve needed to make future progress.

## Important APIs, types, and functions
Public functions include `xfs_zoned_default_resblks`, `xfs_zoned_resv_wake_all`, `xfs_zoned_add_available`, `xfs_zoned_space_reserve`, and `xfs_zoned_space_unreserve`. Internal pieces include `struct xfs_zone_reservation`, `xfs_zoned_space_wait_error`, `xfs_zoned_reserve_available`, and `xfs_zoned_reserve_extents_greedy`.

## Control flow
Reservation first decrements `XC_FREE_RTEXTENTS`, optionally flushes inodegc, and optionally greedily shrinks short writes to remaining space. It then decrements `XC_FREE_RTAVAILABLE`; if unavailable and waiting is allowed, it queues the task on `zi_reclaim_reservations`, wakes GC when needed, sleeps until enough space appears or shutdown/signal/no-reclaimable conditions occur, and removes the waiter. Unreserve returns both total and immediately available counters and drops any held open-zone reference.

## State and persistence
Reservations are in-memory and per task or allocation context. Free counters are runtime mount accounting backed by filesystem metadata changes elsewhere. Default reserved block calculations reserve zones for GC, block zeroing, one free zone, and persistent `sb_rtreserved`.

## Dependencies and integration points
It depends on zoned allocator private state, free-counter helpers, inodegc, GC running state, wakeups from GC reset completion, and mount superblock reserve fields.

## Risks and test signals
Risks include starvation or unfair wake ordering, counter leaks on failure unwind, nowait returning the wrong errno, greedy reservations racing other writers, sleeping while no GC progress is possible, and reserved-pool misuse. Test signals include NOWAIT and RESERVED callers, signal interruption, shutdown wakeups, no reclaimable zones, inodegc freeing space, concurrent waiters, and ENOSPC under tiny zone counts.
