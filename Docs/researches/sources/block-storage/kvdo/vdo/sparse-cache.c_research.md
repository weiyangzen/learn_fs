# File Research: sources/block-storage/kvdo/vdo/sparse-cache.c

This file implements the UDS sparse chapter index cache. The cache stores complete sparse chapter indexes for fallback dedupe lookup after faster paths fail. Its critical design is unsynchronized reads by zone threads with cache membership changes coordinated only through triage-issued barrier messages and `update_sparse_cache()`.

Important invariants:
- Cache membership is represented solely by `cached_chapter_index.virtual_chapter`; `UINT64_MAX` means dead/unused.
- Membership answers from `sparse_cache_contains()` must not vary between coordinated update calls, even if a chapter becomes too old or marked `skip_search`.
- Only zone zero mutates shared cache membership during the barrier-protected critical section; other zone search lists are copied from zone zero afterward.
- Each zone keeps an independent `search_list` LRU order, avoiding synchronization for search and membership checks.

Data model:
- `cached_chapter_index` owns decoded `delta_index_page` entries and backing `volume_page` buffers for one chapter.
- `cached_index_counters` and `sparse_cache_counters` are cache-line aligned to reduce false sharing.
- `search_list` stores an LRU permutation plus `first_dead_entry`, and is overallocated with temporary arrays used by purge.

Key operations:
- `make_sparse_cache()` allocates the cache, barriers, cached chapter arrays, and per-zone search lists.
- `sparse_cache_contains()` linearly searches the caller zone's live entries, scores zone-zero hits/misses, and rotates hits to MRU.
- `purge_search_list()` stable-partitions entries into active, skippable, and dead based on oldest chapter and `skip_search`.
- `update_sparse_cache()` uses begin/end barriers; zone zero purges, evicts/replaces the LRU/dead victim, reads and decodes the target chapter, then copies LRU state to all zones.
- `search_sparse_cache()` searches either one requested chapter or all eligible cached chapters and returns the first possible record page match.

Search performance uses a miss heuristic: zone-zero consecutive misses beyond `SKIP_SEARCH_THRESHOLD / zone_count` set `skip_search`, suppressing whole-cache searches while still allowing explicit hook lookups to clear the flag on hit.
