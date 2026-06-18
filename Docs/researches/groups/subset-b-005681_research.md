# subset-b-005681 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_logmgr.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_logmgr.c

## Purpose
`jfs_logmgr.c` implements the JFS journal/log manager. It owns log device open/close, append-only log record packing, circular log page advancement, sync-point generation, group commit, log buffer I/O, journal formatting, and the helper kernel threads that redrive log I/O. It sits between `jfs_txnmgr.c`, which builds transaction log records, and log replay (`jfs_logredo.c`, outside this work item), which consumes the on-disk format defined here and in `jfs_logmgr.h`.

## Important APIs, types, and functions
The public entry points are `lmLogOpen()`, `lmLogClose()`, `lmLogInit()`, `lmLogShutdown()`, `lmLogFormat()`, `lmLog()`, `lmGroupCommit()`, `jfs_flush_journal()`, `jfs_syncpt()`, and `jfsIOWait()`. The central private paths are `lmWriteRecord()`, `lmNextPage()`, `lmGCwrite()`, `lmPostGC()`, `lmLogSync()`, `lmLogFileSystem()`, `open_inline_log()`, `open_dummy_log()`, and the `lbm*` log-buffer-manager functions. Important global state includes `jfs_external_logs`, `dummy_log`, `jfs_log_mutex`, `log_redrive_list`, `log_redrive_lock`, and the optional `lmStat` counters.

## Control flow
Mount-time `lmLogOpen()` selects no-integrity dummy logging, an inline log extent, or a shared external journal. External journals are looked up by device and UUID under `jfs_log_mutex`; new journals are opened with `bdev_file_open_by_dev()`, initialized through `lmLogInit()`, linked into `jfs_external_logs`, and marked active in the log superblock. `lmLogInit()` validates `LOGMAGIC` and `LOGREDONE`, reads the end-of-log page, writes an initial `LOG_SYNCPT`, marks the journal `LOGMOUNT`, and initializes `log->lsn`, `syncpt`, `sync`, `nextsync`, and group-commit queues.

At runtime `lmLog()` serializes through `LOG_LOCK()`, optionally attaches a metapage and transaction block to `log->synclist`, calls `lmWriteRecord()` to copy line-vector data and the `struct lrd` descriptor into the current log page, may call `lmLogSync()` when the distance from `syncpt` reaches `nextsync`, and advances `log->lsn`. `lmWriteRecord()` handles records that cross page boundaries by calling `lmNextPage()`. Commit records enqueue their `tblock` on `log->cqueue`; `lmGroupCommit()` either returns immediately for lazy commits or waits on `tblk->gcwait` until `lmPostGC()` marks the commit durable.

The log buffer manager allocates a small private pool of `LOGPAGES` log buffers in `lbmLogInit()`. `lbmWrite()` maintains a circular per-log FIFO write queue and starts I/O only for the queue head. Completion in `lbmIODone()` updates `log->clsn`, wakes synchronous waiters, invokes `lmPostGC()` for group commit pages, frees released buffers, and redrives subsequent queued buffers through `jfsIOthread` when completion context cannot submit more I/O.

## State and persistence behavior
The persistent journal layout is block 1 `struct logsuper`, followed by circular data pages containing `struct logpage` headers/trailers and packed log records. `lmLogFormat()` writes this layout from scratch, including a formatted sync-point page and simulated wrapped sequence numbers so replay can find the end. Clean shutdown writes a final sync point, writes the current log page synchronously, updates the log superblock to `LOGREDONE`, and records the final `end` LSN. During normal operation `LOGMOUNT` means the log is active and must not be treated as clean without replay or shutdown.

In memory, `struct jfs_log` tracks current page/eor, lsn, committed lsn, sync point, sync list, active transaction count, group-commit queue, write queue, free log buffers, active superblocks sharing the journal, and flags such as `log_INLINELOG`, `log_SYNCBARRIER`, `log_QUIESCE`, and `log_FLUSH`. `lmLogSync()` computes forward progress from the oldest item on `synclist`; if too much log space is consumed while transactions are active, it sets `log_SYNCBARRIER`, flushes the journal, and transaction begin paths block until `txEnd()` clears the barrier after a hard sync point.

## Dependencies and integration points
This file depends on block-layer BIO APIs, buffer-head helpers, kthreads/freezer support, wait queues, mutexes/spinlocks, UUID helpers, JFS superblock state, metapages, and transaction manager structures. It is called by mount/unmount (`jfs_mount.c`, `jfs_umount.c`), transaction commit (`jfs_txnmgr.c`), metadata writeback (`jfs_metapage.c` through log sync lists), and module threads (`jfsIOthread`, `jfsSyncThread`). It also provides proc/stat output when JFS debug/statistics are enabled.

## Risks
Correctness depends on lock ordering across `LOG_LOCK`, `LOGGC_LOCK`, `LOGSYNC_LOCK`, and `LCACHE_LOCK`; wrong ordering can deadlock commit, sync, or writeback. Lazy commits and group commits share `tblock` state with user threads and the lazy commit thread, so flag transitions such as `tblkGC_READY`, `tblkGC_COMMIT`, `tblkGC_COMMITTED`, `tblkGC_LAZY`, and `tblkGC_UNLOCKED` are high risk. The no-integrity dummy log bypasses disk I/O but still exercises most in-memory paths, so callers must not assume durable recovery. The shutdown path relies on `jfs_flush_journal(log, 2)` draining both `cqueue` and `synclist`; any metapage left pinned on `synclist` can prevent clean log advancement and force recovery risk. I/O errors are propagated mostly as `lbmERROR` and `-EIO`, but several paths continue cleanup after warnings, so tests need to inspect mount state and filesystem dirty flags.

