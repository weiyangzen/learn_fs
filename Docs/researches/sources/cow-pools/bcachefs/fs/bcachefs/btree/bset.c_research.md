# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bset.c

This file implements sorted key sets inside btree nodes, auxiliary search trees, btree-node iterators, insertion/deletion within the current bset, lookup, stats, and debug rendering.

Key contents:
- Extensive documentation explains read-write bsets, read-only bsets, and auxiliary search trees.
- Text/debug helpers render btree node keys, individual bsets, and iterators.
- Key counting and verification keep `struct btree_nr_keys` consistent with actual non-deleted keys.
- Auxiliary tree implementation:
  - Read-only bsets use Eytzinger-layout array search trees with compact `struct bkey_float` nodes containing exponent, key offset, and mantissa.
  - Writable bsets use a cheaper `struct rw_aux_tree` table with one sampled key per cacheline-ish region.
  - Builders `__build_ro_aux_tree()` and `__build_rw_aux_tree()` allocate/search structures in `b->aux_data`.
  - Verification helpers check aux tree layout, offsets, and consistency.
- Bset initialization: `bch2_btree_keys_init()`, `bch2_bset_init_first()`, and `bch2_bset_init_next()`.
- Predecessor lookup uses aux structures to find a nearby previous key, then linearly scans.
- Insert/delete:
  - `bch2_bset_insert()` packs inserted keys when possible, shifts storage, writes key/value, updates bset size, lookup table, and key accounting.
  - `bch2_bset_delete()` removes clobbered u64s and fixes lookup tables.
- Lookup:
  - `bch2_btree_node_iter_init()` searches each bset using a lossy packed search key when possible, then linear-searches to the exact iterator start.
  - Fallback handles positions that cannot be packed.
- Iterator logic merges up to `MAX_BSETS` sorted bsets using compact offset pairs, with sorted advance, previous-key support, and deleted-key filtering.
- `bch2_btree_keys_stats()` reports set types, bytes, float count, and failed compressed-key nodes.
- `bch2_bfloat_to_text()` prints auxiliary-tree compression failures.

Important invariants:
- Deleted duplicate keys are sorted before the live key for equal non-extent keys; extent lookup has special semantics around equal positions.
- Auxiliary tree nodes may fail compressed comparison and fall back to real-key comparison.
- Debug branches aggressively verify sorted order, insert positions, lookup tables, and accounting.
