# File Research: sources/cow-pools/bcachefs-tools/fs/btree/interior.c

## Purpose

`interior.c` implements btree interior-node structural updates: node allocation, replacement, root updates, splits, merges, rewrites, parent pointer updates, asynchronous completion, and fake root allocation.

This file is the structural counterpart to `commit.c`: when commit discovers a leaf cannot fit an update or a node should merge/rewrite, `interior.c` performs the multi-node transformation while preserving crash consistency.

## Topology Checking

- `bch2_btree_node_check_topology_msg()` verifies that a node’s children exactly span the node range.
  - Roots must have `POS_MIN` min and `SPOS_MAX` max.
  - Interior child pointers must be `btree_ptr_v2`.
  - Each child `min_key` must match successor of the previous child max, or parent min for first child.
  - Last child key must equal parent max.
  - Empty interior nodes are topology errors.
- `bch2_btree_node_check_topology()` wraps it with a suppressed log message.

This is used by split, merge, and commit paths to catch structural corruption immediately.

## Whiteouts

`bch2_push_whiteout()` appends an unwritten whiteout key at the end of the node buffer, using packed position if possible. This preserves deletion semantics for already-written keys that cannot be physically removed from old bsets.

## Bkey Format Calculation

- `__bch2_btree_calc_format()` walks live keys and feeds them into a format-state accumulator.
- `bch2_btree_calc_format()` includes node min/max positions and returns the ideal local packed format.
- `btree_node_u64s_with_format()` predicts live key size after repacking.
- `bch2_btree_node_format_fits()` checks whether a rewritten node would fit with a new format.

These helpers allow rewrites/splits/merges to shrink metadata via better packed formats while falling back when repacking would expand too much.

## Node Allocation and Reserve Cache

### Allocation

- `__bch2_btree_node_alloc()` allocates in-memory btree node state, then obtains disk sectors from the allocator.
- It first attempts to reuse `c->btree.reserve_cache` entries that satisfy durability/target constraints via `can_use_btree_node()`.
- If no cached allocation is usable, it allocates new btree sectors and records open bucket references.
- Allocated nodes remain intent+write locked while reserved for a `btree_update`.

### Consumption

- `bch2_btree_node_alloc()` consumes a preallocated node from the current `btree_update`, initializes node header fields, sequence/pointer metadata, btree id/level, aux trees, and cache state.

### Return/Rollback

- `bch2_btree_reserve_put()` returns unused or bailed nodes to the reserve cache when possible, releases open buckets otherwise, frees in-memory state, and drops locks.
- `bch2_btree_reserve_get()` preallocates enough leaf/interior nodes for the worst-case operation.

The reserve cache prevents livelock where partially allocated btree reserves would otherwise have to go all the way back through the allocator.

## `struct btree_update` Lifecycle

A `btree_update` tracks a structural update whose child node writes and parent pointer update are not durable at the same instant.

### Start

`bch2_btree_update_start()`:

- Verifies paths and calculates how many nodes may be required.
- Escalates or normalizes watermarks where needed.
- Waits if journal space is low and reclaim would deadlock.
- Acquires `gc.lock` read to synchronize with GC.
- Allocates the update object from a mempool.
- Records operation metadata for diagnostics.
- Adds it to `interior_updates.list`.
- Checks journal error state before allocating.
- Gets disk reservation and allocation request.
- Preallocates node reserves.
- Relocks the transaction and verifies no restart occurred.

### Foreground Completion

`bch2_btree_update_done()`:

- Unlocks transaction write locks.
- Releases `gc.lock`.
- Returns unused reserves.
- Schedules async completion after child writes.
- Records foreground timing.

### Failure

`bch2_btree_update_free()`:

- Unlocks writes.
- Releases GC lock, journal pins, disk reservation, node reserves.
- Removes the update from lists.
- Frees it to the mempool.
- Wakes waiters.

## Async Completion and Crash Consistency

Structural updates make new nodes visible only after the new nodes are written and the parent/root update is journaled.

Key functions:

- `bch2_btree_update_write_new_node()` adds a new node to `as->new_nodes`, marks it `will_make_reachable`, sets dirty/need-write, captures open bucket references, and submits the first write.
- `btree_update_set_nodes_written()` marks an update as ready after writes complete and queues worker processing.
- `btree_interior_update_work()` drains written updates.
- `btree_update_nodes_written()` is the transactional completion path:
  - Marks new btree nodes in the superblock bitmap if needed.
  - Waits for old-node writes in flight.
  - Commits triggers and journal records for old and new node keys via `btree_update_nodes_written_trans()`.
  - Clears `will_make_reachable`.
  - Unblocks parent node writes and attaches journal pins.
  - Writes newly reachable nodes if needed.
  - Releases open buckets and frees the update.

Journal pins from old dirty nodes are transferred to the structural update so old disk space is not reclaimed until replacement nodes are persistent and reachable.

## Parent and Root Updates

