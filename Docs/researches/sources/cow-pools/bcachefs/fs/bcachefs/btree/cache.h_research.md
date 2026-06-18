# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/cache.h

This header exposes the btree node cache API and core inline helpers.

Key contents:
- Declarations cover reserve recalculation, node memory/data free, cache-state transitions, pin/unpin, dirty/write completion, early key update, cannibalize lock/unlock, memory allocation, node get/get_noiter/prefetch/evict, cache init/exit, and evicted-size table lifecycle.
- `btree_evicted_size_pack()`, `bch2_btree_evicted_size_record()`, and `bch2_btree_evicted_size_lookup()` maintain a compact hash-indexed record of recently evicted node live-u64 counts.
- `btree_ptr_hash_val()` derives the cache key from `KEY_TYPE_btree_ptr` start pointer or `KEY_TYPE_btree_ptr_v2` sequence.
- `btree_node_mem_ptr()` extracts the optional in-memory pointer optimization from v2 btree pointers.
- `btree_node_hashed()` and `btree_node_live_state()` classify node state from hash value and dirty/write-in-flight flags.
- `for_each_cached_btree` iterates the rhashtable under RCU.
- Size helpers compute btree buffer bytes, max key u64s, sectors, and blocks.
- Split/merge thresholds are derived from max node u64s.
- Root helpers map btree id to root, including dynamic extra roots.
- `btree_node_is_root()` verifies a node against its root and checks level consistency.
- Text rendering declarations cover btree ids, positions, nodes, and cache stats.
- `trace_btree_node()` standardizes trace rendering of node positions.

Role:
- This is the shared interface used by btree traversal, read/write, topology repair, and diagnostics to work with cached btree nodes.
