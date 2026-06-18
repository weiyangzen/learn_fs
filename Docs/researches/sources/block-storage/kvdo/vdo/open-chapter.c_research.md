# File Research: sources/block-storage/kvdo/vdo/open-chapter.c

## Purpose
Implements the in-memory “open chapter” of the UDS index, where newest chunk records are staged before being closed into indexed chapter pages.

## Core Model
Each index zone has an `open_chapter_zone`:
- Records are stored 1-based in insertion order.
- A hash table maps chunk names to record numbers.
- Record number 0 means empty slot.
- Deleted records are marked with a flag, not physically removed.
- Hash slots are sized as a power of two above capacity times load ratio.

## Key Operations
- `make_open_chapter`: validates geometry, sizes hash slots, allocates zone and cache-aligned records.
- `reset_open_chapter`: clears records and slots.
- `probe_chapter_slots`: name lookup with quadratic probing.
- `search_open_chapter`: returns metadata if a live record exists.
- `put_open_chapter`: updates existing metadata or appends a new record.
- `remove_from_open_chapter`: marks matching record deleted.
- `close_open_chapter`: builds a delta chapter index and writes chapter contents.
- `save_open_chapters` / `load_open_chapters`: versioned persistence of open-chapter records.
- `compute_saved_open_chapter_size`: computes saved representation size.

## Close / Save Behavior
When closing, records from zones are interleaved to preserve temporal locality. Deleted or unused records are replaced with a valid fill record so record pages contain valid records. Live records are inserted into the open chapter index by page number.

## Persistence
Saved data starts with magic `ALBOC`, version `02.00`, a little-endian record count, then live `uds_chunk_record` entries. Load redistributes records by current zone mapping and can discard overflow in zones that become too full.

## Integration Notes
Depends on geometry, volume writing, open chapter index, volume index zone selection, buffered readers/writers, and numeric unaligned helpers.
