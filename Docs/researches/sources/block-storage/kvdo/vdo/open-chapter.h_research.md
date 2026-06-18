# File Research: sources/block-storage/kvdo/vdo/open-chapter.h

## Purpose
Declares the open-chapter structures and operations for UDS index staging.

## Key Definitions
- `OPEN_CHAPTER_RECORD_NUMBER_BITS = 23`.
- `OPEN_CHAPTER_MAX_RECORD_NUMBER`.
- `struct open_chapter_zone_slot`: packed bitfield containing record number and deleted flag.
- `struct open_chapter_zone`: per-zone capacity, size, deleted count, records array, slot count, and flexible slot table.

## API Surface
Construction, reset, lookup, insertion, deletion, free, close, save/load, and saved-size computation are declared.

## Integration Notes
Includes chapter index, geometry, index, and volume headers. The record array is 1-based by contract, matching the implementation’s use of zero as “empty slot.”
