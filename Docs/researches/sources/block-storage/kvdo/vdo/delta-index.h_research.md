# File Research: sources/block-storage/kvdo/vdo/delta-index.h

## Purpose
Declares the delta index data structures and public API used by UDS/VDO dedupe index code.

## Main Interfaces
- `struct delta_list`: bit offset, bit size, and cached search position.
- `struct delta_zone`: memory arena, list headers, save writer, coding constants, stats, list range, and tag.
- `struct delta_index`: zone array, global list counts, per-zone load counters, mutability, and tag.
- `struct delta_index_page`: wrapper for treating an immutable chapter-index page as a one-zone delta index.
- `struct delta_index_entry`: iterator/search result/insertion point for a delta list.
- `struct delta_index_stats`: aggregate stats from zones.

## Exported Operations
- Lifecycle: `initialize_delta_index()`, `initialize_delta_index_page()`, `uninitialize_delta_index()`, `empty_delta_index()`, `empty_delta_zone()`.
- Immutable page packing: `pack_delta_index_page()`.
- Save/restore: `start_restoring_delta_index()`, `finish_restoring_delta_index()`, `abort_restoring_delta_index()`, `start_saving_delta_index()`, `finish_saving_delta_index()`, `write_guard_delta_list()`.
- Search/mutate: `start_delta_index_search()`, `next_delta_index_entry()`, `get_delta_index_entry()`, `put_delta_index_entry()`, `remove_delta_index_entry()`, value/collision accessors.
- Sizing/stats: `compute_delta_index_save_bytes()`, `compute_delta_index_size()`, `get_delta_index_page_count()`, zone bit/allocation helpers.

## Invariants
Callers must respect mutable versus immutable indexes: mutation/value-setting APIs assert mutable entries. `delta_index_entry` fields marked private are state carried between module calls and should not be externally mutated.
