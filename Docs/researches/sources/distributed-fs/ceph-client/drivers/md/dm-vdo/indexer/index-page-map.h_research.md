# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-page-map.h

## Purpose
Declares the page-map structure and API used to map record-name delta lists to physical chapter-index pages.

## Important APIs, Types, And Functions
`struct index_page_map` contains a geometry pointer, `last_update`, `entries_per_chapter`, and the u16 `entries` array. The header exposes allocation/free, read/write, update, lookup, list-bound calculation, and saved-size computation functions.

## Control Flow
Writers call `uds_update_index_page_map()` as chapter index pages are produced or replayed. Readers call `uds_find_index_page_number()` to decide which index page to fetch, and `uds_get_list_number_bounds()` to interpret the list span represented by a page.

## State And Persistence
The header describes an in-memory object backed by a serialized save-region payload. The `last_update` field is used by rebuild and logging paths to detect whether replay changed the map.

## Dependencies And Integration Points
Includes `geometry.h` and `io-factory.h`, tying it to fixed index geometry and buffered save/load streams. It is shared by volume lookup, sparse-cache search, index rebuild, and layout save/restore code.

## Risks
Callers must pass chapter numbers in physical chapter space for lookups and updates where required. Confusing virtual and physical chapter numbers can index the wrong entries. The map depends on geometry immutability across save/load.

## Test Signals
Compile tests should catch API changes; functional tests should validate physical chapter indexing, final-page bounds, and persistence through `index-layout` saves.
