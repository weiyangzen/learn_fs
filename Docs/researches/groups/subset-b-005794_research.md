# subset-b-005794 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_item.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_item.c

Purpose: Implements XFS buffer log items, the transaction-log objects that describe dirty metadata buffer regions, pin buffer lifetime during CIL/log commit, push dirty buffers from the AIL, and handle stale/cancelled metadata buffers.

Important APIs, types, and functions: Defines `xfs_buf_item_cache` and item ops for size, format, pin, unpin, release, commit, and push. Public entry points are `xfs_buf_item_init()`, `xfs_buf_item_put()`, `xfs_buf_item_log()`, `xfs_buf_item_dirty_format()`, `xfs_buf_item_done()`, `xfs_buf_log_check_iovec()`, and `xfs_buf_inval_log_space()`. Internal helpers manage per-map `xfs_buf_log_format` allocation, bitmap sizing, chunk-copy iovecs, stale completion, and dirty bitmap updates.

Control flow: `xfs_buf_item_init()` creates one format record per buffer map, computes dirty bitmap sizes in `XFS_BLF_CHUNK` units, attaches the item to `bp->b_log_item`, and holds the buffer. Logging marks byte ranges in the segment bitmap; formatting emits a buffer-format record plus one data iovec per contiguous dirty chunk, or only cancel format records for stale buffers. Pinning takes both buffer and BLI references; unpin drops refs, wakes buffer waiters, finishes stale buffers, or hands aborted buffers to I/O failure handling. AIL push tries to lock and delwri-queue the buffer.

State and persistence: Persistent log state is `xfs_buf_log_format` plus dirty buffer chunks. In-core state includes `bli_flags`, `bli_refcount`, `bli_format_count`, per-segment bitmaps, and the buffer attachment. Stale buffers log `XFS_BLF_CANCEL`, while inode buffers can log `XFS_BLF_INODE_BUF` to constrain recovery to unlinked-list fields. `iop_committed` preserves old LSNs for newly allocated inode buffers until full inode images reach disk.

Dependencies and integration points: Tied to `xfs_trans`, CIL vector formatting, AIL writeback, buffer cache locking/refcounts, buffer verifiers, inode and dquot iodone paths, log recovery cancel records, and tracepoints.

Risks and test signals: Risks are refcount/lifetime races between unpin, AIL, shutdown, and stale completion; dirty bitmap off-by-one errors for discontiguous buffers; incorrect ordered-buffer accounting; verifier failures late in transaction commit; and stale inode buffer cleanup leaks. Test with metadata updates crossing segment boundaries, repeated relogging, forced shutdown during checkpoint completion, inode allocation/free recovery, quota buffers, discontiguous buffer logging, AIL pressure, and DEBUG_EXPENSIVE verifier checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_item.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_item.h

Purpose: Declares the in-core buffer log item structure, BLI flags, and buffer-log helper APIs shared by XFS transactions, buffer I/O completion, quota code, and recovery.

Important APIs, types, and functions: Defines flags `XFS_BLI_HOLD`, `DIRTY`, `STALE`, `LOGGED`, `INODE_ALLOC_BUF`, `STALE_INODE`, `INODE_BUF`, and `ORDERED`; `XFS_BLI_FLAGS` for tracing; and `struct xfs_buf_log_item` containing common `xfs_log_item`, attached `xfs_buf`, flags, recursion count, refcount, format array, and embedded single format. Declares `xfs_buf_item_init()`, `xfs_buf_item_done()`, `xfs_buf_item_put()`, `xfs_buf_item_log()`, `xfs_buf_item_dirty_format()`, `xfs_buf_inode_iodone()`, optional `xfs_buf_dquot_iodone()`, `xfs_buf_iodone()`, `xfs_buf_log_check_iovec()`, and `xfs_buf_inval_log_space()`.

Control flow: The header is consumed by transaction code to attach, dirty, hold, release, or finish buffer items and by iodone paths to dispatch attached inode/dquot completions. The `CONFIG_XFS_QUOTA` wrapper makes quota iodone a no-op when quota support is absent.

State and persistence: Defines only in-memory item state and log-format pointers; persistence is represented indirectly by `xfs_buf_log_format` records emitted by `xfs_buf_item.c`.

Dependencies and integration points: Depends on XFS log-format definitions and buffer/mount forward declarations. It is part of the transaction/log ABI for metadata buffers.

Risks and test signals: Risks are flag semantic drift between transaction, recovery, and trace code, structure layout assumptions, and missing quota stubs in non-quota builds. Test all XFS quota/non-quota configurations and trace formatting for every BLI flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_item_recover.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_item_recover.c

