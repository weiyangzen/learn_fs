# File Research: sources/block-storage/kvdo/vdo/volume-index005.c

## Purpose
Implements volume index format/version 005: a dense-only volume index backed by `struct delta_index`. It maps chunk-name-derived hash fields to delta-list entries whose payload is a compact chapter number. It handles lazy LRU invalidation of expired chapters, collision entries, save/restore, sizing, and statistics.

## Core Data Structures
- `struct volume_index_zone`: per-zone indexed virtual chapter low/high bounds and early-flush counter.
- `struct volume_index5`: concrete implementation embedding `struct volume_index common`, `struct delta_index`, flush state, zones, nonce, bit masks, chapter/list counts, and sizing controls.
- `struct chapter_range`: compact range of index-chapter values to flush.
- `struct vi005_data`: persisted header with magic `MI5-0005`, volume nonce, virtual chapter range, and saved delta-list span.
- `struct parameters005`: computed construction/sizing parameters such as address bits, chapter bits, mean delta, delta-list count, estimated memory size, and target free space.

## Major Behavior
The file distinguishes three chapter number forms:
- Virtual chapter: 64-bit external chapter number.
- Index chapter: low-order bits stored in the delta index.
- Rolling chapter: index chapter adjusted relative to a zone’s current low virtual chapter.

`extract_address()` and `extract_dlist_num()` split hash-derived volume-index bytes into an address key and a delta-list number. Delta lists are distributed over zones by the delta-index layer.

`get_volume_index_record_005()` is the central lookup routine. It derives address/list/zone, lazily flushes invalid entries if a list’s `flush_chapters[]` lags behind the zone low chapter, then returns a `volume_index_record` describing either an existing entry or an insertion point.

## Lazy Flushing
`flush_invalid_entries()` advances a delta-index iterator and removes entries whose stored chapter falls inside an expired range. `get_volume_index_entry()` uses it while preserving the lookup insertion offset and while scanning collision records. After processing, it narrows the next flush range so future lookups avoid repeating work.

`set_volume_index_zone_open_chapter_005()` updates a zone’s indexed range when the open chapter moves. It handles:
- backward moves that empty or trim newest entries,
- forward moves preserving all or part of the old range,
- large jumps that reset the range,
- early expiration when zone bit usage exceeds `max_zone_bits`.

`remove_newest_chapters()` renumbers or explicitly flushes entries when a zone moves backward into overlapping state.

## Record Mutation
- `put_volume_index_record()` validates the record magic and chapter range, optionally locks `record->mutex`, inserts into the delta index, updates found/collision state, and logs `UDS_OVERFLOW`.
- `remove_volume_index_record()` validates an existing record, invalidates its magic, optionally locks, then removes the delta entry.
- `set_volume_index_record_chapter()` validates and updates the stored chapter payload after range checking.

These exported functions serve the common API declared in `volume-index-ops.h`.

## Persistence
`start_saving_volume_index_005()` writes:
1. `vi005_data` header,
2. `flush_chapters` array for the zone’s delta-list range,
3. delta-index contents via `start_saving_delta_index()`.

`finish_saving_volume_index_005()` delegates to `finish_saving_delta_index()`.

`start_restoring_volume_index_005()` reads one header and flush-range array per reader/zone stream, validates magic and nonce consistency, reconciles virtual chapter bounds, initializes all zone ranges, then starts delta-index restore.

`abort_restoring_volume_index_005()` and `finish_restoring_volume_index_005()` delegate to the delta-index restore lifecycle.

## Sizing and Construction
`compute_volume_index_parameters005()` computes dense-index parameters from geometry and configuration. Important constraints:
- Sparse geometry is rejected.
- `records_per_chapter` and `chapters_per_volume` must be nonzero.
- delta-list count is at least `MAX_ZONES * MAX_ZONES` unless tests override `min_volume_index_delta_lists`.
- reduced geometry rounds chapters up to preserve hash-to-delta-list mapping.

The memory estimate accounts for live chapters plus estimated invalid chapters retained by lazy LRU. `compute_volume_index_save_bytes005()` adds header, flush ranges, and delta-index save bytes.

`make_volume_index005()` allocates and initializes the concrete object, vtable, delta index, flush-chapter array, and zones.

## Statistics
`get_volume_index_stats_005()` reports all data as dense stats and zeroes sparse stats. It includes delta-index stats plus memory for `volume_index5`, `flush_chapters`, and zones.

## Dependencies
Uses `buffer.h`, `config.h`, `errors.h`, `geometry.h`, `hash-utils.h`, `logger.h`, `memory-alloc.h`, `uds.h`, `delta-index.h` through the public ops header.

## Invariants and Risks
- `volume_index_record_magic` guards legal record operations.
- Stored chapter payload is limited by `chapter_mask`; virtual chapters are reconstructed relative to zone low.
- Lazy flushing means lookup can mutate the index.
- `min_volume_index_delta_lists` is intentionally externally mutable for tests.
- Save/restore depends on matching nonce and consistent per-zone headers.