- `bch2_btree_set_root_inmem()` marks roots permanent, installs root cache pointers under `root_lock`, and recalculates btree reserve.
- `bch2_btree_set_root()` installs a new root as part of a structural update and records root update state.
- `bch2_insert_fixup_btree_ptr()` inserts a new child pointer into an interior node, validates it, handles journal overlay overwrite during replay, and marks the parent node for interior write.
- `bch2_btree_insert_keys_interior()` atomically inserts a sorted keylist into an interior node and verifies topology afterward.
- `bch2_btree_insert_node()` inserts keys into an interior node or recursively splits when it cannot fit.

## Splits and Compaction

`btree_split()` handles both real splits and compaction rewrites:

- It checks topology and decides whether compaction is enough or a split is required.
- It avoids compact-only loops by checking whether the failed leaf key could fit after compaction.
- For real splits, it uses `find_balanced_split()` to choose a pivot and `btree_pack_into_dsts()` to build two destination nodes.
- For compaction, it allocates one replacement node and sorts live keys into it.
- It inserts parent keys recursively, or creates a new root if splitting the root.
- It records trace events for split/compact.
- It marks the old node as dying, writes new nodes, frees the old node in memory before unlocking replacements, and adds new nodes to the transaction.

Public split entry points:

- `bch2_btree_split_leaf()` starts a structural update for a leaf split and may attempt merges upward afterward.
- `bch2_btree_increase_depth()` creates a new root above an existing root, or splits a fake root.

## Merge Algorithm

Foreground merge is implemented by `__bch2_foreground_maybe_merge()`.

Main stages:

1. Gather previous sibling, current node, and next sibling candidates via `btree_merge_push_pos()`.
2. Use `sib_u64s` estimates and evicted-size lookup to avoid expensive reads when a merge is unlikely.
3. Estimate destination count with `compute_merge()`.
4. Fill deferred siblings if the estimate says a merge may fit.
5. Recheck topology and parent identity.
6. Start a `btree_update`.
7. Lock all source nodes for write.
8. Allocate one or two destination nodes.
9. Pack source keys into destinations.
10. Build parent keylist consisting of deletes for removed nodes and keys for new nodes.
11. Insert parent updates.
12. Mark old nodes for freeing, write new nodes, free old nodes in memory, and complete the update.

Supporting helpers:

- `btree_merge_topology_check()` checks source contiguity.
- `merge_node_u64s_and_format()` computes precise or estimated merged size.
- `merge_fail_reset_sib_u64s()` updates sibling estimates after a failed merge attempt.
- `predict_split()` predicts split layouts and packed formats.
- `find_balanced_split()` selects a pivot for split or 3-to-2 merge.
- `compute_merge()` chooses N-to-1 or 3-to-2 destination shape.

Important nuance: exact max-size fits are treated as overflow because write paths add varint slack and round bsets to blocks.

## Node Rewrite

- `bch2_btree_node_rewrite()` rewrites one node to a replacement, updating parent or root and freeing the old node.
- `bch2_btree_node_rewrite_key()` finds a node by btree pointer key hash and rewrites it.
- `bch2_btree_node_rewrite_pos()` finds by position/level and rewrites it.
- `bch2_btree_node_update_key()` updates a btree node’s pointer key, including the special case where the node is currently `will_make_reachable` and its pending `btree_update` record must be updated instead of committing a separate parent update.

## Async Rewrites and Merges

`bch2_async_btree_op()` queues asynchronous operations:

- rewrite,
- merge,
- merge without read.

It stores a copied btree key in `struct async_btree_rewrite`, uses write references to prevent shutdown races, and queues work after journal replay. Pending operations can be flushed, started, or freed via:

- `bch2_async_btree_node_rewrites_flush()`
- `bch2_do_pending_node_rewrites()`
- `bch2_free_pending_node_rewrites()`

## Fake Roots and Bringup

- `bch2_btree_set_root_for_read()` installs a root during filesystem bringup.
- `bch2_btree_root_alloc_fake_trans()` allocates an in-memory fake root, marks it needing rewrite, initializes an empty node spanning the full range, and installs it.
- `bch2_btree_root_alloc_fake()` wraps fake root allocation in a transaction.

Fake roots are used during reconstruction or empty btree setup.

## Diagnostics and Init/Exit

- `bch2_btree_update_to_text()` and `bch2_btree_updates_to_text()` dump active structural update state.
- `bch2_btree_interior_updates_flush()` waits for all interior updates to complete.
- `bch2_journal_entry_to_btree_root()` and `bch2_btree_roots_to_journal_entries()` convert between root journal entries and in-memory root records under `root_lock`.
- `bch2_btree_reserve_cache_to_text()` dumps reserved node allocations.
- `bch2_fs_btree_interior_update_init_early()` initializes locks/lists/work item.
- `bch2_fs_btree_interior_update_init()` creates workqueues and mempool.
- `bch2_fs_btree_interior_update_exit()` destroys workqueues and pool.

## Important Invariants

- Parent pointer updates must not be written before referenced new child nodes are durable.
- Old nodes must not be freed on disk until replacements are persistent and reachable.
- Old nodes are freed in memory before replacement locks are released to prevent stale reads.
- Structural update reserves remain locked until consumed or released.
- `gc.lock` read is held across foreground structural update setup to coordinate with allocation GC.
- `will_make_reachable` synchronizes node-key updates with pending structural update completion.
- Roots are protected from reclaim with `btree_node_permanent`.
- Source nodes for merges must be contiguous and share a parent.