Purpose: Replays buffer log items during XFS log recovery, including freed-buffer cancellation, inode-buffer special handling, quota buffer suppression after quotaoff, metadata LSN skip logic, verifier attachment, and recovery-time growfs superblock updates.

Important APIs, types, and functions: Defines `struct xfs_buf_cancel`, cancel-table helpers `xlog_is_buffer_cancelled()`, `xlog_alloc_buf_cancel_table()`, `xlog_free_buf_cancel_table()`, and debug `xlog_check_buf_cancel_table()`. Recovery item ops are `xlog_buf_item_ops` with reorder, readahead, pass1, and pass2 callbacks. Core helpers include `xlog_recover_validate_buf_type()`, `xlog_recover_do_reg_buffer()`, `xlog_recover_do_dquot_buffer()`, `xlog_recover_do_inode_buffer()`, `xlog_recover_do_primary_sb_buffer()`, and `xlog_recover_get_buf_lsn()`.

Control flow: Pass 1 records all `XFS_BLF_CANCEL` buffers in a 64-bucket cancel table, with refcounts for repeated cancellations. Pass 2 skips cancelled items until the last cancel record is consumed, reads uncancelled buffers, extracts any on-disk metadata LSN, and skips replay if the buffer is already newer than the transaction. Regular recovery copies logged dirty chunks by bitmap; inode-buffer recovery copies only `di_next_unlinked` fields and recalculates inode CRCs; dquot-buffer recovery skips types disabled by quotaoff records; primary superblock recovery updates in-core superblock, device sizes, perag, and rtgroup structures.

State and persistence: Mutates on-disk metadata buffers through delwri recovery writes and marks them `_XBF_LOGRECOVERY`. Cancel records are in-memory recovery state only. Recovered CRC filesystems get buffer ops and temporary BLIs so write verifiers can stamp correct LSNs. Realtime superblock mirrors are updated when present.

Dependencies and integration points: Integrates with log recovery reorder queues, buffer cache, metadata verifiers for all major XFS block types, quotaoff recovery, superblock/perag/rtgroup initialization, inode unlinked-list replay, and AIL item cleanup.

Risks and test signals: Risks include replaying stale freed metadata over user data, skipping replay due to wrong LSN/UUID interpretation, missing verifier attachment after readahead, corrupting inode buffers by replaying full inode data, and mishandling growfs/rtgroup changes. Test interrupted recovery, buffer reuse after cancellation, CRC and non-CRC filesystems, quotaoff with pending dquot buffers, inode unlinked-list recovery, growfs replay, rt metadata, unknown magic blocks, and corrupted log item sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_item_recover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_mem.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_mem.c

Purpose: Implements memory-backed XFS buffer targets (`xmbuf`) for online fsck and other ephemeral ordered recordsets that want normal buffer-cache and btree machinery without a block device.

Important APIs, types, and functions: Provides `xmbuf_alloc()`, `xmbuf_free()`, `xmbuf_map_backing_mem()`, `xmbuf_verify_daddr()`, `xmbuf_finalize()`, and `xmbuf_trans_bdetach()`. Internal state uses an unlinked shmem file stored in `xfs_buftarg.bt_file`, a private inode lock class, and PAGE_SIZE block geometry.

Control flow: Allocation creates an anonymous shmem kernel file, marks its inode lock private for lockdep, forces non-highmem page-cache allocation, expands `i_size` to `s_maxbytes`, initializes an `xfs_buftarg` with no block device, and calls `xfs_init_buftarg()`. Mapping validates single-map PAGE_SIZE buffers at page-aligned daddrs, obtains a shmem folio with `shmem_get_folio()`, checks writeback errors, marks the folio dirty to resist reclaim, and points `bp->b_addr` directly at the folio. Finalization truncates stale folios or runs the buffer verifier. Detach clears BLI dirty/logged/stale flags and repeatedly detaches from a transaction.

State and persistence: Data persists only in the private shmem page cache until `xmbuf_free()`. There is no block device, journal persistence, or userspace file descriptor. Stale buffers discard backing folios with `shmem_truncate_range()`.

Dependencies and integration points: Depends on tmpfs/shmem, XFS buffer targets, buffer items, transaction detach helpers, verifiers, tracepoints, and `CONFIG_XFS_MEMORY_BUFS`.

Risks and test signals: Risks are accidental userspace exposure, highmem folio assumptions, non-page-sized buffer misuse, stale folio leaks, verifier false positives on ephemeral data, and transaction detach loops if flags are inconsistent. Test online repair btrees backed by xmbuf, stale buffer recycling, page-cache writeback-error injection, lockdep with private shmem inodes, and non-memory buftarg rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_mem.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_mem.h

