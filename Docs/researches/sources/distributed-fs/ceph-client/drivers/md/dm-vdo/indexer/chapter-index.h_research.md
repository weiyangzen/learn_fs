# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/chapter-index.h

## Purpose
`chapter-index.h` defines the open chapter index structure and declares APIs for building, packing, validating, and searching UDS chapter indexes.

## Important APIs, Types, And Functions
- `NO_CHAPTER_INDEX_ENTRY` is `U16_MAX`, used when no index entry points to a candidate record page.
- `struct open_chapter_index` holds geometry, mutable `delta_index`, current virtual chapter number, volume nonce, and memory footprint.
- Public APIs mirror the lifecycle: make, free, empty for new chapter, put record, pack page, initialize immutable page, validate page, and search page.

## Control Flow And Data Flow
Callers maintain one open index while accumulating chapter records. When a chapter closes, they pack pages in list order. Readers initialize a `delta_index_page` from raw page data and search it for a name to narrow candidate record-page reads.

## State And Persistence Behavior
Open chapter state is volatile. Packed page state is persistent through `delta-index` immutable page encoding and includes the nonce/list range needed to validate pages during read or rebuild.

## Dependencies And Integration Points
The header depends on `delta-index.h` and `geometry.h`. It is part of the UDS volume/index writer and lookup path.

## Risks
- The sentinel value must stay outside valid record-page numbers.
- `memory_size` is informational but useful for resource accounting; callers should not assume it is only the requested memory.
- The APIs rely on consistent geometry across creation, packing, and search.

## Test Signals
Compile and integration tests should verify closed-chapter lookup after writing records, sparse/dense geometry compatibility, and behavior when no entry is found.
