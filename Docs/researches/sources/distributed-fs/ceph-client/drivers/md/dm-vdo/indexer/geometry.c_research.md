# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/geometry.c

## Purpose
`geometry.c` computes and manages `index_geometry`, the derived layout model for a UDS index volume. It maps memory/page/chapter parameters into record capacity, delta-index sizing, persistent volume size, sparse/dense chapter behavior, and reduced-index physical remapping.

## Important APIs, Types, And Functions
- `uds_make_index_geometry()` allocates geometry and computes all derived fields.
- `uds_copy_index_geometry()` clones an existing geometry through the same constructor.
- `uds_free_index_geometry()` releases geometry.
- `uds_map_to_physical_chapter()` maps a virtual chapter number to a physical chapter, including reduced-index remap handling.
- `uds_has_sparse_chapters()` determines whether the active window extends into sparse chapters.
- `uds_is_chapter_sparse()` checks whether one virtual chapter should be treated as sparse.
- `uds_chapters_to_expire()` returns how many chapters to expire after opening a new chapter, with special reduced-index behavior.

## Control Flow And Data Flow
Geometry construction stores direct parameters, derives dense chapter count, records per page/chapter/volume, chapter delta-list coding parameters, index pages per chapter using `uds_get_delta_index_page_count()`, pages per chapter/volume, and bytes per volume including header pages. Hashing and chapter-index code then use these derived bit counts to split record names into list/address/payload fields.

Virtual-to-physical mapping is simple modulo for normal geometry. Reduced geometry handles an eliminated physical chapter 0 by remapping one virtual chapter to a replacement physical chapter and adjusting nearby virtual chapters to avoid the removed slot. Expiration logic normally expires one old chapter after the volume is full, but may expire two or zero around the remapped chapter to keep physical space consistent.

## State And Persistence Behavior
Geometry is runtime state derived from persistent configuration. `remapped_virtual` and `remapped_physical` are persisted by config version 8.02. The derived values control persistent index layout, so a mismatch between saved and requested geometry makes an index unusable.

## Dependencies And Integration Points
The file depends on errors, logging, memory allocation, assertions, delta-index sizing, and indexer constants. It feeds config creation, volume mapping, sparse cache, chapter-index packing/search, and index layout size checks.

## Risks
- Arithmetic uses a mix of `u32`, `u64`, and `size_t`; large sparse configurations need overflow scrutiny.
- `uds_is_reduced_index_geometry()` infers reduced geometry from odd `chapters_per_volume`, so constructors must preserve that convention.
- Remap mapping is nontrivial and off-by-one errors can read/write the wrong physical chapter.
- Delta-list bit calculations must remain aligned with `hash-utils.h`.

## Test Signals
Tests should cover every memory-size geometry produced by config, dense and sparse active windows, reduced-index mapping before/at/after remapped virtual chapters, expiration counts around remap boundaries, and computed page/byte sizes against known fixtures.
