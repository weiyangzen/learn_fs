# File Research: sources/block-storage/kvdo/vdo/page-cache.c

## Purpose
Implements UDS volume page cache management, queued reads, LRU victim selection, and safe invalidation around concurrent zone searches.

## Core Structures Used
Uses `page_cache` from the header:
- `index` maps physical pages to cache entries or queued-read entries.
- `cache` stores `cached_page` records.
- `read_queue` stores coalesced pending reads.
- `search_pending_counters` protect zone-thread searches from concurrent invalidation.

## Key Operations
- `make_page_cache` / `free_page_cache`: allocate and destroy cache, index, read queue, counters, and page buffers.
- `invalidate_page_cache`: clears all index entries and releases page data.
- `invalidate_page_cache_for_chapter`: invalidates all pages in a chapter.
- `get_page_from_cache`: returns a cached page if present.
- `enqueue_read`: queues/coalesces a physical page read and links requests.
- `reserve_read_queue_entry` / `release_read_queue_entry`: read-thread queue reservation lifecycle.
- `select_victim_in_cache`: chooses least-recent non-pending page and marks it pending.
- `put_page_in_cache`: installs completed read into cache.
- `cancel_page_in_cache`: cancels pending read and invalidates mapping.
- `get_page_cache_size`: reports delta-index page footprint.

## Concurrency
Zone threads use pending-search counters around page searches. Read threads holding the read mutex invalidate mappings only after `wait_for_pending_searches` observes active searches finish. Memory barriers pair:
- `begin_pending_search` with `wait_for_pending_searches`
- `put_page_in_cache` with `get_page_and_index`
- `end_pending_search` with readers observing counter updates

## Queue Model
The high bit of `index[physical_page]` marks queued reads. The remaining bits store either a cache index or read-queue index. `read_queue_first`, `read_queue_last_read`, and `read_queue_last` let multiple read threads reserve entries while preserving queue reuse ordering.

## Integration Notes
Works with geometry, volume pages, delta index pages, record pages, UDS threads, and buffered request structures.
