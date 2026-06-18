# File Research: sources/block-storage/kvdo/vdo/vdo-page-cache.h

## Purpose
Defines the VDO page cache data structures, page state model, page completion API, and statistics/drain interfaces.

## Key Types
- `vdo_page_read_function`: optional callback after a page is read.
- `vdo_page_write_function`: optional callback after a page is written; can request rewrite.
- `struct vdo_page_cache`: owns page slots, raw buffers, LRU/free/outgoing lists, dirty lists, waiters, stats, and owning block map zone.
- `enum vdo_page_buffer_state`: page slot lifecycle state.
- `enum vdo_page_write_status`: normal, discard-driven, or deferred write status.
- `struct page_info`: per-page slot metadata and per-page client context.
- `struct vdo_page_completion`: async page request and live page reference.

## Public API
- Construction/destruction: `vdo_make_page_cache()`, `vdo_free_page_cache()`.
- Period/rebuild state: `vdo_set_page_cache_initial_period()`, `vdo_set_page_cache_rebuild_mode()`, `vdo_advance_page_cache_period()`.
- Async page access: `vdo_init_page_completion()`, `vdo_get_page()`, `vdo_release_page_completion()`.
- Dirty/write control: `vdo_mark_completed_page_dirty()`, `vdo_request_page_write()`.
- Dereference/context access: `vdo_dereference_readable_page()`, `vdo_dereference_writable_page()`, `vdo_get_page_completion_context()`.
- Lifecycle/statistics: `vdo_is_page_cache_active()`, `vdo_drain_page_cache()`, `vdo_invalidate_page_cache()`, `vdo_get_page_cache_statistics()`.

## Important Invariant
A completed `vdo_page_completion` pins the page slot until `vdo_release_page_completion()` is called.
