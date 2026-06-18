# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/cache.c

This file implements the in-memory btree node cache: allocation, buffer ownership, hash lookup, state transitions, pinning, reclaim/shrinker integration, cannibalization under memory pressure, node read/fill, eviction, initialization/exit, evicted-size tracking, and diagnostics.

Key contents:
- Top-level documentation defines the cache model: nodes are hashed by physical btree pointer, roots are pinned, non-roots may be evicted/reused, and callers must verify identity after locking.
- Cache states are `NONE`, `FREED`, `FREEABLE`, `CLEAN`, and `DIRTY`, managed by `bch2_btree_node_transition_state_locked()` / `bch2_btree_node_transition_state()`.
- Memory allocation:
  - Data and auxiliary buffers are allocated separately.
  - Allocation avoids compaction when configured and falls back between vmalloc/kmalloc/kvmalloc.
  - Node shells preserve locks and may move through freed/freeable/live lists.
- Pinning:
  - `bch2_node_pin()` and `bch2_btree_cache_unpin()` move nodes between normal and pinned live lists according to `bbpos` ranges and btree masks.
- Dirty/write-state handling:
  - `bch2_btree_node_set_dirty()` marks nodes dirty and moves hashed nodes to dirty lists.
  - `bch2_btree_node_write_done_clean()` settles clean/dirty state after writes.
- Key update:
  - `bch2_btree_node_update_key_early()` temporarily unhashes and rehashes a cached node when its pointer key changes.
- Reclaim:
  - Shrinker scan/count functions reclaim freeable and clean nodes while respecting reserve, permanent/noevict/write-blocked/reachable/dirty/in-flight constraints.
  - `btree_node_reclaim()` obtains intent/write locks before removing nodes from live state.
- Cannibalization:
  - `bch2_btree_cache_cannibalize_lock()` serializes emergency reclaim.
  - `btree_node_cannibalize()` can reclaim clean or dirty nodes; dirty nodes are written and waited on before reuse.
- Lookup/fill:
  - `bch2_btree_node_mem_alloc()` obtains reusable or fresh node memory, possibly unlocking/relocking transactions.
  - `bch2_btree_node_fill()` allocates a node, hashes it, starts read IO, and handles races where another fill inserted the same node.
  - `bch2_btree_node_get()` and `bch2_btree_node_get_noiter()` find, lock, validate, prefetch, and return nodes.
  - `bch2_btree_node_prefetch()` starts asynchronous read/fill when absent.
- Eviction:
  - `bch2_btree_node_evict()` waits for IO, writes dirty nodes if necessary, and transitions clean nodes to freed.
- Init/exit:
  - `bch2_fs_btree_cache_init_early()`, `bch2_fs_btree_cache_init()`, and `bch2_fs_btree_cache_exit()` manage locks, lists, hash table, reserves, shrinkers, and teardown diagnostics.
- Diagnostics render btree ids, positions, nodes, and cache accounting.

Important invariants:
- Hash transitions require write lock unless both old and new states are live hashed states.
- Dirty flags are meaningful only for hashed live states.
- Permanent nodes must never be evicted.
- After any lookup and lock, `hash_val`, btree id, level, and node header are rechecked because cached nodes may be reused.
