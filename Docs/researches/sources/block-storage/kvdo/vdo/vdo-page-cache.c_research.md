# File Research: sources/block-storage/kvdo/vdo/vdo-page-cache.c

## Purpose
Implements VDO's asynchronous metadata page cache, primarily for block map pages. It manages page allocation, lookup, LRU replacement, dirty-period tracking, reads, writes, flush-before-write ordering, wait queues, statistics, and drain/invalidation behavior.

## Main Concepts
- Each cache slot is represented by `struct page_info`, with a PBN, buffer, state, busy count, waiter queue, LRU entry, and metadata `vio`.
- Page state moves through `PS_FREE`, `PS_INCOMING`, `PS_FAILED`, `PS_RESIDENT`, `PS_DIRTY`, and `PS_OUTGOING`.
- `cache->page_map` maps physical block numbers to resident/in-flight page slots.
- `busy` pins a page while page completions hold references.
- Dirty pages are tracked by `dirty_lists` and written when their period expires or during drain.
- Writes are batched behind an explicit flush so journal entries that dirtied pages are stable before metadata pages are written.

## Key Functions
- `vdo_make_page_cache()` allocates page metadata, buffers, page map, per-slot metadata VIOs, dirty lists, and queues.
- `vdo_free_page_cache()` releases all per-page VIOs, dirty lists, maps, buffers, and cache storage.
- `vdo_init_page_completion()` initializes an async request for a specific page.
- `vdo_get_page()` resolves a page request from cache, waits on in-flight pages, launches a load, or queues behind replacement.
- `vdo_release_page_completion()` drops a busy reference and may trigger deferred write/replacement work.
- `vdo_mark_completed_page_dirty()` marks a writable completed page dirty and places it in dirty-period lists.
- `vdo_request_page_write()` forces a dirty page to be saved as soon as possible.
- `vdo_dereference_readable_page()` and `vdo_dereference_writable_page()` expose page memory after validating completion state.
- `vdo_drain_page_cache()` flushes dirty pages during block map drain unless suspending.
- `vdo_invalidate_page_cache()` asserts no dirty pages and rebuilds the PBN map.
- `vdo_get_page_cache_statistics()` returns cross-thread-safe snapshots using `READ_ONCE`.

## I/O Flow
- Reads use `launch_page_load()`, transition a slot to `PS_INCOMING`, submit metadata read I/O, optionally run `read_hook`, then distribute the loaded page to waiters.
- Rebuild-mode read errors are treated as zero-filled uninitialized pages.
- Dirty writes use `schedule_page_save()`, `save_pages()`, a flush VIO, then `write_pages()` to submit page writes.
- `write_hook` can request a rewrite after a page write completes.
- Persistent write/flush/load failures enter read-only mode and complete queued waiters with the error.

## Replacement And Waiters
- Free pages are used first.
- If no free page exists, `discard_a_page()` selects an unbusy, non-in-flight LRU page.
- Clean pages can be immediately reset and reused.
- Dirty pages are written first, with `WRITE_STATUS_DISCARD` indicating replacement-driven writeback.
- If all pages are busy or in flight, requests wait on `free_waiters` and cache pressure stats are incremented.

## Important Invariants
- Most mutations must run on the owning logical zone thread.
- A page must have no waiters and `busy == 0` before reset.
- `set_info_pbn()` requires either the old or new PBN to be `NO_PAGE`.
- Writable requests fail immediately when the zone is read-only.
- Outgoing pages are readable but not writable.
- `outstanding_reads` and `outstanding_writes` are decremented only immediately before drain-complete checks to avoid use-after-free during callbacks.
