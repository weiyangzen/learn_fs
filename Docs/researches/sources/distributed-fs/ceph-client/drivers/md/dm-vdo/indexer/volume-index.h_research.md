# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume-index.h

## Purpose
Declares the volume-index data model and API for mapping record names to chapters, including sparse hook support, per-zone locking, record mutation handles, persistence, and statistics.

## Important APIs, Types, And Functions
Defines `NO_CHAPTER`, `struct volume_index_stats`, `struct volume_sub_index_zone`, `struct volume_sub_index`, `struct volume_index_zone`, `struct volume_index`, and `struct volume_index_record`. Public APIs cover creation/free, save-block computation, zone mapping, sparse sampling, hook lookup, record lookup/put/remove/chapter update, open-chapter advancement, save/load, and stats.

## Control Flow
Request processing obtains a `volume_index_record` for a name, checks its public fields (`virtual_chapter`, `is_collision`, `is_found`), and then calls put/remove/set-chapter as needed. Chapter rollover calls the open-chapter setters to advance valid ranges. Sparse-cache triage uses `uds_lookup_volume_index_name()` to decide whether a sampled name references a sparse chapter.

## State And Persistence
The structures expose compact delta-index state, flush watermarks, per-zone virtual chapter ranges, masks, chapter/list counts, memory sizing, sparse sample rate, and per-zone hook mutexes. Save/load are implemented in the C file but declared here for layout integration.

## Dependencies And Integration Points
Includes configuration, delta-index, public indexer types, limits, and thread utilities. It is included by `index.h`, `index.c`, `index-layout.c`, and sparse-cache control paths.

## Risks
`volume_index_record` is a live mutation cursor into the delta index; callers should not retain it across unrelated operations or after removing the record. Hook records carry a mutex pointer that the mutation helpers lock internally. `NO_CHAPTER` is `U64_MAX` and must not collide with valid virtual chapter arithmetic.

## Test Signals
Compile and functional tests should validate record cursor lifecycle, sparse hook locking paths, public field semantics after mutations, save/load declarations, and stats structure population.
