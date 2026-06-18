# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/types.h

This is the central type definition header for bcachefs B-tree state.

Major structures:
- `btree_nr_keys`: live metadata and per-bset key accounting.
- `bset_tree`: offsets and aux-tree layout for one bset.
- `btree_bkey_cached_common`: shared lock/id/level/cached fields for B-tree nodes and cached keys.
- `struct btree`: cached B-tree node state, including cache membership, flags, format, data buffer, bsets, write pins, key pointer, async interior-update blockers, open buckets, and LRU/cache list links.
- `bch_fs_btree_cache`: root state, rhashtable, freeable/freed/live node lists, inflight counters, shrinker stats, allocation cannibalization state, and pinned-node metadata.
- `btree_path` and `btree_iter`: low-level locked traversal path and high-level key iterator.
- `btree_insert_entry`: pending transaction update entry.
- `btree_trans`: transaction context with paths, sorted lock order, updates, bump allocator, journal reservation/subbuffers, locks, restart state, hooks, and embedded initial storage.
- `bch_fs_btree`: filesystem-level B-tree subsystem including cache, key cache, write buffers, trans pool, reserve cache, interior updates, node rewrites, and node scan state.

Important flags and policy:
- Defines iterator/update/trigger flag bits, transaction path limits, write types, node flags, and rewrite reasons.
- Encodes btree id properties such as extent behavior, snapshots, data pointers, write-buffer usage, and trigger ordering.
- Provides inline accessors for bsets, keys, node offsets, live/dirty cache counts, current/previous write pins, and node rewrite reason.

This file is the shared contract for nearly every file in the B-tree subsystem.
