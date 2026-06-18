# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/geometry.h

## Purpose
`geometry.h` defines `struct index_geometry`, layout constants, and helper predicates for UDS index-volume geometry.

## Important APIs, Types, And Functions
- `struct index_geometry` contains direct parameters such as page size, record pages per chapter, total/sparse chapters, remap fields, and derived fields such as pages/records per chapter/volume, delta-list counts, address bits, payload bits, and dense chapter count.
- Constants define record size, default page size, record pages per chapter, chapters per volume, sparse defaults, chapter mean delta bits, default delta-list bit counts, and header pages.
- APIs include make/copy/free, virtual-to-physical chapter mapping, reduced/sparse predicates, sparse-window checks, chapter sparse check, and chapters-to-expire.

## Control Flow And Data Flow
The geometry object is created from configuration and then passed by pointer to index components. Hash utilities use `chapter_delta_list_bits` and `chapter_address_bits`; chapter-index code uses `record_pages_per_chapter`, `delta_lists_per_chapter`, `chapter_mean_delta`, and `chapter_payload_bits`; volume code uses chapter mapping and sparse predicates.

## State And Persistence Behavior
Runtime geometry mirrors persisted configuration. Direct fields and remap fields are saved by config metadata; derived fields must be recomputed consistently after load rather than stored independently.

## Dependencies And Integration Points
The header includes `indexer.h` for record name/data sizes and basic UDS types. It is included broadly by config, chapter-index, hash-utils, volume, sparse-cache, and index layout code.

## Risks
- Changing constants changes index format and capacity.
- Derived fields are assumed internally consistent; callers should not mutate direct fields after construction.
- `records_per_volume` is `u64`, but many page/list fields are `u32`; boundary sizes need testing.

## Test Signals
Tests should verify derived values for default, small, sparse, and reduced geometries, and ensure helper predicates match persisted config semantics.
