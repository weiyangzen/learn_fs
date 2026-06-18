# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/chapter-index.c

## Purpose
`chapter-index.c` manages UDS chapter indexes. An open chapter index is mutable and tracks record names as they are added to the currently written chapter; closed chapter index pages are immutable delta-index pages used for lookup and rebuild validation.

## Important APIs, Types, And Functions
- `uds_make_open_chapter_index()` allocates an `open_chapter_index` and initializes a single-zone mutable `delta_index`.
- `uds_free_open_chapter_index()` tears down the delta index and wrapper.
- `uds_empty_open_chapter_index()` resets the mutable index for a new virtual chapter number.
- `uds_put_open_chapter_index_record()` inserts a record name mapped to a record page number.
- `uds_pack_open_chapter_index_page()` packs a range of delta lists into one immutable chapter-index page, removing entries if a page would overflow.
- `uds_initialize_chapter_index_page()` wraps a page buffer as an immutable `delta_index_page`.
- `uds_validate_chapter_index_page()` walks all entries in a loaded page and verifies page-number payloads.
- `uds_search_chapter_index_page()` maps a record name to a possible record page or `NO_CHAPTER_INDEX_ENTRY`.

## Control Flow And Data Flow
Insertion hashes the record name with `hash-utils.h` into a chapter delta list and address. It searches the mutable delta index for the address and detects full-name collision entries. If the same full name already appears as a collision, it returns a bad-state signal. Otherwise it stores the record page payload, passing the full name only when a collision entry is needed.

Packing repeatedly calls `uds_pack_delta_index_page()`. If the first not-yet-packed list cannot fit, or the caller is packing the last page and remaining lists do not fit, the code logs stats and removes whole non-empty delta lists until the page fits. This sacrifices some chapter-index precision to keep the persistent page bounded; later record-page verification still prevents false metadata reads from becoming matches.

Search initializes an immutable page delta index, computes the sub-list number from the page's `lowest_list_number`, searches by address and full name, and returns the payload if found.

## State And Persistence Behavior
Open chapter state is memory-resident until packed. Packed pages persist nonce, virtual chapter number, list range, and delta-list bitstreams through the delta-index page format. Page validation treats corrupt random data and implausible record page payloads as `UDS_CORRUPT_DATA`, but avoids logging expected unwritten-volume cases as hard errors.

## Dependencies And Integration Points
This module depends on `delta-index`, `geometry`, `hash-utils`, `indexer`, errors, logging, memory allocation, and assertions. It is used by `open-chapter.c`, `volume.c`, sparse cache paths, and index writer/rebuild code.

## Risks
- Overflow handling removes entries, reducing lookup selectivity and potentially increasing record-page scans or misses.
- Correctness depends on hash partitioning matching `index_geometry` values used when the chapter was written.
- Duplicate-name detection differs between normal and rebuild-style collision replay paths.
- Immutable page validation must keep payload bounds aligned with `record_pages_per_chapter`.

## Test Signals
Tests should insert dense collision-heavy records, pack across multiple pages, force last-page overflow, validate corrupt page buffers, search absent/present/collision names, and ensure page payloads equal or exceed `record_pages_per_chapter` are rejected.
