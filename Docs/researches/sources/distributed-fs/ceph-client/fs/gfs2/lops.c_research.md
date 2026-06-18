<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/lops.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/lops.c

## Purpose
`lops.c` implements GFS2 log operations for metadata buffers, revoke records, and journaled data buffers. It writes log descriptors and payload blocks during commit, unpins buffers afterward, scans journal descriptors during recovery, replays non-revoked blocks to their in-place locations, and provides low-level journal bio helpers and journal-head discovery.

## Important APIs, types, and functions
External helpers include `gfs2_pin`, `gfs2_log_incr_head`, `gfs2_log_bmap`, `gfs2_log_write`, `gfs2_log_submit_write`, `gfs2_find_jhead`, and `gfs2_drain_revokes`. The operation table is `gfs2_log_ops[]`, containing `gfs2_databuf_lops`, `gfs2_buf_lops`, and `gfs2_revoke_lops`. Important internals include `gfs2_unpin`, `maybe_release_space`, `gfs2_end_log_write`, `gfs2_log_get_bio`, `gfs2_jhead_folio_search`, `gfs2_get_log_desc`, `gfs2_before_commit`, `buf_lo_scan_elements`, `revoke_lo_scan_elements`, and `databuf_lo_scan_elements`.

## Control Flow
During transaction construction, `gfs2_pin` clears buffer dirty state, marks it pinned, moves preexisting AIL entries to AIL2, takes a buffer reference, and increments `sd_log_pinned`. During flush, `lops_before_commit` dispatches to `databuf`, `buf`, and `revoke` handlers. Metadata and data handlers sort buffers by in-place block number, write one or more log descriptor blocks, then write the actual payload blocks to the journal. Journaled data descriptors store both block numbers and escape flags; if a data block begins with the GFS2 magic value, a copied page is written with the magic zeroed and replay later restores it. Revoke commit writes revoke descriptors and continuation blocks from `sd_log_revokes`.

After the log header is committed, `lops_after_commit` unpins metadata and journaled-data buffers. `gfs2_unpin` marks the in-place buffer dirty, updates rgrp clone state and discard information for resource-group buffers, links bufdata into the transaction's AIL1 list, clears `GLF_LFLUSH`, and decrements `sd_log_pinned`. Revokes are drained and their held glocks are released.

For recovery, `gfs2_find_jhead` maps journal extents, reads journal blocks in large bio batches into the journal inode page cache, searches for the highest valid log header sequence, and truncates the page cache afterward. Recovery scanning runs in two passes: pass 0 collects revokes and initializes counters; pass 1 replays metadata and journaled data descriptors unless `gfs2_revoke_check` says the block was revoked after the descriptor. Replayed metadata is validated with `gfs2_meta_check`; resource-group replay emits diagnostics if an in-core rgrp buffer looks obsolete.

## State and Persistence
Persistent journal records are `GFS2_LOG_DESC_METADATA`, `GFS2_LOG_DESC_JDATA`, `GFS2_LOG_DESC_REVOKE`, continuation blocks, and payload blocks. Runtime state includes pinned buffer flags, bufdata lists, transaction counts, `jd_log_bio`, journal extent mappings, journal-head search page-cache folios, replay counters, and in-memory revoke lists. Resource-group clone state can be refreshed when rgrp buffers are unpinned after commit.

## Dependencies and Integration Points
The file depends on bmap extent mapping, glock and glops behavior, metadata I/O, recovery revoke helpers, rgrp bitmap helpers, transaction structs, tracepoints, mempool page allocation, buffer-head state, bio submission, and filesystem block-size geometry. `log.c` calls the lops table for every flush; `recovery.c` calls scan hooks through `lops.h`.

## Risks
The escape path contains a high-risk copy operation because journaled data that looks like metadata magic must be transformed without corrupting caller pages. Commit and replay descriptor lengths must match `buf_limit` and `databuf_limit`. Journal-head search uses page-cache refs and chained bios, so refcount mistakes would leak or prematurely release folios. Replay must honor revokes across wraparound, validate metadata, and avoid stale rgrp state. Log I/O errors set `sd_log_error` and withdraw, so error propagation is intentionally severe.

## Test Signals
Signals include metadata and journaled-data transactions spanning multiple descriptors, data blocks beginning with GFS2 magic, revoke collection and replay skip behavior, journal wraparound head detection, discontinuous journal extents, bio chaining under large journals, rgrp replay diagnostics, log write I/O errors, mempool pressure, and recovery pass counters for found versus replayed blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/lops.c -->
