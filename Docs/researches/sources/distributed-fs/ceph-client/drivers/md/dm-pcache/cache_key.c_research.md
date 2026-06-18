
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_key.c

## Purpose
Manages pcache cache keys: allocation/refcounting, on-media encode/decode, keyset append/flush, rb-tree search and overlap fixup, invalid-key cleanup, keyset replay during startup, and cache tree lifecycle.

## Important APIs, Types, And Functions
`cache_key_alloc()`, `cache_key_get()`, and `cache_key_put()` manage mempool-backed keys. `cache_key_encode()`/`cache_key_decode()` convert between runtime keys and `pcache_cache_key_onmedia`, optionally checking data CRCs. `cache_kset_close()` writes accumulated keysets to the key-head position, inserts `LAST` keysets when crossing segments, and flushes persistent memory. `cache_key_append()` selects a kset by offset and schedules delayed flushing or closes full/FUA keysets. `cache_subtree_search()` and `cache_subtree_walk()` provide ordered overlap traversal. `cache_key_insert()` fixes overlapping keys before rb insertion. `clean_fn()` removes generation-invalid keys. `kset_flush_fn()` retries failed keyset closure. `cache_replay()` scans persisted keysets from key tail and rebuilds request trees.

## Control Flow
Writes/read-miss fills append keys to per-kset buffers, which are written to DAX media as keysets. On insertion with fixup, existing overlapping keys are trimmed, split, or deleted so the tree contains non-overlapping current ranges. Replay reads keysets until invalid magic/CRC, follows `LAST` records across segments, decodes valid keys, marks used segments, inserts keys if their segment generation is current, and updates key head to the replay stop point.

## State And Persistence
Persistent state is the sequence of keysets in cache segments, including `LAST` records linking segments. Runtime state is rbtrees partitioned by logical range, key refs, kset buffers, delayed flush work, and segment refs. Generation numbers allow GC to invalidate old keys lazily.

## Dependencies And Integration Points
Depends on cache metadata/CRC helpers, segment allocation/refcounting, persistent memory flushes, rbtrees, mempools, workqueues, DAX safe copy, and request/GC/writeback code that consumes trees.

## Risks
Overlap fixup is subtle and tree-lock dependent; incorrect trimming can expose stale data or lose current data. `cache_kset_close()` can return `-EBUSY` when no segment is available, requiring retry. Replay trusts keyset CRC/magic boundaries and optional data CRC. There is a likely typo in `SUBTREE_WALK_RET_RESEARCH`, but it consistently means restart search. Several paths use `BUG()` for impossible states.

## Test Signals
Test insertion overlap cases (tail/head/contain/contained), empty placeholder behavior, keyset full and forced closure, segment rollover with `LAST`, replay after restart, corrupted keyset and data CRC, invalid generation cleanup, allocation fallback with preallocated keys, delayed flush retry on `-EBUSY`, and large tree teardown.