## Test signals
Useful signals include clean mount/unmount with inline and external journals, remount read-write, shared external journal activation/deactivation for multiple filesystems, forced flushes from `sync`, log wrap pressure that sets `log_SYNCBARRIER`, lazy and synchronous commit ordering, injected BIO errors on log reads/writes, no-integrity mount behavior, `lmLogFormat()` output replayability, and debug counters for commits, submitted/completed writes, full-page commits, and partial-page commits. Crash-recovery tests should verify that `LOG_SYNCPT`, `LOG_COMMIT`, `LOG_MOUNT`, redopage, noredopage, and updatemap records replay to a consistent block/inode map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_logmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_logmgr.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_logmgr.h

## Purpose
`jfs_logmgr.h` defines the JFS journal ABI and the in-memory structures shared by the log manager, transaction manager, metapage layer, mount/unmount code, and replay code. It describes the on-disk log superblock, log pages, log record descriptor, line-vector descriptor, active log state, log buffers, log-sync list prefix, and the public log-manager API.

## Important APIs, types, and functions
Key constants are `LOGPSIZE`, `L2LOGPSIZE`, `LOGPAGES`, `LOGSUPER_B`, `LOGSTART_B`, `LOGMAGIC`, `LOGVERSION`, and `MAX_ACTIVE`. On-disk structures are `struct logsuper`, `struct logpage`, `struct lrd`, and `struct lvd`. In-memory structures are `struct jfs_log`, `struct lbuf`, and `struct logsyncblk`. The header exports `lmLogOpen()`, `lmLogClose()`, `lmLogShutdown()`, `lmLogInit()`, `lmLogFormat()`, `lmGroupCommit()`, `jfsIOWait()`, `jfs_flush_journal()`, and `jfs_syncpt()`.

## Control flow
The header does not execute code, but it encodes the contracts used by `jfs_logmgr.c` and `jfs_txnmgr.c`. Transaction code fills `struct lrd` with record type and type-specific fields, then calls `lmLog()`. Log manager code packs optional line-vector data before the fixed descriptor, updates `struct logpage` header/trailer `eor`, and records current and committed LSNs in `struct jfs_log` and `struct tblock`.

## State and persistence behavior
`struct logsuper` is stored in log block 1 and records magic/version, serial number, size, block size, state, end-of-log, journal UUID/label, and up to `MAX_ACTIVE` filesystem UUIDs sharing the journal. `struct logpage` stores duplicate page and eor values in header/trailer to detect partial writes. `struct lrd` is the replay descriptor for commit, sync point, mount, after-image, no-redo, and map-update records. `struct jfs_log` is volatile state and includes current append page/eor, sync-point cursors, group-commit queue, log buffer queue, shared-superblock list, and journaling-disabled flag.

## Dependencies and integration points
The header pulls in UUID support, `jfs_filsys.h` for filesystem state and flags, and `jfs_lock.h` for sleep/locking helpers. It relies on `pxd_t` from JFS types for physical extents and on `struct tblock`/`struct metapage` users treating the leading fields as a `struct logsyncblk`. The exported API is consumed by mount, unmount, transaction commit, metapage writeback, log formatting, and background I/O threads.

## Risks
The on-disk structures use little-endian fields and fixed field placement; layout changes would break replay and userspace repair tools. `struct logsyncblk` must remain a common prefix for both transaction blocks and metapages, so field reordering in either embedding structure is dangerous. The `logdiff()` macro assumes circular log arithmetic relative to `log->syncpt`; wrong inputs can miscompute sync pressure and allow log overwrite. Constants such as `LOGPHDRSIZE`, `LOGPTLRSIZE`, and `LOGRDSIZE` are baked into record packing.

## Test signals
Build-time layout checks are implicit, so recovery tests are the main signal: formatted logs should validate with `LOGMAGIC`, dirty logs should reject mount before replay, active filesystem lists should be updated on shared external journals, and replay should correctly interpret all `LOG_*` record and data-type flags. Endian-sensitive tests should inspect log descriptors and extent fields on disk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_logmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_metapage.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_metapage.c

## Purpose
`jfs_metapage.c` implements JFS metadata-page caching, locking, writeback, read I/O, invalidation, migration, and integration with the journal log-sync list. A metapage is JFS's logical metadata unit layered on Linux folios, normally one `PSIZE` metadata block per folio on 4 KiB page systems but with anchor support for multiple metapages per larger folio.

## Important APIs, types, and functions
Public functions are `metapage_init()`, `metapage_exit()`, `__get_metapage()`, `grab_metapage()`, `force_metapage()`, `hold_metapage()`, `put_metapage()`, `release_metapage()`, and `__invalidate_metapages()`. The exported address-space operations are `jfs_metapage_aops` with `.read_folio`, `.writepages`, `.release_folio`, `.invalidate_folio`, `.dirty_folio`, and optional `.migrate_folio`. Important private helpers include `folio_to_mp()`, `insert_metapage()`, `remove_metapage()`, `inc_io()`, `dec_io()`, `drop_metapage()`, `metapage_get_blocks()`, `metapage_write_folio()`, `metapage_read_folio()`, `metapage_release_folio()`, and `remove_from_logsync()`.