Purpose: Declares the memory-buffer target interface and fixed PAGE_SIZE block geometry used by `xfs_buf_mem.c`.

Important APIs, types, and functions: Defines `XMBUF_BLOCKSIZE` and `XMBUF_BLOCKSHIFT`. Under `CONFIG_XFS_MEMORY_BUFS`, `xfs_buftarg_is_mem()` identifies buftargs with `bt_bdev == NULL` and the header declares allocation, free, daddr verification, transaction detach, and finalize helpers. Without the config, most helpers compile to false/no-op style stubs; `xmbuf_map_backing_mem()` remains declared for callers guarded elsewhere.

Control flow: Callers use the inline predicate before taking memory-buftarg paths in buffer mapping, validation, or teardown. Config stubs keep non-memory-buffer builds compiling without carrying runtime behavior.

State and persistence: No state is stored here; it defines the memory-backed buftarg contract that data lives in page cache and block size equals PAGE_SIZE.

Dependencies and integration points: Shared by buffer cache, online fsck support, transaction code, and memory buftarg implementation.

Risks and test signals: Risks are configuration mismatches and callers invoking xmbuf operations without checking the predicate. Test `CONFIG_XFS_MEMORY_BUFS=y/n` builds and verify no block-device paths treat `bt_bdev == NULL` as a real device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dahash_test.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_dahash_test.c

Purpose: Provides a boot/init-time regression test for XFS directory/attribute name hashing, covering both normal `xfs_da_hashname()` and ASCII case-insensitive `xfs_ascii_ci_hashname()`.

Important APIs, types, and functions: Contains a 4096-byte aligned `__initdata` random byte buffer, an array of 100 `struct dahash_test` cases with start offsets, lengths, expected normal hashes, and expected ASCII-CI hashes, and the exported init function `xfs_dahash_test()`.

Control flow: `xfs_dahash_test()` iterates every test case, hashes the selected byte slice directly with `xfs_da_hashname()`, then constructs an `xfs_name` and hashes it with `xfs_ascii_ci_hashname()`. Mismatches increment an error counter; any mismatch logs a kernel error and returns `-ERANGE`, otherwise it returns zero.

State and persistence: Test vectors are `__initdata` and discarded after init. The file has no filesystem persistence and mutates no runtime XFS state.

Dependencies and integration points: Depends on directory/attribute hash helpers from `xfs_dir2_priv.h` and is declared by `xfs_dahash_test.h`. It is a low-cost internal test signal for hash algorithm stability.

Risks and test signals: Risks are accidental hash ABI changes, endian/char signedness differences, and missed coverage outside the fixed random cases. Test by enabling the init self-test on multiple architectures and intentionally changing hash code to confirm the test fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dahash_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dahash_test.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_dahash_test.h

Purpose: Declares the XFS directory/attribute hash self-test entry point.

Important APIs, types, and functions: Exposes `int xfs_dahash_test(void);` to init or test wiring.

Control flow: There is no local control flow; callers invoke `xfs_dahash_test()` and treat nonzero return as failure.

State and persistence: No state or persistence.

Dependencies and integration points: Paired with `xfs_dahash_test.c`; included by code that runs XFS self-tests.

Risks and test signals: Risk is mostly stale declaration if the self-test wiring changes. Test by building configurations that include the hash test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dahash_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dir2_readdir.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_dir2_readdir.c

Purpose: Implements XFS directory iteration for shortform, block, leaf, and node directory formats, translating XFS directory cookies and filetype metadata into VFS `dir_context` emissions.

Important APIs, types, and functions: Exports `xfs_readdir()` and `xfs_dir3_get_dtype()`. Internal readers are `xfs_dir2_sf_getdents()`, `xfs_dir2_block_getdents()`, `xfs_dir2_leaf_readbuf()`, and `xfs_dir2_leaf_getdents()`. Uses `xfs_dir2_dataptr`/byte/db conversions, `dir_emit()`, `xfs_dir2_namecheck()`, and `xfs_dirattr_mark_sick()`.

Control flow: `xfs_readdir()` rejects shutdown or zapped forks, sets up `xfs_da_args`, and chooses a reader based on inode fork format and `xfs_dir2_format()`. Shortform emits synthetic `.` and `..` then inline entries. Block directories read the single block, drop the data-map lock before scanning, skip unused records, and emit live entries. Leaf/node directories scan mapped data blocks below `XFS_DIR2_LEAF_OFFSET`, maintain a readahead cursor, skip holes and unused records, update `ctx->pos` to stable cookies, and release buffers between blocks.

