# Group Research: group_771_linux_sources_os_linux_linux_fs_jfs_jfs_logmgr_c_sources_os_linux_li_435644391078

Scope: `Docs/research_subset_a.md`. All listed JFS source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_logmgr.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_logmgr.c

Implements the JFS journal/log manager: log record packing, log page rollover, group commit, syncpoint advancement, log open/close/format, and private log-buffer I/O. It coordinates tightly with `jfs_txnmgr.c`, `jfs_metapage.c`, and recovery code via the on-disk log structures from `jfs_logmgr.h`.

Key entry points:
- `lmLog()` serializes log writes, attaches metapages and transaction blocks to the log sync list, writes one logical log record, and triggers `lmLogSync()` when the next sync threshold is crossed.
- `lmWriteRecord()` copies changed metadata ranges from tlocks into current log pages, appends an `lrd` descriptor, handles cross-page records, and queues COMMIT records for group commit.
- `lmNextPage()` finalizes/writes the current log page and allocates/initializes the next circular log page.
- `lmGroupCommit()`, `lmGCwrite()`, and `lmPostGC()` batch transactions whose COMMIT records share a log page, submit the page, wake synchronous waiters, or hand lazy commits to `txLazyUnlock()`.
- `jfs_syncpt()` and `lmLogSync()` flush special metadata inodes, compute the oldest unresolved logsync item, write `LOG_SYNCPT`, and enforce `log_SYNCBARRIER` when the log gets too full.
- `lmLogOpen()`, `open_inline_log()`, and `open_dummy_log()` open external, inline, or no-integrity logs. External logs are shared through `jfs_external_logs` and UUID-checked.
- `lmLogInit()` validates the log superblock, opens append mode at the recovered end, writes an initial syncpoint, marks the log mounted, and initializes sync/group-commit state.
- `lmLogClose()` and `lmLogShutdown()` flush outstanding journal work, mark the log clean, update the log superblock, and tear down buffers.
- `lmLogFormat()` writes a new log superblock and initializes circular log pages.
- `jfs_flush_journal()` forces queued commit records through the group commit path and can wait until all log and logsync work drains.
- `jfsIOWait()` is the kernel thread redriving log buffers that cannot be submitted from completion/interrupt-sensitive paths.

Important state and synchronization:
- `LOG_LOCK` serializes append-side log writes.
- `LOGGC_LOCK` protects the commit queue and group commit flags.
- `LOGSYNC_LOCK` protects `synclist`, metapage/tblock LSN state, and syncpoint advancement.
- `jfsLCacheLock` protects lbuf free/write queue state.
- `log_redrive_list` is a global redrive queue consumed by `jfsIOthread`.

Log buffer manager details:
- Each log owns preallocated `lbuf` buffers backed by pages, avoiding page-cache allocation deadlocks during journal activity.
- `lbmWrite()` maintains a circular FIFO write queue per log and submits only the head.
- `lbmIODone()` updates committed LSN, removes released buffers, redrives the next queued page, runs group-commit completion, and wakes synchronous waiters.
- `no_integrity` mode still runs journaling logic but bypasses actual block I/O by directly completing bios.

Risks and invariants:
- Correctness depends on strict ordering between COMMIT record write, group-commit completion, map updates, and metapage `homeok`.
- `lmPostGC()` may run from I/O completion context, so it carefully avoids blocking and redrives later work through `jfsIOthread`.
- Log wrap pressure activates a sync barrier; transactions must drain before new work resumes.
- Shared external journals rely on UUID and active filesystem slots in the log superblock.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_logmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_logmgr.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_logmgr.h

Defines the JFS journal on-disk formats, in-memory log state, log-buffer state, and log manager public API.