## Control flow
`__get_metapage()` maps a logical block to a folio and offset, rejects metadata that crosses a page boundary, selects either the inode mapping or the aggregate direct-inode mapping for absolute reads, reads or grabs the folio, finds or allocates the `struct metapage`, verifies logical size, locks it, clears discard state for newly allocated pages, and returns it with the folio unlocked. Updates mark the metapage dirty and release it through `write_metapage()`/`flush_metapage()` in the header. `release_metapage()` unlocks the metapage, decrements the reference count, marks the folio dirty, optionally performs synchronous writeback for `META_sync`, removes stale log-sync entries, and drops unreferenced clean metapages.

Read I/O is driven by `metapage_read_folio()`, which calls `metapage_get_blocks()` to translate logical to physical blocks through `xtLookup()` for mapped metadata inodes, builds BIOs, and ends the folio read in `last_read_complete()`. Writeback scans metapages inside a folio in `metapage_write_folio()`, skips clean pages, redirties pages blocked by `nohomeok` unless `META_forcewrite` is set, clears `META_dirty`, sets `META_io`, builds contiguous BIO segments, and completes through `last_write_complete()`, which clears `META_io` and removes committed pages from `log->synclist`.

## State and persistence behavior
Metapage state includes flags (`META_locked`, `META_dirty`, `META_sync`, `META_discard`, `META_forcewrite`, `META_io`), a reference count, data pointer, logical block index, folio pointer, owning superblock, logical size, and journal fields (`clsn`, `nohomeok`, `log`, `lsn`, `synclist`). `metapage_nohomeok()` pins the folio and delays home-location writeback while a transaction's after-image is not yet durable in the journal. `metapage_homeok()` releases that pin once commit/write ordering is safe. Persistent effects happen through metadata writeback to home blocks; journal ordering is coordinated by `lsn` and `log->synclist`.

## Dependencies and integration points
The file depends on Linux folios, address-space writeback, BIOs, mempools, slab caches, migration, block devices, and JFS helpers from `jfs_incore.h`, `jfs_superblock.h`, `jfs_filsys.h`, `jfs_txnmgr.h`, and `jfs_debug.h`. It integrates with transaction locking (`txLock()` marks pages no-home-ok), log sync (`remove_from_logsync()` updates `log->count` and `synclist`), extent lookup (`xtLookup()`), aggregate direct I/O (`direct_inode` mapping), and map invalidation macros in `jfs_metapage.h`.

## Risks
The code has subtle folio/private ownership rules, especially when `PAGE_SIZE > PSIZE` and a `meta_anchor` multiplexes several metapages. Incorrect `nohomeok` handling can write metadata home before its journal commit is durable, while missed `metapage_homeok()` can pin folios and block clean unmount. `metapage_write_folio()` must balance every `inc_io()` with `dec_io()` even on bad mappings or empty BIO dumps. Migration must refuse locked metapages and update `mp->data` offsets correctly. Invalidation marks dirty pages discarded rather than immediately freeing them, so later callers must not reuse discarded pages except via `new` allocation.

## Test signals
Test signals include metadata reads and writes for aggregate/direct and inode mappings, folio migration under memory pressure, large-page builds, synchronous metapage flush, forced writeback while `nohomeok` is set, log-sync list removal after writeback, invalidation of freed extents, injected mapping failures in `metapage_get_blocks()`, BIO read/write errors, and proc statistics for allocations, frees, and lock waits. Crash tests should verify that home metadata never advances ahead of committed journal records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_metapage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_metapage.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_metapage.h

## Purpose
`jfs_metapage.h` declares the metapage abstraction used for all JFS metadata I/O and journaling coordination. It exposes the metapage structure, state bits, allocation/read helpers, release/write helpers, journal home-location ordering helpers, and extent invalidation macros.

## Important APIs, types, and functions
The central type is `struct metapage`, whose leading fields mirror `struct logsyncblk` for membership on `jfs_log.synclist`. Public APIs include `metapage_init()`, `metapage_exit()`, `__get_metapage()`, `release_metapage()`, `grab_metapage()`, `force_metapage()`, `hold_metapage()`, `put_metapage()`, `__invalidate_metapages()`, and `jfs_metapage_aops`. Convenience macros `read_metapage()` and `get_metapage()` select read-existing versus create/new behavior. Inline helpers include `write_metapage()`, `flush_metapage()`, `discard_metapage()`, `metapage_nohomeok()`, `metapage_wait_for_io()`, `_metapage_homeok()`, and `metapage_homeok()`.

## Control flow
Callers fetch metadata with `read_metapage()` or `get_metapage()`, modify `mp->data` under the metapage lock, then either release clean, mark dirty via `write_metapage()`, force synchronous write via `flush_metapage()`, or discard invalidated metadata via `discard_metapage()`. Transaction code calls `metapage_nohomeok()` when a metadata page is journal-protected and `_metapage_homeok()`/`metapage_homeok()` after the commit reaches stable storage.

## State and persistence behavior
`META_dirty` controls home writeback, `META_sync` requests synchronous write on release, `META_discard` suppresses stale writes for invalidated extents, `META_forcewrite` bypasses normal no-home blocking, and `META_io` tracks writeback in progress. `nohomeok` is a counter, not a boolean, allowing nested transaction holds. The `log`, `lsn`, `clsn`, and `synclist` fields bind metapages to journal sync-point advancement.

## Dependencies and integration points
The header depends on `linux/pagemap.h`, JFS transaction IDs (`lid_t`), extent helpers (`addressPXD`, `lengthPXD`, `addressDXD`, `addressXAD`), and `struct jfs_log`. It is used by inode, directory, extent-tree, allocation-map, mount, transaction, and log code wherever metadata pages are read, modified, invalidated, or flushed.