State and persistence: Mutates only `ctx->pos` and user-visible directory output. Persistent directory contents are read from inode local data or directory data buffers and are not changed. Invalid names mark the directory data fork sick for health tracking.

Dependencies and integration points: Integrates with VFS `iterate_dir`, XFS inode I/O/data-map locking, directory bmap extent lookup, dir buffer verifiers, block plugging readahead, health reporting, stats, and tracepoints.

Risks and test signals: Risks include cookie truncation/masking, skipped or repeated entries around holes, lock mode leaks, invalid name handling, readahead verifier gaps, and bad shortform offsets. Test `getdents` on all directory formats, tiny buffers, seekdir/telldir cookies, concurrent mutation under IOLOCK rules, corrupt names, sparse large directories, ftype disabled/enabled filesystems, and shutdown/zapped-fork paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dir2_readdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_discard.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_discard.c

Purpose: Implements online discard and FITRIM for XFS data and realtime devices while avoiding long allocation-group locks by batching free-space discovery and marking extents busy during discard.

Important APIs, types, and functions: Defines global `xfs_discard_wq`, public `xfs_discard_extents()` and `xfs_ioc_trim()`, data-device helpers `xfs_trim_gather_extents()`, `xfs_trim_perag_extents()`, and `xfs_trim_datadev_extents()`, plus realtime helpers under `CONFIG_XFS_RT` for rtdev and rtgroup scans. Uses `struct xfs_trim_cur`, `struct xfs_trim_rtdev`, `struct xfs_trim_rtgroup`, and `XFS_DISCARD_MAX_EXAMINE`.

Control flow: FITRIM validates privilege, discard support, norecovery state, user range, granularity, and min length. Data-device trim converts byte ranges to daddrs, walks perags, repeatedly forces the log, locks the AGF, scans bnobt or cntbt records in bounded batches, skips busy or too-small extents, inserts selected extents into the busy-under-discard list, drops locks, and issues asynchronous discard bios. Completion runs through `xfs_discard_wq` to clear busy extents outside IRQ context. Realtime code trims either legacy rtbitmap extents synchronously or rtgroups through the same busy extent machinery.

State and persistence: Does not change allocation btrees directly. It temporarily adds busy extent records that prevent allocation until discard completion clears them. User-visible `fstrim_range.len` is clamped to the filesystem range on success.

Dependencies and integration points: Uses block discard APIs, XFS log force, allocation btrees, perag/rtgroup iteration, busy extent tracking, realtime bitmap queries, freezer/signal checks, user-copy helpers, and tracepoints.

Risks and test signals: Risks are discard of recently freed but uncommitted space, busy extent leaks after bio errors, excessive AGF lock holds, range conversion overflow, realtime/data device boundary mistakes, and poor behavior on slow discard devices. Test FITRIM with sparse ranges, minlen/granularity edges, concurrent allocation/free, signal/freezer interruption, no-discard devices, norecovery mounts, realtime devices with and without rtgroups, discard bio failures, and ceph/RBD-like slow discard latency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_discard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_discard.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_discard.h

Purpose: Declares XFS discard and FITRIM entry points.

Important APIs, types, and functions: Forward-declares `struct fstrim_range`, `struct xfs_mount`, and `struct xfs_busy_extents`; declares `xfs_discard_extents()` and `xfs_ioc_trim()`.

Control flow: Callers submit prepared busy extent lists to `xfs_discard_extents()` or service userspace FITRIM through `xfs_ioc_trim()`.

State and persistence: No state is defined here; the implementation manages transient busy extents and discard bios.

Dependencies and integration points: Included by ioctl, extent-busy, and discard implementation code.

Risks and test signals: Risks are declaration drift or missing userspace pointer annotation. Test build coverage with realtime and non-realtime configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_discard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot.c

Purpose: Implements XFS in-core dquot lifetime, cache lookup, on-disk dquot block allocation/read/initialization, quota limit/timer adjustment, dquot flushing, attached-buffer handling for AIL pushes, locking helpers, and quota slab lifecycle.

