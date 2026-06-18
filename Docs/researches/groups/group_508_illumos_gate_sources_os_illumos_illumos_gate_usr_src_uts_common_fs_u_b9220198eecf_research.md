# Group Research: group_508_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_u_b9220198eecf

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is in subset A. All eight listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_vnops.c

## Purpose

`udf_vnops.c` implements the illumos UDFS vnode operation vector and the local read/write/page-cache helpers behind it. It is the bridge between generic VFS/VM operations and UDF inode, directory, allocation, symlink, and device I/O routines.

## Main Interfaces

The file installs `udf_vnodeops_template`, covering open/close/read/write, getattr/setattr/access, lookup/create/remove/link/rename/mkdir/rmdir/readdir/symlink/readlink, fsync/inactive/fid, rwlock/rwunlock/seek/frlock/space, getpage/putpage/map/addmap/delmap/pathconf/pageio, and vnode event support.

Internal helpers include `ud_rdwri`, `ud_rdip`, `ud_wrip`, `ud_getpage_miss`, `ud_getpage_ra`, `ud_page_fill`, `ud_putpages`, `ud_putapage`, `ud_iodone`, `ud_multi_strat`, and `ud_slave_done`.

## Behavior And Data Flow

Simple vnode calls mostly delegate into UDF inode/directory helpers: `ud_dirlook`, `ud_direnter`, `ud_dirremove`, `ud_iaccess`, `ud_itrunc`, `ud_iupdat`, `ud_syncip`, `ud_sync_indir`, and `ud_iinactive`.

Read and write paths use `segmap_getmapflt()` and `segmap_release()` for cached file I/O. `ud_wrip()` allocates blocks with `ud_bmap_write()` before increasing `i_size`, handles page creation and zero-fill for partial EOF pages, enforces process file-size limits, and clears set-id bits when required. `ud_rdip()` handles EOF/offset validation, read-ahead/free-behind hints, and synchronous read flush semantics.

The VM path handles UDF-specific storage shapes: embedded one-AD files, holes, logical blocks smaller than pages, and discontiguous extents. Multi-part I/O uses a master `mio_master_t` plus cloned slave buffers, with `ud_slave_done()` aggregating errors and completing the original buffer.

## Namespace And Metadata Semantics

Lookup uses DNLC first, then `ud_dirlook()`, and wraps device vnodes with `specvp()`. Create, mkdir, link, rename, remove, and rmdir serialize directory mutation with inode `i_rwlock` and rely on UDF directory helpers for on-disk updates. Rename has a filesystem-wide `udf_rename_lck`, validates sticky-directory removal access, rejects mounted-over directories, emits vnode pre/post rename events, links target first, then removes source.

Symlink creation converts POSIX path text into UDF `path_comp` records; readlink reverses those records into a slash-separated path. Readdir synthesizes `.` and converts UDF FIDs into `dirent64` records, skipping deleted entries and decompressing UDF names.

## Locking And State

`i_rwlock` serializes high-level read/write and directory mutation. `i_contents` protects inode size, metadata, and bmap/page operations. `i_tlock` protects transient flags, map counts, delayed write clustering, timestamps, and write throttle counters. Mandatory locking blocks mmap/frlock combinations when required.

## Notable Invariants And Risks