## Risks
Callers must pair holds/releases carefully or the metapage can remain locked, pinned, or no-home-blocked. `metapage_nohomeok()` waits for folio writeback while holding folio state and increments a counter that must eventually be decremented. The invalidation macros operate on block extents; incorrect extent lengths or addresses can discard unrelated metadata or leave stale pages dirty.

## Test signals
Useful tests exercise dirty release, synchronous flush, discard, nested no-home sections, wait-for-I/O serialization, and invalidation through PXD/DXD/XAD macros. Debugging should watch metapage refcounts, `nohomeok`, and `META_io` transitions during transaction commit and unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_metapage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_mount.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_mount.c

## Purpose
`jfs_mount.c` implements JFS aggregate/fileset mount setup, read-write mount completion, superblock validation, synchronous superblock state updates, primary/secondary superblock reads, and the mount log record. It turns the on-disk aggregate into the in-memory special inodes and maps needed for normal filesystem operation.

## Important APIs, types, and functions
Public functions are `jfs_mount()`, `jfs_mount_rw()`, `updateSuper()`, and `readSuper()`. Private helpers are `chkSuper()` and `logMOUNT()`. Important integrations are `diReadSpecial()`, `diMount()`, `diUnmount()`, `diFreeSpecial()`, `dbMount()`, `dbUnmount()`, `lmLogOpen()`, `lmLogClose()`, and `lmLog()`.

## Control flow
`jfs_mount()` first calls `chkSuper()` to read and validate the aggregate superblock. It then reads and mounts the aggregate inode allocation map (`AGGREGATE_I`), the block allocation map (`BMAP_I`), optionally the secondary aggregate inode allocation map unless `JFS_BAD_SAIT` is set, and finally the fileset inode allocation map (`FILESYSTEM_I`). On each failure it unwinds already-mounted maps and special inodes in reverse order.

`jfs_mount_rw()` handles completing a read-write mount or remounting from read-only. On remount it revalidates a clean superblock, truncates cached inode/block map pages because fsck may have updated them, remounts the inode and block maps, opens the log with `lmLogOpen()`, marks the superblock mounted/dirty through `updateSuper(sb, FM_MOUNT)`, and writes a `LOG_MOUNT` record via `logMOUNT()`.

## State and persistence behavior
`chkSuper()` validates `JFS_MAGIC`, superblock version, 4 KiB block size, clean state for read-write mounts, secondary AIM/AIT descriptors, block-size logarithms, padding, and state range. It populates `jfs_sb_info` fields including mount flags, state, block-size shifts, UUID, inline/external log descriptors, fsck workspace, and secondary AIT descriptor. `updateSuper()` writes `s_state` synchronously, records external log device and serial on `FM_MOUNT`, and marks DASD usage stale on `FM_CLEAN` for OS/2 compatibility. With `JFS_NOINTEGRITY`, it maps requested states through `sbi->p_state` so no-integrity mounts do not advertise normal clean journaling semantics incorrectly.

## Dependencies and integration points
The file depends on Linux superblock/buffer-head/block-device APIs and JFS incore, filesystem, superblock, dmap, imap, metapage, and debug headers. It is invoked by the VFS JFS mount path and prepares state consumed by inode lookup, allocation maps, transaction manager, log manager, and unmount. The `LOG_MOUNT` record is aggregate-level so replay can stop processing older records for this filesystem.

## Risks
Mount correctness depends on exact cleanup ordering; leaking or double-freeing special inodes would corrupt later mount/unmount. Dirty superblocks are rejected for read-write mounts, so recovery must have completed before `jfs_mount_rw()`. The secondary AIM/AIT validation mutates `j_sb->s_flag` in memory before `brelse()` but does not by itself persist that fix. Remount assumes `chkSuper()` and `FM_CLEAN` are enough before truncating and remounting map pages. `updateSuper()` performs synchronous buffer writes but does not check `sync_dirty_buffer()` failure directly.

## Test signals
Tests should cover clean read-only and read-write mounts, dirty read-write rejection, remount read-only to read-write after fsck changes, primary superblock fallback to secondary, bad magic/version/block-size/padding/state failures, invalid secondary AIM/AIT descriptors, inline and external log setup, no-integrity mount state transitions, and mount/unwind failures injected at each special inode or map mount step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_superblock.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_superblock.h

## Purpose
`jfs_superblock.h` defines the on-disk JFS aggregate superblock layout and declares mount, unmount, superblock I/O, error, and extendfs entry points. It is the shared contract for interpreting block-size geometry, aggregate size, state, flags, log location, fsck workspace, labels, and UUIDs.

## Important APIs, types, and functions
Key constants are `JFS_MAGIC`, `JFS_VERSION`, and `LV_NAME_SIZE`. The central type is `struct jfs_superblock`, containing geometry fields (`s_size`, `s_bsize`, shifts, physical block size), allocation group size, flags/state/compression, secondary AIM/AIT extents, log device/serial/inline log extent, fsck workspace, timestamp, fsck service log fields, extendfs fields, volume UUID/label, and external log UUID. The header declares `readSuper()`, `updateSuper()`, `jfs_error()`, `jfs_mount()`, `jfs_mount_rw()`, `jfs_umount()`, `jfs_umount_rw()`, `jfs_extendfs()`, and the global JFS I/O/sync thread task pointers.

