# sources/distributed-fs/ceph-client/fs/nilfs2/segment.c

## Purpose

`segment.c` is NILFS2's segment constructor and log-writer implementation. It serializes filesystem transactions, collects dirty file and metadata buffers, creates segment-summary records, assigns physical log block numbers through bmaps, writes partial segments, finalizes checkpoints and super roots, manages background segctord wakeups, and provides the GC segment-cleaning write path.

## Important APIs, Types, and Functions

Public entry points are `nilfs_transaction_begin()`, `nilfs_transaction_commit()`, `nilfs_transaction_abort()`, `nilfs_relax_pressure_in_lock()`, `nilfs_construct_segment()`, `nilfs_construct_dsync_segment()`, `nilfs_clean_segments()`, `nilfs_attach_log_writer()`, and `nilfs_detach_log_writer()`.

The key state object is `struct nilfs_sc_info` from `segment.h`, holding dirty-file lists, GC inodes, segment buffers, write logs, freed segment arrays, collection stage, summary pointers, counters, checkpoint number, flags, request queues, timer, and segctord task.

Internal flow is split across dirty-buffer discovery (`nilfs_lookup_dirty_data_buffers()`, `nilfs_lookup_dirty_node_buffers()`), collection (`nilfs_segctor_collect_blocks()`), segment allocation/extension (`nilfs_segctor_begin_construction()`, `nilfs_segctor_extend_segments()`), bmap assignment (`nilfs_segctor_update_payload_blocknr()`), write preparation and completion (`nilfs_prepare_write_logs()`, `nilfs_segctor_write()`, `nilfs_segctor_wait()`, `nilfs_segctor_complete_write()`), and abort cleanup.

## Control Flow

Ordinary filesystem updates call `nilfs_transaction_begin()` to enter a read side of `ns_segctor_sem`, then commit marks the transaction committed, starts the background timer, and may request immediate flush when dirty blocks exceed a watermark. A synchronous transaction flag calls `nilfs_construct_segment()` after leaving the transaction.

Segctord or a direct caller obtains the writer transaction lock, accepts pending requests, determines a mode (`SC_LSEG_SR`, `SC_LSEG_DSYNC`, `SC_FLUSH_FILE`, or `SC_FLUSH_DAT`), and calls `nilfs_segctor_do_construct()`. Construction first moves globally queued dirty inodes into `sc_dirty_files`, pins their ifile buffers, marks metadata dirty if needed, and exits early if there is no work.

Collection progresses through explicit stages: GC inodes, normal files, ifile, checkpoint file, sufile/free-segment updates, DAT, and optional super root. Each scanned file collects dirty data buffers, node buffers, and bmap buffers using operation tables that differ for normal files, DAT, and dsync logs. If a segment buffer fills, construction may extend with more full segments, cancel provisional sufile frees, reset stage state, and retry.

After collection, payload buffers are assigned physical log block numbers through `nilfs_bmap_assign()`, binfo records are written into the segment summaries, segment summaries and optional super root are filled, sufile usage is updated, folios are put into writeback state, CRCs are calculated, and logs are submitted. Completion clears dirty/async/delay/volatile/redirected bits, ends folio writeback, drops collected inode state, advances `ns_segnum`, `ns_nextnum`, `ns_pseg_offset`, `ns_seg_seq`, timestamps, and if a super root was written, advances the last checkpoint and clears metadata dirty flags.

Abort waits for submitted logs, redirties collected inodes when needed, cancels provisional segment usage and free-segment changes, marks failed segments discontinued or erroneous, and destroys logs.

## State and Persistence Behavior

This file is the main persistence engine for NILFS2. Persistent state affected includes file data, btree nodes, ifile entries, cpfile checkpoints, sufile segment states, DAT translations, super roots, superblock log cursors, and checkpoint numbers. It also maintains volatile coordination state: dirty inode lists, `NILFS_I_BUSY/COLLECTED/UPDATED`, `NILFS_SC_UNCLOSED`, request sequence counters, flush bitmaps, and construction stage cursors.

Data-sync construction can write data-only logical segments without a super root unless strict ordering, an unclosed segment, or discontinued state forces a full checkpoint-style construction. GC construction uses shadow DAT state and freed segment arrays, and discards segments after successful cleaning if the mount option is enabled.

## Dependencies and Integration Points

`segment.c` integrates with nearly every NILFS2 subsystem: bmaps, btree node caches, metadata file dirty tracking, ifile/cpfile/sufile/DAT, GC ioctls, superblock commit logic, page/buffer helpers, segment buffers, kernel threads, timers, wait queues, freezer support, block device discard, and tracepoints.

## Risks and Edge Cases

This is a high-risk concurrency and crash-consistency file. Correctness depends on stage retry logic, sufile cancellation on failures, exact folio writeback begin/end pairing, dirty inode list state, and checkpoint finalization ordering. The code has special handling for block sizes smaller than page size because folios spanning segments can otherwise be double-buffered incorrectly. `nilfs_construct_segment()` deliberately BUGs if called inside a NILFS transaction to avoid deadlock. Segment allocation failures, BIO failures, bmap assignment replacements, and GC shadow-map failures all need exact cleanup.

## Test Signals

Core tests should cover ordinary buffered writes, fsync/data-sync ranges, strict-order mounts, background timer checkpointing, dirty-block watermark flushes, blocksize smaller than page size, super-root checkpoint creation, metadata-only updates, interrupted sync waits, writer teardown with pending work, ENOSPC, injected bmap assignment errors, injected BIO errors, and GC cleaning with DAT shadow rollback and discard failures.
