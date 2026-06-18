# Group Research: group_222_bcachefs_tools_sources_cow_pools_bcachefs_tools_fs_btree_check_c_sou_f5a420d19551

Scope: `Docs/research_subset_a.md`, source tree `sources/cow-pools/bcachefs-tools`.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/check.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/check.c

## Purpose

`check.c` implements bcachefs btree topology checking/repair and allocation garbage collection. It has three major jobs:

- Validate and repair btree node topology during recovery/fsck.
- Run a mark-and-sweep style allocation check that recomputes allocation, stripe, accounting, reflink, and btree pointer reference state from live metadata.
- Perform related maintenance passes such as stale pointer generation cleanup and opportunistic btree node merging.

This file is central to recovery correctness: it reconciles on-disk btree structure with journal overlays, scanned nodes, allocation keys, and generated GC state.

## Key Responsibilities

### GC Position Tracking

The file defines printable GC phase names and updates `c->gc.pos` through seqcount-protected helpers:

- `bch2_gc_pos_to_text()` prints current GC phase, btree/level, and position.
- `__gc_pos_set()` writes the GC position without monotonicity checks.
- `gc_pos_set()` enforces monotonic GC progress via `gc_pos_cmp()`.

This position is used by concurrent updates and commit-time GC triggers to decide whether an update touches an area GC has already visited.

### Topology Repair

The topology repair path repairs parent/child range mismatches and unreadable roots.

Important helpers:

- `btree_ptr_to_v2()` normalizes a node pointer into `btree_ptr_v2` form, preserving pointer payload while stamping `min_key`, sequence, and write metadata.
- `set_node_min()` updates a child node’s `min_key`, journals the parent pointer update, drops out-of-range node keys, and updates the in-memory key.
- `set_node_max()` updates a child node’s max key and parent pointer key position, including cache unhash/rehash because the node key changes.
- `btree_check_node_boundaries()` checks expected child start against current child `min_key`, detects gaps and overlaps, and either adjusts min/max or signals node deletion.
- `btree_check_root_boundaries()` ensures roots cover `[POS_MIN, SPOS_MAX]`.
- `btree_repair_node_end()` ensures the last child ends at the parent’s max key.
- `bch2_btree_repair_topology_recurse()` walks interior children with a btree+journal iterator, handles EIO/stale nodes, repairs adjacency, drops overwritten nodes, rescans when scanned nodes fill gaps, and recursively validates children.
- `bch2_topology_check_root()` handles unreadable roots by reconstructing fake roots or using scanned nodes when the btree can recover from scan.
- `bch2_check_topology()` is the public entry point. It iterates all alive btrees, runs root reconstruction if needed, locks roots, checks root boundaries, recursively repairs topology, and resets btree read-error ratelimiters after repair.

Notable behavior: topology repair still uses no-fail root locking in a narrow mount/recovery context. The file comments explain this is acceptable only because worker threads are not running and there is no real contention.

### Allocation GC

`bch2_check_allocations()` orchestrates the allocation check. It:

1. Takes `state_lock` read and `gc.lock` write.
2. Flushes pending btree interior updates.
3. Starts accounting GC, device usage GC, alloc GC storage, and reflink GC.
4. Sets GC phase to `start`.
5. Marks superblocks.
6. Walks btrees in GC order.
7. Reconciles allocation keys, accounting, stripes, and reflinks.
8. Clears GC state and frees temporary GC tables under `capacity.mark_lock`.
9. Wakes allocation waiters and cleans deleted member devices if no unfixed errors remain.

The ordering is documented as correctness-critical: references may move forward in the GC order, but must not move backward, otherwise GC may miss them.

### Marking Btree Keys

- `bch2_gc_mark_key()` validates and repairs each key, checks btree bitmap marking for interior btree pointers, updates key version if needed during initial walk, and runs GC insert triggers.
- `bch2_gc_btree_root()` marks the root pointer after confirming iterator root identity.
- `bch2_gc_btree()` walks levels from `target_depth` upward and marks keys, then marks the root.
- `bch2_gc_btrees()` walks alive btrees in `gc_btree_order()`, checking leaves when fsck needs full readability before RW mode.

