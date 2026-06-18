# sources/distributed-fs/ceph-client/fs/gfs2/aops.c

## Purpose
Provides GFS2 address-space operations for buffered reads, readahead, writeback, dirtying, bmap, invalidation, and folio release, with separate behavior for ordinary/ordered data and journaled-data files.

## Important APIs, Types, And Functions
`gfs2_read_folio()` dispatches to iomap, stuffed-file read, or mpage read for jdata. `gfs2_readahead()` selects mpage or iomap readahead and skips stuffed files. `gfs2_writepages()` uses `iomap_writepages()` with `gfs2_writeback_ops` and can force AIL flush. `gfs2_jdata_writepages()` and helpers batch dirty folios inside GFS2 transactions before log flush/retry. `gfs2_jdata_writeback()` writes journaled data when the inode glock is exclusive. `gfs2_internal_read()` reads internal files through the page cache. `adjust_fs_space()` updates statfs state after filesystem growth. `gfs2_bmap()` maps logical blocks under a shared glock. `gfs2_invalidate_folio()` and `gfs2_release_folio()` handle buffer-head cleanup for jdata. `gfs2_set_aops()` chooses `gfs2_aops` or `gfs2_jdata_aops`.

## Control Flow
Ordinary files use iomap read/writeback/dirty/release paths. Journaled-data writeback walks tagged dirty folios, starts transactions before locking batches, adds checked folios to the transaction, writes via block helpers, and flushes the log for data-integrity sync. Stuffed reads copy inline data from the dinode into a folio. Invalidation discards journal buffer state for full or partial folio ranges. Release refuses folios with active, dirty, pinned, or transaction-owned buffers.

## State And Persistence
Mutates folio dirty, checked, uptodate, writeback, and buffer-head journal state. Updates GFS2 transaction logs, AIL flush flags, inode dirty state, statfs master/local counters, and rindex freshness. Persistent data reaches disk through iomap/mpage writeback or the GFS2 journal.

## Dependencies And Integration Points
Depends on `bmap.c` iomap/writeback operations, glocks, log, transactions, metadata I/O, quota/resource-group code, and Linux folio/writeback APIs. Selected by inode setup and used by VFS page cache.

## Risks
Journaled-data mode must start transactions before folio locks to avoid lock-order problems. Dirty buffers in AIL can stall `balance_dirty_pages()` unless AIL flush is forced. Stuffed/jdata paths use buffer heads while ordinary files use iomap, so aops selection must track inode mode. Folio release must not free journal-owned buffers.

## Test Signals
Test buffered reads for stuffed, jdata, and ordinary files; readahead; WB_SYNC_NONE and WB_SYNC_ALL writeback; log flush after jdata sync; bmap under glock; folio invalidation/release with pinned/dirty buffers; filesystem grow statfs adjustment; and withdrawn filesystem `EIO`.