Core definitions:
- Log page size is fixed at `LOGPSIZE` 4096 bytes with `LOGPAGES` preallocated in-memory buffers per mounted filesystem.
- `struct logsuper` is the log superblock at page/block 1. It stores magic/version, state, size, block size, end LSN, log UUID, label, and up to `MAX_ACTIVE` filesystem UUIDs sharing an external journal.
- `struct logpage` is the journal data page layout: header, data area, and trailer. Header/trailer duplicate page sequence and EOR for recovery validation.
- `struct lrd` is the fixed-size log record descriptor placed after variable-length record data. It covers `LOG_COMMIT`, `LOG_SYNCPT`, `LOG_MOUNT`, redo/noredo page records, inode extent filters, and map update records.
- `struct lvd` describes logged line-vector data ranges.

In-memory structures:
- `struct jfs_log` contains active superblocks, journal block device file, circular log cursor, current lbuf, write lock, syncpoint fields, group-commit queue, sync list, write queue, UUID, and no-integrity flag.
- `struct lbuf` is a private log I/O buffer with queue links, page pointer, page offset, log page number, EOR/committed EOR, disk block, and completion wait queue.
- `struct logsyncblk` is the common prefix used by metapages and transaction blocks so both can be linked into `jfs_log.synclist`.

Flags and macros:
- Log flags include inline log, sync barrier, quiesce, and flush.
- Group commit flags describe queued, ready, committed, end-of-page, lazy, and error states.
- `logdiff()` computes circular distance from the current syncpoint.

Exports:
- Lifecycle: `lmLogOpen`, `lmLogClose`, `lmLogInit`, `lmLogShutdown`, `lmLogFormat`.
- Runtime: `lmGroupCommit`, `jfs_flush_journal`, `jfs_syncpt`, `jfsIOWait`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_logmgr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_metapage.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_metapage.c

Implements JFS metadata-page management on top of Linux folios. A metapage represents a filesystem metadata block or 4K metadata page, carries transaction/logsync state, and supplies custom address-space operations for metadata inodes.

Core responsibilities:
- Allocate/free `struct metapage` objects from a slab-backed mempool.
- Attach one or more metapages to a folio. When `PAGE_SIZE > PSIZE`, a `meta_anchor` tracks multiple metapages and outstanding I/O count/status for the folio.
- Provide locking around each metapage while temporarily dropping and reacquiring the folio lock to avoid deadlock.
- Resolve metadata file logical blocks to physical blocks through `xtLookup()` in `metapage_get_blocks()`.
- Read metadata folios with bios and complete them through `metapage_read_end_io()`.
- Write dirty metapages with contiguous-bio coalescing in `metapage_write_folio()`.
- Remove written metapages from the log sync list after home write completion.
- Release, invalidate, and migrate folios containing metapage private state.

Key exported operations:
- `metapage_init()` / `metapage_exit()` create and destroy the slab/mempool.
- `__get_metapage()` maps or reads the target folio, finds/creates a metapage at the requested offset, validates logical size, locks it, and optionally zeroes it for new metadata.
- `grab_metapage()` adds a reference and locks an existing metapage.
- `release_metapage()` unlocks, decrements references, marks dirty/sync, writes synchronously if needed, removes logsync state if clean, and drops unused metapages.
- `force_metapage()` forces synchronous writeback of a metadata page.
- `hold_metapage()` / `put_metapage()` support callers that need to hold the folio lock across metapage homeok transitions.
- `__invalidate_metapages()` marks direct-inode metapages in an extent as discarded and removes any logsync state.

Address-space integration:
- `jfs_metapage_aops` provides `read_folio`, `writepages`, `release_folio`, `invalidate_folio`, `dirty_folio`, and optional `migrate_folio`.
- Writeback skips `nohomeok` metapages unless forcewrite is set, redirties them, and may flush the journal to unblock them.

Important invariants:
- Dirty metadata protected by a transaction is marked `nohomeok`; writeback must not send it home until the journal commit is durable.
- `mp->lsn` membership in a log sync list must be cleared only under the corresponding log sync lock.
- Folio private data may be either a single metapage or a `meta_anchor` depending on `MPS_PER_PAGE`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_metapage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_metapage.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_metapage.h

