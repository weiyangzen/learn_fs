# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/key_cache.c

## Role

This file implements the btree key cache: an rhashtable-backed cache for frequently accessed single keys in selected btrees. Cached keys behave like lockable synthetic leaf nodes and are integrated with the normal btree transaction, lock, journal pin, and shrinker systems.

The main user called out in the file is the alloc btree, where extent operations repeatedly read/update bucket allocation keys.

## Major Responsibilities

- Lookup cached keys by `(btree_id, bpos)`.
- Fill cache entries from ordinary btree lookups and replay journal overlay keys.
- Represent cached entries as `struct bkey_cached` objects protected by SIX locks.
- Integrate cached entries with `struct btree_path` traversal.
- Track dirty cached keys and pin journal sequences until flushed.
- Flush dirty cached keys to real btrees for journal reclaim and read-only transition.
- Drop stale cache entries when updates bypass the key cache.
- Reclaim clean cache entries through a shrinker.
- Reuse freed cache objects after SRCU-safe pending callbacks.
- Initialize and destroy per-filesystem cache state and the global slab cache.

## Lookup And Fill

`bch2_btree_key_cache_find()` performs rhashtable lookup using `struct bkey_cached_key`.

`bch2_btree_path_traverse_cached()` first tries `btree_path_traverse_cached_fast()`. The fast path finds the cached key, takes the desired SIX lock, verifies the key still matches after locking, marks it accessed, and installs it into the btree path.

On miss, `btree_key_cache_fill()` performs a real btree slot lookup with flags that avoid recursive cache fill, optionally overlays a journal replay key, marks deleted entries for immediate flush, then calls `btree_key_cache_create()`.

`btree_key_cache_create()` allocates or reuses a cache object, sizes its key buffer with slack to avoid transaction commit reallocations, copies the key, write-locks the underlying btree node to serialize insertion, inserts into the rhashtable, and converts the cached path to point at the new cached key.

## Allocation And Reuse

Cache objects are allocated from a global `bkey_cached` slab plus a separately allocated key buffer. Freed objects are not immediately reused: `bkey_cached_free_noassert()` queues them through `rcu_pending`, with separate queues for normal and per-CPU-reader locks.

`bkey_cached_alloc()` first tries to claim pending objects whose locks are idle, then attempts fresh allocation using the transaction lock-dropping allocation helper, and finally can steal from all pending queues. `bkey_cached_reuse()` scans the hashtable for clean, unaccessed, lockable entries to evict when allocation fails.

## Dirty Tracking And Journal Pins

`bch2_btree_insert_key_cached()` copies an inserted key into the cached object, marks it dirty if needed, increments `nr_dirty`, records or updates the journal sequence, adds a journal pin, and kicks journal reclaim if the dirty ratio is too high.

The comments are explicit that nojournal commits must not advance `ck->seq` unless the pin is inactive, otherwise a crash could lose a dirty cached update.

`bch2_btree_key_cache_journal_flush()` is the journal reclaim callback. It uses a lockless bailout when the key is already clean or pinned past the requested sequence, then locks the cached key through a transaction path, handles races with pin sequence updates, and flushes the key if appropriate.

## Flushing

`btree_key_cache_flush_pos()` is the core flush routine. It opens an ordinary btree slot iterator and a cached iterator, traverses the cached key, and if the key is dirty and sequence-matched, stages an internal update to the real btree, commits it with reclaim/no-ENOSPC/no-skip-noops flags, drops the journal pin, and clears dirty state or evicts the entry.

When evicting, it unlocks unrelated transaction paths, takes a nofail write lock on the cached entry, clears dirty state, removes it from the hashtable, and frees it.

`bch2_btree_key_cache_flush_going_ro()` directly walks dirty entries while going read-only. It forces `BCH_TRANS_COMMIT_no_journal_res` so flushing drops existing pins without creating fresh ones, allowing read-only cleanup loops to converge.

## Dropping Stale Entries

`bch2_btree_key_cache_drop()` handles updates that bypass the key cache. It clears dirty state and journal pins, evicts and frees the cached key, unlocks or invalidates every transaction path that points at it, marks those paths for retraversal, and verifies transaction locks.

## Shrinker

`bch2_btree_key_cache_scan()` scans the rhashtable under SRCU and RCU. It skips dirty entries, clears recently accessed entries on first pass, skips entries it cannot lock, evicts clean lockable entries, records skip/free stats, and advances `shrink_iter`.

`bch2_btree_key_cache_count()` reports reclaimable clean keys minus a small reserve to avoid excessive shrinker pressure and lock contention when the cache is nearly empty.

## Init, Exit, Diagnostics

`bch2_fs_btree_key_cache_init()` initializes pending queues, the rhashtable, and the shrinker. `bch2_fs_btree_key_cache_exit()` frees shrinker state, drains/evicts all hashtable entries while handling rehash races, asserts dirty/key counters are zero when required, destroys the rhashtable, pending queues, and percpu counters.

`bch2_btree_key_cache_to_text()` prints counters and shrinker stats. `bch2_btree_key_cache_init()` and `bch2_btree_key_cache_exit()` create/destroy the global slab cache.