Important APIs, types, and functions: Defines caches `xfs_dqtrx_cache` and `xfs_dquot_cache`. Public routines include `xfs_qm_dqdestroy()`, `xfs_qm_adjust_dqlimits()`, `xfs_dquot_set_timeout()`, `xfs_dquot_set_grace_period()`, `xfs_qm_adjust_dqtimers()`, `xfs_qm_init_dquot_blk()`, `xfs_dquot_set_prealloc_limits()`, `xfs_qm_dqget()`, `xfs_qm_dqget_inode()`, `xfs_qm_dqget_next()`, `xfs_qm_dqget_uncached()`, `xfs_qm_dqrele()`, `xfs_buf_dquot_iodone()`, `xfs_dquot_attach_buf()`, `xfs_dquot_use_attached_buf()`, `xfs_dquot_detach_buf()`, `xfs_qm_dqflush()`, `xfs_dqlock2()`, `xfs_dqlockn()`, `xfs_qm_init()`, and `xfs_qm_exit()`.

Control flow: Dquot lookup first validates quota type enablement, checks the radix-tree cache under `qi_tree_lock`, reads or allocates on-disk chunks on miss, converts disk records into in-core counters, and inserts with duplicate-retry handling. Inode attachment can drop and reacquire the inode ILOCK around disk I/O and rechecks races. Disk allocation maps quota inode space, initializes a full dquot chunk, orders or logs the buffer depending on quotacheck state, and returns a locked buffer. Flush takes the dquot flush lock, validates counters and timers, writes the disk record, stamps LSN/CRC, attaches the dquot log item to the buffer, and lets iodone remove AIL state and unlock flushing.

State and persistence: In-core dquots track ids, type, qflags, usage/reservation counters, timers, speculative preallocation watermarks, lockref cache refs, LRU state, log item, flush completion, pin count, and backing buffer location. Persistent dquot records live in quota inodes as chunks of `struct xfs_dqblk` with magic, id, type, optional bigtime, UUID, LSN, and CRC. Health bits are marked sick on quota metadata corruption.

Dependencies and integration points: Integrates with quota manager state, quota inodes, bmap allocation, transactions/defer ops, AIL, buffer verifiers, log force, list_lru reclaim, health reporting, lockdep classes, and inode uid/gid/projid lookup.

Risks and test signals: Risks include lock-order deadlocks, cache duplicate races, quotaoff during disk I/O, allocation transaction failure leaving locked buffers, wrong v4 root group/project type handling, timer/grace corruption, CRC/LSN mistakes, attached-buffer leaks, and AIL tail advancement before flushed dquots reach disk. Test quotaon/off races, quotacheck, dquot allocation holes, cache shrinker pressure, flush under AIL pressure, shutdown during dqflush, bigtime and non-bigtime dquots, project/group switching on v4, corrupt quota blocks, and `Q_GETNEXTQUOTA` scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot.h

Purpose: Defines the in-core XFS dquot data model, quota resource counters, preallocation thresholds, lock helpers, type/enforcement predicates, and public dquot APIs.

Important APIs, types, and functions: Defines low-space indexes, `struct xfs_dquot_res`, `xfs_dquot_res_over_limits()`, `struct xfs_dquot_pre`, and `struct xfs_dquot`. Inline helpers include `xfs_dqflock()`, `xfs_dqflock_nowait()`, `xfs_dqfunlock()`, `xfs_dquot_type()`, `xfs_this_quota_on()`, `xfs_inode_dquot()`, `xfs_dquot_is_enforced()`, `xfs_dquot_lowsp()`, and `xfs_qm_dqhold()`. Declares lookup, flush, locking, disk conversion, timer, preallocation, and buffer-attach functions.

Control flow: Callers use type predicates before lookup/enforcement, completion helpers around flush serialization, and lock helpers for single or multiple dquot transactions. Inline inode-dquot access deliberately returns NULL for metadata directory inodes.

State and persistence: `struct xfs_dquot` mirrors persistent quota limits, usage counters, and timers while adding reservation counters, file offsets, backing daddr, log item, LRU/cache refs, flush serialization, and pin wait state.

Dependencies and integration points: Used by quota accounting, transaction reservation code, inode ownership changes, dquot log items, AIL writeback, and quota ioctl implementations.

Risks and test signals: Risks are incorrect enforcement predicates, reservation/count confusion, low-space threshold underflow with zero hard limits, and lock nesting mistakes. Test multi-dquot transaction locking, quota disabled/enforced permutations, metadata inode exclusion, and low-space preallocation decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot_item.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot_item.c

Purpose: Implements the XFS dquot log item used to journal individual dquot updates and coordinate pinning, transaction release, AIL push, precommit buffer attachment, and debug validation.

Important APIs, types, and functions: Provides `xfs_qm_dquot_logitem_init()` and item ops for size, format, pin, unpin, release, committing, precommit, and push. Internal helpers include `xfs_qm_dquot_logitem_size()`, `xfs_qm_dquot_logitem_format()`, `xfs_qm_dqunpin_wait()`, `xfs_qm_dquot_logitem_push()`, and DEBUG_EXPENSIVE precommit verification.

