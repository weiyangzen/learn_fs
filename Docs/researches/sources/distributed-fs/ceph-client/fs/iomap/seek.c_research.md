## sources/distributed-fs/ceph-client/fs/iomap/seek.c

Purpose: implements generic `SEEK_HOLE` and `SEEK_DATA` for iomap filesystems.

Important APIs: `iomap_seek_hole` and `iomap_seek_data` scan from a requested offset to EOF with `IOMAP_REPORT`. Helpers treat `IOMAP_HOLE`, `IOMAP_UNWRITTEN`, and data mappings differently. For unwritten extents, page-cache state is queried with `mapping_seek_hole_data` because dirty cached data can make an otherwise unwritten extent contain visible data.

Control flow: both entry points reject negative or EOF-and-beyond positions with `-ENXIO`. Hole seek advances over mapped data, returns immediately for holes, and probes unwritten extents for cached holes. Data seek advances over holes, probes unwritten extents for cached data, and returns the first non-hole mapping position. If no data is found before EOF, data seek returns `-ENXIO`; hole seek returns EOF.

State and persistence: no state is persisted. Results reflect a combination of filesystem extent mappings and current page-cache state, so they are snapshot-like and can race with writes.

Dependencies and integration points: uses VFS seek semantics, iomap report callbacks, and page-cache hole/data scanning. Filesystems wire these helpers into `llseek` implementations.

Risks and test signals: correctness depends on treating unwritten extents with dirty cache accurately. Test sparse files, unwritten preallocation with and without cached writes, EOF boundary cases, negative offsets, and concurrent buffered writes while seeking.