## Control flow
The header is consumed by mount code to read and validate the superblock, by unmount/remount paths to update state, by log manager code to access log descriptors, and by other filesystem code to report errors through `jfs_error()`. It does not execute control flow directly.

## State and persistence behavior
`struct jfs_superblock` is persistent disk data and all numeric fields are little-endian. `s_state` controls clean, mounted, dirty, and recovery-sensitive states. `s_flag` carries aggregate attributes such as inline log, group commit, no-integrity-adjacent behavior, DASD flags, and bad secondary AIT state from `jfs_filsys.h`. `s_logpxd`, `s_logdev`, and `s_loguuid` determine whether the journal is inline or external. Extendfs fields preserve in-progress grow state.

## Dependencies and integration points
The header depends on UUID support and on JFS extent/time types (`pxd_t`, `timestruc_t`). It is included by mount, unmount, metapage, log manager, transaction manager, and other JFS modules that need filesystem state or exported lifecycle functions. Userspace tools must agree with this layout, as noted by the compatibility comments.

## Risks
Changing field order or sizes breaks on-disk compatibility. The `s_fpack` and `LV_NAME_SIZE` OS/2 compatibility constraints are easy to overlook. Callers must always convert little-endian values before arithmetic. Log and fsck extents are trusted during mount after validation; corrupt descriptors can misdirect metadata I/O if checks are incomplete.

## Test signals
Signals include mounting filesystems with inline and external logs, validating UUID/label handling, dirty-state transitions across mount/unmount/remount, extendfs interruption/recovery, DASD flag updates on clean unmount, and compatibility with fsck/jfsutils expectations for the superblock layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_superblock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_txnmgr.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_txnmgr.c

## Purpose
`jfs_txnmgr.c` implements the JFS transaction manager. It allocates transaction IDs and transaction locks, records metadata changes as typed lock records, drives commit logging through the log manager, updates persistent and working allocation maps after commits, handles anonymous transactions from write paths, provides lazy commit and sync kernel threads, and coordinates quiesce/resume barriers.

## Important APIs, types, and functions
Public entry points include `txInit()`, `txExit()`, `txBegin()`, `txBeginAnon()`, `txEnd()`, `txLock()`, `txMaplock()`, `txLinelock()`, `txCommit()`, `txFreeMap()`, `txEA()`, `txFreelock()`, `txAbort()`, `txLazyUnlock()`, `txQuiesce()`, `txResume()`, `jfs_lazycommit()`, and `jfs_sync()`. Major private paths are `txLockAlloc()`, `txLockFree()`, `txRelease()`, `txUnlock()`, `txLog()`, `diLog()`, `dataLog()`, `dtLog()`, `xtLog()`, `mapLog()`, `txForce()`, `txUpdateMap()`, `txAllocPMap()`, `txLazyCommit()`, and `LogSyncRelease()`.

## Control flow
`txInit()` sizes and allocates global `TxBlock` and `TxLock` tables, builds freelists, initializes wait queues, watermarks, anonymous lists, and the lazy unlock queue. `txBegin()` blocks behind log sync/quiesce barriers and low tlock conditions, reserves a `tblock`, assigns a monotonically increasing log transaction id, and increments `log->active`. `txBeginAnon()` performs the same barrier/low-lock throttling for anonymous write-path updates without allocating a `tblock`.

`txLock()` either reuses an existing lock for the same transaction, transfers anonymous locks to a real transaction, allocates and initializes a tlock, marks metapages `nohomeok`, binds the lock to a metapage or in-memory inode, and initializes line-lock overlays based on inode, xtree, dtree, or data logging type. `txMaplock()` records allocation-map updates without a metapage. `txCommit()` sorts inodes by descending inode number to avoid deadlock, inherits anonymous tlocks, calls `diWrite()` to lock/log on-disk inode pages, emits typed log records through `txLog()`, writes the `LOG_COMMIT` record, waits or schedules group commit through `lmGroupCommit()`, forces careful updates when needed, updates maps for forced commits, releases tlocks for other transactions, and either unlocks immediately or leaves lazy cleanup to `jfs_lazycommit()`.

`txLog()` dispatches each tlock to `diLog()`, `dataLog()`, `dtLog()`, `xtLog()`, or `mapLog()`. These functions choose `LOG_REDOPAGE`, `LOG_NOREDOPAGE`, `LOG_NOREDOINOEXT`, or `LOG_UPDATEMAP`, prepare line vectors and maplocks, and disable lazy commit when the map update points directly into mutable xtree data. After commit durability, `txUpdateMap()` applies allocation and free operations to persistent and/or working maps, handles inode create/delete pmap updates, invalidates freed metapages, and clears XAD new/extended state where appropriate.

## State and persistence behavior
Transaction state is global in `TxAnchor`, `TxBlock`, and `TxLock`. `TxAnchor` tracks free transaction blocks, free locks, low-water waits, lock pressure, anonymous inode lists, and the lazy unlock queue. `tblock->xflag` carries commit intent such as sync, force, map update type, inode create/delete/truncate, lazy, page, and inode. `tlock->type` and line-lock overlays describe the metadata after-image or allocation-map operation to log. Persistent state changes occur in two stages: after-images and commit records are written to the journal first, then allocation maps and home metadata are allowed to reach disk in a replay-safe order.

