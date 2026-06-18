# File Research: sources/cow-pools/bcachefs-tools/fs/btree/types.h

Read completeness: full file read, 1205 lines.

Purpose: central type and flag definitions for bcachefs btree nodes, cache state, iterators, transaction state, key cache, write types, filesystem-level btree state, bset accessors, and btree-id property helpers.

Major type groups:
- Node/key accounting: `MAX_BSETS`, `struct btree_nr_keys`, `struct bset_tree`, and `struct btree_write`.
- Common lock identity: `struct btree_bkey_cached_common` is shared by real btree nodes and cached bkeys.
- Node cache state: `enum btree_node_cache_state` defines NONE, FREED, FREEABLE, CLEAN, and DIRTY membership states.
- `struct btree` contains the common lock header, rhashtable linkage, state flags, on-disk format/unpack metadata, node data buffers, bset trees, key counts, sibling estimates, whiteouts, current/previous write pins, node key, async write-blocking lists, open buckets, LRU list, and cache state.
- Cache/root state: `struct btree_root` and `struct bch_fs_btree_cache` hold packed root pointers, known/extra roots, rhashtable, free/live lists, in-flight counters, shrinker stats, alloc/cannibalize state, and pinned-node ranges.
- Iterator/update/trigger flags: `BTREE_ITER_FLAGS`, `STR_HASH_FLAGS`, `BTREE_UPDATE_FLAGS`, and `BTREE_TRIGGER_FLAGS` generate the shared `enum btree_iter_update_trigger_flags`.
- Path/iterator types: `struct btree_path`, `struct btree_iter`, and `struct get_locks_fail` model low-level locked paths and high-level key iterators.
- Key cache: `struct bkey_cached` stores cached non-leaf? key values with dirty/immediate flush flags, rhashtable linkage, journal pin, sequence, and RCU.
- Transaction staging: `struct btree_insert_entry`, `struct btree_trans_subbuf`, and `struct btree_trans` store path arrays, sorted path order, pending updates, bump allocation, restart/debug state, queued write bios, journal/accounting subbuffers, hooks, journal reservations, disk reservations, and inline initial storage.
- Transaction infrastructure: `struct btree_transaction_stats`, `struct bch_fs_btree_trans`, per-CPU buffers, mempools, SRCU barrier, and stats.
- Write state: `BCH_BTREE_WRITE_TYPES`, `enum btree_write_type`, `BTREE_FLAGS`, generated flag accessors, and rewrite reasons.
- Filesystem-level state: `struct bch_fs_btree` aggregates write stats, biosets, read/write workqueues, cache, evicted-size sidecar, key cache, per-btree write buffers, write-buffer workqueues, transaction state, reserve cache, interior updates, rewrites, and node scan state.

Important inline helpers:
- Cache counts: `btree_cache_nr_live()` and `btree_cache_nr_dirty()`.
- Iterator path access: `btree_iter_path()` and `btree_iter_key_cache_path()`.
- Node position: `btree_node_pos()`.
- Bset/node pointer conversion and accessors: `bset()`, `set_btree_bset_end()`, `set_btree_bset()`, `btree_bset_first()`, `btree_bset_last()`, `btree_bkey_first()`, `btree_bkey_last()`, `bset_u64s()`, `bset_dead_u64s()`, and `bset_byte_offset()`.
- Node type and btree property helpers: `__btree_node_type()`, `btree_node_type()`, `btree_node_type_has_*_triggers()`, `btree_id_is_extents()`, `btree_type_has_snapshots()`, `btree_id_is_extents_snapshots()`, `btree_type_has_snapshot_field()`, `btree_type_has_data_ptrs()`, `btree_type_uses_write_buffer()`, and `btree_trigger_order()`.

Dependencies and integration:
- Pulls in allocation, replica, bbpos, bkey, interior, key-cache, node-scan, write-buffer, journal, darray, and six-lock types.
- Almost every other file in this group depends on this header directly or indirectly.
- `struct bch_fs_btree` is the aggregation point tying node read/write, write buffer, transactions, cache, and recovery scanning together.

Risks and validation notes:
- This header carries many bitfield and packed-layout assumptions: lock state bits, root pointer low-bit packing, bkey unpack byte alignment, write type bits embedded in node flags, and `wb_key_ref` ordering in related write-buffer types.
- Transaction memory is capped by 16-bit offsets and `BTREE_TRANS_MEM_MAX`; subbuffer allocation depends on arena offsets fitting in `u16`.
- `BTREE_ITER_FLAG_BIT_*` is intended to fit in a `u16`; adding flags can break iterator flag storage if not audited.
- Many invariants are checked by `BUG_ON`/`EBUG_ON` in users rather than by this header itself.
