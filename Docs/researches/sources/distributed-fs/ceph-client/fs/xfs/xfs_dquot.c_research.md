# sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot.c

Purpose: Implements XFS dquot lifetime, radix-tree cache lookup, on-disk dquot block allocation/read/initialization, quota timer and limit adjustment, flushing, attached-buffer handling for AIL pushes, locking helpers, and slab lifecycle.

Important APIs, types, and functions: Defines `xfs_dqtrx_cache` and `xfs_dquot_cache`. Key public functions include dquot destroy, limit/timer adjustment, dquot block initialization, preallocation threshold setup, `xfs_qm_dqget*()` lookup variants, `xfs_qm_dqrele()`, `xfs_buf_dquot_iodone()`, buffer attach/use/detach helpers, `xfs_qm_dqflush()`, `xfs_dqlock2()`, `xfs_dqlockn()`, `xfs_qm_init()`, and `xfs_qm_exit()`.

Control flow: Lookup validates quota enablement, checks the radix-tree cache, reads or allocates disk chunks on miss, converts disk records, and inserts with duplicate retry. Inode lookup drops and reacquires ILOCK around disk I/O and rechecks races. Disk allocation maps quota inode space, initializes a full dquot chunk, and logs or orders the buffer depending on quotacheck. Flush validates counters, writes the disk record, stamps LSN/CRC, attaches the log item to the buffer, and lets iodone clear AIL state and unlock flushing.

State and persistence: In-core dquots track ids, type, flags, usage/reservation counters, timers, preallocation watermarks, cache refs, LRU state, log item, flush completion, pin count, and backing buffer location. Persistent records live in quota inodes as `xfs_dqblk` chunks with magic, id, type, UUID, LSN, and CRC.

Dependencies and integration points: Integrates with quota manager state, quota inodes, bmap allocation, transactions/defer ops, AIL, buffer verifiers, log force, list_lru reclaim, health reporting, lockdep classes, and inode uid/gid/projid lookup.

Risks and test signals: Risks include lock deadlocks, cache duplicate races, quotaoff during I/O, allocation failure leaving buffers locked, timer/grace corruption, CRC/LSN mistakes, and attached-buffer leaks. Test quotaon/off races, quotacheck, allocation holes, shrinker pressure, shutdown during dqflush, bigtime, v4 group/project switching, corrupt quota blocks, and `Q_GETNEXTQUOTA`.
