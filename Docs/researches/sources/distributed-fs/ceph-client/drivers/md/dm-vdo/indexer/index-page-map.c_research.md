# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-page-map.c

## Purpose
Implements the compact page map that records, for each chapter and index page except the final one, the highest delta-list number stored on that page. This lets volume lookups read only the relevant chapter-index page for a record name.

## Important APIs, Types, And Functions
Public functions are `uds_make_index_page_map()`, `uds_free_index_page_map()`, `uds_update_index_page_map()`, `uds_find_index_page_number()`, `uds_get_list_number_bounds()`, `uds_compute_index_page_map_save_size()`, `uds_write_index_page_map()`, and `uds_read_index_page_map()`. The serialized format begins with magic `ALBIPM02`, then `last_update`, then little-endian u16 entries.

## Control Flow
Allocation sizes the entries array as `chapters_per_volume * (index_pages_per_chapter - 1)`. During chapter write or rebuild, `uds_update_index_page_map()` records the last delta list for each non-final index page and updates `last_update` to the virtual chapter number. Lookup hashes a record name to a chapter delta list, scans that chapter's per-page bounds, and returns the first page whose high list is greater than or equal to the desired list.

## State And Persistence
State is an in-memory u16 array plus `last_update`. The last page of each chapter is omitted because its upper bound is always `delta_lists_per_chapter - 1`. Save/load are whole-map operations through buffered writer/reader objects and validate only the magic before decoding the rest.

## Dependencies And Integration Points
Uses geometry fields, hash helpers, numeric encoding, memory allocation, and buffered I/O. `index-layout.c` saves and restores it in an index save region; `index.c` rebuilds it from on-disk chapter index pages during recovery; `sparse-cache.c` and volume lookup code use it to select cached index pages.

## Risks
The implementation assumes u16 is sufficient for each highest delta-list value, so geometry must keep `delta_lists_per_chapter` within that bound. A stale or corrupt map can send lookups to the wrong index page and create false misses. Load validates the magic but not monotonicity of entries, so recovery/rebuild tests should catch malformed page boundaries.

## Test Signals
Test map allocation for dense and sparse geometries, update behavior for final and non-final pages, lookup boundaries around each page transition, save/load round trips, bad magic handling, and rebuild comparison against actual chapter-index page `lowest_list_number` and `highest_list_number`.