## Dependencies and integration points
The file depends on JFS inode, dinode, imap, dmap, metapage, superblock, log manager, extent-tree, directory-tree, Linux vmalloc, kthreads, wait queues, freezer, and VFS inode state. It is called from most mutating JFS operations. It calls `lmLog()`/`lmGroupCommit()` for journal persistence, `metapage_nohomeok()`/`metapage_homeok()` for write ordering, `dbUpdatePMap()`/`dbFree()` for block maps, `diUpdatePMap()` for inode maps, and `jfs_flush_journal()` for pressure and barriers.

## Risks
This is one of the most concurrency-sensitive JFS files. Risks include exhausting transaction locks, deadlocking on page locks or inode commit mutexes, losing anonymous tlocks during transfer to real transactions, allowing lazy commits while maplocks point into mutable xtree pages, failing to clear `nohomeok`, freeing a tblock still referenced by lazy commit, or updating persistent maps before commit durability. The disabled pre-commit data flush notes a historical uninitialized-data exposure concern for non-journaled file data. Several invariants are enforced only by `assert()`/`BUG()` or debug dumps.

## Test signals
Signals include high-concurrency create/unlink/rename/truncate workloads, tlock exhaustion that wakes `jfsSyncThread`, lazy versus synchronous commit ordering, directory and xtree splits/merges, inode extent allocation/free, EA/ACL extent replacement, file deletion with zero links, truncation crash recovery, forced commits for imap updates, `txQuiesce()` during remount/freeze, abort paths after `diWrite()` failure, and proc debug counters for transaction starts, waits, lock allocation, and low-lock pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_txnmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_txnmgr.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_txnmgr.h

## Purpose
`jfs_txnmgr.h` defines the shared transaction-manager data structures, flags, lock overlays, commit descriptor, global tables, and exported transaction APIs. It is the contract between mutating JFS code, transaction commit, log manager, and metadata page handling.

## Important APIs, types, and functions
Important types are `struct tblock`, `struct tlock`, `struct lv`, `struct linelock`, `struct xtlock`, `struct maplock`, `struct xdlistlock`, and `struct commit`. Macros `tid_to_tblock()` and `lid_to_tlock()` index global `TxBlock` and `TxLock`. Flags include commit flags (`COMMIT_SYNC`, `COMMIT_FORCE`, `COMMIT_PMAP`, `COMMIT_WMAP`, `COMMIT_PWMAP`, `COMMIT_DELETE`, `COMMIT_TRUNCATE`, `COMMIT_CREATE`, `COMMIT_LAZY`, `COMMIT_PAGE`, `COMMIT_INODE`), tlock state/type/operation flags, and maplock allocation/free flags. Exported APIs include transaction begin/end/commit/abort, tlock/maplock allocation, line-lock extension, map free, EA logging, freelock cleanup, quiesce/resume, lazy commit, and sync thread entry points.

## Control flow
The header itself is declarative. Callers begin a transaction with `txBegin()`, obtain tlocks through `txLock()`/`txMaplock()`, add line vectors through `txLinelock()`, commit with `txCommit()`, and finish with `txEnd()`. The log manager uses the common leading fields of `struct tblock` as a log-sync block and group-commit state carrier.

## State and persistence behavior
`struct tblock` tracks transaction identity, lock list, log transaction id, commit queue linkage, commit LSN/page/eor, group-commit wait queue, and inode create/delete payload. `struct tlock` binds a transaction to a metapage or inode and stores a 48-byte overlay used as a line lock, xtree lock, or map lock. Maplock and xdlistlock overlays describe persistent and working map allocation/free operations that are applied only after the journal commit is durable.

## Dependencies and integration points
The header includes `jfs_logmgr.h`, so transaction records share log descriptor types and group commit flags. It depends on metapage, inode, extent, and JFS-specific lock users to interpret overlays correctly. The fixed sizes and comments about alignment matter for both 32-bit and 64-bit builds.

## Risks
The overlay design is compact but fragile: `struct linelock`, `struct xtlock`, `struct maplock`, and `struct xdlistlock` all occupy `tlock.lock`, so field growth or alignment changes can corrupt commit records. `tid_t` and `lid_t` are 16-bit, matching table limits and on-structure fields; increasing table sizes without changing the types would wrap. The common `logsyncblk` prefix in `tblock` must stay compatible with log manager list operations.

## Test signals
Build and runtime tests should stress every tlock type and operation flag: inode updates, xtree growth/truncation/free, dtree split/free, map-only EA/ACL changes, anonymous locks, lazy commits, and forced commits. Debug builds should watch lock overlay counts (`TLOCKSHORT`, `TLOCKLONG`) and assert that line-vector indexes never exceed their maximums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_txnmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_types.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_types.h

## Purpose
`jfs_types.h` defines basic JFS scalar IDs, endian-aware on-disk extent descriptors, directory component names, and DASD limit accounting helpers. It is intended to be the first JFS include in C files so core types are available consistently.

## Important APIs, types, and functions
The header defines `tid_t`, `lid_t`, `struct timestruc_t`, bit constants, `pxd_t`, `struct pxdlist`, `dxd_t`, `struct component_name`, and `struct dasd`. Inline helpers `PXDlength()`, `PXDaddress()`, `lengthPXD()`, and `addressPXD()` pack and unpack physical extents. DXD macros wrap PXD helpers and size conversion. DASD macros read and write 40-bit-ish limit/used counters split into high-byte and little-endian low-word fields.

## Control flow
This header is purely declarative and inline. Extent creators call `PXDlength()` and `PXDaddress()` or the DXD wrappers when constructing on-disk descriptors; readers call `lengthPXD()` and `addressPXD()` before doing allocation-map, metapage, or log arithmetic. Directory and unicode code use `struct component_name` as the in-kernel UCS name container.

