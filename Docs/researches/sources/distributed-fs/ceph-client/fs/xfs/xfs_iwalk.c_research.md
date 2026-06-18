## sources/distributed-fs/ceph-client/fs/xfs/xfs_iwalk.c

Purpose: provides generic inode and inode-btree record walkers for XFS. It traverses allocation groups in inode-number order, caches inobt records outside AGI locks, performs inode cluster readahead, supports resumable starts, and optionally parallelizes by AG.

Important APIs and functions: public entry points are `xfs_iwalk`, `xfs_iwalk_threaded`, and `xfs_inobt_walk`. Internal machinery is centered on `struct xfs_iwalk_ag`, `xfs_iwalk_ag_start`, `xfs_iwalk_ag`, `xfs_iwalk_run_callbacks`, `xfs_iwalk_ag_recs`, `xfs_iwalk_args`, `xfs_iwalk_prefetch`, and `xfs_inobt_walk_prefetch`. `xfs_iwalk_ichunk_ra` prefetches inode clusters; `xfs_iwalk_adjust_start` masks inodes before the requested start within the first record.

Control flow: setup computes a prefetch record count, allocates a record cache, and iterates per-AG objects from the start AG. For each AG, it opens the AGI/inobt cursor at or before the requested agino, caches records, skips empty chunks when requested, records forward progress, and when the cache fills, tears down the cursor and AGI buffer before invoking callbacks. After callbacks, it recreates the cursor at the next record. Threaded mode creates one work item per AG with its own empty transaction and perag hold.

State and persistence: the walker is read-oriented and does not itself change persistent metadata. It reads AGI/inobt records, may readahead inode cluster buffers, owns temporary empty transactions for recursive buffer-lock detection, and tracks in-memory cursor state such as `startino`, `lastino`, `nr_recs`, and abort flags.

Dependencies and integration: used by bulkstat/inumbers, scrub-like scans, and other inode iteration users. It depends on perag iteration, inobt btree cursors, transaction buffer handling, parallel work control, inode buffer ops, and corruption health marking.

Risks and test signals: key risks are deadlocks if callbacks run under btree cursor/AGI locks, duplicate or regressive inode records, excessive prefetch memory, start-in-middle masking, abort handling, and threaded perag lifetime. Tests should cover starts at zero and mid-chunk, same-AG walks, sparse/empty chunks, callback `-ECANCELED`, corrupt/non-monotonic inobt records, threaded and polled walks, and prefetch bounds.
