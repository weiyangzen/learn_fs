# sources/distributed-fs/ceph-client/mm/folio-compat.c

## Purpose
`folio-compat.c` provides out-of-line compatibility wrappers for older `struct page` APIs while the kernel transitions callers to folio-native interfaces. It keeps legacy exported symbols available without forcing large inline wrappers into every caller.

## Important APIs, types, and functions
The file exports page-based wrappers for common folio operations: `unlock_page()`, `end_page_writeback()`, `wait_on_page_writeback()`, `mark_page_accessed()`, `set_page_writeback()`, `set_page_dirty()`, `set_page_dirty_lock()`, `clear_page_dirty_for_io()`, `redirty_page_for_writepage()`, `add_to_page_cache_lru()`, and `pagecache_get_page()`. Each wrapper converts `struct page *` to the containing folio with `page_folio()` and delegates to the folio or filemap implementation.

## Control flow
Most functions are single-step adapters: convert page to folio, call the folio helper, and return its result if any. `add_to_page_cache_lru()` delegates to `filemap_add_folio()`. `pagecache_get_page()` calls `__filemap_get_folio()` with caller-provided `fgp_flags` and `gfp`; if lookup returns an error pointer it returns `NULL`, otherwise it returns the page within the folio corresponding to the requested index with `folio_file_page()`.

## State and persistence
This file owns no state. It mutates page-cache, dirty, writeback, and LRU state indirectly through the folio APIs it wraps. Symbol exports preserve ABI/API continuity for in-tree and module callers still using page names.

## Dependencies and integration points
The wrappers depend on `pagemap`, migration/rmap/swap headers, writeback control, and the generic filemap folio APIs. They integrate legacy page API users with the folio-first MM implementation, including filesystem writeback, migration, dirty accounting, and page-cache insertion/lookup.

## Risks and test signals
The main risk is semantic drift between legacy page functions and folio-native behavior, especially for large folios where a page pointer may refer to a subpage. `pagecache_get_page()` must return the correct subpage for an index inside a folio. Useful signals are successful builds of legacy callers, module symbol resolution, page-cache/dirty/writeback tests that still use page APIs, and large-folio tests ensuring wrappers preserve expected page-level results.