Control flow: Formatting emits a `xfs_dq_logformat` plus a serialized `xfs_disk_dquot`. Pin/unpin manipulate `q_pincount` and wake waiters. Release unlocks the dquot at transaction completion. Precommit verifies the disk image when enabled and attaches the backing buffer before commit so AIL push can flush from reclaim-sensitive contexts. AIL push skips pinned or locked dquots, acquires qlock and dqflock, uses the attached buffer, calls `xfs_qm_dqflush()`, and queues the buffer for delwri.

State and persistence: The log item serializes dquot id, block, offset, length, and complete disk dquot contents. In-core dirty state is split between dquot flags and `qli_dirty`/attached `li_buf` protected by `qli_lock`.

Dependencies and integration points: Depends on dquot conversion/verification, transaction log item framework, AIL push protocol, attached-buffer helpers in `xfs_dquot.c`, and log force for unpin waits.

Risks and test signals: Risks include flushing without an attached buffer, losing dirty state after relogging, qlock/dqflock ordering bugs, AIL push races with reclaim, and logging corrupt quota records. Test quota updates under memory reclaim, concurrent relog and dqflush, shutdown after commit before flush, DEBUG_EXPENSIVE dquot verification, and pinned dquot log-force behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot_item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot_item.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot_item.h

Purpose: Declares the in-core dquot log item that ties an XFS dquot to transaction logging and AIL flush state.

Important APIs, types, and functions: Defines `struct xfs_dq_logitem` with common `xfs_log_item`, back pointer to `xfs_dquot`, `qli_flush_lsn`, `qli_lock`, and `qli_dirty`. Declares `xfs_qm_dquot_logitem_init()`.

Control flow: The log item is initialized when a dquot is allocated and later used by transaction code for logging and by flush iodone paths for AIL cleanup.

State and persistence: Stores transient flush LSN and dirty/attached-buffer coordination state; persistent payload is produced by `xfs_dquot_item.c`.

Dependencies and integration points: Included by dquot, quota transaction, and log item code.

Risks and test signals: Risks are races around `qli_dirty` and `li_buf` if callers bypass `qli_lock`. Test relogging while dqflush I/O is in flight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot_item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot_item_recover.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot_item_recover.c

Purpose: Replays dquot and quotaoff log items during recovery, ensuring quotaoff suppresses obsolete quota records and individual dquot log payloads are validated before writing to quota metadata.

Important APIs, types, and functions: Defines recovery ops `xlog_dquot_item_ops` and `xlog_quotaoff_item_ops`. Core callbacks are `xlog_recover_dquot_ra_pass2()`, `xlog_recover_dquot_commit_pass2()`, and `xlog_recover_quotaoff_commit_pass1()`.

Control flow: Quotaoff pass1 records disabled user, group, or project quota types in `log->l_quotaoffs_flag`. Dquot pass2 exits if quotas are off, validates the dquot payload buffer and quota type, skips any type disabled by quotaoff, verifies the logged dquot id/type, reads the containing dquot buffer with verifier ops, skips replay if the on-disk CRC dquot LSN is newer, copies the disk dquot into place, updates CRC, verifies the recovered block, and queues it for recovery writeback. Readahead mirrors these checks before prefetching the dquot buffer.

State and persistence: Mutates quota inode dquot blocks during recovery and sets `_XBF_LOGRECOVERY`. Quotaoff state is transient log recovery state controlling replay suppression.

Dependencies and integration points: Depends on quota flags supplied at mount, dquot verifiers/checksums, buffer recovery delwri lists, quotaoff log formats, and XFS log recovery item registration.

Risks and test signals: Risks include replaying dquots after quotaoff, accepting truncated or corrupt log payloads, wrong LSN skip behavior, and checksum mismatch after copy. Test crashes around quotaoff, dquot updates with CRC/non-CRC filesystems, corrupted dquot log vectors, disabled quota support, and repeated recovery interruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot_item_recover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_drain.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_drain.c

Purpose: Implements a passive drain counter used to let online fsck and similar exclusive metadata checkers wait for deferred work intents targeting an allocation or realtime group to finish.

Important APIs, types, and functions: Defines static key `xfs_defer_drain_waiter_gate` and functions `xfs_defer_drain_wait_disable()`, `xfs_defer_drain_wait_enable()`, `xfs_defer_drain_init()`, `xfs_defer_drain_free()`, `xfs_group_intent_get()`, `xfs_group_intent_put()`, `xfs_group_intent_drain()`, and `xfs_group_intent_busy()`. Internal helpers increment/decrement atomic counts and wake waiters.

