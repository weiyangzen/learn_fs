<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_aops.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_aops.c

Purpose: Implements XFS address-space operations for buffered and DAX files, including iomap-based read/writeback, write I/O completion, append-size updates, COW/unwritten conversion, zoned writeback, bmap, readahead, and swap activation.

Important APIs and functions: `xfs_setfilesize` transactionally advances on-disk file size after append writeback. `xfs_end_bio` queues iomap ioends to inode work; `xfs_end_io` sorts/merges and completes them. `xfs_end_ioend_write` handles write completion, COW cancellation/conversion, unwritten extent conversion, zoned completion, and page-cache completion. `xfs_map_blocks` validates/rebuilds cached writeback iomaps and converts delalloc extents. Zoned equivalents are `xfs_zoned_map_blocks`, `xfs_zoned_writeback_range`, and `xfs_zoned_writeback_submit`. Exported operation tables are `xfs_address_space_operations` and `xfs_dax_aops`.

Control flow: Writeback starts in `xfs_vm_writepages`, clears truncate state, and dispatches to normal or zoned iomap writepages. Normal mapping checks COW fork precedence, data/cow sequence counters, holes, delalloc conversion, and COW boundaries before adding folios to ioends. Submit can convert COW extents before bio submission and routes transaction-requiring completions to the unwritten workqueue. Completion updates metadata only in workqueue context when appending, COW, unwritten, zoned, or dontcache work is needed. Read paths use iomap read ops, optionally wrapping bios in ioends for integrity checksum completion.

State and persistence: Persists file size, extent state transitions from delayed/unwritten/COW to real data fork mappings, zoned allocation completion state, and page writeback status. It clears stale delalloc mappings on errors to keep block accounting correct. DAX writeback delegates to `dax_writeback_mapping_range`.

Dependencies and integration: Heavily integrates with iomap, XFS bmap, reflink, zone allocation, inodegc, realtime groups, block integrity, page cache, swapfile activation, and XFS trace/error injection. The operation tables plug into the VFS address_space for regular and DAX inodes.

Risks: Races around COW fork changes, truncate, direct I/O, and writeback mapping reuse are mitigated by page locks and fork sequence checks; regressions here can corrupt extents or leave stale delalloc. Error handling must punch delalloc on failed COW writeback. Zoned writeback requires open-zone lifetime pairing and correct append-sector recording. Swap activation must flush inodegc before checking shared extents.

Test signals: Buffered writeback under ENOSPC/EIO, reflink COW writeback and cancellation, unwritten extent conversion, append file-size persistence, DAX writeback, bmap refusal for reflink/realtime swap use, zoned inode writeback, block-integrity reads, and swapfile activation races with inodegc.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_aops.c -->