`BTREE_ID_alloc` and `BTREE_ID_stripes` receive special GC ordering through `gc_btree_order()` in `check.h`.

### Allocation Key Reconciliation

- `bch2_alloc_v4_cmp()` compares the alloc fields GC rebuilds.
- `bch2_alloc_write_key()` compares the on-disk alloc key with the GC bucket state and fixes mismatched `data_type`, `gen`, dirty/cached/stripe sectors, and stripe refcount.
- `bch2_gc_alloc_done()` scans alloc keys for every member device bucket and commits repairs.
- `bch2_gc_alloc_start()` preallocates per-device temporary bucket GC state.

Important nuance: empty-bucket state such as `need_discard` and `need_gc_gens` is not directly produced by GC. The code preserves on-disk empty-state hints when GC has no nonempty data type, avoiding false mismatches during alloc reconstruction.

### Stripe Reconciliation

- `bch2_gc_write_stripes_key()` compares stripe block sector counts against GC stripe state and zeroes parity block sector counts.
- `bch2_gc_stripes_done()` scans the stripes btree and commits repairs.

### Generation Cleanup

- `bch2_gc_gens()` computes oldest live bucket generations by copying bucket generation arrays, walking data-pointer btrees with stale-pointer dropping, then updating alloc keys’ `oldest_gen`.
- `bch2_gc_gens_async()` schedules that work under a write reference.
- `bch2_gc_gens_work()` runs it and releases the write ref.

This pass also sets the `BCH_COMPAT_no_stale_ptrs` compat bit after successful completion if needed.

### Merge Pass

- `merge_btree_node_one()` traverses an iterator to a node and invokes foreground merge if the node is under threshold.
- `bch2_merge_btree_nodes()` scans all btrees and levels, reporting merge counts.

## External Interfaces

Public functions exported through `check.h`:

- `bch2_check_topology()`
- `bch2_check_allocations()`
- `bch2_gc_pos_to_text()`
- `bch2_gc_gens()`
- `bch2_gc_gens_async()`
- `bch2_merge_btree_nodes()`
- `bch2_fs_btree_gc_init_early()`

## Important Invariants

- GC position must move monotonically except when explicitly resetting to `not_running`.
- Topology ranges are closed child ranges where the child key position is max key and `btree_ptr_v2.min_key` is min key.
- A parent’s children must exactly cover the parent interval with no gaps or overlaps.
- Root nodes must span `POS_MIN` through `SPOS_MAX`.
- Allocation GC must run in a total order compatible with concurrent reference movement.
- Commit-time GC triggers rely on `gc_visited()` and the same `gc_pos` ordering.
- Temporary GC state must be freed and `c->gc.pos` reset even on failure.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/check.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/check.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/check.h

## Purpose

`check.h` declares the btree check/GC public API and defines inline helpers for GC ordering and position comparison.

The include guard uses `_BCACHEFS_BTREE_GC_H`, reflecting that this header covers btree GC as well as checking.

## Public API

Declared functions:

- `bch2_check_topology(struct bch_fs *)`
- `bch2_check_allocations(struct bch_fs *)`
- `bch2_gc_pos_to_text(struct printbuf *, struct gc_pos *)`
- `bch2_gc_gens(struct bch_fs *)`
- `bch2_gc_gens_async(struct bch_fs *)`
- `bch2_merge_btree_nodes(struct bch_fs *)`
- `bch2_fs_btree_gc_init_early(struct bch_fs *)`

## GC Position Helpers

- `gc_phase(enum gc_phase)` constructs a phase-only GC position.
- `gc_pos_btree(enum btree_id, unsigned level, struct bpos)` constructs a btree-position GC marker.
- `gc_btree_order(enum btree_id)` imposes special ordering: alloc btree before all others, stripes after alloc but before normal btrees.
- `gc_pos_cmp()` compares phase, btree GC order, level, then bpos.
- `gc_visited()` reads `c->gc.pos` under `pos_lock` seqcount and returns whether a position has already been visited.

