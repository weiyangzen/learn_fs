# File Research: sources/cow-pools/bcachefs-tools/fs/btree/cache.h

## Purpose
Declares btree cache APIs and provides inline helpers for root packing, cache state inspection, node sizing, evicted-size hints, btree id lookup, and diagnostics.

## Main API Declarations
- cache lifecycle:
  - `bch2_fs_btree_cache_init_early()`
  - `bch2_fs_btree_cache_init()`
  - `bch2_fs_btree_cache_exit()`
- node allocation/free:
  - `__bch2_btree_node_mem_alloc()`
  - `bch2_btree_node_mem_alloc()`
  - `bch2_btree_node_mem_free()`
  - `bch2_btree_node_data_free()`
- cache state:
  - `bch2_btree_node_transition_state()`
  - `bch2_btree_node_transition_state_locked()`
  - `bch2_btree_node_set_dirty()`
  - `bch2_btree_node_write_done_clean()`
- lookup/fill/prefetch/evict:
  - `bch2_btree_node_get()`
  - `bch2_btree_node_get_noiter()`
  - `bch2_btree_node_prefetch()`
  - `bch2_btree_node_evict()`
- pinning and cannibalization:
  - `bch2_node_pin()`
  - `bch2_btree_cache_unpin()`
  - `bch2_btree_cache_cannibalize_lock()`
  - `bch2_btree_cache_cannibalize_unlock()`

## Inline Helpers
- Evicted-size table:
  - `btree_evicted_size_pack()`
  - `bch2_btree_evicted_size_record()`
  - `bch2_btree_evicted_size_lookup()`
- Btree pointer identity:
  - `btree_ptr_hash_val()`
  - `btree_node_mem_ptr()`
- Cache state:
  - `btree_node_hashed()`
  - `btree_node_cache_state()`
  - `btree_node_live_state()`
- Node sizing:
  - `btree_buf_bytes()`
  - `btree_buf_max_u64s()`
  - `btree_max_u64s()`
  - `btree_sectors()`
  - `btree_blocks()`
- Thresholds:
  - `BTREE_SPLIT_THRESHOLD`
  - foreground merge thresholds and hysteresis
- Root lookup and packing:
  - `bch2_btree_id_root()`
  - `bch2_btree_root_pack()`
  - `bch2_btree_root_unpack_b()`
  - `bch2_btree_root_unpack_level()`
  - `bch2_btree_id_root_packed()`
  - `bch2_btree_id_root_b()`
  - `btree_node_root()`
  - `btree_node_is_root()`

## Notable Details
- Root pointer and level are packed into one word using three low bits, relying on `struct btree` alignment.
- Standard roots use a hot side array `roots_b[]`; extra roots fall back to `roots_extra`.
- `btree_node_live_state()` treats dirty or write-in-flight nodes as `DIRTY`, otherwise `CLEAN`.
- `btree_node_buf_swap_account()` tracks vmalloc count when node buffers are swapped.

## Risks / Review Notes
- `btree_node_is_root()` assumes a root exists and compares levels; callers must use it only when root lookup is valid.
- Packed root pointer helpers depend on pointer alignment and `BTREE_MAX_DEPTH` fitting in three bits.
- `btree_ptr_hash_val()` reads raw little-endian-ish fields through casts to avoid sparse warnings; it is identity-oriented, not semantic decoding.
