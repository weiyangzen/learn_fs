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
