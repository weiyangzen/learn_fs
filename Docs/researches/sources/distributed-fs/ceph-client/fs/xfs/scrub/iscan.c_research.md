<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/iscan.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/iscan.c

Purpose: Provides a live inode scanner for online scrub/repair tasks that must walk all allocated inodes while concurrent allocation, deletion, and metadata updates continue.

Important APIs, types, and functions: Exports `xchk_iscan_start()`, `xchk_iscan_finish_early()`, `xchk_iscan_iter()`, `xchk_iscan_iter_finish()`, `xchk_iscan_teardown()`, `xchk_iscan_mark_visited()`, and `xchk_iscan_want_live_update()`. Internal helpers advance through inobt records under AGI protection, batch iget up to one inode chunk, maintain skipped-inode masks, retry inodegc races, and choose a rotor start AG.

Control flow: Start chooses a rotating start inode, initializes cursor and visited state, and stores iget timeout policy. Iteration first returns already batched inodes; otherwise it advances under AGI lock to the next allocated inode, moves cursor and visited range across sparse inode address gaps, igets the first inode with no-retry/dontcache flags, optionally batches consecutive allocated inodes, and records unallocated inodes in the batch as skipped. Callers mark each inode visited after scanning under sufficient locks. `xchk_iscan_want_live_update()` tells hook code whether an inode update lies in the visited range, accounts for wraparound, and treats skipped newly allocated inodes as requiring live updates.

State and persistence: All state is transient in `struct xchk_iscan`: start/cursor/visited inode numbers, opstate bits, retry deadline, batch array, and skipped mask, guarded by a mutex for hook-visible fields. No on-disk state is modified.

Dependencies and integration points: Depends on inobt lookup, AGI locking, `xfs_iget`, inodegc push/flush, perag references, scrub transactions, and tracepoints. Used by parent finding, inode mode recovery, and any repair that builds a new live index with metadata update hooks.

Risks and test signals: Correctness depends on never missing updates for inodes already scanned or skipped during a batch. Test wraparound scans, empty AG gaps, sparse inode address spaces, trylock AGI mode under rename/AGI lock pressure, inodegc races returning ENOENT/EAGAIN, EBUSY timeout behavior, abort bit handling, batch skipping for newly allocated inodes, live-update predicates before start/after finish, and teardown releasing batched inode references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/iscan.c -->