## State and persistence behavior
`pxd_t` stores a 24-bit length and a 40-bit address split across `len_addr` and `addr2`. `dxd_t` persists extended attribute or data extent metadata with flags for inline, index, single extent, file-backed, or corrupt forms. `timestruc_t`, PXD, DXD, and DASD fields are little-endian on disk, so every arithmetic path must convert explicitly.

## Dependencies and integration points
The header depends on Linux integer types and NLS declarations. It is used throughout JFS by superblock, log, transaction, inode map, block map, xtree, xattr, unicode, and metapage code. It also underpins on-disk compatibility with fsck and OS/2-derived layout constraints.

## Risks
The PXD packing is easy to misuse because `len_addr` contains both length and high address bits. Lengths are masked to 24 bits; addresses beyond the supported bit split would truncate. Macros such as `setDASDLIMIT` and `setDASDUSED` are statement blocks without `do { } while (0)`, so callers need normal care in conditional contexts. Any change to `tid_t` or `lid_t` affects transaction table indexing and lock overlay alignment.

## Test signals
Unit-style tests should round-trip PXD and DXD lengths/addresses across boundary values, validate little-endian encodings, check DASD counter macros over 32-bit boundaries, and mount filesystems with EA, ACL, fsck, and log descriptors that exercise each DXD/PXD consumer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_umount.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_umount.c

## Purpose
`jfs_umount.c` implements full JFS unmount and read-write-to-read-only unmount cleanup. It flushes outstanding journal transactions, closes fileset and aggregate metadata maps, writes metadata home, marks the superblock clean, and closes/removes the filesystem from its journal.

## Important APIs, types, and functions
The public functions are `jfs_umount()` and `jfs_umount_rw()`. They call `jfs_flush_journal()`, `diUnmount()`, `diFreeSpecial()`, `dbUnmount()`, `dbSync()`, `diSync()`, `filemap_write_and_wait()`, `updateSuper()`, and `lmLogClose()`. State comes from `struct jfs_sb_info` fields `ipimap`, `ipaimap`, `ipaimap2`, `ipbmap`, `direct_inode`, and `log`.

## Control flow
`jfs_umount()` flushes the journal when mounted read-write, takes `LOG_LOCK(log)` while it clears special inode pointers so log sync cannot iterate `log->sb_list` and see half-cleared state, unmounts and frees fileset, secondary aggregate, aggregate inode, and block maps, writes the direct inode mapping, unlocks the log, marks the superblock clean, and closes the log. `jfs_umount_rw()` is the remount-read-only path: it flushes the journal, syncs block and inode maps, writes direct metadata, marks the superblock clean, and closes the log without tearing down all special inodes.

## State and persistence behavior
The key persistence guarantee is ordering: committed metadata must reach home locations before `updateSuper(sb, FM_CLEAN)` advertises a clean filesystem, and the log active filesystem list is updated only after metadata is safe. Full unmount nulls the special inode pointers in `sbi` after freeing them, which prevents later log sync iteration from treating freed inodes as live.

## Dependencies and integration points
The file depends on JFS incore state, filesystem flags, superblock helpers, dmap/imap close paths, log manager, metapage/direct mapping writeback, and debug logging. It is called from the VFS unmount/remount path and is the inverse of the setup in `jfs_mount.c`.

## Risks
Ordering mistakes can create falsely clean filesystems or stale active-journal entries. The `LOG_LOCK()` region exists to avoid a race with `write_special_inodes()` in log sync; future changes to log iteration or unmount cleanup need to preserve that race protection. Error handling is limited after map teardown starts, so failures from `lmLogClose()` are returned late but cannot fully roll back the unmount.

## Test signals
Tests should cover clean full unmount, read-only mounts where `sbi->log` is NULL, remount read-only, unmount under metadata-heavy workloads, injected writeback/log-close errors, filesystems with and without secondary aggregate maps, and races between sync, lazy commit, and unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_umount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_unicode.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_unicode.c

## Purpose
`jfs_unicode.c` implements filename conversion between JFS's internal UCS-2-ish `wchar_t`/little-endian Unicode names and Linux dentry byte strings using an optional NLS table. It allocates converted component names for lookup/create paths and converts on-disk Unicode names back to user-visible strings.

## Important APIs, types, and functions
Public functions are `jfs_strfromUCS_le()` and `get_UCSname()`. The private helper `jfs_strtoUCS()` converts byte strings to `wchar_t`. The code uses `struct nls_table` callbacks `uni2char()` and `char2uni()`, `struct component_name`, dentry names, `JFS_NAME_MAX`, and the mount's `JFS_SBI(sb)->nls_tab`.

## Control flow
`jfs_strfromUCS_le()` iterates over a little-endian Unicode input until `len` or NUL. With a codepage, it calls `uni2char()` and substitutes `?` on conversion failure. Without a codepage, it accepts only Latin-1 range characters, substitutes `?` for higher values, and rate-limits a warning to five total strings. `get_UCSname()` checks the dentry length, allocates a `wchar_t` buffer with `GFP_NOFS`, calls `jfs_strtoUCS()`, frees the buffer on conversion failure, and leaves `uniName->namlen` set on success.

## State and persistence behavior
The conversion functions do not persist data directly, but their output feeds directory operations and therefore determines on-disk name encoding. Returned UCS names are heap-owned and must be freed with `free_UCSname()`. The static `warn_again` counter persists across calls to limit log spam when mounted without an appropriate charset.

