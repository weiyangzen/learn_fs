# File Research: sources/block-storage/kvdo/vdo/volume.h

## Purpose
Declares the `struct volume` state and public operations for persisted chapter IO, page-cache search, chapter writing, cache management, boundary discovery, and physical page mapping.

## Public Types
- `enum reader_state`: bit flags for reader thread state:
  - `READER_STATE_RUN`
  - `READER_STATE_EXIT`
  - `READER_STATE_STOP`
- `enum index_lookup_mode`:
  - `LOOKUP_NORMAL`
  - `LOOKUP_FOR_REBUILD`
- `struct volume`: owns geometry, volume store, scratch page, nonce, sorting helpers, sparse/page caches, index-page map, reader-thread synchronization, reader-thread array/state, lookup mode, read-thread count, and reserved buffer count.

## Public API Groups
Lifecycle:
- `make_volume()`
- `free_volume()`
- `replace_volume_storage()`

Read/search:
- `enqueue_page_read()`
- `search_volume_page_cache()`
- `search_cached_record_page()`
- `get_volume_page_locked()`
- `get_volume_page_protected()`
- `get_volume_page()`
- `read_chapter_index_from_volume()`

Write/invalidate:
- `forget_chapter()`
- `write_index_pages()`
- `write_record_pages()`
- `write_chapter()`

Discovery/utilities:
- `find_volume_chapter_boundaries()`
- `find_volume_chapter_boundaries_impl()`
- `get_cache_size()`
- `map_to_physical_page()`

## Dependencies
Includes core configuration and index/cache/storage headers:
`common.h`, `config.h`, `chapter-index.h`, `index-layout.h`, `index-page-map.h`, `page-cache.h`, `radix-sort.h`, `sparse-cache.h`, `uds.h`, `uds-threads.h`, and `volume-store.h`.

## Notes
The header exposes some functions primarily for tests or rebuild/single-threaded code, especially direct page-fetch helpers and `find_volume_chapter_boundaries_impl()`.

The comments document important concurrency contracts: callers of protected page access must manage pending-search state as expected, while locked page access requires `read_threads_mutex`.
