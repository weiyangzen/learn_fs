# sources/distributed-fs/ceph-client/fs/gfs2/trans.c

## Purpose
`trans.c` implements GFS2 transaction begin/end, metadata and journaled-data buffer attachment, revoke addition/removal, and transaction object cleanup. It is the bridge between higher-level filesystem mutations and the GFS2 log.

## Important APIs, Types, And Functions
`__gfs2_trans_begin` initializes a caller-provided transaction and reserves log space and revokes. `gfs2_trans_begin` allocates a transaction from `gfs2_trans_cachep`. `gfs2_trans_end` releases unused reservations or commits touched transactions. `gfs2_trans_add_data`, `gfs2_trans_add_databufs`, and `gfs2_trans_add_meta` attach buffers to transaction lists. `gfs2_trans_add_revoke`, `gfs2_trans_remove_revoke`, and `gfs2_trans_free` manage revoke state and final cleanup.

## Control Flow
Transaction begin rejects nesting through `current->journal_info`, rejects zero-work transactions, fails with `-EROFS` when withdrawn or journal-live is false, calculates reserved log blocks, starts an internal write, then reserves log blocks and revokes under `sd_log_flush_lock`. If fast reservation fails, it does a full reservation outside the read lock and then rechecks journal liveness.

Adding a metadata buffer allocates or reuses `gfs2_bufdata`, validates the metadata magic, checks withdrawn/frozen state, pins the buffer, stamps the journal id, marks the glock dirty, and links the buffer into the transaction. Journaled data follows a similar flow but links into `tr_databuf`. Transaction end releases unused revokes, validates that touched buffers and revokes fit the requested credits, commits through `gfs2_log_commit`, releases the flush lock, optionally flushes synchronous mounts, and ends the internal write.

## State And Persistence
State is held in `current->journal_info`, `struct gfs2_trans` lists and counters, buffer private `gfs2_bufdata`, glock flags `GLF_LFLUSH`/`GLF_DIRTY`, log reservation counters, and the on-disk journal after commit. Untouched transactions release their reservations without log commit.

## Dependencies And Integration Points
This file depends on GFS2 log reservation/commit APIs, metadata I/O, glocks, buffer heads, folios, revokes, and withdrawal helpers. All metadata mutators in rgrp, xattr, superblock, inode, quota, and directory code depend on these routines.

## Risks And Test Signals
Risks include incorrect credit estimates, missing `gfs2_trans_add_meta` before mutation, stale revoke removal when reusing blocks, nested transaction bugs, and mutations while frozen or withdrawn. Signals include assertion output from `gfs2_print_trans`, log flush tracepoints, xfstests journal replay coverage, synchronous mount behavior, and fsck after crash/recovery tests.
