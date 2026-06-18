# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/sparse-cache.c

## Purpose
Implements the sparse chapter-index cache used by sparse UDS indexes after dense/open/writing chapter lookups fail. It caches complete chapter indexes, maintains per-zone LRU search lists, and uses barrier coordination so cache membership changes are lock-free for normal reads.

## Important APIs, Types, And Functions
Public functions are `uds_make_sparse_cache()`, `uds_free_sparse_cache()`, `uds_sparse_cache_contains()`, `uds_update_sparse_cache()`, `uds_invalidate_sparse_cache()`, and `uds_search_sparse_cache()`. Private types include `cached_chapter_index`, `cached_index_counters`, `search_list`, `threads_barrier`, and `sparse_cache`.

Important helpers are `enter_threads_barrier()`, `initialize_cached_chapter_index()`, `make_search_list()`, `set_newest_entry()`, `purge_search_list()`, `cache_chapter_index()`, `copy_search_list()`, `should_skip_chapter()`, and `search_cached_chapter_index()`.

## Control Flow
Normal membership checks linearly scan the calling zone's search list up to `first_dead_entry`, update that zone's LRU order, and only zone zero updates hit/miss scoring. Cache update is called once by every zone for the same virtual chapter. All zones enter a begin barrier; zone zero purges dead/skipped entries, moves an eviction candidate to the front, reads the requested chapter index from the volume if still valid, and copies its search list to all other zones; all zones then leave through an end barrier.

Search scans active cached chapters unless a specific virtual chapter is requested. It skips dead, expired, or heuristic-skipped chapters, finds the right index page through the page map, searches that delta index page, promotes hits in the local LRU list, and records zone-zero hit/miss scores. Many misses set `skip_search` to avoid repeated full-cache scans until a targeted hook hit clears it.

## State And Persistence
The cache is volatile. Each cached entry owns dm-bufio page buffers and decoded `delta_index_page` arrays. `virtual_chapter == NO_CHAPTER` is the sole membership-dead marker. Search lists are per-zone and cache-line aligned; cache entry counters are also separated to reduce false sharing. No read locks are taken outside coordinated update barriers.

## Dependencies And Integration Points
Depends on geometry, chapter-index search, volume chapter-index reads, index zones, page maps, dm-bufio, semaphores, allocation, logging, and assertions. `index.c` creates sparse barrier messages through triage and invokes updates from zone workers.

## Risks
Correctness relies on every zone reaching `uds_update_sparse_cache()` exactly once for the same chapter; missing or duplicated barrier messages can deadlock or diverge cache membership. `uds_sparse_cache_contains()` must remain invariant between updates even for expired or skipped chapters. Zone zero is the only writer inside the critical section, so any future mutation outside that path risks races with lock-free readers. `__down()` loops on interrupted semaphore waits, so deadlocks can consume time even if signals arrive.

## Test Signals
Test single-zone simulated updates, multi-zone barrier ordering, cache hit/miss search, LRU promotion, eviction of dead entries before live entries, skip threshold behavior, expired chapter handling, invalidate/free releasing dm-bufio buffers, and fault injection for volume chapter-index read failures.