- `VNOMAP` vnodes reject mapping and page I/O paths.
- Writable mmap faults over holes may upgrade `i_contents` to writer and allocate blocks.
- UDF reports `_PC_FILESIZEBITS` as 41 because other block-number limits constrain practical file size.
- Delayed async putpage clustering uses `i_delayoff/i_delaylen` and is flushed on close or explicit putpage.
- Audit hotspots are symlink path-component buffer sizing, multi-I/O error cleanup, embedded-file page copying/tag CRC updates, partial write rollback after extending `i_size`, and write-throttle accounting in `ud_iodone()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs.c

## Purpose

`lufs.c` is the top-level UFS logging control file. It enables and disables UFS logging, allocates/frees log extents, reconstructs in-core log state at mount/remount, provides the logging strategy hook for buffer I/O, initializes kstats/caches, and manages log header identity generation.

## Main Interfaces

Important routines include `lufs_snarf`, `lufs_unsnarf`, `lufs_enable`, `lufs_disable`, `lufs_read_strategy`, `lufs_write_strategy`, `lufs_strategy`, `lufs_hd_genid`, and `lufs_init`. Static helpers allocate/free on-disk log space and initialize the first log state sectors.

## Behavior And Data Flow

`lufs_enable()` computes a safe log size from requested size, filesystem size, cylinder group count, and tunables, then write-locks the filesystem, allocates contiguous-ish log extents through a dummy shadow inode, initializes log state, calls `lufs_snarf()`, starts logging support threads, and marks the superblock `FSLOG`.

`lufs_disable()` write-locks and quiesces the filesystem, flushes outstanding transactions, stops delete/reclaim/roll activity as needed, tears down in-core log state, frees on-disk log extents, marks the superblock active/no-log, and unlocks the filesystem.

`lufs_snarf()` reads and checksums the log extent table, builds an in-core extent table, reads duplicated log state sectors, validates version/checksum/bad-log state, creates delta/log/mata maps, scans existing log records, and starts the roll thread for read-write mounts.

## Logged I/O Strategy

`lufs_read_strategy()` overlays logmap deltas on reads. If no overlapping deltas exist, it reads the master device directly; otherwise it may read the master first, then calls `ldl_read()` to apply logged deltas.

`lufs_write_strategy()` removes matching deltas from the deltamap and moves them to the logmap with `logmap_add()` or cached roll buffers. Writes without metadata deltas pass through to the device or snapshot layer, with debug checks preventing unlogged metadata writes.

## Dependencies And Risks

This file depends on the transaction layer in `lufs_top.c`, map/logmap code in `lufs_map.c`, log-device code in `lufs_log.c`, UFS lockfs/quiesce/thread helpers, snapshots, and kstats.

High-risk areas are enable/disable ordering, superblock state transitions, log extent allocation rollback, bad-log handling on read-only mounts, `ufs_scan_lock` synchronization while linking/unlinking `vfs_log`, and the strategy paths that decide whether data must be served from master, log, or both.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_debug.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_debug.c

## Purpose

`lufs_debug.c` contains DEBUG-kernel support for UFS logging assertions, transaction tracing, metadata-map verification, scan-test trimming checks, and transaction statistics. The only always-compiled symbol is the global `lufs_debug` tunable because UFS ioctl code references it.

## Main Interfaces

DEBUG-only routines include `top_mataadd`, `top_matadel`, `top_mataclr`, `top_begin_debug`, `top_end_debug`, `top_delta_debug`, `top_roll_debug`, `top_init_debug`, `logmap_logscan_debug`, `logmap_logscan_commit_debug`, `logmap_logscan_add_debug`, `map_check_ldl_write`, `map_put_debug`, `map_get_debug`, `map_check_linkage`, `matamap_overlap`, `matamap_within`, `ldl_sethead_debug`, and `lufs_initialize_debug`.

## Behavior

The file maintains a circular `toptrace` buffer when `MT_TRACE` is enabled. It records transaction begin/end and delta events by device, thread, type, offset, and length.

Metadata-map helpers track legal metadata ranges and assert that deltas are within those ranges. Transaction debug state is stored in thread-specific `threadtrans_t` data keyed by `topkey`; begin/end checks verify device, transaction id, expected size, and actual recorded delta size.

Map debug routines validate hash/list/cancel-list consistency, log offset ordering across wraparound, and log-read-after-log-write correctness by rereading logged data and comparing it to the original buffer.

## Invariants And Risks

- Most checks assert `T_DONTBLOCK`, matching transaction-layer expectations.
- `matamap_within()` and `matamap_overlap()` scan per-MAPBLOCK hash ranges under map mutexes.
- Debug scan fields such as `mtm_trimrlof`, `mtm_trimclof`, and `mtm_trimalof` model safe log trimming during scan tests.
- Because this file is assertion-heavy and mostly DEBUG-only, its correctness value is in catching transaction/map corruption early rather than providing production behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_log.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_log.c

## Purpose

`lufs_log.c` implements the low-level logical log device layer for UFS logging. It maps logical log offsets through extent tables, manages circular read/write buffers, writes delta records and sector trailers, scans logs at mount, advances head/tail state, and transitions the filesystem into log-error state on I/O failure.

## Main Interfaces

Important routines include `ldl_strategy`, `ldl_write`, `ldl_read`, `ldl_waito`, `ldl_round_commit`, `ldl_push_commit`, `ldl_has_space`, `ldl_need_commit`, `ldl_sethead`, `ldl_settail`, `ldl_savestate`, `ldl_logscan_begin`, `ldl_logscan_read`, `ldl_logscan_end`, `ldl_need_roll`, `ldl_seterror`, `ldl_bufsize`, `alloc_wrbuf`, `alloc_rdbuf`, and `free_cirbuf`.

## Behavior And Data Flow

`ldl_strategy()` clones a logical log I/O into one or more physical device I/Os according to the in-core log extent table. It also routes writes through the snapshot layer when snapshots are active and uses task-specific bypass state to avoid snapshot throttling deadlocks.

`ldl_write()` writes a delta header, then optional delta data, into the circular write buffer. `storebuf()` inserts sector trailers containing transaction id and monotonically increasing sector identity. Full or wrapped buffers are asynchronously pushed with `writelog()`.

`ldl_read()` reconstructs data from log offsets, handling cached roll buffers, zero deltas, sector trailers, and wraparound. `ldl_logscan_read()` validates sector identities during mount scan so partial or torn transactions are rejected.

## State Management

`ldl_sethead()` advances the durable log head after deltas are rolled to the master device, invalidates affected cached buffers, updates head identity/tid, and saves duplicated state sectors. `ldl_settail()` establishes the tail after log scan. `ldl_savestate()` writes the in-core `ml_odunit_t` state twice into the state buffer with checksum.

## Notable Invariants And Risks

- Writers are single-threaded through `un_log_mutex`.
- One extra sector is reserved so `head == tail` can mean empty, not full.
- Sector trailers are part of the logical stream and must be skipped by readers.
- `LDL_ERROR` causes future log I/O to fail, marks `un_badlog` on disk, saves state, warns the operator, and asks UFS to hard-lock itself outside scan.
- Audit hotspots are wraparound math, sector identity validation, cloned I/O completion, snapshot throttling bypass, and state-sector update ordering.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_map.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_map.c

## Purpose

`lufs_map.c` implements the UFS logging map layer: generic map allocation, the deltamap of dirty metadata not yet logged, the logmap of deltas already in the log, cancellation records, cached roll buffers, log commit records, roll-thread coordination, and log scan reconstruction.

## Main Interfaces

Core routines include `map_get`, `map_put`, `map_free_entries`, `deltamap_add`, `deltamap_remove`, `deltamap_del`, `deltamap_push`, `logmap_add`, `logmap_add_buf`, `logmap_commit`, `logmap_cancel`, `logmap_iscancel`, `logmap_list_get`, `logmap_list_get_roll`, `logmap_setup_read`, `logmap_remove_roll`, `logmap_sethead`, `logmap_settail`, `logmap_roll_dev`, `logmap_logscan`, `_init_map`, and `handle_dquot`.

## Behavior And Data Flow

`deltamap_add()` splits metadata ranges at `MAPBLOCKSIZE` boundaries and records dirty deltas with optional push functions. At sync end, `deltamap_push()` invokes those functions to move all remaining deltas into the logmap.

`logmap_add()` and `logmap_add_buf()` write deltas into the log through `ldl_write()`, insert them into logmap hash/list structures, cancel older overlapping entries, and track transaction id/age. `logmap_add_buf()` optionally attaches a memory-capped cached roll buffer so the roll thread can write master data without rereading and overlaying deltas.

`logmap_commit()` writes a commit delta, rounds/pushes the log buffer, and resets dirty counters after successful commit. `logmap_logscan()` rebuilds the logmap from on-disk deltas and discards the last partial transaction.

## Roll And Cancel Semantics

The roll thread asks `logmap_next_roll()` for stable, committed deltas, uses `logmap_list_get_roll()` to age/mark entries, then `logmap_remove_roll()` frees rolled entries. `logmap_setup_read()` decides whether rolling needs a master read and builds a sector map to avoid overwriting user data between metadata sectors.

Cancel records prevent reuse or stale replay of blocks whose metadata was superseded. User-data cancel placeholders protect deleted user blocks within a transaction without logging user data. `logmap_free_cancel()` frees canceled entries only after the commit record is known durable.

## Notable Invariants And Risks

- `mtm_mutex` protects hash/list fields; `mtm_rwlock` blocks readers while aged entries are being rolled or freed.
- Entries for current transaction or commit-in-progress are not rolled.
- Cached roll buffers are reference-counted and invalidated on cancellation.
- Quota deltas carrying dquot references require `handle_dquot()` cleanup when replaced by non-quota deltas.
- Audit hotspots are overlap/cancel rules, `ME_AGE` lock upgrade paths, CRB memory accounting, partial transaction abort, and dquot reference cleanup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_thread.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_thread.c

## Purpose

`lufs_thread.c` implements the per-log roll thread that copies committed logmap deltas back to their master filesystem locations and frees log space. It is the asynchronous cleaner that keeps the physical log from filling.

## Main Interfaces

Important routines are `trans_roll`, `log_roll_read`, `log_roll_write`, `log_roll_write_crb`, `log_roll_write_bufs`, and the static helpers `trans_roll_wait` and `log_roll_buffers`.

Tunables include roll buffer count limits, `logmap_maxnme`, `trans_roll_tics`, and counters for new-delta/read-wait behavior.

## Behavior And Data Flow

`trans_roll()` allocates a configurable number of `MAPBLOCKSIZE` roll buffers, marks its thread-specific state to bypass snapshot throttling, then loops until exit/error. It rolls when forced, when the logmap is too full, when the log is idle but nonempty, or when physical log usage is high.

`log_roll_read()` finds a committed map block to roll, obtains logmap entries under the logmap reader lock, uses cached roll buffers when available, otherwise reads the master block and overlays deltas from the log. It avoids spinning if entries are in use by taking the logmap writer lock and retrying later.

`log_roll_write()` sorts roll buffers by block number, issues writes, waits for all master writes and cloned subwrites, and reports errors through `ldl_seterror()`.

## Snapshot And I/O Handling

Roll writes go through `fssnap_strategy()` when snapshots are active, otherwise through `bdev_strategy()`. Cached roll buffers can be written directly. Non-cached roll buffers use a sector map so only metadata sectors are written when a full master-block write could overwrite user data.

## Notable Invariants And Risks

- The roll thread exits through `MTM_ROLL_EXIT` or `LDL_ERROR` and broadcasts waiters.
- `MT_SCAN` debug mode suppresses normal rolling unless forced.
- Force-roll waiters are released after a complete force-roll cycle.
- Audit hotspots are ordering of sorted writes, cloned buffer cleanup, handling of `B_INVAL` roll buffers, snapshot bypass deadlock avoidance, and wakeup/exit flag transitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_thread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_top.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_top.c

## Purpose

`lufs_top.c` implements the transaction operation layer for UFS logging. It coordinates synchronous and asynchronous transaction entry/exit, reservation accounting, commit sequencing, forced empty sync transactions, delta declaration/cancellation, and movement of dirty metadata into the log.

## Main Interfaces

Key routines include `top_delta`, `top_cancel`, `top_iscancel`, `top_seterror`, `top_begin_sync`, `top_begin_async`, `top_end_sync`, `top_end_async`, `top_read_roll`, `top_log`, and `_init_top`.

## Transaction Flow

`top_begin_sync()` enters a synchronous transaction, waits if the current transaction is closed or over-reserved, handles fsync-specific fast failure for `T_DONTPEND` threads, and reserves log space. `top_begin_async()` enters async work unless the async side is closed or the transaction is over-reserved; when needed, it dispatches an empty sync operation on `system_taskq` to drain reservations.

`top_end_sync()` is the commit path. The last sync operation closes the current transaction to sync and async callers, waits for active async work, pushes remaining deltamap entries, writes a commit record, waits for log writes, frees canceled deltas only after commit durability, opens the next transaction, wakes waiters, and may force log rolling.

`top_end_async()` releases reservation slack, records the last async transaction id when deltas were generated, wakes sync commit waiters when it was the final async operation, and triggers sync/roll pressure handling when maps or log usage are high.

## Delta And Logging Operations

`top_delta()` records metadata ranges into the deltamap and marks the current thread transaction as having deltas. `top_cancel()` removes metadata deltas and adds logmap cancel records. `top_log()` removes deltas from the deltamap and adds them to the logmap, using cached roll buffers when possible.

`top_read_roll()` is called by the roll thread to gather logmap entries for a master block, choose cached-roll-buffer or read/overlay behavior, and initiate asynchronous master reads when required.

## Notable Invariants And Risks

- Thread-specific `threadtrans_t` state is stored under `topkey`.
- `un_resv`, `un_resv_wantin`, `mtm_active`, `mtm_activesync`, and `mtm_wantin` are the main reservation/concurrency counters.
- Commit ordering deliberately allows async operations before the commit write completes, but holds `un_log_mutex` so no new deltas are written before the commit record is durable.
- Audit hotspots are forced sync taskq counting, condition-variable sequencing, fsync `T_DONTPEND` behavior, commit/cancel durability ordering, and reservation arithmetic under error paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_top.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/quota.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/quota.c

## Purpose

`quota.c` manages UFS in-core dquot structures: initialization, hash/free-list caching, lookup/loading from the on-disk quota file, release/writeback, and invalidation when quotas are disabled or a filesystem unmounts.

## Main Interfaces

The file provides `qtinit`, `qtinit2`, `getdiskquota`, `dqput`, `dqupdate`, `dqinval`, and `invalidatedq`.

## Behavior And Data Flow

`qtinit()` initializes the global quota subsystem rwlock. `qtinit2()` allocates the dquot table on first quota use, initializes hash heads and the free list, and creates per-dquot mutexes.

`getdiskquota()` requires the filesystem quota rwlock, checks whether quotas are enabled unless forced, looks up the `(uid, ufsvfs)` dquot in the hash cache, and otherwise reuses a free dquot. It reads `struct dqblk` from the quota inode when the uid offset is valid, records the master offset for later logging, handles quota-file I/O errors by removing the dquot from the cache, and returns the dquot referenced.

`dqput()` decrements the reference count. Last release writes modified quota data with `dqupdate()`, clears flags, and either invalidates the dquot if quotas are disabled or returns it to the free list.

## Logging Integration

`dqupdate()` writes modified quota data either through UFS logging or directly to the quota inode. If the caller is not already in a transaction, it temporarily sets `T_DONTBLOCK`, starts an async `TOP_QUOTA` transaction, logs a `DT_QR` delta and quota record, then ends the transaction. Non-logging updates write with `ufs_rdwri()` under the quota inode contents lock.

## Invalidation And Locking

`dqinval()` removes a zero-reference dquot from its hash chain and returns it to the head of the free list, temporarily clearing `dq_ufsvfsp` to avoid lookup races while lock order is adjusted. `invalidatedq()` scans all dquots for a filesystem after quotas are disabled, skipping transient `DQ_TRANS` records that logging still owns.

Global cache/free-list locks protect hash and free-list mutation, while per-dquot locks protect object fields. The filesystem `vfs_dqrwlock` is required around most external quota operations.

## Notable Risks

High-risk areas are lock-order transitions between `dq_cachelock`, `dq_freelock`, `dq_lock`, and `vfs_dqrwlock`; quota I/O error cleanup; `DQ_TRANS` orphan handling during unmount; and ensuring logged quota deltas release dquot references through the logging map layer.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/quota.c -->