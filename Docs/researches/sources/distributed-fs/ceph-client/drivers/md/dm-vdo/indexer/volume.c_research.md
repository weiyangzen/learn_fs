# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume.c

## Purpose
`volume.c` implements the UDS index volume: a persistent circular log of deduplication chapters stored through `dm-bufio`. It reads, writes, caches, invalidates, and rebuilds volume chapter pages. A chapter contains static delta-index pages followed by sorted record pages. The file is the bridge between in-memory indexing requests and on-disk chapter/index/record layout.

## Important APIs, Types, and Functions
The main exported API is `uds_make_volume()`, `uds_free_volume()`, `uds_replace_volume_storage()`, `uds_find_volume_chapter_boundaries()`, `uds_search_volume_page_cache()`, `uds_search_volume_page_cache_for_rebuild()`, `uds_search_cached_record_page()`, `uds_forget_chapter()`, `uds_write_chapter()`, `uds_prefetch_volume_chapter()`, `uds_read_chapter_index_from_volume()`, `uds_get_volume_record_page()`, and `uds_get_volume_index_page()`. Internals center on physical-page mapping helpers, the `page_cache` LRU, `queued_read` processing, `search_pending_counter` invalidation protection, record-page binary-tree searches, chapter-index validation, record page encoding, and chapter probing.

## Control Flow
Reads first map virtual chapter/page coordinates to physical page numbers. Zone threads perform a fast cache lookup under a per-zone pending-search counter; cache misses are enqueued to reader threads unless the caller is in a synchronous rebuild path. Reader threads reserve circular queue entries, read pages with `dm_bufio_read()`, initialize index pages when needed, install pages into the cache, perform the queued lookup immediately, then requeue waiting requests to `STAGE_INDEX`. Writes pack index pages from `open_chapter_index`, update the index page map, donate newly written index pages into the cache, encode sorted records into heap-ordered binary-search pages, mark buffers dirty, and finally flush dirty buffers. Rebuild probing validates chapter index pages, detects empty or partially written tails, then finds lowest/highest virtual chapter numbers across the circular volume.

## State and Persistence Behavior
Persistent state is the chapter log on the block device. Runtime state includes `dm_bufio_client`, `index_page_map`, optional sparse cache, radix sorter, record pointer workspace, and page cache arrays. Cache entries own `dm_buffer` references until eviction/free. Pending search counters and memory barriers protect readers from cache invalidation while not holding the read-thread mutex. `uds_forget_chapter()` invalidates all physical pages for a virtual chapter, including pending reads. `uds_replace_volume_storage()` drops all cached buffers and sparse-cache entries before reopening storage.

## Dependencies and Integration Points
This file depends on `dm-bufio`, UDS geometry/config/chapter-index/index-page-map/radix-sort/sparse-cache code, VDO logging, memory allocation, assertions, and thread/condition helpers. Requests are requeued through `uds_enqueue_request()`. Volume results feed the UDS index search path and rebuild path; writes are driven when open chapters close.

## Risks and Edge Cases
Concurrency is subtle: cache installation, invalidation, async read completion, and search-pending counters must keep memory barriers paired. Reader queue saturation blocks enqueuers on a condition variable. Corrupt chapter-index pages can poison rebuild boundary discovery. `MAX_BAD_CHAPTERS` limits tolerated contiguous bad chapters. Cache slot counts are capped by `VOLUME_CACHE_MAX_ENTRIES`; configuration errors can fail initialization. Index page map mismatches are treated as corrupt data except during rebuild lookup mode.

## Test Signals
Useful tests include cache hit/miss searches, queued duplicate page reads, invalidation during pending reads, volume writes followed by immediate searches, rebuild boundary scans with empty, full, wrapped, and partially written volumes, dm-bufio read/write errors, sparse index configurations, and shutdown with reader threads blocked on the queue.
