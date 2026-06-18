# File Research: sources/block-storage/linux-dm/drivers/md/bcache/btree.c

## Purpose
Implements bcache's btree cache, btree node IO, root management, GC, startup btree checking, insertion and splitting, traversal APIs, key-buffer scanning, and btree workqueue lifecycle.

## Main Interfaces
- Node IO: `bch_btree_node_read_done()`, `bch_btree_node_write()`, `__bch_btree_node_write()`.
- Cache management: `bch_btree_cache_alloc()`, `bch_btree_cache_free()`, `bch_btree_node_get()`, `__bch_btree_node_alloc()`.
- GC/checking: `bch_gc_thread_start()`, `bch_initial_gc_finish()`, `bch_btree_check()`, `bch_initial_mark_key()`, `bch_update_bucket_in_use()`.
- Insertion/root: `bch_btree_insert_check_key()`, `bch_btree_insert()`, `bch_btree_set_root()`.
- Traversal: `__bch_btree_map_nodes()`, `bch_btree_map_keys()`, `bch_btree_map_keys_recurse()`.
- Keybuf: `bch_keybuf_init()`, `bch_refill_keybuf()`, `bch_keybuf_check_overlapping()`, `bch_keybuf_next()`, `bch_keybuf_next_rescan()`, `bch_keybuf_del()`.
- Lifecycle: `bch_btree_init()`, `bch_btree_exit()`.

## Control Flow
Node reads load the on-disk bucket, validate bset sequence, version, magic, checksums, and block bounds, then merge/sort/fix extents into in-memory form. Node writes append the current unwritten bset with FUA metadata IO, pins journal references for dirty leaves, and schedules delayed writeback for dirty nodes. The btree cache reuses nodes through LRU/freeable/freed lists and can cannibalize cached nodes under memory pressure.

Insertions walk leaves with `bcache_btree_root()`/`bcache_btree()` recursion macros, insert until a node lacks space, then restart with stronger locking or split/compact the node. Splits can create a sibling and, when the root splits, a new root. Freed btree nodes are represented by generation-incremented zero keys inserted into the parent before prio writes may proceed.

GC clears mark state, walks/rechecks the btree, marks live metadata/data/dirty buckets, coalesces sparse sibling nodes, rewrites stale or inefficient nodes, flushes dirty leaves, then recomputes available buckets and `need_gc`. Startup checking parallelizes subtrees below the root across up to half the online CPUs.

## State And Synchronization
Btree nodes use rwsems for tree access, a `write_lock` mutex for write state, `io_mutex` plus closures for in-flight metadata IO, and flags for dirty, IO error, write index, and journal flush. Cache-set `bucket_lock`, `btree_cannibalize_lock`, cache lists, shrinker, and wait queues coordinate allocation and memory reclaim. GC cooperates with front-side IO through `search_inflight`, `sectors_to_gc`, and `gc_wait`.

## Integration Points
Uses allocation from `alloc.c`, key/bset mechanics from `bset.c`, extent and interior pointer ops from `extents.c`, journal metadata writes, moving GC, writeback key buffers, debug verification, tracepoints, block bio helpers, and Linux shrinker/workqueue/kthread APIs.

## Notable Behaviors
- Btree nodes are log structured: writes append bsets until sorting/compaction or split is needed.
- The root is pinned outside the btree cache LRU and updated only after journal metadata persistence.
- The btree cache reserve is required for forward progress under memory pressure.
- GC may intentionally return `-EAGAIN` to yield when front-side IO is in flight or rescheduling is needed.
- `bch_btree_insert_check_key()` upgrades read to write locking using node pointer and sequence checks to avoid cache-miss races.

## Risks And Review Focus
- Lock ordering among btree rwsems, `write_lock`, `io_mutex`, `bucket_lock`, journal flush state, and cannibalization is highly sensitive.
- Crash consistency depends on ordered node writes, journal pins, generation persistence, and parent updates.
- Split/GC paths deliberately invalidate iterators and rely on restart conventions.
- Memory reclaim must never consume the btree cache reserve needed for future inserts.
