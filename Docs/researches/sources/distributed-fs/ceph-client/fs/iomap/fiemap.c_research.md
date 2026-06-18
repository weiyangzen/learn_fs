## sources/distributed-fs/ceph-client/fs/iomap/fiemap.c

Purpose: provides generic iomap-backed file extent reporting and legacy block mapping. `iomap_fiemap` converts filesystem-provided iomaps into FIEMAP extents for userspace, while `iomap_bmap` implements the old `->bmap` sector query.

Important APIs: `iomap_to_fiemap` maps iomap types to `FIEMAP_EXTENT_*` flags: holes are skipped, delalloc becomes DELALLOC/UNKNOWN, unwritten becomes UNWRITTEN, inline becomes DATA_INLINE, and shared/merged iomap flags propagate. `iomap_fiemap_iter` delays emission by one extent so the final extent can be marked `FIEMAP_EXTENT_LAST`. `iomap_bmap` flushes dirty mapping data with `filemap_write_and_wait` before looking up one block.

Control flow: `iomap_fiemap` calls `fiemap_prep`, creates an `iomap_iter` with `IOMAP_REPORT`, scans mappings via `iomap_iter`, emits the previous non-hole mapping, and after the loop emits the last mapping with LAST. `-ENOENT` from an inode with no mapping is tolerated as empty output. `iomap_bmap` requests a single block-sized mapping and returns the physical block number only for `IOMAP_MAPPED`.

State and persistence: no durable state is changed, but `iomap_bmap` forces writeback before exposing a physical block number. FIEMAP output is a snapshot of filesystem mapping state supplied by callbacks, including delalloc and shared extent status.

Dependencies and integration points: integrates with VFS FIEMAP, block-device mapping consumers, and filesystem `iomap_ops`. It relies on `iomap_iter_advance_full` to make progress over whole mappings.

Risks and test signals: risks include incorrect last-extent marking, exposing stale mappings if filesystem callbacks do not synchronize, and legacy bmap returning 0 for both holes and errors. Test with sparse files, inline data, delayed allocation, unwritten extents, shared/reflink extents, empty mapping callbacks, and bmap after dirty buffered writes.
