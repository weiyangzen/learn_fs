# sources/distributed-fs/ceph-client/fs/xfs/xfs_extent_busy.c

## Purpose
`xfs_extent_busy.c` tracks blocks that have been freed logically but whose freeing transactions are not yet durable or whose discard is in progress. This prevents immediate unsafe reallocation and coordinates allocation retries, log forcing, discard completion, and unmount waits.

## Important APIs, types, and functions
The private `struct xfs_extent_busy_tree` holds a spinlock, rb-tree, generation counter, and waitqueue per allocation group or realtime group. Public functions insert normal and discard busy extents, search for overlap, trim allocation candidates, reuse or clear busy ranges, flush/wait for busy extents, sort busy lists, test emptiness, and allocate the tree. The per-entry type and flags are declared in `xfs_extent_busy.h`.

## Control flow
Freeing code inserts a busy extent into the group rb-tree and a transaction/CIL list. Allocators call `xfs_extent_busy_search` or `xfs_extent_busy_trim` to detect overlap; trim returns a usable subrange and the current generation if busy extents forced a reduction. If an allocator decides to reuse a busy metadata extent, `xfs_extent_busy_reuse` walks overlaps and either shrinks/removes entries at the ends, delays for discard, or forces the log when splitting would be necessary. CIL checkpoint completion calls `xfs_extent_busy_clear`, which removes committed entries from rb-trees or marks them `DISCARDED` when discard must finish first. `xfs_extent_busy_flush` log-forces and then waits for the generation to change unless the current transaction holds unresolved busy extents, in which case it may return early or `-EAGAIN` to avoid deadlock.

## State and persistence
Busy extents are runtime state, keyed by group and block number, with held group references. They mirror transaction durability: once the freeing transaction is committed and optional discard handling completes, entries are removed, the generation counter increments, and waiters wake. No busy-tree state persists on disk; recovery reconstructs allocation safety from the log and metadata.

## Dependencies and integration points
It is used by `libxfs/xfs_alloc.c` allocation/freeing paths, `xfs_log_cil.c` checkpoint completion, scrub repair code, AG/rtgroup lifetime, tracepoints, and discard scheduling. Zoned realtime groups bypass busy tracking through the macro in the header because zone reset ordering supplies the needed safety.

## Risks and test signals
Risks include rb-tree/list consistency when entries are zero-length invalidated but still present on immutable transaction lists, deadlocks when a transaction waits on its own busy frees, reuse during discard, generation wakeups that do not guarantee emptiness, and allocation fragmentation from trim choices. Test signals include low-space allocation requiring log force, busy exact and partial overlap searches, discard and skip-discard paths, AGFL/userdata reuse behavior, fatal-signal interruption expectations, unmount waiting across AGs and rtgroups, and zoned realtime configurations.
