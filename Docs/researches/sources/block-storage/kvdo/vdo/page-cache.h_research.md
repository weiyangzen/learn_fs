# File Research: sources/block-storage/kvdo/vdo/page-cache.h

## Purpose
Declares page cache data structures, queue helpers, cache operations, and pending-search counter helpers for UDS volume pages.

## Key Structures
- `struct request_list`: first/last request chain.
- `struct cached_page`: pending flag, physical page id, last-used clock, volume page data, and delta index page.
- `struct queued_read`: invalid/reserved flags, physical page, and waiting requests.
- `struct search_pending_counter`: cache-line-aligned atomic64 counter.
- `struct page_cache`: geometry, zone count, index/cache sizing, index array, cache array, counters, read queue, queue cursors, and clock.

## Constants
- `VOLUME_CACHE_MAX_ENTRIES = UINT16_MAX >> 1`
- `VOLUME_CACHE_QUEUED_FLAG = 1 << 15`
- `VOLUME_CACHE_MAX_QUEUED_READS = 4096`

## Inline Counter Semantics
`invalidate_counter_t` stores physical page in low 32 bits and a sequence counter in high bits. Odd/even counter state indicates search pending. `begin_pending_search` and `end_pending_search` update counters with memory barriers.

## API Surface
Declares cache allocation/free, invalidation, lookup, queue operations, victim selection, completion/cancel of reads, and cache size query.

## Integration Notes
The header exposes some functions explicitly for unit tests, especially `assert_page_in_cache`.