## Important Invariant Documentation

The header contains the high-level concurrency contract for GC:

- GC defines a total ordering of all references it walks.
- Some references share a GC position, such as references inside the same btree node, so local locking must protect them.
- Any caller of `bch2_mark_pointers()` must hold a lock preventing GC from passing the caller’s current position.
- GC clears marks under the GC position seqlock, and bucket marking checks the GC position inside its compare/exchange loop.

This comment is the conceptual bridge between the allocation checker in `check.c` and transaction commit GC triggers in `commit.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/check.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/check_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/check_types.h

## Purpose

`check_types.h` defines small data structures used by btree GC/checking.

## Types

### GC Phases

`GC_PHASES()` expands to:

- `not_running`
- `start`
- `sb`
- `btree`

`enum gc_phase` is generated from that macro.

### `struct gc_pos`

Represents current GC progress:

- `phase`: current GC phase.
- `btree`: btree id for btree-walk phase.
- `level`: btree level.
- `pos`: btree key position.

This is the state compared by `gc_pos_cmp()` and read by `gc_visited()`.

### `struct reflink_gc`

Temporary reflink GC accounting record:

- `offset`
- `size`
- `refcount`

`reflink_gc_table` is a generic radix tree of these entries.

### `struct bch_fs_gc`

Filesystem-wide GC runtime state:

- `pos_lock`: seqcount protecting `pos`.
- `pos`: current GC position.
- `lock`: rw semaphore protecting GC state and allocation marking.

### `struct bch_fs_gc_gens`

State for asynchronous generation cleanup:

- `pos`: progress marker as `bbpos`.
- `work`: workqueue item.
- `lock`: mutex ensuring one generation GC at a time.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/check_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/commit.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/commit.c

## Purpose

`commit.c` implements btree transaction commit. It is the core path that turns staged `btree_insert_entry` updates into journal records, accounting changes, trigger side effects, btree/key-cache mutations, and retryable structural changes such as splits and merges.

The file coordinates ordering between locks, journal reservation, triggers, disk accounting, GC interaction, and recovery/journal replay.

## Main Flow

The top-level function is `__bch2_trans_commit()`:

1. Validate transaction state and maybe inject a restart.
2. Return early if there are no updates.
3. Run transactional triggers, which may append more updates.
4. Compute journal space requirements.
5. Drop no-op updates unless flags require keeping them.
6. Upgrade relevant paths to intent locks.
7. Possibly perform foreground merges before inserting.
8. Acquire extra disk reservation if requested.
9. If filesystem cannot take a write ref and commit is allowed during recovery, route to journal-replay overlay commit.
10. Retry the real commit loop:
   - lock update nodes for write,
   - reserve journal space,
   - run hooks/accounting/atomic triggers/GC triggers,
   - validate in debug builds,
   - fill journal entries,
   - mutate btree leaves or cached keys,
   - handle retryable errors.
11. Release write ref, downgrade transaction locks, and reset updates.

## Commit Flags

`bch2_trans_commit_flags_to_text()` prints the watermark and named commit flags for diagnostics.

Flags influence:

- journal reservation requirements,
- ENOSPC behavior,
- journal replay behavior,
- whether no-op updates are skipped,
- watermark escalation for btree structural work,
- whether journal reclaim paths are allowed.

## Write Locking

- `bch2_trans_lock_write_inlined()` takes write locks for update target nodes, skipping duplicate locks when consecutive updates hit the same leaf.
- `bch2_trans_unlock_updates_write()` releases write locks for all updated nodes.
- `bch2_btree_node_prep_for_write()` handles post-write cleanup and starts a new bset when the current append area is written or too large.

The file carefully separates intent locks already held by paths from write locks needed for final mutation.

## Leaf Insertion

`bch2_btree_bset_insert_key_inlined()` performs the final in-node insert/delete for non-extent overwrites:

- Validates position, node range, and space.
- Finds an existing key at the insert position.
- Marks overwritten keys deleted.
- Preserves whiteout needs when deleting already-written keys.
- Inserts into the writable current bset or appends if the old key is in a written bset.
- Fixes node iterators when key size changes.

`bch2_btree_insert_key_leaf()` wraps this with topology checks for interior nodes, journal sequence stamping, journal pinning, dirty marking, sibling size estimate updates, and whiteout compaction.

## Journal Pinning and Flush

- `__btree_node_flush()` is called when journal reclaim needs a pinned btree node written.
- `bch2_btree_node_flush0()` and `bch2_btree_node_flush1()` dispatch by write slot.
- `bch2_btree_add_journal_pin()` pins the current btree write slot to a journal sequence.

Pinned journal entries prevent reclaim until the corresponding btree write is durable.

## Insert Feasibility

- `btree_key_can_insert()` checks whether a normal btree node can fit pending updates and may wait for btree writeback pressure to drop.
- `btree_key_can_insert_cached()` handles key-cache sizing and journal reclaim pressure.
- `btree_key_can_insert_cached_slowpath()` can allocate a larger cached-key buffer after dropping locks, then relock.

Failure with `btree_insert_btree_node_full` is handled by splitting the leaf in the commit error path.

## Triggers

Two trigger classes are handled:

### Transactional Triggers

`bch2_trans_commit_run_triggers()` runs transactional triggers before the final commit. They may append further updates, so the code loops through sort-order groups until all insert/overwrite trigger halves have run.

The insert-before-overwrite ordering for a given btree avoids transiently dropping references before re-adding them, important for extent moves.

### Atomic and Memory Triggers

During final commit:

- `run_one_mem_trigger()` runs non-transactional memory/accounting triggers.
- `run_one_trans_trigger()` runs transactional trigger halves.
- `bch2_trans_commit_run_gc_triggers()` runs GC triggers only for positions GC has already visited, preserving concurrent GC correctness.

## Accounting

Accounting entries in `trans->accounting` are applied under `capacity.mark_lock`.

- `bch2_accounting_trans_commit_hook()` applies accounting.
- `trans_commit_accounting_revert()` rolls back applied accounting on failure.
- `bch2_trans_account_disk_usage_change()` applies accumulated disk usage deltas.

In early fsck/recovery, `do_bch2_trans_commit_to_journal_replay()` applies accounting and inserts updates into the journal overlay rather than the live btree.

## Journal Construction

`bch2_trans_commit_write_locked()` fills the journal reservation after all non-fatal failure points have passed:

- Optional transaction-name log entry.
- Optional overwrite records when transaction names are enabled.
- `BCH_JSET_ENTRY_btree_keys` for normal updates.
- Prebuilt transaction journal entries.
- Accounting updates as `BCH_JSET_ENTRY_write_buffer_keys`.
- Optional external journal sequence return.
- Optional journal pin.

After journal fill, it applies updates to btree leaves or key cache.

## Journal Replay Path

When recovery has not completed, commits go through:

- `trans_commit_to_journal_replay_pre()`
- `bch2_check_drop_overwrites_from_journal()`
- `do_bch2_trans_commit_to_journal_replay()`
- `trans_commit_to_journal_replay_post()`

This path inserts updates into the journal-key overlay and handles root journal entries without performing normal RW btree mutation.

## Error Handling and Retries

`bch2_trans_commit_error()` handles retryable failures:

- Journal reservation blocked: drop locks and acquire/wait.
- Btree node full: split leaf and restart if needed.
- Need mark replicas: update superblock accounting.
- Need journal reclaim: unlock, wait for key-cache/journal reclaim, relock.
- Nested commits with `no_journal_res`: force transaction restart.

Fatal errors call `bch2_fs_fatal_error()` or emergency read-only paths.

## Structural Merge Integration

During no-op compaction and update preparation, the commit path can call `trans_commit_merge()` when a target btree node is below merge threshold. This escalates watermarks, invokes `__bch2_foreground_maybe_merge()`, and then repairs update-array pointers because path-table reallocations can move `trans->updates`.

## Important Invariants

- No journal reservation is taken until the code believes inserts can fit.
- After journal reservation, failures are treated as fatal or must be handled without abandoning the reservation.
- Trigger execution must be complete before journal fill and in-memory mutation.
- No-op inode updates are retained because fsync depends on updated journal sequence state.
- GC triggers run only for GC-visited positions.
- Btree structural changes are retryable and expressed as transaction restarts.
- Commit must leave locks verifiable after every retry path.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/commit.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/init.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/init.c

## Purpose

`init.c` contains btree subsystem lifecycle initialization/teardown plus an extensive embedded design document explaining bcachefs btree architecture.

## Embedded Design Documentation

The file documents bcachefs as a transactional key-value store built on B+trees. It states that filesystem metadata such as extents, inodes, dirents, allocation state, snapshots, quotas, stripes, and accounting all live as key-value pairs in btrees rather than separate specialized structures.

Documented btree groups include:

- Core filesystem data: extents, inodes, dirents, xattrs, reflink.
- Allocation and space management: alloc, freespace, need_discard, bucket_gens, backpointers.
- Snapshots/subvolumes: subvolumes, snapshots, snapshot_trees, subvolume_children, deleted_inodes.
- Reconcile/background maintenance queues.
- Other metadata: quotas, stripes, LRU, logged ops, accounting.

The documentation emphasizes:

- Shallow large btree nodes for scale.
- Atomic cross-object operations through shared transactions.
- Online fsck/repair through the transaction and locking infrastructure.
- Efficient background maintenance via backpointers.
- Snapshot efficiency through snapshot-aware key positions.
- No duplicate keys.
- Deletion by whiteouts because written bsets cannot be modified in place.
- Ordering preservation through journal sequencing.
- Log-structured btree nodes composed of multiple sorted bsets.
- Packed on-disk keys via `bkey_format`.
- Interior btree pointers whose key position is child max key and whose value includes child `min_key`.

## Lifecycle Functions

### `bch2_fs_btree_exit()`

Destroys btree subsystems in reverse-ish dependency order:

- node scan,
- write buffer,
- key cache,
- iterators,
- interior update subsystem,
- evicted-size table,
- btree cache,
- read/write completion workqueues,
- bounce/fill pools and bioset.

### `bch2_fs_btree_init_early()`

Initializes lock/list-only and early structures:

- btree cache,
- interior update state,
- iterators,
- write buffer,
- node scan.

This is early enough to run before full allocation-backed initialization.

### `bch2_fs_btree_init()`

Allocates core btree runtime resources:

- sets foreground merge threshold,
- computes sort iterator pool size from btree block count,
- creates high-priority read completion workqueue,
- initializes fill iterator mempool,
- initializes btree bio set,
- initializes bounce buffer mempool sized to btree node size,
- initializes btree cache,
- initializes iterators,
- initializes key cache,
- initializes read error ratelimiters.

Returns `ENOMEM_fs_other_alloc` on allocation failure.

### `bch2_fs_btree_init_rw()`

Initializes RW-only btree resources:

- high-priority write completion workqueue,
- interior update worker/pool,
- write buffer,
- evicted-size tracking.

This separates mount/read preparation from resources only needed after RW transition.

## Dependencies

Includes btree cache, init, interior, key cache, node scan, read, sort, write, and write buffer headers.

## Important Invariants

- Workqueues and mempools must be torn down only after dependent btree subsystems are stopped.
- `foreground_merge_threshold` is computed from runtime filesystem geometry/options.
- RW initialization is separate because some resources and workers are not valid or needed during early recovery.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/init.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/init.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/init.h

## Purpose

`init.h` declares the btree subsystem lifecycle API.

## Public API

- `bch2_fs_btree_exit(struct bch_fs *)`
- `bch2_fs_btree_init_early(struct bch_fs *)`
- `bch2_fs_btree_init(struct bch_fs *)`
- `bch2_fs_btree_init_rw(struct bch_fs *)`

These correspond directly to the lifecycle functions implemented in `init.c`.

## Role

This header lets the broader filesystem mount/recovery/init code sequence btree setup and teardown in phases:

- early structure initialization,
- core btree resource allocation,
- RW resource allocation,
- final cleanup.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/init.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/interior.c -->
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
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/interior.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/interior.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/interior.h

## Purpose

`interior.h` declares and partially defines the API and helper logic for btree interior-node structural updates: topology checks, split/merge/rewrite entry points, root handling, node layout helpers, whiteout handling, journal root serialization, and update subsystem lifecycle.

## Key Types

### `enum btree_update_mode`

Generated from `BTREE_UPDATE_MODES()`:

- `none`
- `node`
- `root`
- `update`

This tracks what kind of visibility update a `btree_update` represents.

### `struct btree_update_node`

Captures a node/key participating in a structural update:

- `b`: in-memory btree node, when available.
- `level`: node level.
- `root`: whether it is a root update.
- `update_node_key`: whether the in-memory node key must be patched after reconcile.
- `seq`: sequence number for old node identity checks.
- `key`: padded btree pointer key.

`btree_update_nodes` is a preallocated dynamic array of these records.

### `struct btree_update`

The central state object for an in-progress split/merge/rewrite/root update.

Important fields:

- closure and filesystem pointer,
- list links for active/unwritten updates,
- mode and commit flags,
- `nodes_written` and `took_gc_lock`,
- btree id and node range diagnostics,
- update level range,
- `new_key_u64s` to decide split versus compact,
- disk reservation,
- blocked parent node state,
- journal pin used to hold old-node durability dependencies,
- preallocated node reserves,
- old and new node arrays,
- open bucket references,
- inline parent-key buffer.

The header comment documents the crash-consistency model: new nodes may be written before the parent update makes them visible, and old nodes cannot be reclaimed until the visibility update completes.

## Public Structural APIs

Declared functions include:

- `bch2_btree_node_check_topology_msg()`
- `bch2_btree_node_check_topology()`
- `__bch2_btree_node_alloc_replacement()`
- `bch2_btree_split_leaf()`
- `bch2_btree_increase_depth()`
- `__bch2_foreground_maybe_merge()`
- `bch2_btree_node_get_iter()`
- `bch2_btree_node_rewrite_key()`
- `bch2_btree_node_rewrite_pos()`
- `bch2_async_btree_op()`
- `bch2_btree_node_update_key()`
- `bch2_btree_set_root_for_read()`
- `bch2_btree_root_alloc_fake_trans()`
- `bch2_btree_root_alloc_fake()`

## Merge Helpers

- `btree_update_set_watermark_hipri()` escalates commit watermarks for btree structural work, mapping copygc to btree-copygc and anything below btree to btree.
- `btree_node_needs_merge()` compares sibling-size estimates against `foreground_merge_threshold`, unless merging is disabled.
- `bch2_foreground_maybe_merge()` checks locks and threshold before calling `__bch2_foreground_maybe_merge()`.

## Reserve Sizing

`btree_update_reserve_required()` computes worst-case nodes needed for a split from a given node to the root:

- If depth can grow, `(depth - level) * 2 + 1`.
- If already at max depth, `(depth - level) * 2 - 1`.

This matches the split-all-the-way-up case with possible new root allocation.

## Node Layout Helpers

The header defines several inline helpers for interpreting and managing btree node buffers:

- `btree_node_reset_sib_u64s()`
- `btree_data_end()`
- `unwritten_whiteouts_start()`
- `unwritten_whiteouts_end()`
- `write_block()`
- `__btree_addr_written()`
- `bset_written()`
- `bkey_written()`
- `__bch2_btree_u64s_remaining()`
- `bch2_btree_keys_u64s_remaining()`
- `btree_write_set_buffer()`
- `want_new_bset()`

These helpers distinguish already-written bsets from appendable data, account for whiteout storage at the end of the buffer, and leave varint decode slack.

## Insert/Compact Fit Helpers

- `bch2_btree_node_insert_fits()` rejects nodes needing rewrite and checks remaining append space.
- `bch2_btree_node_compact_fits()` models whether a compacted node plus a follow-on bset for a new key can fit after write-path block rounding.

This latter helper prevents infinite compact/retry loops for leaves that still cannot accept the failed insert after compaction.

## Equality Helper

`btree_bkey_and_val_eq()` compares btree pointer keys while skipping the `mem_ptr` field for `btree_ptr_v2`, because that field can differ in memory without changing persistent identity.

## Maintenance APIs

Declared functions:

- `bch2_btree_updates_to_text()`
- `bch2_btree_interior_updates_pending()`
- `bch2_btree_interior_updates_flush()`
- `bch2_journal_entry_to_btree_root()`
- `bch2_btree_roots_to_journal_entries()`
- `bch2_async_btree_node_rewrites_flush()`
- `bch2_do_pending_node_rewrites()`
- `bch2_free_pending_node_rewrites()`
- `bch2_btree_reserve_cache_to_text()`
- `bch2_fs_btree_interior_update_exit()`
- `bch2_fs_btree_interior_update_init_early()`
- `bch2_fs_btree_interior_update_init()`

## Important Invariants

- Write lock must be held when testing insert fit because the append bset may be written out otherwise.
- Whiteouts occupy space at the end of the btree node buffer.
- Btree nodes need one extra u64 of slack for varint decode read-ahead.
- Structural updates must reserve enough nodes for recursive split/root growth.
- Active interior updates are visible via filesystem lists and can be waited on.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/interior.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/interior_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/btree/interior_types.h

## Purpose

`interior_types.h` defines compact filesystem-level structures for btree interior update allocation, reserve caching, async update tracking, and async node rewrites.

## Types and Constants

### `struct btree_alloc`

Represents a reserved but unused btree node allocation:

- `ob`: open bucket references.
- `k`: padded btree pointer key.

This is stored in the reserve cache to avoid throwing away partially allocated btree node space.

### `BTREE_RESERVE_MAX`

Maximum number of btree nodes that may need to be allocated atomically:

`BTREE_MAX_DEPTH + (BTREE_MAX_DEPTH - 1)`

This covers recursive split needs plus associated parent/root allocation.

### `BTREE_NODE_RESERVE`

Freelist size for btree node reserves:

`BTREE_RESERVE_MAX * 4`

### `struct bch_fs_btree_reserve_cache`

Filesystem cache of allocated btree node disk reservations:

- `lock`
- `nr`
- `data[BTREE_NODE_RESERVE * 2]`

The comment explains why it exists: if a btree node is allocated but unused, freeing it would force the space back through the allocator and can contribute to reserve-allocation livelock. Keeping it cached allows reuse.

### `struct bch_fs_btree_interior_updates`

Tracks active asynchronous interior updates:

- mempool for `struct btree_update`,
- active list,
- unwritten/completion list,
- lock,
- commit lock,
- waitlist,
- worker workqueue and work item.

This structure backs the split/merge/rewrite async completion machinery in `interior.c`.

### `struct bch_fs_btree_node_rewrites`

Tracks queued async node rewrite/merge work:

- active list,
- pending list,
- spinlock,
- waitlist,
- worker workqueue.

Pending rewrites are held until journal replay/RW state permits execution.

## Important Invariants

- Reserve cache is lock-protected and stores ownership of open bucket references.
- Interior update completion has both a general lock and a separate commit lock to serialize sensitive parent/root-key update completion.
- Node rewrite tracking uses a spinlock because it is small, list-oriented queue state.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/btree/interior_types.h -->