Declares the JFS metapage abstraction and helper APIs used throughout metadata, transaction, and log code.

`struct metapage` begins with the same logsync prefix layout as `struct logsyncblk`, allowing metapages to be linked directly into `jfs_log.synclist`. It then stores flag bits, reference count, data pointer, block index, wait queue, backing folio, superblock, logical size, committed LSN, no-home-write counter, and owning log pointer.

Flags:
- `META_locked`: per-metapage lock.
- `META_dirty`: metadata needs writeback.
- `META_sync`: write synchronously on release.
- `META_discard`: page should not be reused/written.
- `META_forcewrite`: override `nohomeok`.
- `META_io`: writeback in progress.

Exports:
- Lifecycle: `metapage_init`, `metapage_exit`.
- Acquisition: `read_metapage()`, `get_metapage()`, `__get_metapage()`.
- Release/write helpers: `release_metapage`, `grab_metapage`, `force_metapage`, `write_metapage`, `flush_metapage`, `discard_metapage`.
- Transaction coordination: `metapage_nohomeok`, `metapage_homeok`, `_metapage_homeok`, `metapage_wait_for_io`.
- Extent invalidation helpers for PXD, DXD, and XAD descriptors.

Integration:
- Exposes `jfs_metapage_aops` for metadata inode mappings.
- The inline helpers encode the critical journal invariant that home writes are blocked while `nohomeok` is nonzero.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_metapage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_mount.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_mount.c

Implements JFS mount and read-write mount setup. It validates the aggregate superblock, opens special metadata inodes, initializes inode/block maps, opens the journal, marks the filesystem mounted, and writes a mount log record.

Mount flow:
- `jfs_mount()` calls `chkSuper()`, reads the aggregate inode map inode (`AGGREGATE_I`), mounts the aggregate inode map, reads and mounts the block map (`BMAP_I`), optionally reads/mounts the secondary aggregate inode map, and finally reads/mounts the fileset inode map (`FILESYSTEM_I`).
- Error paths unwind in reverse order using `diUnmount`, `diFreeSpecial`, and `dbUnmount`.

Read-write mount/remount:
- `jfs_mount_rw()` revalidates clean state on remount, truncates cached imap/bmap pages so fsck-updated maps are reread, remounts maps, opens the log with `lmLogOpen()`, updates the superblock to mounted/dirty state, and emits a `LOG_MOUNT` record.

Superblock handling:
- `chkSuper()` reads primary or secondary superblock through `readSuper()`, validates magic/version, enforces 4K JFS block size, checks state for read-write mounts, repairs in-memory flags for secondary AIT/AIM validity and group commit, computes JFS block geometry, copies UUID/log/fsck descriptors, and records inline/external log configuration.
- `updateSuper()` writes the mount state synchronously, with special `JFS_NOINTEGRITY` handling that preserves prior state externally while treating the live mount as dirty.
- `readSuper()` tries primary then secondary superblock offsets.

Journal mount record:
- `logMOUNT()` writes a `LOG_MOUNT` record with aggregate device identity. Recovery uses this boundary to avoid replaying older records for the same filesystem past the mount point.

Important invariants:
- Read-write mount requires clean filesystem state unless mounted read-only.
- JFS Linux support here requires `PSIZE` block size.
- Map initialization precedes journal activation; superblock dirtying follows successful journal open.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_superblock.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_superblock.h

Defines the on-disk JFS aggregate superblock layout and declares mount/superblock-facing functions.

`struct jfs_superblock` includes:
- Magic/version, aggregate size, logical and physical block sizes.
- Allocation group size, flags, state, compression flag.
- Secondary aggregate inode table/map descriptors.
- External log device/serial or inline log extent.
- Fsck workspace and service log fields.
- Extendfs staging fields.
- Volume UUID/label and external log UUID.

Constants:
- `JFS_MAGIC` is `"JFS1"`.
- `JFS_VERSION` is `2`.
- `LV_NAME_SIZE` preserves OS/2 boot-sector volume-name compatibility.

