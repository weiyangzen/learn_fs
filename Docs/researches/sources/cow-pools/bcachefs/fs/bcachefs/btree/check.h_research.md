# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/check.h

This header declares bcachefs btree checking and GC entry points, and defines inline helpers for ordering online garbage-collection progress against concurrent btree updates.

Core responsibilities:
- Declares full-btree consistency entry points: `bch2_check_topology()` and `bch2_check_allocations()`.
- Defines `gc_phase()` and `gc_pos_btree()` constructors for `struct gc_pos`.
- Defines `gc_btree_order()` so allocation and stripe btrees are ordered before ordinary btree IDs during GC.
- Defines `gc_pos_cmp()` as the total ordering for GC phases, btree IDs, levels, and key positions.
- Defines `gc_visited()` as a seqcount-protected check of whether a reference position is at or behind current GC progress.
- Declares GC diagnostics and operations: `bch2_gc_pos_to_text()`, `bch2_gc_gens()`, `bch2_gc_gens_async()`, `bch2_merge_btree_nodes()`, and early GC initialization.

Important invariants:
- Concurrent mark/sweep relies on a total order over all references GC walks.
- Callers that mark pointers must hold a lock preventing GC from passing their current reference position.
- Some references share the same GC position, so local object locking, such as btree-node write locks, is still required.
- GC progress is read under `c->gc.pos_lock` seqcount; writers can move the position while readers retry.

Dependencies:
- Includes btree key, GC type, and btree type declarations.
- Uses `struct bch_fs`, `struct printbuf`, `enum btree_id`, `struct bpos`, and `cmp_int()`/`bpos_cmp()` helpers from the wider bcachefs codebase.

Risk points:
- Correctness depends on every updater using the same GC position ordering as GC itself.
- If a pointer-marking path omits the relevant lock, GC can pass an update window and double-count or miss references.
