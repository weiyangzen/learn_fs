# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/interior.h

This header defines the public interface and key inline helpers for bcachefs interior btree updates, node split/merge/rewrite operations, btree root handling, and btree-node capacity accounting.

Core responsibilities:
- Defines `BTREE_UPDATE_NODES_MAX`, update modes, `struct btree_update_node`, and the central `struct btree_update`.
- Describes the crash-consistency model for split/rewrite operations: new child nodes are written, then parent/root updates make them visible, then old nodes can be freed.
- Declares topology checking, split, merge, depth increase, node rewrite, async operation, node-key update, root setup, journal root serialization, flush, diagnostics, and lifecycle functions.
- Defines `btree_update_set_watermark_hipri()` to raise write watermarks for btree metadata paths.
- Defines `btree_update_reserve_required()` for worst-case split allocation requirements.
- Defines helpers for sibling-size reset, btree data bounds, unwritten whiteouts, write-block boundaries, written-address tests, and remaining key capacity.
- Defines `want_new_bset()` to decide when an append should start a new bset.
- Defines `push_whiteout()` to preserve deletion semantics when overwriting written keys.
- Defines `bch2_btree_node_insert_fits()` and `bch2_btree_node_compact_fits()` for insert/split decisions.
- Defines `btree_bkey_and_val_eq()`, intentionally ignoring the mutable `mem_ptr` field in `btree_ptr_v2` values.

Important invariants:
- `struct btree_update` owns replacement-node reserves, old/new node lists, journal pin state, disk reservation, write-blocked parent linkage, and inline parent key storage.
- `BTREE_RESERVE_MAX` and `BTREE_UPDATE_NODES_MAX` bound how many nodes a worst-case split/merge can allocate atomically.
- `bch2_btree_keys_u64s_remaining()` leaves one extra u64 for varint decode slack.
- `bch2_btree_node_insert_fits()` refuses inserts into nodes marked need-rewrite.
- `bch2_btree_node_compact_fits()` models write-path block rounding, preventing compact/retry loops where the follow-on key would still not fit.
- Whiteouts are stored at the end of node data and counted against remaining capacity.

Dependencies:
- Includes btree cache, locking, update declarations, and data write types.
- Uses btree node structures, bpos, key formats, journal pins, disk reservations, open buckets, closures, workqueues, and bcachefs transaction flags.

Risk points:
- The `struct btree_update` lifecycle is shared between foreground mutation and async completion; fields like `mode`, `nodes_written`, `b`, and `will_make_reachable` have synchronization requirements.
- Capacity helpers must stay aligned with the write path's exact rounding/slack behavior.
- `btree_bkey_and_val_eq()` deliberately skips `mem_ptr`; using a raw value comparison elsewhere would create false inequality for btree pointers.
