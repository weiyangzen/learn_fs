# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/open-chapter.c

## Purpose
Implements per-zone in-memory open chapters, which hold the newest records before they are committed to the volume. It supports lookup, insert/update, delete marking, close-to-volume collation, and save/load of live open-chapter records.

## Important APIs, Types, And Functions
Public functions are `uds_make_open_chapter()`, `uds_reset_open_chapter()`, `uds_search_open_chapter()`, `uds_put_open_chapter()`, `uds_remove_from_open_chapter()`, `uds_free_open_chapter()`, `uds_close_open_chapter()`, `uds_save_open_chapter()`, `uds_load_open_chapter()`, and `uds_compute_saved_open_chapter_size()`. Private helpers include `probe_chapter_slots()`, `fill_delta_chapter_index()`, and `load_version20()`. The saved format uses magic `ALBOC` and version `02.00`.

## Control Flow
Allocation divides `records_per_chapter` by zone count for per-zone capacity and creates a power-of-two hash table at twice that capacity. Searches and puts use quadratic probing from a name-derived hash slot. Insert updates an existing record or appends a new 1-based record number. Delete marks a slot indexed by record number rather than removing hash-chain entries.

Closing empties an open-chapter index for the virtual chapter, interleaves records from zones to preserve temporal locality, replaces deleted or unused slots with a valid fill record so record pages are full, populates the chapter delta index, and writes the chapter to the volume. Save writes non-deleted records interleaved across zones. Load verifies magic/version, reads records, assigns each to the current zone mapping, and discards overflow records if a new zone distribution is too small.

## State And Persistence
Runtime state includes `size`, `deletions`, 1-based record array, and hash slots with record number and deleted flag. Saved state contains only live records, not deleted tombstones or hash slots; load rebuilds the open chapter from records. The code deliberately prevents loaded zones from filling completely so rollover remains possible.

## Dependencies And Integration Points
Depends on geometry, hash utilities, chapter-index construction, volume writes, buffered I/O, numeric helpers, allocation, and logging. It is used by `index.c` zone processing and `index-layout.c` save/load.

## Risks
`fill_delta_chapter_index()` assumes at least one filled zone can provide a non-deleted fill record when replacing holes; chapter close should only be triggered by a filled zone. Deleted flag storage overlays the slot array and uses record-number indexing, so capacity/slot-count relationships are critical. Save/load with changed zone counts can drop newest records for overloaded zones, reducing dedupe history after reconfiguration.

## Test Signals
Test probing collision chains, update-in-place, delete and reinsert behavior, capacity rollover, close with deleted records, delta-index overflow warnings, save/load with same and different zone counts, invalid magic/version, and full-page volume writes.
