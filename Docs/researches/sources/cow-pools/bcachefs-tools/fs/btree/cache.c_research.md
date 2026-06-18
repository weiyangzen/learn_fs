# File Research: sources/cow-pools/bcachefs-tools/fs/btree/cache.c

## Purpose
Implements the in-memory btree node cache: allocation, state transitions, hash lookup, pinning, reclaim/shrinker integration, cache cannibalization under memory pressure, btree-node fill/read paths, eviction, init/exit, evicted-size hints, and diagnostics.

## Cache Model
Btree nodes are hashed by physical on-disk pointer, not logical position, because bcachefs btree updates are copy-on-write. `struct btree` shells are normally retained until shutdown, allowing lock drop/reacquire patterns without refcounting.

## State Machine
`bch2_btree_node_transition_state_locked()` maintains the canonical cache states:
- `NONE`: off lists and not hashed.
- `FREED`: shell only, no data buffer.
- `FREEABLE`: unhashed with buffer, available for reuse.
- `CLEAN`: hashed/live, clean.
- `DIRTY`: hashed/live, dirty or write in flight.

The transition function handles:
- rhashtable insertion/removal,
- list movement,
- per-btree counts,
- pinned vs unpinned live lists,
- vmalloc accounting,
- buffer freeing,
- lock wakeups on identity removal.

## Allocation
- `__btree_node_data_alloc()` allocates node data and aux buffers with kernel/user differences:
  - kernel uses `kvmalloc`/`__vmalloc`,
  - userspace path can `mmap()` executable aux space.
- `__btree_node_mem_alloc()` creates the `struct btree` shell and initializes locks.
- `bch2_btree_node_mem_alloc()` first tries freeable nodes, self-reclaim under high memory pressure, allocator paths, freed shell reuse, and finally cannibalization.

## Pinning
- `__btree_node_pinned()` checks configured pinned ranges using `bbpos`.
- `bch2_node_pin()` moves a live node from unpinned to pinned lists.
- `bch2_btree_cache_unpin()` clears pin masks and splices pinned lists back into normal lists.

## Reclaim / Shrinker
- `bch2_btree_cache_scan()` reclaims from `freeable` and clean live lists while preserving reserve nodes.
- Reclaim skips permanent, noevict, write-blocked, will-make-reachable, dirty, read-in-flight, and write-in-flight nodes unless the caller allows dirty reclaim.
- Dirty cannibalized nodes are written before reuse.
- `not_freed[]` counters explain shrinker misses.

## Cannibalization
- `bch2_btree_cache_cannibalize_lock()` serializes emergency cache reuse through `bc->alloc_lock`.
- `btree_node_cannibalize()` searches clean lists first, then dirty lists with writeback/wait.
- This is used when normal node allocation fails and the transaction already holds the cannibalize lock.

## Lookup / Fill
- `btree_cache_find()` performs rhashtable lookup by btree pointer hash.
- `bch2_btree_node_fill()` allocates a node, validates pointer key shape, transitions it into the clean hash state, marks read-in-flight, unlocks for IO when needed, reads from disk, and relocks.
- `bch2_btree_node_get()` has a fast path through `btree_ptr_v2.mem_ptr`; it validates `hash_val`, locks the node, checks for reuse/read errors/read-in-flight, prefetches aux data, and verifies headers.
- `__bch2_btree_node_get()` is the slower lookup/fill/retry path.
- `bch2_btree_node_get_noiter()` provides lookup without a `btree_path`.
- `bch2_btree_node_prefetch()` starts async fill/read when absent.

## Eviction
`bch2_btree_node_evict()`:
- finds cached node,
- waits on read/write IO,
- locks intent/write,
- writes dirty nodes before eviction,
- records evicted live size,
- transitions to `FREED`.

Permanent/root nodes must not be evicted.

## Init / Exit
- `bch2_fs_btree_cache_init_early()` initializes locks and lists.
- `bch2_fs_btree_cache_init()` initializes rhashtable, reserve nodes, and two shrinkers: normal and pinned.
- `bch2_fs_btree_cache_exit()` frees shrinkers, drains write-complete workqueue, drains all live/freeable nodes to freed, frees shells, verifies counters, and destroys the hash table.

## Diagnostics
- `bch2_btree_id_str()`, `bch2_btree_id_to_text()`, and `bch2_btree_id_level_to_text()` print btree IDs.
- `bch2_btree_pos_to_text()` and `bch2_btree_node_to_text()` describe cached nodes.
- `bch2_btree_cache_to_text()` reports live/pinned/vmalloc/reserve/freeable/dirty/in-flight counts, per-btree memory, cannibalize state, and not-freed counters.
- `btree_cache_exit_locked_dump()` emits lock-owner diagnostics before teardown BUGs.

## Risks / Review Notes
- Correctness depends on checking identity after locking, because cache lookups race with node reuse.
- State transitions require write locks for hash/buffer transitions; assertions enforce this.
- Reclaim has to preserve reserve nodes to guarantee forward progress for btree updates.
- The userspace `mmap(PROT_EXEC)` aux-data allocation is tied to the dormant compiled-unpack path and may matter if that feature is re-enabled.
