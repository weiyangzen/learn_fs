# File Research: sources/block-storage/kvdo/vdo/volume-index-ops.h

## Purpose
Defines the abstract volume-index interface used by the UDS/VDO index code. The volume index maps chunk names to virtual chapters, supports lookup/update/removal, persistence save/restore, per-zone chapter advancement, sparse sampling queries, and statistics collection.

## Public Types
- `struct volume_index_stats`: aggregate memory and behavior counters for an index portion, including allocation, rebalance time/count, record/collision/discard/overflow counts, delta-list count, and early flush count.
- `struct volume_index_record`: mutable handle returned by `get_volume_index_record()`. It carries public result state (`virtual_chapter`, `is_collision`, `is_found`) plus private state tying the lookup to a delta-index entry, optional sampled-index mutex, zone, name, and owning `volume_index`.
- `struct volume_index`: vtable for concrete implementations. Methods cover lifecycle, record lookup, stats, zone mapping, sample detection, sampled/dense lookups, chapter movement, tag setting, and save/restore phases.

## Key APIs
- Creation/sizing:
  - `make_volume_index()`
  - `compute_volume_index_save_blocks()`
- Persistence:
  - `load_volume_index()`
  - `save_volume_index()`
  - inline wrappers for `start_*`, `finish_*`, and `abort_restoring_volume_index()`
- Record operations:
  - `get_volume_index_record()`
  - `put_volume_index_record()`
  - `remove_volume_index_record()`
  - `set_volume_index_record_chapter()`
- Chapter/range control:
  - `set_volume_index_open_chapter()`
  - `set_volume_index_zone_open_chapter()`
- Lookup/stat helpers:
  - `lookup_volume_index_name()`
  - `lookup_volume_index_sampled_name()`
  - `is_volume_index_sample()`
  - `get_volume_index_zone()`
  - `get_volume_index_stats()`
  - `get_volume_index_combined_stats()`

## Implementation Notes
This header is intentionally dispatch-oriented. Almost every operation is an inline vtable call, allowing versioned implementations such as `volume-index005.c` and `volume-index006.c` to share one external API.

`volume_index_record` is stateful: callers must first populate it through `get_volume_index_record()`, then reuse that handle for insert/update/delete. The private `magic` field is validated by the concrete 005 implementation to prevent illegal record reuse or operations on uninitialized handles.

The optional `mutex` field is used by sampled sparse indexes. In the 006 implementation, sampled records are backed by the hook subindex and carry a per-zone mutex so later `put`, `remove`, or `set_chapter` operations can synchronize with concurrent read-only sample lookups.

## Dependencies
Includes core UDS/VDO types from `compiler.h`, `config.h`, `delta-index.h`, `uds-threads.h`, and `uds.h`.

## Invariants and Risks
- A `volume_index` object must have all vtable entries initialized before use.
- `free_volume_index()` tolerates `NULL`; most other wrappers do not.
- `volume_index_record` operations are valid only after successful `get_volume_index_record()`.
- Persistence is split into start/finish phases, so callers must complete or abort restore/save flows consistently.
