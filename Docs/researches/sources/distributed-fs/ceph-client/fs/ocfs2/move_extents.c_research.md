# sources/distributed-fs/ceph-client/fs/ocfs2/move_extents.c

## Purpose
`move_extents.c` implements `OCFS2_IOC_MOVE_EXT`, supporting manual extent relocation to a requested physical goal and automatic defragmentation. It copies file data to new clusters, rewrites extent records, handles refcounted extents, updates allocation bitmaps, and reports partial progress to userspace.

## Important APIs, types, and functions
- `struct ocfs2_move_extents_context` carries inode/file, mode flags, credits, new physical position, moved count, refcount location, userspace range, extent tree, metadata/data alloc contexts, and deferred deallocation context.
- `ocfs2_ioctl_move_extents()` validates the user request, write access, file type, immutable/append flags, thresholds, and movement flags before calling `ocfs2_move_extents()`.
- `ocfs2_move_extents()` takes inode mutex, OCFS2 rw lock, metadata lock, and allocation semaphore, then updates ctime after the range operation.
- `__ocfs2_move_extents_range()` walks logical clusters, skips holes, chooses defrag or move behavior, invalidates the extent cache after each moved range, and returns moved length/new offset.
- `ocfs2_defrag_extent()` allocates new clusters from normal allocator paths for auto defrag.
- `ocfs2_move_extent()` moves to a user-specified goal by probing the global bitmap group near the goal and setting bits directly.
- `__ocfs2_move_extent()` copies clusters, splits/replaces the extent record, clears refcounted flag on replacement, and frees/decrements the old extent through truncate log or refcount tree.

## Control flow
The ioctl path copies `struct ocfs2_move_extents`, clamps length to EOF, defaults threshold to 1 MiB, validates flags, and either enables auto defrag or validates the physical goal. The main move path excludes concurrent writes with `ocfs2_rw_lock()`, locks the inode metadata, and serializes extent tree changes with `ip_alloc_sem`.

For each allocated extent in the requested logical range, auto defrag accumulates extents until the threshold and calls `ocfs2_defrag_extent()`, which may allow partial cluster claims if requested. Manual movement converts the userspace goal to clusters, finds the containing global bitmap group, probes for a free run within `me_threshold`, copies data, updates the extent tree, updates global bitmap dinode/group counts, and advances the goal. Both paths schedule truncate-log flush and run deferred deallocations after the range walk.

## State and persistence behavior
Persistent changes include new data clusters, updated extent records, global bitmap/group descriptor updates, truncate-log entries or refcount decrements for old clusters, ctime updates, and inode fsync transaction ids. The userspace range is copied back with `me_moved_len`, `me_new_offset`, and `OCFS2_MOVE_EXT_FL_COMPLETE` when fully complete. Runtime extent cache is truncated at each moved logical cluster to avoid stale flags or physical mappings.

## Dependencies and integration points
This file integrates with ioctl dispatch, mount write accounting, OCFS2 rw/meta locks, allocation and localalloc, global bitmap system inode, extent tree/path splitting, refcount tree, copy-on-write page duplication/writeback, truncate log, deferred deallocation, inode journaling, and extent map invalidation.

## Risks and edge cases
- Manual movement's goal validation is best effort; the bitmap can change before actual move.
- Partial defrag can improve success rate but may increase fragmentation; userspace controls this through flags.
- Refcounted extents need refcount tree locking and extra credits before replacement removes `OCFS2_EXT_REFCOUNTED`.
- Truncate-log flushing must happen before reserving clusters in defrag to avoid deadlocks on the global bitmap.
- Error paths still copy progress back to userspace, so tests should verify partial results.
- The code comments note xattr extents are not handled.

## Test signals
Exercise manual move to valid/invalid goals, group-boundary validation, auto defrag with threshold behavior, partial defrag ENOSPC behavior, holes in the range, refcounted/reflinked extents, immutable/append/non-regular/no-write-fmode rejection, ctime update, extent-cache invalidation, truncate-log flush scheduling, and user copy-out after partial failure.
