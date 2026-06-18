# File Research: sources/cow-pools/bcachefs-tools/fs/btree/update.c

Read completeness: full file read, 944 lines.

Purpose: transaction update staging for btree key modifications. This file handles extent overwrite splitting/merging, snapshot whiteout insertion, key-cache update routing, sorted pending-update insertion, transaction subbuffer allocation, delete/range-delete helpers, bit updates, and journal log entries.

Major components:
- `btree_insert_entry_cmp()` orders pending updates by trigger order, cached state, level, and position so commit can run updates deterministically.
- Extent merge helpers `extent_front_merge()` and `extent_back_merge()` coalesce adjacent mergable extents when journal replay is complete and snapshot overwrite checks permit it.
- Snapshot whiteout helpers `need_whiteout_for_snapshot()`, `__bch2_insert_snapshot_whiteouts()`, and `bch2_trans_update_extent_overwrite()` preserve visibility semantics when overwriting or splitting keys across snapshots.
- `bch2_trans_update_extent()` handles extent insertions by walking overlapping keys, front/back merging, converting whiteout types, splitting overwritten extents, and finally staging the non-deleted insert.
- `btree_trans_update_by_path()` is the core staging helper. It asserts path/position invariants, builds a `btree_insert_entry`, replaces an existing same-position pending update if present, snapshots the old btree key/value, consults journal overlay during replay, refs the path, and emits trace data.
- Key-cache handling uses `bch2_trans_update_get_key_cache()` and `flush_new_cached_update()` to ensure cached btrees update the key cache while preserving the invariant that a cached key also exists in the backing btree.
- `bch2_trans_update_ip()` is the public low-level update entry: it validates memory, dispatches extent updates, turns snapshot deletes into whiteouts when needed, routes cached btrees through the key cache, and triggers immediate key-cache flush when required.
- `bch2_trigger_get_mutable_new()` lets triggers grow the buffer for an in-flight inserted key before atomic trigger phase.
- Transaction arena helpers `__bch2_trans_subbuf_alloc()` and `bch2_trans_subbuf_reserve()` manage journal/accounting subbuffers inside `trans->mem`.
- Public insert/delete helpers include `bch2_btree_insert_nonextent()`, `bch2_btree_insert_trans()`, `bch2_btree_insert()`, `bch2_btree_delete_at()`, `bch2_btree_delete()`, `bch2_btree_delete_range_trans()`, and `bch2_btree_delete_range()`.
- Bitset-like helpers include `bch2_btree_bit_mod_iter()`, `bch2_btree_bit_mod()`, and `bch2_btree_bit_mod_buffered()`.
- Logging helpers append log strings and bkeys to journal entries, including early-journal storage before the journal is running.

Dependencies and integration:
- Includes iterator, journal overlay, locking, update declarations, keylist, debug, counters, and snapshot helpers.
- Depends on `update.h` for public wrappers and commit macros.
- Feeds commit logic implemented outside this file through `__bch2_trans_commit()` and transaction update arrays.
- Uses write-buffer insertion through `bch2_trans_update_buffered()` in the header and `bch2_btree_bit_mod_buffered()` here.

Risks and validation notes:
- Snapshot and extent overwrite paths are sensitive: wrong whiteout type or split boundaries can expose stale extents in descendant snapshots.
- During journal replay, normal write-buffer use is mostly bypassed except accounting and need-discard cases because replay synchronization depends on locked btree nodes.
- Pending update replacement assumes triggers have not run on the overwritten pending entry.
- Key-cache coherency requires immediate backing-btree flush when a new cached update would otherwise have no old btree key.
