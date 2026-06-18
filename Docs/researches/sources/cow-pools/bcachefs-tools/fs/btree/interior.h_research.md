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
