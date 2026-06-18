# File Research: sources/block-storage/kvdo/vdo/chapter-index.c

## Purpose

Implements the open and packed chapter index used by UDS/VDO deduplication metadata to map chunk names to record pages within a chapter.

## Main Responsibilities

- Allocates an open chapter index backed by a delta index.
- Clears an open chapter index for a new virtual chapter.
- Adds chunk-name to record-page mappings.
- Packs delta lists into chapter index pages.
- Handles overflow by removing entries/lists when needed.
- Initializes packed chapter index pages.
- Validates packed chapter index pages during rebuild.
- Searches a packed chapter index page for a chunk name.

## Important Functions

- `make_open_chapter_index()` allocates `struct open_chapter_index` and initializes its delta index.
- `free_open_chapter_index()` uninitializes and frees it.
- `empty_open_chapter_index()` resets delta index contents for a new chapter.
- `put_open_chapter_index_record()` hashes a chunk name to delta address/list and inserts a record page number.
- `pack_open_chapter_index_page()` packs a range of delta lists into one page.
- `initialize_chapter_index_page()` initializes a packed delta index page.
- `validate_chapter_index_page()` walks all entries and verifies record page values are plausible.
- `search_chapter_index_page()` looks up a chunk name and returns a record page or `NO_CHAPTER_INDEX_ENTRY`.

## Behavior Details

The open chapter index gives the delta index one extra page because delta lists may rebalance under memory pressure.

`pack_open_chapter_index_page()` may remove entries if a delta list cannot fit, or if the final page must contain all remaining lists. It logs warnings when removals are needed to avoid page overflow.

`put_open_chapter_index_record()` asserts that duplicate collisions for the same chunk do not occur within a chapter.

## Dependencies and Interactions

- Uses `delta-index`, `geometry`, hash helpers, and UDS chunk names.
- Used by deduplication index chapter construction and rebuild/search paths.

## Notable Edge Cases

- Validation returns `UDS_CORRUPT_DATA` without logging an error when a record page field is implausible, because this can happen during rebuild before the whole volume has been written.
- Search converts the chapter-level delta list number to a sub-list number relative to the packed page’s lowest list number.
