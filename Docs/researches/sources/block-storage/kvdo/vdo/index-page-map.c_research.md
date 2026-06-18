# File Research: sources/block-storage/kvdo/vdo/index-page-map.c

Persistent map from chapter/index-page number to highest delta-list number stored on each index page.

Key responsibilities:
- Allocates and frees `struct index_page_map`.
- Maintains a compact two-dimensional array: chapter number by index page, omitting the last page in each chapter because its upper bound is implied by geometry.
- Updates map entries as chapter index pages are built or rebuilt.
- Finds the index page for a chunk name by hashing to a chapter delta list and scanning the chapter's page bounds.
- Provides lower/upper delta-list bounds for a chapter index page.
- Serializes/deserializes the page map with magic `ALBIPM02`, `last_update`, and little-endian `uint16_t` entries.

Important behavior:
- `entries_per_chapter` is `index_pages_per_chapter - 1`.
- `last_update` records the virtual chapter number of the last map update.
- `find_index_page_number()` returns the first page whose recorded high list is >= the hashed list, or the implicit final page.
- `compute_index_page_map_save_size()` returns exact serialized size for save-region sizing.
- Read validates magic before consuming `last_update` and entries.

Dependencies:
- Uses `geometry`, `hash-utils`, buffer serialization, buffered reader/writer, memory allocation, logging, and UDS error codes.

Notable risks:
- Assumes `index_pages_per_chapter >= 1`; if it were 0, `entries_per_chapter` underflows.
- Lookups scan per chapter linearly over index pages; acceptable if page count is small.
- Integrity checking is limited to magic and buffer read success; entry monotonicity is validated elsewhere during rebuild.