## Dependencies and integration points
The file depends on Linux slab allocation, NLS tables, JFS incore mount options, filesystem name length constants, unicode helpers in `jfs_unicode.h`, and debug logging. Directory lookup, create, rename, and readdir paths use these conversions around directory-tree keys and on-disk names.

## Risks
Without `iocharset`, non-Latin-1 names degrade to `?`, which can make names inaccessible or ambiguous. `jfs_strtoUCS()` returns negative NLS errors directly; callers must stop and free partial state. `get_UCSname()` uses byte length for allocation, which is safe for multibyte-to-UCS conversion when each input sequence produces at most one `wchar_t`, but malformed input can fail mid-string. Conversion behavior depends on the mounted NLS table and must match lookup/readdir symmetrically.

## Test signals
Tests should cover ASCII, Latin-1 without NLS, UTF-8 or other NLS mounts, invalid multibyte sequences, maximum-name boundary, embedded NUL behavior from dentries, high Unicode values warning/substitution, and round-trip lookup/readdir for non-ASCII filenames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_unicode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_unicode.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_unicode.h

## Purpose
`jfs_unicode.h` declares filename conversion APIs and provides inline Unicode string utilities for JFS directory names. It bridges JFS component names, little-endian on-disk Unicode arrays, Linux NLS conversion, and uppercase comparisons.

## Important APIs, types, and functions
The header declares `get_UCSname()` and `jfs_strfromUCS_le()`, defines `free_UCSname()`, and provides inline `UniStrcpy()`, `UniStrncpy_le()`, `UniStrncmp_le()`, `UniStrncpy_to_le()`, `UniStrncpy_from_le()`, `UniToupper()`, and `UniStrupr()`. It uses `NlsUniUpperTable` and `NlsUniUpperRange` from the local NLS UCS-2 data.

## Control flow
Callers allocate component names through `get_UCSname()`, free them with `free_UCSname()`, copy names to or from little-endian disk arrays with the `UniStrncpy_*` helpers, compare native and little-endian names with `UniStrncmp_le()`, and uppercase names in place with `UniStrupr()` for case-insensitive behavior where needed.

## State and persistence behavior
The string helpers operate in caller-provided buffers and do not allocate except through the declared C implementation. The little-endian copy helpers are persistence-sensitive because they write on-disk directory/name fields. `UniToupper()` is table-driven and returns the input unchanged when no uppercase mapping is found.

## Dependencies and integration points
The header depends on slab allocation, byteorder helpers, `nls_ucs2_data.h`, and `jfs_types.h`. It is used by directory and name-handling code as well as `jfs_unicode.c`.

## Risks
The copy helpers assume destination buffers are large enough for `n` entries and always pad with NULs after source termination. `UniStrncmp_le()` compares native `wchar_t` to little-endian `__le16`, so wrong pointer types can produce incorrect ordering. Uppercase mapping is limited to the included UCS-2 tables and may not match full modern Unicode case folding.

## Test signals
Tests should validate bounded copies with padding, endian conversions, comparisons at equal/prefix/different names, uppercase conversion for table and range entries, and directory lookup behavior on case-sensitive and non-ASCII names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_unicode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_xattr.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_xattr.h

## Purpose
`jfs_xattr.h` defines the on-disk extended-attribute list format, helper macros for walking variable-length EA records, maximum EA sizes, xattr operation declarations, and the optional security-label initialization hook.

## Important APIs, types, and functions
The persistent structures are `struct jfs_ea` and `struct jfs_ea_list`. Macros include `MAXEASIZE`, `MAXEALISTSIZE`, `EA_SIZE()`, `NEXT_EA()`, `FIRST_EA()`, `EALIST_SIZE()`, and `END_EALIST()`. Exported functions are `__jfs_setxattr()`, `__jfs_getxattr()`, `jfs_listxattr()`, `jfs_xattr_handlers`, and `jfs_init_security()` when `CONFIG_JFS_SECURITY` is enabled. Without security support, `jfs_init_security()` is an inline no-op.

## Control flow
Xattr implementation code includes this header to parse an EA list from its size header, start at `FIRST_EA()`, advance through records with `NEXT_EA()`, and stop at `END_EALIST()`. Set/get/list operations use the declarations here; inode creation calls `jfs_init_security()` to attach security attributes when configured.

## State and persistence behavior
Each EA stores an unused flag byte, name length, little-endian value length, and a flexible name field that includes a NUL terminator, with the value immediately following the name. The list begins with a little-endian total size. The macros compute sizes from on-disk fields, so validation in implementation code must ensure records remain inside `EALIST_SIZE()`.

## Dependencies and integration points
The header depends on Linux xattr APIs and JFS transaction IDs/inodes from included compile context. It integrates with transaction manager EA extent logging through `txEA()`, inode create security hooks, and VFS xattr handlers.

## Risks
Variable-length parsing is vulnerable to corrupt size, name length, or value length fields if callers do not bounds-check before using `NEXT_EA()`. `MAXEASIZE` is 65535, so callers must reject larger buffers. The name includes a null terminator despite a stored length for OS/2 compatibility; code that assumes ordinary C strings without checking `namelen` can misparse malformed attributes.

## Test signals
Tests should cover empty EA lists, multiple packed attributes, max-size attributes, corrupt list size and truncated records, names with expected NUL terminators, set/get/list VFS behavior, EA extent allocation/free logging, and security xattr initialization with and without `CONFIG_JFS_SECURITY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_xattr.h -->
