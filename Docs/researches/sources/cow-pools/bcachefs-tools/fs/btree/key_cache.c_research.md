# File Research: sources/cow-pools/bcachefs-tools/fs/btree/key_cache.c

## Purpose
`key_cache.c` implements the btree key cache: a hash-table-backed cache for frequently accessed single keys, especially alloc-btree keys touched by extent updates. It supports cached path traversal, fill/reuse/eviction, dirty-key flushing through journal reclaim, read-only transition flushing, and shrinker integration.

## Main Responsibilities
- Allocates, initializes, reuses, and frees `struct bkey_cached` objects, including separate pending queues for normal and per-CPU-reader SIX locks.
- Implements cached traversal with `bch2_btree_path_traverse_cached()`: find a cached key, lock it as a cached btree path, or fill from the underlying btree/journal.
- Creates cache entries with `btree_key_cache_create()`, sizing the key buffer with extra room to avoid commit-time realloc restarts.
- Flushes dirty cached entries back to the real btree with `btree_key_cache_flush_pos()` and journal pin callback `bch2_btree_key_cache_journal_flush()`.
- Provides `bch2_btree_key_cache_flush_going_ro()` to force dirty cache entries out during read-only transition without creating new journal pins.
- Applies cached updates in `bch2_btree_insert_key_cached()` and drops stale cache entries in `bch2_btree_key_cache_drop()` when the underlying btree is updated directly.
- Registers a memory shrinker that evicts clean, unaccessed, lockable cache entries and records shrinker statistics.
- Initializes and tears down global and per-filesystem key-cache state.

## Important Behaviors
- Dirty cached keys are journal-pinned. The flush path may re-journal in normal reclaim but the going-read-only path forces `no_journal_res` so cleanup converges.
- Cache fill uses a normal iterator with key-cache fill flags and disables journal overlay after it has explicitly checked replay keys.
- Eviction only takes clean entries. Dirty entries must be flushed first and have their journal pins dropped.
- Cached btree paths use the same lock/path infrastructure as btree nodes, with the cached object stored in `path->l[0].b` and marked cached.
- Pending freed entries are RCU/SRCU delayed; reuse tries to claim intent+write locks without blocking so entries are not reused while readers may still observe them.

## Dependencies and Coupling
- Depends on `iter.c` path management, `locking.c` SIX lock helpers, journal reclaim/pin APIs, rhashtable, shrinker APIs, and update/commit paths.
- `iter.c` consults this file through `bch2_btree_path_traverse_cached()`, `bch2_btree_key_cache_find()`, and cached path semantics.

## Research Notes
- This is a high-performance coherency layer. Bugs are likely to involve stale cache entries, journal pin sequencing, dirty count accounting, direct btree updates bypassing cache, or lock/SRCU lifetime interactions.
