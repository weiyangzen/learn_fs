# File Research: sources/block-storage/kvdo/vdo/volume.c

## Purpose
Implements persisted chapter storage for the UDS/VDO volume. It manages:
- physical page mapping,
- asynchronous and synchronous page reads,
- page-cache coordination,
- reader threads,
- index-page and record-page search,
- chapter writes,
- volume boundary discovery after restart,
- volume construction, replacement, and cleanup.

## Page Mapping
Physical page zero is reserved for the header. Chapter pages begin at physical page one:
- `map_to_physical_page(geometry, chapter, page)` returns `1 + pages_per_chapter * chapter + page`.
- `map_to_page_number()` and `map_to_chapter_number()` reverse physical pages to chapter-local coordinates.
- `is_record_page()` identifies record pages as pages after the chapter’s index pages.

## Reader Thread Model
`enqueue_page_read()` records a queued page read in the page cache, waits if read queues are full, and signals reader threads. It rejects new reads during shutdown.

`read_thread_function()` loops under `read_threads_mutex`:
1. reserves a queued read entry,
2. selects a cache victim,
3. reads the volume page outside the mutex,
4. initializes index pages when needed,
5. inserts the page into cache unless invalidated,
6. searches the newly read page for queued requests,
7. requeues requests to `STAGE_INDEX`,
8. releases the read-queue entry and broadcasts completion.

Invalidation and pending-search counters are used to avoid races with page-cache invalidation while requests are searching cached pages.

## Page Retrieval
- `get_volume_page_locked()`: caller holds read mutex; returns cached page or synchronously reads it.
- `get_volume_page_protected()`: request path that may queue asynchronous read. It carefully toggles pending-search state and read mutex ownership to prevent cache invalidation races.
- `get_volume_page()`: synchronous convenience wrapper used by rebuild/explorer/tests and other single-threaded paths.

`read_page_locked()` performs either synchronous reads when there is no request/session, or enqueues asynchronous reads for live request processing.

## Search Flow
`search_cached_index_page()`:
- maps chapter/index page to physical page,
- begins pending-search protection,
- fetches page through `get_volume_page_protected()`,
- searches the initialized chapter index page for a record-page number,
- ends pending-search protection.

`search_cached_record_page()`:
- validates the record-page number,
- fetches the record page under pending-search protection,
- searches the record page for the chunk name,
- returns duplicate metadata if found.

`search_volume_page_cache()` combines index-page lookup and record-page search. If a request resumes from an earlier asynchronous index-page read, it uses the saved record-page number in `request->old_metadata`.

## Writing Chapters
`write_index_pages()` writes all index pages for a chapter:
- prepares scratch bufio page,
- packs open-chapter delta lists,
- writes/marks the page dirty,
- optionally copies page bytes for tests,
- updates the index-page map,
- donates the freshly written index page into the page cache.

`write_record_pages()` writes sorted/encoded record pages from the open chapter’s 1-based record array.

`write_chapter()` maps the virtual chapter to its physical chapter slot, writes index pages, writes record pages, releases the scratch page, and syncs the volume store.

## Cache and Invalidation
`forget_chapter()` invalidates cached pages for a physical chapter under the read mutex.

`donate_index_page_locked()` swaps scratch page data into a cache victim, initializes its chapter-index representation, and inserts it into the page cache. This keeps recently written index pages available without rereading them.

`get_cache_size()` combines page-cache memory and sparse-cache memory when geometry is sparse.

## Volume Boundary Discovery
`probe_chapter()` reads all index pages for a physical chapter and validates:
- consistent virtual chapter number across index pages,
- expected delta-list range progression,
- chapter-index page structure,
- virtual chapter maps back to the physical chapter.

`find_real_end_of_volume()` works backward from the configured volume end, skipping corrupt trailing chapters to find the actual last usable physical chapter.

`find_volume_chapter_boundaries()` uses that real end and delegates to `find_volume_chapter_boundaries_impl()`.

`find_volume_chapter_boundaries_impl()` performs a binary-search-like scan over circular chapter order to find lowest/highest virtual chapter numbers, tolerating a bounded run of bad chapters and accounting for remapped physical chapters.

## Construction and Lifecycle
`allocate_volume()` allocates the volume, copies geometry, computes reserved bufio buffers, opens the volume store, initializes scratch page, radix sorter, record pointer array, sparse cache if needed, page cache, and index-page map.

`make_volume()` initializes mutex/condition variables, allocates reader-thread handles, starts configured reader threads, and returns the constructed volume.

`replace_volume_storage()` swaps the underlying index-layout storage, releases scratch/page-cache/sparse-cache state, closes the old store, and opens a new store.

`free_volume()` stops reader threads, destroys scratch/cache/store/sync primitives, frees map/sorter/geometry/record pointers, and frees the volume.

## Dependencies
Uses chapter/index/page-cache/storage helpers from `chapter-index.h`, `config.h`, `geometry.h`, `hash-utils.h`, `index.h`, `record-page.h`, `sparse-cache.h`, `uds-threads.h`, `volume-store.h`, and logging/assertion/memory utilities.

## Invariants and Risks
- Read mutex and pending-search counters must be ordered carefully; many comments document race-prevention requirements.
- Reader threads must be stopped before caches and volume store are destroyed.
- Index-page validation is skipped differently in rebuild lookup mode.
- Boundary discovery assumes at most one contiguous bad-chapter run, capped by `MAX_BAD_CHAPTERS`.
- `read_chapter_index_from_volume()` initializes a local `volume_page` but reads into the caller-provided `volume_pages[]`; cleanup of those pages is caller-sensitive.