Control flow: Writers call `xfs_group_intent_get()` to obtain a passive group reference and increment the group drain count before queuing deferred metadata updates. Completion calls `xfs_group_intent_put()`, which decrements and wakes waiters if the count reaches zero and the static key indicates waiters exist. Scrub/repair calls `xfs_group_intent_drain()` without holding locks that would block deferred work.

State and persistence: Maintains transient atomic intent counts and waitqueues in `xfs_group`. No on-disk state is changed.

Dependencies and integration points: Depends on group lookup/refcounting, deferred work lifetime rules, waitqueues, static branches, tracepoints, and online fsck synchronization.

Risks and test signals: Risks include missed wakeups, unbalanced intent get/put, enabling/disabling the static key while holding reclaim-sensitive locks, and deadlock if drain waiters hold AG/rt metadata locks needed by completions. Test scrub versus long deferred chains, cancellation paths, signals during wait, lockdep, and intent leak assertions at group teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_drain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_drain.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_drain.h

Purpose: Defines the optional deferred-intent drain interface used to coordinate online fsck with in-flight group metadata intent chains.

Important APIs, types, and functions: Under `CONFIG_XFS_DRAIN_INTENTS`, defines `struct xfs_defer_drain` with `dr_count` and `dr_waiters`, declares init/free, waiter gate, group intent get/put, drain, and busy helpers. Without the config, it defines an empty struct and maps group get/put to normal group references.

Control flow: The documented protocol requires intent creators to increment when items are added to a transaction and not decrement until finish or cancel. Drain callers wait only after acquiring the higher-level locks needed for their check but without locks that prevent intent completion.

State and persistence: Defines transient in-memory counters only.

Dependencies and integration points: Used by deferred work manager, allocation group/realtime group code, and online scrub/repair.

Risks and test signals: Risks are config-dependent behavior differences and misuse of the drain as a hard lock. Test `CONFIG_XFS_DRAIN_INTENTS=y/n` builds and scrub collision scenarios with BUI/RUI-style chained intents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_drain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_error.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_error.c

Purpose: Provides XFS corruption/error reporting helpers and, in DEBUG builds, sysfs-controlled random error injection tags and delay injection.

Important APIs, types, and functions: DEBUG code builds errortag default/name tables from `xfs_errortag.h`, sysfs attributes under `m_errortag_kobj`, and functions `xfs_errortag_init()`, `xfs_errortag_del()`, `xfs_errortag_test()`, `xfs_errortag_delay()`, `xfs_errortag_add()`, `xfs_errortag_add_name()`, `xfs_errortag_copy()`, and `xfs_errortag_clearall()`. Always-built reporting functions are `xfs_error_report()`, `xfs_corruption_error()`, `xfs_buf_corruption_error()`, `xfs_buf_verifier_error()`, `xfs_verifier_error()`, and `xfs_inode_verifier_error()`.

Control flow: Errortag sysfs store accepts numeric factors or `default`, updates `mp->m_errortag[]`, and tests inject when random selection hits zero; delay tags sleep via `mdelay()`. Reporting functions gate stack traces and hex dumps by global `xfs_error_level`, stamp buffer I/O errors for verifier failures, tag alerts with panic tags, and tell operators to unmount and run repair.

State and persistence: Debug errortag values are in-memory per mount and exposed through sysfs. Error reporting mutates buffer error state but does not persist metadata; it emits logs and optional dumps.

Dependencies and integration points: Integrates with XFS sysfs, mount objects, panic-tag alerting, random number generation, buffer and inode verifiers, global error level sysctl, and stack/hex dump helpers.

Risks and test signals: Risks include overly noisy or insufficient diagnostics, missing buffer error stamping, unsafe delay injection contexts, stale errortag tables, and debug-only behavior assumptions. Test verifier CRC/corruption paths, sysfs errortag store/show, panic mask behavior, error-level dump thresholds, and non-DEBUG stub behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_error.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_error.h

Purpose: Declares XFS error/corruption reporting APIs, debug errortag injection hooks, error-level constants, corruption dump length, and panic tag bitmasks/string mappings.

