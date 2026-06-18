# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/open-chapter.h

## Purpose
Declares the open-chapter data structures and operations used by zone workers and persistence code.

## Important APIs, Types, And Functions
Defines `OPEN_CHAPTER_RECORD_NUMBER_BITS`, `struct open_chapter_zone_slot`, and `struct open_chapter_zone`. The zone stores capacity, current size, deletion count, record array, slot count, and flexible hash slot array. The API exposes allocation, reset, search, put, remove, free, close-to-volume, save, load, and saved-size computation.

## Control Flow
Index zones use search/put/remove while processing requests. The chapter writer uses `uds_close_open_chapter()` when all zones have closed a chapter. Layout save/load uses the serialization helpers.

## State And Persistence
The header makes clear that record number 0 means unused and records are 1-based. Deleted records remain in memory until reset or save/load, where only live records are serialized.

## Dependencies And Integration Points
Includes chapter-index, geometry, index, and volume headers. This links request processing, chapter-index generation, and volume writes.

## Risks
Bitfield width limits record numbers to `OPEN_CHAPTER_RECORD_NUMBER_BITS`; geometry must not allow per-zone capacities beyond that. Direct users must not assume hash slots and record arrays have the same semantic index except for the intentional deleted flag overlay.

## Test Signals
Build and unit tests should exercise slot bitfield limits, per-zone capacity calculation, and close/save/load integration with volume geometry.
