# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bset.h

## Purpose
Declares bset and btree-node key-iteration APIs and documents the design of bsets, bkeys, btree node iterators, and auxiliary search trees.

## Main Concepts
- A bset is a contiguous sorted array of variable-length bkeys plus a header.
- A btree node consists of multiple bsets written at different times.
- In-memory nodes allow a bounded number of bsets and lazily rebuild/search them.
- Auxiliary structures index roughly one key per `BSET_CACHELINE` bytes, then finish by linear scan.

## Main Constants And Types
- `enum bset_aux_tree_type`:
  - `BSET_NO_AUX_TREE`
  - `BSET_RO_AUX_TREE`
  - `BSET_RW_AUX_TREE`
- `BSET_CACHELINE` is 256.
- Special `extra` values encode no-tree and writable-tree state.

## Helpers
- Aux tree classification:
  - `bset_aux_tree_type()`
  - `bset_has_ro_aux_tree()`
  - `bset_has_rw_aux_tree()`
  - `bch2_bset_set_no_aux_tree()`
- Btree node format setup:
  - `btree_node_set_format()` sets format, key bits, unpack constants, optional compiled format, and clears aux trees.
- Bset iteration macros:
  - `for_each_bset`
  - `for_each_bset_c`
  - `bset_tree_for_each_key`
- Key lookup support:
  - `bch2_bkey_to_bset_inlined()`
  - `bch2_bkey_prev_all()`
  - `bch2_bkey_prev()`
- Node iterator API:
  - init, push, sort, advance, prev, peek/unpack helpers.
- Accounting:
  - `btree_keys_account_key()`
  - `btree_keys_account_val_delta()`
  - add/drop macros
- Debug/statistics:
  - `struct bset_stats`
  - text dump declarations
  - debug verification wrappers

## Notable Details
- `btree_node_set_format()` also computes fast unpack constants and stores compiled-unpack length if enabled.
- Iterator comparison uses packed comparison and deleted-key tie-breaking.
- Iterator storage is small and fixed-size, matching the maximum number of in-memory bsets.

## Risks / Review Notes
- `BSET_CACHELINE` is a logical search granularity, not necessarily hardware cacheline size.
- Accounting helpers require the key to map to the correct bset; bad pointers will trip debug assertions or corrupt counts.
