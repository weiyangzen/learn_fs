# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bset.c

## Purpose
Implements bset operations inside a btree node: auxiliary search-tree construction, per-bset search, insertion/deletion maintenance, btree-node iteration across multiple bsets, diagnostics, and bset statistics.

## Core Model
A btree node contains multiple sorted bsets. Each bset stores variable-length packed bkeys, so direct binary search over the raw array is not practical. This file builds auxiliary lookup structures:
- read-write bsets use a simple offset table,
- read-only bsets use a compact Eytzinger-layout search tree of `struct bkey_float`.

## Diagnostics And Verification
- `bch2_btree_node_keys_to_text()`
- `bch2_bset_to_text()`
- `bch2_dump_btree_node_iter()`
- `bch2_btree_node_count_keys()`
- `__bch2_verify_btree_nr_keys()`
- iterator and insert-position verification under debug static branches

## Auxiliary Tree Structures
- `struct bkey_float`:
  - `exponent`
  - `key_offset`
  - `mantissa`
- `struct ro_aux_tree`: array of `bkey_float`.
- `struct rw_aux_tree`:
  - btree-node key offset
  - unpacked `bpos` for comparison
- `BKEY_MANTISSA_BITS` is 16.
- Failure sentinels mark bfloat entries that must fall back to full key comparison.

## Aux Tree Construction
- `bch2_btree_keys_init()` resets bset metadata and accounting.
- `bch2_bset_build_aux_tree()` allocates aux space and builds either writable or read-only structures.
- `__build_rw_aux_tree()` records periodic key offsets for the active write set.
- `__build_ro_aux_tree()` maps cachelines into Eytzinger nodes and builds bfloats.
- `make_bfloat()` chooses the mantissa/exponent based on key ranges and differing bits.

## Insert/Delete
- `bch2_bset_insert()`:
  - verifies insert position in debug mode,
  - attempts to pack the inserted key into the node format,
  - updates live-key accounting,
  - memmoves following keys if size changes,
  - copies packed key and value,
  - fixes writable lookup table.
- `bch2_bset_delete()`:
  - removes `clobber_u64s`,
  - shifts remaining keys down,
  - updates bset end and writable lookup table.

## Search
- `bset_search_write_set()` binary-searches the writable offset table.
- `bset_search_tree()` walks the read-only Eytzinger bfloat tree with prefetching and falls back to full comparison when bfloat precision is insufficient.
- `bch2_bset_search_linear()` finishes with a linear scan inside the selected cacheline/range.
- Search can use exact packed search, lossy packed search, or unpacked search depending on pack result.

## Node Iterator
- `bch2_btree_node_iter_init()` searches each bset, prefetches candidate cachelines, linearly finalizes each candidate, then sorts per-bset cursors.
- `bch2_btree_node_iter_init_from_start()` initializes iteration from all bset starts.
- `bch2_btree_node_iter_sort()` is an unrolled small bubble sort for up to `MAX_BSETS`.
- `bch2_btree_node_iter_advance()` advances the current lowest key and re-sorts.
- `bch2_btree_node_iter_prev_all()` is explicitly expensive and reconstructs previous position across bsets.
- `bch2_btree_node_iter_peek_unpack()` returns a disassembled key/value pair.

## Important Ordering Rule
Duplicate keys can exist when deleted keys are retained. The ordering puts deleted keys before live keys for equal positions, which is required by insertion and lookup semantics.

## Risks / Review Notes
- Aux-tree correctness relies on packed key comparison, lossy search keys, and bfloat fallback being conservative.
- `bch2_btree_node_iter_init()` has a special slow path when search-position packing fails; it starts from the beginning and advances linearly.
- Insert/delete maintenance only updates writable aux trees; read-only aux trees are rebuilt when needed.