Exports:
- Superblock I/O/state: `readSuper`, `updateSuper`, `jfs_error`.
- Mount lifecycle: `jfs_mount`, `jfs_mount_rw`, `jfs_umount`, `jfs_umount_rw`, `jfs_extendfs`.
- Background task globals: `jfsIOthread`, `jfsSyncThread`.

Integration:
- Included by mount, unmount, log, metapage, and transaction code to share on-disk aggregate state and lifecycle hooks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_superblock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_txnmgr.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_txnmgr.c

Implements JFS transaction management: transaction/tlock allocation, metadata locking, log record generation, commit sequencing, persistent/working map updates, lazy commit, quiesce, and tlock-starvation relief.

Global state:
- `TxAnchor` tracks free transaction IDs, free lock words, wait queues, tlock pressure, lazy-commit queues, and anonymous transaction inode lists.
- `TxBlock` is the transaction block table; `TxLock` is the transaction lock table.
- Tunables `nTxBlock` and `nTxLock` size the tables, bounded to 65536 entries.
- Low/high/very-high tlock watermarks wake `jfsSyncThread` and throttle new transactions.

Initialization:
- `txInit()` sizes and allocates transaction and lock tables, initializes wait queues/lists, and builds freelists.
- `txExit()` frees the tables.

Transaction lifecycle:
- `txBegin()` waits for log barriers/quiesce/tlock pressure/free tblocks, allocates a tblock, assigns a log transaction id, and increments log activity.
- `txBeginAnon()` gates anonymous metadata updates on barriers and tlock pressure without allocating a tblock.
- `txEnd()` wakes waiters, returns a tblock to the freelist, and if the last active transaction drains a sync barrier, writes a hard syncpoint and wakes blocked starters.
- `txAbort()` frees tlocks, clears metapage bindings/logsync state, and can mark the filesystem dirty.

Locking:
- `txLock()` binds a tlock to a metapage or in-memory inode, handles directory xtree special cases, transfers anonymous tlocks into a real transaction, initializes linelock/xtlock state, and waits only for expected aggregate-map conflicts.
- `txMaplock()` creates map-update-only tlocks for extent allocation/free work.
- `txLinelock()` chains additional line-vector lock storage.
- `txFreelock()` frees anonymous tlocks marked `tlckFREELOCK`.

Commit path:
- `txCommit()` sorts inodes by descending inode number, transfers anonymous tlocks, writes on-disk inode tlocks via `diWrite()`, dispatches all tlocks through `txLog()`, writes the COMMIT record, waits or queues group commit, optionally forces careful-update pages, updates maps, releases tlocks/metapages, and resets inode commit state.
- `txLog()` dispatches by tlock type to `xtLog`, `dtLog`, `diLog`, `mapLog`, or `dataLog`.
- `diLog()` logs inode after-images or freed inode extents.
- `dataLog()` logs directory table/data metapages and discards obsolete inline table pages.
- `dtLog()` logs directory tree page after-images, new/extended pages, noredo records, and block-map updates.
- `xtLog()` handles xtree growth, deletion, truncation, relocation-related map records, lazy-commit-safe extent snapshots, and force-synchronous cases when map data points into mutable xtree pages.
- `mapLog()` logs standalone allocation/free map updates, including relocation source extents.
- `txEA()` records extended attribute/ACL extent allocation/free maplocks or inline-EA commit flags.

Map and page completion:
- `txForce()` reverses tlock order for careful update and synchronously writes selected metapages.
- `txUpdateMap()` applies persistent and/or working map changes for block allocation/free and inode create/delete.
- `txAllocPMap()` marks allocated extents in the persistent block map and clears new/extended XAD flags.
- `txFreeMap()` frees extents from persistent and/or working maps.
- `txRelease()` unbinds tlocks from metapages before home writes are allowed.
- `txUnlock()` marks metapages homeok, propagates committed LSNs, removes tblocks from the log sync list, and frees tlocks.