Important APIs, types, and functions: Declares reporting functions for generic errors, corruption, buffer corruption/verifier failures, and inode verifier failures. Defines `XFS_ERROR_REPORT()` and `XFS_CORRUPTION_ERROR()` macros, `XFS_ERRLEVEL_OFF/LOW/HIGH`, `XFS_CORRUPTION_DUMP_LEN`, DEBUG errortag APIs and stubs, `XFS_TEST_ERROR()`, `XFS_ERRORTAG_DELAY()`, panic tags such as `XFS_PTAG_VERIFIER_ERROR`, `XFS_PTAG_MASK`, and `XFS_PTAG_STRINGS`.

Control flow: Macros capture source file, line, and return address for diagnostics. DEBUG stubs compile injection out cleanly when disabled.

State and persistence: No state is stored here; panic tags and errortag hooks control reporting behavior elsewhere.

Dependencies and integration points: Included broadly by XFS verifiers, metadata code, and sysfs/sysctl plumbing.

Risks and test signals: Risks are panic tag ABI drift, macro misuse with wrong buffer sizes, and disabled DEBUG callers expecting injection. Test all panic tag string mappings and DEBUG/non-DEBUG builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_exchmaps_item.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_exchmaps_item.c

Purpose: Implements log intent/done items for atomic file mapping exchange operations, including deferred operation integration, relogging, cancellation, and recovery of unfinished exchanges.

Important APIs, types, and functions: Defines caches `xfs_xmi_cache` and `xfs_xmd_cache`, XMI/XMD item ops, public `xfs_exchmaps_defer_add()`, defer type `xfs_exchmaps_defer_type`, and recovery ops `xlog_xmi_item_ops` and `xlog_xmd_item_ops`. Key helpers include `xfs_xmi_init()`, `xfs_xmi_release()`, `xfs_exchmaps_create_intent()`, `xfs_exchmaps_create_done()`, `xfs_exchmaps_finish_item()`, `xfs_xmi_validate()`, `xfs_xmi_item_recover_intent()`, `xfs_exchmaps_recover_work()`, and `xfs_exchmaps_relog_intent()`.

Control flow: Creating an intent logs two inode numbers/generations, start offsets, block count, sizes, and supported flags into an XMI. Done items point back to the XMI id and release it when committed. Deferred finish calls `xfs_exchmaps_finish_one()` and retains the item on `-EAGAIN` so the operation can be relogged after other deferred work. Recovery reconstructs XMI items in the AIL from log records, cancels them when matching XMD records appear, validates feature/flags/inodes/extents, reopens both inodes by handle with generation checks, estimates resources, locks both inodes, ensures reflink/extent-count prerequisites, finishes the intent, and captures/commits deferred work.

State and persistence: Persistent log records are XMI redo records and XMD completion records. In-core XMI uses a two-reference lifecycle so commit/unpin and done processing can race safely. Recovery state is stored in deferred pending items until the exchange completes.

Dependencies and integration points: Integrates with `xfs_defer`, exchange-range/exchange-maps engines, bmap/reflink setup, inode cache and recovery iget, transaction reservation, log recovery intent tracking, AIL matching, and tracepoints.

Risks and test signals: Risks include leaked or prematurely freed intents, replaying exchanges for stale inode generations, accepting invalid flags or extents, deadlocks in two-inode locking, log tail pinning if relogging is wrong, and incomplete recovery after crash mid-exchange. Test exchange-range crashes before and after XMD commit, generation mismatch, unsupported feature flags, multi-transaction large exchanges, reflink/extcount upgrades, recovery corruption injection, and cancellation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_exchmaps_item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_exchmaps_item.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_exchmaps_item.h

Purpose: Declares the XFS exchange-mapping intent (`XMI`) and done (`XMD`) log item structures and the deferred-add entry point.

Important APIs, types, and functions: Defines `struct xfs_xmi_log_item` with common log item, refcount, and `xfs_xmi_log_format`; `struct xfs_xmd_log_item` with common log item, pointer to the intent item, and `xfs_xmd_log_format`; declares caches `xfs_xmi_cache` and `xfs_xmd_cache`; forward-declares `struct xfs_exchmaps_intent`; and declares `xfs_exchmaps_defer_add()`.

Control flow: Exchange-map code allocates an intent state, calls `xfs_exchmaps_defer_add()`, and the implementation creates XMI/XMD log items around the deferred work lifecycle.

State and persistence: The header defines in-core wrappers for persistent XMI/XMD log formats. XMI refcounting covers races between AIL insertion, unpin, done processing, and cancellation.

Dependencies and integration points: Consumed by exchange-map implementation, transaction logging, recovery, and slab-cache initialization code.

Risks and test signals: Risks are struct/log-format drift and wrong lifecycle assumptions around XMI refcounting. Test large exchange operations, log recovery matching, and module/slab lifecycle builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_exchmaps_item.h -->
