# sources/distributed-fs/ceph-client/fs/ocfs2/localalloc.c

## Purpose
`localalloc.c` implements per-node local allocation windows for OCFS2 data clusters. It lets a node reserve a contiguous window from the global bitmap, satisfy small allocations locally, slide or shrink that window under pressure, and recover unused bits from crashed nodes.

## Important APIs, types, and functions
- `ocfs2_la_default_mb()` and `ocfs2_la_set_sizes()` choose local alloc window size based on cluster group geometry, max slots, block size, and user mount options.
- `ocfs2_load_local_alloc()` validates the node-local alloc system inode and enables local allocation if it is clean.
- `ocfs2_shutdown_local_alloc()` returns unused local bits to the global bitmap and marks the local alloc unused.
- `ocfs2_begin_local_alloc_recovery()` clears a recovered slot's local alloc on disk and returns a copy for later cleanup.
- `ocfs2_complete_local_alloc_recovery()` returns unused copied bits to the global bitmap after recovery locks are safe.
- `ocfs2_alloc_should_use_local()`, `ocfs2_reserve_local_alloc_bits()`, `ocfs2_claim_local_alloc_bits()`, and `ocfs2_free_local_alloc_bits()` are allocator-facing operations.
- Internal helpers count bits, find clear ranges through reservations or bitmap scans, sync unused local ranges to the main bitmap, recalculate window size/state, reserve a new global window, initialize it, and slide windows.

## Control flow
At mount, OCFS2 computes a local alloc size, reads the slot's local alloc inode, validates flags and bitmap size, verifies no stale used bits remain, stores the buffer head in `osb->local_alloc_bh`, and sets `OCFS2_LA_ENABLED`. Allocation callers first use a lockless-ish state check in `ocfs2_alloc_should_use_local()`, then `ocfs2_reserve_local_alloc_bits()` locks the local alloc inode, rechecks state, slides the window if needed, and returns an allocation context pinned to the local alloc buffer. Claim/free operations journal the local alloc dinode and update the local bitmap and used count.

Window sliding clears the current local alloc before returning unused bits to the main bitmap, so failures cannot double-free later. It reserves a new range from the global bitmap, starts a window-move transaction, syncs unused old bits back, then initializes the new local bitmap and reservation map. Recovery uses the same invariant in two phases: first clear the crashed local alloc while replay context is still active, then later free copied unused bits to the global bitmap under normal bitmap locks.

## State and persistence behavior
Persistent state is in the slot-local alloc dinode: bitmap totals, used count, local bitmap offset, and bitmap bytes. Runtime state is in `ocfs2_super`: `local_alloc_bh`, `local_alloc_state`, `local_alloc_bits`, `local_alloc_default_bits`, `la_last_gd`, `la_enable_wq`, and the local reservation map. Unused bits are persisted back to the global bitmap through `ocfs2_release_clusters()`. Fragmentation or ENOSPC can shrink or disable the local alloc and schedule delayed re-enable.

## Dependencies and integration points
The file integrates with system file lookup, inode locks, journal transactions and dinode access, global bitmap suballocation, reservation maps, truncate-log interactions through allocator behavior, workqueues for re-enable, and journal recovery via `journal.c`.

## Risks and edge cases
- Local alloc load rejects any non-empty local alloc because a clean journal with unrecovered local alloc would indicate fsck-worthy inconsistency.
- Window size calculations must not starve other nodes or exceed bitmap storage capacity.
- Sliding and shutdown must clear local alloc before freeing old bits to avoid double free after partial failure.
- Fragmented global bitmaps can throttle or disable local allocation and later re-enable it asynchronously.
- Allocation context ownership is unusual: successful reserve keeps the local alloc inode locked until the allocation context is released by higher-level allocator code.

## Test signals
Test default sizing across block/cluster sizes and slot counts, mount with stale local alloc bits, allocation using reservations and reservation-disabled fallback scanning, window slide under insufficient free bits, fragmentation-driven throttling/disable/re-enable, shutdown sync to main bitmap, crashed-node recovery two-phase cleanup, and local alloc free rollback from move-extents partial failures.