Background paths:
- `txLazyUnlock()` queues committed lazy transactions.
- `jfs_lazycommit()` processes the lazy unlock queue while preserving per-superblock transaction order.
- `txLazyCommit()` updates maps, marks group commit complete, wakes waiters, unlocks tlocks, and ends lazy transactions.
- `txQuiesce()` blocks new transactions and commits anonymous inodes.
- `txResume()` clears quiesce and wakes waiters.
- `jfs_sync()` runs when tlocks are low, committing inodes on the anonymous transaction list.

Important invariants:
- Tlock list order matters for truncate and map update correctness.
- Lazy commit is disabled when maplocks point into mutable xtree pages that might change before `txUpdateMap()`.
- Log durability precedes home writes and persistent map updates.
- Allocation map pages inherit transaction LSNs so syncpoints cannot advance past required recovery information prematurely.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_txnmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_txnmgr.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_txnmgr.h

Declares transaction manager structures, flags, lock overlays, and public APIs.

Primary structures:
- `struct tblock` is a transaction block. It shares the logsync prefix layout, stores superblock, tlock chain, wait queues, log transaction id, group-commit queue state, commit LSN/page/EOR, and create/delete payload.
- `struct tlock` is a transaction lock word bound to a metapage or inode, with overlay storage for line locks, xtree locks, or map locks.
- `struct linelock` describes modified byte-line ranges that `lmWriteRecord()` copies into the journal.
- `struct xtlock` extends linelock data with xtree watermarks and inline PXD storage.
- `struct maplock`, `struct xdlistlock`, and `pxd_lock` encode extent allocation/free work for later map updates.
- `struct commit` bundles commit-time context and an `lrd`.

Flags:
- Commit flags cover sync/force/lazy, map update type, create/delete/truncate, metapage, and inode commits.
- Tlock flags distinguish page/inode/line locks, logged state, map updates, directory locks, free locks, writepage, and freepage.
- Tlock type/operation bits distinguish inode, xtree, dtree, map, EA/ACL, data, btree root, grow, truncate, relocate, new/free/relink operations.
- Maplock flags distinguish allocation/free of XAD/PXD singletons or lists.

Exports:
- Initialization: `txInit`, `txExit`.
- Transaction lifecycle: `txBegin`, `txBeginAnon`, `txEnd`, `txCommit`, `txAbort`.
- Locking/map helpers: `txLock`, `txMaplock`, `txLinelock`, `txFreeMap`, `txEA`, `txFreelock`.
- Journal bridge: `lmLog`.
- Background/quiesce: `txQuiesce`, `txResume`, `txLazyUnlock`, `jfs_lazycommit`, `jfs_sync`.

Integration:
- Includes `jfs_logmgr.h`, so transaction code can share log record types and group-commit state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_txnmgr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_types.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_types.h

Provides basic JFS type definitions and compact descriptor helpers shared across the filesystem.

Key types:
- `tid_t` and `lid_t` are 16-bit transaction and lock identifiers. Comments warn that widening them affects transaction lock overlay layout.
- `struct timestruc_t` is the JFS little-endian on-disk time pair.
- `pxd_t` is the physical extent descriptor with 24 bits of length and a 40-bit address split across two little-endian fields.
- `struct pxdlist` stores a fixed stack of PXD descriptors up to `MAXTREEHEIGHT`.
- `dxd_t` is a data extent descriptor for inline, extent, index, file, or corrupt EA/ACL-style data.
- `struct component_name` stores a UCS name and length for directory operations.
- `struct dasd` stores OS/2-compatible directory DASD quota/usage fields.

Helpers:
- `PXDlength`, `PXDaddress`, `lengthPXD`, and `addressPXD` pack/unpack PXD fields.
- DXD macros wrap PXD helpers and size conversion.
- DASD macros pack/unpack 40-bit limit/used values.

