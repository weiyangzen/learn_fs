<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/meta_io.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/meta_io.c

## Purpose
`meta_io.c` provides buffer-cache and address-space operations for GFS2 metadata and resource-group blocks. It maps filesystem blocks into glock-specific or global metadata address spaces, submits metadata reads and writeback, creates new metadata buffers, waits for metadata I/O, wipes journal state for freed blocks, and performs metadata readahead.

## Important APIs, types, and functions
Exported address-space operations are `gfs2_meta_aops` and `gfs2_rgrp_aops`. Exported functions include `gfs2_getbuf`, `gfs2_meta_new`, `gfs2_meta_read`, `gfs2_meta_wait`, `gfs2_journal_wipe`, `gfs2_meta_buffer`, and `gfs2_meta_ra`. Important internals are `gfs2_aspace_write_folio`, `gfs2_aspace_writepages`, `meta_prep_new`, `gfs2_meta_read_endio`, `gfs2_submit_bhs`, `gfs2_ail1_wipe`, and `gfs2_getjdatabuf`.

## Control Flow
`gfs2_getbuf` chooses the glock address space or the filesystem metadata address space, computes the folio index and buffer index from the filesystem block number, optionally creates the folio and empty buffers, maps the selected buffer to the block device, and returns a referenced `buffer_head`. `gfs2_meta_new` gets a created buffer and initializes the metadata magic after marking the buffer uptodate. `gfs2_meta_read` gets the buffer, locks it, queues a metadata read if not uptodate, optionally queues one-block readahead, submits adjacent buffers as one or more bios, and waits if `DIO_WAIT` is requested. `gfs2_meta_wait` waits for a buffer and turns failed reads into EIO, with extra error reporting if the current transaction was touched.

`gfs2_aspace_writepages` iterates dirty metadata folios. `gfs2_aspace_write_folio` locks dirty buffers, marks them async write, starts folio writeback, submits each buffer with metadata/prio flags, and ends writeback immediately if no buffer was submitted. Journal wiping first removes matching buffers from AIL1, then searches metadata or journaled-data page cache buffers for the block range, removes pinned/AIL journal state with `gfs2_remove_from_journal`, and clears dirty/uptodate state. `gfs2_meta_buffer` wraps read plus metatype validation. `gfs2_meta_ra` starts a bounded extent readahead and returns the first buffer, waiting when needed.

## State and Persistence
Runtime state is in buffer-head flags, folio writeback state, glock address-space mappings, AIL and pinned journal lists, and current transaction flags. Persistent effects include metadata writes to in-place disk blocks and removal of freed/deleted blocks from future journal replay. New metadata buffers receive only the GFS2 magic here; callers fill type and body fields.

## Dependencies and Integration Points
This file depends on glock address spaces, log and lops buffer state, transaction helpers, rgrp release paths, metadata validation in `util.h`, Linux buffer-head/page-cache/writeback APIs, and block bio submission. It is used by bmap, dir, xattr, quota, recovery, rgrp, superblock, and lops replay code.

## Risks
Correctness depends on block-size-to-page indexing, buffer refcounts, and locked-buffer state. `gfs2_submit_bhs` assumes the buffer array contains initialized entries; zero-entry submission is avoided by callers' flow. Journal wiping must coordinate `sd_log_lock` and `sd_ail_lock` with buffer locks to avoid leaving stale pinned or AIL buffers that later replay freed blocks. Metadata reads during withdraw return EIO. Readahead must not exceed tune limits and must handle partial extent completion.

## Test Signals
Signals include metadata reads with and without wait, readahead on inode and directory extents, failed metadata I/O in touched transactions, metadata writeback under memory pressure, block free/truncate journal wipe for metadata and journaled-data files, AIL removal of freed blocks, metatype validation failures, and lockdep around log/AIl/buffer lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/meta_io.c -->
