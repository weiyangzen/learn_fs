# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/check.c

This file implements btree topology repair, allocation/reference checking, GC marking, stale pointer generation cleanup, btree-node merging, and GC initialization.

Key contents:
- `bch2_gc_pos_to_text()` renders current GC phase and btree position.
- Topology repair:
  - `btree_ptr_to_v2()` normalizes old btree pointers to v2 form.
  - `set_node_min()` and `set_node_max()` update node boundary metadata, journal replacement keys, drop out-of-range keys, and rehash nodes when max key changes.
  - `btree_check_node_boundaries()` detects gaps/overlaps between sibling child nodes and decides whether to adjust min/max, drop overwritten nodes, or fill from scanned nodes.
  - `btree_check_root_boundaries()` ensures roots span `POS_MIN` to `SPOS_MAX`.
  - `btree_repair_node_end()` fixes a final child whose max does not reach the parent key.
  - `bch2_btree_repair_topology_recurse()` walks child pointers, handles unreadable/stale nodes, deletes invalid journal keys, repairs boundaries, recurses into children, and drops empty interior nodes.
  - `bch2_topology_check_root()` reconstructs unreadable roots from scans or fake roots depending on btree capabilities.
  - `bch2_check_topology()` runs topology checks for all live btrees during recovery and resets read-error ratelimiters afterward.
- GC marking/allocation checking:
  - `bch2_gc_mark_key()` validates topology at node changes, checks future key versions, ensures btree pointer allocation bitmap marking, runs check-repair triggers, commits required repair updates, then runs GC insert triggers.
  - `bch2_gc_btree_root()`, `bch2_gc_btree()`, and `bch2_gc_btrees()` walk all btrees in GC order and mark references.
  - `bch2_mark_superblocks()` marks superblock references.
  - `bch2_gc_start()`, `bch2_gc_alloc_start()`, and `bch2_gc_free()` allocate/free temporary GC state.
  - `bch2_alloc_write_key()` compares allocation btree keys with GC-recomputed bucket state and repairs data type, generation, dirty sectors, stripe sectors, cached sectors, and stripe refcount.
  - `bch2_gc_alloc_done()` applies allocation repairs across member devices.
  - `bch2_gc_write_stripes_key()` repairs erasure-coded stripe block sector counts and clears parity block counts.
  - `bch2_check_allocations()` orchestrates full reference checking: flush interior updates, start accounting/dev/reflink/alloc GC state, mark superblocks, walk btrees, repair alloc/accounting/stripes/reflink, clear GC state, wake allocators, and clean deleted member records.
- Generation cleanup:
  - `bch2_gc_gens()` snapshots oldest bucket generations, walks data-pointer btrees to drop stale ptrs, writes oldest generations back to alloc keys, updates the superblock `no_stale_ptrs` compat bit, and frees temporary arrays.
  - `bch2_gc_gens_async()` queues async generation cleanup under a write reference.
- Btree merge pass:
  - `merge_btree_node_one()` checks whether a node needs merging and calls foreground merge when appropriate.
  - `bch2_merge_btree_nodes()` scans every live btree and level, merging underfull nodes and logging merge counts.
- `bch2_fs_btree_gc_init_early()` initializes GC position seqcount, async work, GC lock, and generation lock.

Important invariants:
- Topology repair runs during mount/recovery and relies on old nofail lock assumptions because no worker contention should exist yet.
- GC trigger execution is carefully split because some trigger modes are not idempotent across transaction restarts.
- GC traversal order matters to avoid missing references that move during index updates.
