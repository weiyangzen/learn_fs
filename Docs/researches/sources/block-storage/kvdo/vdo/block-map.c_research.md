# File Research: sources/block-storage/kvdo/vdo/block-map.c

## Purpose

Implements the top-level VDO block map: zone setup, page-cache integration, logical-zone mapping, block map entry read/write, drain/resume, era advancement, and growth coordination.

## Main Responsibilities

- Allocates and initializes a multi-zone block map from persisted state.
- Creates per-zone page caches for leaf block map pages.
- Creates an action manager for zone-wide block map operations.
- Maintains block map eras tied to recovery journal sequence numbers.
- Validates and formats leaf pages on read.
- Handles leaf page write completion and recovery journal lock release.
- Computes logical zones for data VIOs.
- Finds leaf block map slots for data VIOs.
- Reads mapped block locations.
- Writes updated mappings and transfers recovery journal locks.
- Drains and resumes block map zones.
- Prepares and applies logical growth through forest replacement.
- Aggregates block map page cache statistics.

## Key Structures

`struct block_map_page_context` tracks the earliest recovery journal sequence number that dirtied a cached leaf page. This lock is acquired/released as entries change and when pages are written.

## Important Functions

- `vdo_decode_block_map()` builds a runtime block map from `block_map_state_2_0`.
- `vdo_free_block_map()` frees zones, forests, action manager, and map memory.
- `vdo_record_block_map()` converts runtime state back to persisted component state.
- `vdo_initialize_block_map_from_journal()` seeds era periods from recovery journal state.
- `vdo_compute_logical_zone()` maps an LBN to root index and logical zone.
- `vdo_find_block_map_slot()` prepares tree lock slot state and starts tree lookup.
- `vdo_advance_block_map_era()` records pending era and schedules default action.
- `vdo_drain_block_map()` schedules a draining operation across all zones.
- `vdo_resume_block_map()` schedules resume across zones.
- `vdo_prepare_to_grow_block_map()` allocates a future larger forest.
- `vdo_grow_block_map()` replaces the forest under suspended operation.
- `vdo_update_block_map_page()` updates a mapping entry and adjusts recovery journal locks.
- `vdo_get_mapped_block()` reads the current mapping.
- `vdo_put_mapped_block()` writes a new mapping.
- `vdo_get_block_map_statistics()` aggregates page-cache stats.

## Behavior Details

Block map eras classify dirty pages by journal sequence age. The current era is not proactively written except under cache pressure; older eras are progressively or immediately written. Era advancement is scheduled as a default action on the block map action manager and applied across page caches and tree zones.

Leaf page reads use `validate_page_on_read()`. Bad pages return `VDO_BAD_PAGE`; invalid pages are reformatted as empty pages.

`set_mapped_location()` validates unpacked entries. Bad mappings fail reads because returning zeros would hide known corruption, but writes treat bad old mappings as unmapped so the write can proceed.

`vdo_update_block_map_page()` packs the new mapping, acquires a lock on the newer recovery journal sequence if needed, releases the older lock, releases the per-entry lock transferred from the data VIO, and clears the VIO’s recovery sequence.

## Dependencies and Interactions

- Uses action manager for multi-zone operation dispatch.
- Uses admin state per block map zone.
- Uses block map tree code for interior lookup/allocation.
- Uses VDO page cache for leaf page caching.
- Uses recovery journal for consistency locks.
- Uses forest growth helpers for logical expansion.

## Notable Edge Cases

- Logical block numbers beyond `entry_count` complete with `VDO_OUT_OF_RANGE`.
- A zero block map page PBN means the mapping page is unallocated and the logical block is unmapped.
- Drain completes only when both tree zone and page cache are inactive.
- Read-only mode changes drain completion result to `VDO_READ_ONLY`.
- Growth to a smaller size is treated as no shrink; next entry count is capped at current count.
