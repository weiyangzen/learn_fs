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