Integration:
- Used by superblock, log records, inode/extent trees, EA descriptors, Unicode name handling, and transaction maplocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_umount.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_umount.c

Implements full unmount and read-write-to-read-only unmount handling for JFS.

`jfs_umount()`:
- Flushes outstanding journal work with `jfs_flush_journal(log, 2)` when mounted read-write.
- Takes `LOG_LOCK` while clearing special inode pointers so `write_special_inodes()` in the log sync path cannot see partially torn-down `sbi` state.
- Unmounts and frees the fileset inode map, secondary aggregate inode map, primary aggregate inode map, and block map.
- Flushes direct metadata mapping pages before marking the filesystem clean.
- Calls `updateSuper(sb, FM_CLEAN)` and `lmLogClose()` when a log is active.

`jfs_umount_rw()`:
- Used when remounting read-only from read-write.
- Flushes the journal, syncs block and inode maps, writes all direct metadata pages, marks the superblock clean, and closes the log.

Important invariant:
- Metadata home writes must reach disk before the superblock is marked clean and before the filesystem is removed from the active journal list.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_umount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_unicode.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_unicode.c

Implements filename conversion between JFS on-disk little-endian UCS-2 and Linux dentry byte strings.

Functions:
- `jfs_strfromUCS_le()` converts little-endian UCS-2 to a character string. With an NLS table it uses `uni2char`; without one it falls back to Latin-1-compatible single-byte characters and substitutes `?` for non-Latin-1, warning up to five times globally.
- `jfs_strtoUCS()` converts byte strings to native `wchar_t` using `char2uni` when a codepage is mounted, or direct byte widening otherwise.
- `get_UCSname()` validates `JFS_NAME_MAX`, allocates a UCS buffer for a dentry name, converts it using the mounted NLS table, and returns errors for allocation or conversion failure.

Integration:
- Directory lookup/create paths use `component_name` values produced here.
- Mounted `iocharset`/NLS choice controls round-trip behavior for non-ASCII names.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_unicode.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_unicode.h

Declares Unicode conversion APIs and provides inline UCS string helpers for JFS.

Exports:
- `get_UCSname()` allocates/converts a dentry name to JFS UCS form.
- `jfs_strfromUCS_le()` converts little-endian on-disk UCS strings to byte strings.
- `free_UCSname()` frees a `component_name` buffer.

Inline helpers:
- `UniStrcpy()` copies native `wchar_t` strings.
- `UniStrncpy_le()` copies/pads little-endian UCS strings.
- `UniStrncmp_le()` compares native UCS against little-endian UCS.
- `UniStrncpy_to_le()` and `UniStrncpy_from_le()` convert while copying/padding.
- `UniToupper()` uppercases using Linux UCS-2 NLS tables.
- `UniStrupr()` uppercases an in-place native UCS string.

Integration:
- Used by directory name comparison, case folding, dentry conversion, and on-disk directory entry handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_unicode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_xattr.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_xattr.h

Defines JFS extended attribute on-disk list structures and xattr/security entry points.

On-disk structures:
- `struct jfs_ea` stores one attribute with flag, name length, little-endian value length, and a flexible name field. The name includes a null terminator for OS/2 compatibility; the value follows immediately.
- `struct jfs_ea_list` stores total list size followed by packed `jfs_ea` entries.

Macros:
- `MAXEASIZE` and `MAXEALISTSIZE` cap EA storage at 65535 bytes.
- `EA_SIZE`, `NEXT_EA`, `FIRST_EA`, `EALIST_SIZE`, and `END_EALIST` walk packed EA lists.

Exports:
- `__jfs_setxattr`, `__jfs_getxattr`, `jfs_listxattr`.
- `jfs_xattr_handlers`.
- `jfs_init_security()` when `CONFIG_JFS_SECURITY` is enabled, otherwise a no-op inline.

Integration:
- Transaction-aware xattr updates receive a `tid_t`, tying EA storage changes into JFS commit and map update machinery.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_xattr.h -->