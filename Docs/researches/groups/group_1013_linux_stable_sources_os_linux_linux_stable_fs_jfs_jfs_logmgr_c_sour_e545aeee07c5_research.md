# Group Research: group_1013_linux_stable_sources_os_linux_linux_stable_fs_jfs_jfs_logmgr_c_sour_e545aeee07c5

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux-stable`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_logmgr.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_logmgr.c

## Role

Implements the JFS log manager: journal open/close/init/shutdown, log record append, log page buffering, group commit, sync point advancement, journal flush, and log formatting.

## Main Responsibilities

- `lmLog()` serializes append writes with `LOG_LOCK`, updates metapage/tblock recovery LSN state, emits the record, and advances sync points when `nextsync` is reached.
- `lmWriteRecord()` packs changed line data and the trailing `struct lrd` descriptor into 4 KiB log pages, splitting data/descriptors across pages as needed.
- `lmNextPage()` finalizes the current log page, queues or writes it according to group-commit state, allocates the next circular log page, and advances log sequence page numbers.
- `lmGroupCommit()`, `lmGCwrite()`, and `lmPostGC()` batch transactions whose `LOG_COMMIT` records land on the same log page, write the page, wake synchronous waiters, and hand lazy commits to the transaction manager.
- `lmLogOpen()` supports external shared journals, inline journals, and a dummy no-integrity journal.
- `lmLogInit()` validates the journal superblock, requires `LOGREDONE`, writes an initial `LOG_SYNCPT`, marks the log `LOGMOUNT`, and initializes private log-buffer state.
- `lmLogShutdown()` drains pending commits, writes a final sync point, marks the journal `LOGREDONE`, records the final end LSN, and tears down private buffers.
- `jfs_flush_journal()` forces queued commit records; with full waits it also writes special metadata inodes and waits for `cqueue`/`synclist` drainage.
- `lmLogFormat()` initializes the log superblock and circular data pages, including sequence numbers arranged for log-end discovery.

## Important State and Synchronization

- `LOG_LOCK(log)` serializes log append and sync-point updates.
- `LOGGC_LOCK(log)` protects group commit queues and transaction commit state.
- `LOGSYNC_LOCK(log)` protects the shared log sync list containing both metapages and tblocks.
- `jfs_log_mutex` protects global external-journal discovery and the singleton `dummy_log`.
- `jfsLCacheLock` protects each log’s private `lbuf` freelist and write queue.
- `log_redrive_list` plus `jfsIOWait()` defers log I/O redrive out of interrupt context.

## Interactions

- Consumes `struct tblock`, `struct tlock`, and `struct metapage` state from transaction and metapage code.
- Calls `write_special_inodes()` across all superblocks sharing a journal to flush map/direct-inode metadata before sync points.
- Updates active filesystem UUID slots in `struct logsuper` through `lmLogFileSystem()`.
- Calls `txLazyUnlock()` after commit-record I/O for transactions that can complete in the lazy commit thread.

## Correctness Notes

- Normal journal open requires recovery/logredo to have left the journal in `LOGREDONE`.
- `LOG_SYNCPT` records establish replay boundaries and free space accounting.
- Partial-page group commits keep the buffer queued until a later full-page write or explicit redrive.
- `JFS_NOINTEGRITY` still runs journal state machinery but completes bios without disk I/O.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_logmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_logmgr.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_logmgr.h

## Role

Defines JFS journal on-disk formats, in-memory log structures, log buffer structures, record types, group-commit flags, sync-list layout, and log-manager entry points.

## Key Definitions

- Log geometry constants: `LOGPSIZE`, `L2LOGPSIZE`, `LOGPAGES`, `LOGSUPER_B`, `LOGSTART_B`.
- `struct logsuper`: journal magic/version, serial, size, block size, state, end LSN, UUID, label, and `MAX_ACTIVE` filesystem UUID slots.
- `struct logpage`: matched header/trailer page and EOR fields used by recovery to detect incomplete or split writes.
- `struct lrd`: fixed-size log record descriptor with variants for commit, sync point, mount, redo/no-redo page, inode extent no-redo, map updates, no-redo file, and new page.
- `struct lvd`: line-vector descriptor copied after logged data by `lmWriteRecord()`.
- `struct jfs_log`: active superblock list, journal device, current page/EOR, append lock, group commit queue, sync list, write queue, UUID, and no-integrity state.
- `struct lbuf`: private log I/O page descriptor outside the page cache.
- `struct logsyncblk`: common prefix allowing tblocks and metapages to share `log->synclist`.

## Public Interfaces

Declares `lmLogOpen`, `lmLogClose`, `lmLogShutdown`, `lmLogInit`, `lmLogFormat`, `lmGroupCommit`, `lmLog`, `jfsIOWait`, `jfs_flush_journal`, and `jfs_syncpt`.

## Design Notes

This header is the transaction/log/recovery contract. The shared `logsyncblk` prefix is especially important because recovery-age tracking depends on mixing transaction blocks and metapages on one ordered sync list.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_logmgr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_metapage.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_metapage.c

## Role

Implements JFS metadata-page caching on top of Linux folios, including metapage allocation, locking, read/write address-space operations, journal sync-list interaction, migration, release, and invalidation.

## Main Responsibilities

- `metapage_init()` creates the `jfs_mp` slab cache and mempool; `metapage_exit()` destroys them.
- Folio private data stores either a single metapage or a `meta_anchor` for multiple 4 KiB JFS metapages per folio.
- `__get_metapage()` locates or creates a metapage for a logical block, optionally using the direct inode for absolute block access, locks it, validates logical size, and zeroes newly allocated metadata.
- `metapage_read_folio()` maps metadata blocks through `xtLookup()` unless using direct mappings, then submits bios for mapped ranges.
- `metapage_write_folio()` writes dirty metapages, redirties `nohomeok` pages unless force-write is set, builds contiguous bios, and tracks `META_io`.
- `last_write_complete()` clears home-I/O state and removes written metapages from the log sync list.
- `release_metapage()` unlocks and drops references, marks folios dirty, performs synchronous writes for `META_sync`, removes clean logged pages from log sync, and frees unused metapages.
- `force_metapage()` synchronously writes one metapage home, overriding `nohomeok`.
- `__invalidate_metapages()` marks direct-mapped metapages discarded and clears dirty/logsync state for freed extents.

## Important State

- `META_locked`: metapage-level lock separate from the folio lock.
- `META_dirty`: metadata changed and needs home writeback.
- `META_sync`: release should force synchronous write.
- `META_discard`: metadata is invalidated and must not be reused as valid old contents.
- `META_forcewrite`: permits home write despite `nohomeok`.
- `META_io`: home I/O is in progress.
- `nohomeok`: journal ordering gate preventing metadata home write before its log commit is safe.

## Interactions

- Uses `LOGSYNC_LOCK` to remove metapages from `log->synclist`.
- Calls `jfs_flush_journal()` when writeback encounters `nohomeok` pages and no group commit is active.
- Provides `jfs_metapage_aops` for metadata mappings.
- Uses `xtLookup()` for metadata file block translation except for direct/absolute mappings.

## Correctness Notes

- Multiple metapages per folio require `meta_anchor` aggregation for private pointers and I/O completion.
- Write completion deliberately avoids dropping metapages because the folio is not locked there.
- `__get_metapage()` treats metadata crossing a folio boundary as a hard error.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_metapage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_metapage.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_metapage.h

## Role

Declares `struct metapage`, metapage flags, public metapage operations, convenience wrappers, and extent invalidation macros.

## Key Definitions

- `struct metapage` starts with the same log-sync prefix shape used by `struct logsyncblk`, then stores flags, refcount, data pointer, block index, wait queue, folio, superblock, logical size, commit LSN, `nohomeok`, and journal pointer.
- Flags include `META_locked`, `META_dirty`, `META_sync`, `META_discard`, `META_forcewrite`, and `META_io`.
- `read_metapage()` and `get_metapage()` wrap `__get_metapage()` for existing versus new metadata.
- `write_metapage()`, `flush_metapage()`, and `discard_metapage()` are inline state transitions followed by release.
- `metapage_nohomeok()` pins the folio, marks metadata dirty, and waits for writeback so journal ordering can block unsafe home writes.
- `_metapage_homeok()` and `metapage_homeok()` decrement `nohomeok` and release the folio pin once log ordering permits home writeback.
- `metapage_wait_for_io()` serializes against home I/O for logsync-list operations.
- `invalidate_pxd_metapages`, `invalidate_dxd_metapages`, and `invalidate_xad_metapages` map extent descriptors to `__invalidate_metapages()`.

## Design Notes

This header exposes the core JFS metadata ordering mechanism: transaction code marks pages `nohomeok` while journal records are pending, then releases them for home writeback after commit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_metapage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_mount.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_mount.c

## Role

Implements JFS aggregate/fileset mount setup, read-write mount completion, superblock validation/update, raw superblock reads, and mount log record emission.

## Main Responsibilities

- `jfs_mount()` validates the superblock, opens aggregate inode allocation map, aggregate block map, optional secondary aggregate inode map, and fileset inode allocation map.
- Error paths unwind mounted maps and special inodes in reverse order.
- `jfs_mount_rw()` handles read-write mount and read-only-to-read-write remount:
  - Revalidates clean state on remount.
  - Truncates cached inode/block map pages.
  - Remounts imap and bmap.
  - Opens the journal via `lmLogOpen()`.
  - Updates the superblock to `FM_MOUNT`.
  - Writes a `LOG_MOUNT` record.
- `chkSuper()` reads and validates the superblock magic/version, requires 4 KiB block size, rejects dirty read-write mounts, validates secondary AIM/AIT descriptors, enables group commit, and copies mount parameters into `jfs_sb_info`.
- `updateSuper()` synchronously writes filesystem state changes and records journal device/serial on mount.
- `readSuper()` tries the primary superblock first, then the replicated secondary.
- `logMOUNT()` writes a mount record so replay does not cross this aggregate mount boundary.

## Important Interactions

- Uses `diReadSpecial`, `diMount`, `diUnmount`, and `diFreeSpecial` for internal inode maps.
- Uses `dbMount` and `dbUnmount` for the aggregate block map.
- Uses `lmLogOpen`, `lmLogClose`, and `lmLog` from the log manager.
- Populates `sbi->logpxd`, `logdev`, `loguuid`, `fsckpxd`, `ait2`, `uuid`, and block-size derived fields.

## Correctness Notes

- Linux JFS supports only `PSIZE` 4 KiB filesystem block size in this path.
- Dirty filesystems are rejected for read-write mount.
- No-integrity mounts preserve prior state separately while presenting dirty semantics internally.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_superblock.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_superblock.h

## Role

Defines the on-disk JFS superblock layout and declares mount, unmount, superblock, extendfs, and background-thread interfaces.

## Key Definitions

- `JFS_MAGIC` is `"JFS1"` and `JFS_VERSION` is `2`.
- `LV_NAME_SIZE` preserves the OS/2 boot-sector name size expectation.
- `struct jfs_superblock` stores magic, version, aggregate size, block sizes, allocation group size, flags, state, compression fields, secondary AIM/AIT descriptors, journal descriptor/device/serial/UUID, fsck workspace, timestamps, filesystem UUID, and label.

## Public Interfaces

Declares `readSuper`, `updateSuper`, `jfs_error`, `jfs_mount`, `jfs_mount_rw`, `jfs_umount`, `jfs_umount_rw`, `jfs_extendfs`, `jfsIOthread`, and `jfsSyncThread`.

## Design Notes

This header is the shared mount/unmount/log/growth contract. On-disk fields use explicit little-endian types.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_superblock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_txnmgr.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_txnmgr.c

## Role

Implements the JFS transaction manager: transaction/tlock pools, transaction begin/end, metadata locking, commit logging, allocation-map updates, abort, lazy commit, quiesce/resume, and anonymous-transaction sync.

## Main Responsibilities

- `txInit()` sizes and allocates global `TxBlock` and `TxLock` tables, initializes tlock watermarks, wait queues, anonymous lists, and lazy commit queue.
- `txBegin()` starts a transaction while respecting log sync barriers, quiesce state, tlock pressure, and free tblock availability.
- `txBeginAnon()` gates anonymous updates on the same barrier and tlock-pressure conditions.
- `txEnd()` returns the tblock to the free list, handles lazy-commit handoff, decrements active transaction count, and clears log sync barriers after hard sync.
- `txLock()` binds a tlock to a metapage or inode, handles directory xtree special locking, transfers anonymous tlocks to real transactions, marks metapages `nohomeok`, and initializes line/xtree lock overlays.
- `txMaplock()` creates map-only tlocks for extent allocation/free records.
- `txLinelock()` appends extra line-vector capacity when a tlock exceeds inline line descriptors.
- `txCommit()` sorts inodes by descending inode number, absorbs anonymous tlocks, writes disk inode state through `diWrite()`, logs all tlocks, writes `LOG_COMMIT`, runs group commit, optionally forces careful-update pages, updates maps, releases locks, and resets inode commit state.
- `txLog()` dispatches each tlock to `diLog`, `dataLog`, `dtLog`, `xtLog`, or `mapLog`.
- `txUpdateMap()` applies allocation/free effects to persistent and working maps, handles inode create/delete map updates, and discards freed metadata pages.
- `txAbort()` frees transaction locks, resets metapage log sync state, and can mark the filesystem dirty.
- `jfs_lazycommit()` drains committed transactions from `TxAnchor.unlock_queue` while preserving per-superblock ordering.
- `jfs_sync()` commits inodes with anonymous tlocks when tlocks are scarce.
- `txQuiesce()` blocks new transactions and forces anonymous transactions to commit; `txResume()` clears quiesce.

## Logging Helpers

- `diLog()` logs inode after-images or inode extent no-redo records and prepares bmap updates.
- `dataLog()` logs directory table data pages, with special handling when inline directory tables are truncated.
- `dtLog()` logs dtree after-images, no-redo records for freed pages, and maplock updates for page allocation/free.
- `xtLog()` handles xtree growth, free, truncate, relocation, root cases, and lazy-commit copy-versus-force decisions for extent lists.
- `mapLog()` logs block map update records for relocation, EA/ACL, and other data extent changes.
- `txEA()` prepares maplocks for external EA/ACL extent allocation/free and marks inline EA commits.

## Important State and Synchronization

- `jfsTxnLock` protects free tblock/tlock lists, anonymous transaction lists, and transaction wait queues.
- `TxAnchor.LazyLock` protects the lazy unlock queue.
- `jfs_tlocks_low` wakes `jfsSyncThread` and changes group-commit behavior under tlock pressure.
- `tlock.lock` is a 48-byte overlay used as `linelock`, `xtlock`, `maplock`, or `xdlistlock`.
- `COMMIT_LAZY` lets group commit return before map updates and lock release, which are later completed by the lazy commit thread.
- `COMMIT_FORCE` performs careful synchronous pageout and map update in caller context.

## Correctness Notes

- Metapages are marked `nohomeok` before logging so home writeback cannot beat the journal commit.
- Lazy commits copy small extent lists into the tlock overlay; larger lists force synchronous commit because they point into mutable xtree pages.
- Inode commit order is sorted to reduce deadlock risk.
- Truncation and map-update paths distinguish persistent map and working map updates carefully.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_txnmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_txnmgr.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_txnmgr.h

## Role

Defines transaction-manager data structures, commit flags, tlock formats, maplock overlays, and public transaction entry points.

## Key Definitions

- `tid_to_tblock()` and `lid_to_tlock()` index global transaction and lock tables.
- `struct tblock` represents an active transaction and embeds the logsync prefix, tlock list, wait queues, log transaction id, group commit state, commit page/EOR, and create/delete-specific union state.
- Commit flags include sync, force, flush, persistent/working-map update modes, create/delete/truncate/lazy, and page/inode element markers.
- `struct tlock` binds a transaction to a metapage or inode and contains the 48-byte overlay region.
- Tlock flags describe page/inode locks, line locks, logged state, map-update state, directory state, writepage/freepage state, and free-lock state.
- Tlock types distinguish inode, xtree, dtree, map, EA, ACL, data, and B-tree root updates.
- `struct linelock` and `struct lv` encode changed line ranges for after-image logging.
- `struct xtlock` stores xtree line state plus low/high/truncate watermarks and inline PXD storage.
- `struct maplock` and `struct xdlistlock` encode allocation/free map updates using inline PXDs or XAD/PXD lists.
- `struct commit` packages commit arguments and a reusable log record descriptor.

## Public Interfaces

Declares transaction lifecycle, lock allocation, map update, EA logging, lazy commit, sync daemon, and quiesce/resume functions.

## Design Notes

The 48-byte `tlock.lock` overlay is central to JFS transaction design. Alignment and size compatibility across lock variants are broad contracts with logging and map update code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_txnmgr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_types.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_types.h

## Role

Provides basic JFS type definitions and on-disk extent helper structures used throughout the filesystem.

## Key Definitions

- `tid_t` and `lid_t` are 16-bit transaction and lock identifiers.
- `struct timestruc_t` is a little-endian on-disk seconds/nanoseconds pair.
- `pxd_t` is a physical extent descriptor with 24-bit length and 40-bit address encoding split across two little-endian words.
- Inline helpers `PXDlength`, `PXDaddress`, `lengthPXD`, and `addressPXD` construct and decode `pxd_t`.
- `struct pxdlist` stores up to `MAXTREEHEIGHT` physical extents.
- `dxd_t` describes extended attribute or ACL storage, with flags for inline, extent, file, index, and corrupt states.
- DXD helper macros reuse PXD address/length encoding and expose size helpers.
- `struct component_name` represents a UCS directory component.
- `struct dasd` stores OS/2 DASD quota/usage fields, with macros to get/set 40-bit limit and used values.

## Design Notes

This foundational header must be included early by JFS code. Its packed extent encodings are shared by superblock, log, inode, xtree, xattr, and map-update paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_umount.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_umount.c

## Role

Implements full JFS unmount and read-write-to-read-only unmount paths.

## Main Responsibilities

- `jfs_umount()` flushes outstanding journal transactions, protects special inode pointer teardown with the log lock, unmounts/frees fileset and aggregate maps, waits for direct-inode metadata writeback, marks the superblock clean, and closes the log on read-write mounts.
- `jfs_umount_rw()` flushes the journal, syncs block and inode maps, waits for direct-inode metadata writeback, updates the superblock to `FM_CLEAN`, and closes the log.

## Important Interactions

- Uses `jfs_flush_journal`, `LOG_LOCK`, `updateSuper`, and `lmLogClose`.
- Uses `diUnmount`, `diFreeSpecial`, `dbUnmount`, `dbSync`, and `diSync`.
- Coordinates with log-manager metadata flushing over `log->sb_list`.

## Correctness Notes

The code forces metadata to disk before marking the filesystem clean. It also avoids a race where `write_special_inodes()` could observe partially cleared `jfs_sb_info` special inode pointers during unmount.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_umount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_unicode.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_unicode.c

## Role

Implements conversion between Linux dentry byte names and JFS UCS-2-style internal names.

## Main Responsibilities

- `jfs_strfromUCS_le()` converts little-endian UCS strings to byte strings using the mounted NLS table when present.
- Without an NLS table, `jfs_strfromUCS_le()` performs Latin-1-style byte conversion and replaces unsupported non-Latin-1 characters with `?`, warning at most five total times.
- `jfs_strtoUCS()` converts byte strings to `wchar_t` UCS names using NLS `char2uni()` when available, otherwise direct byte widening.
- `get_UCSname()` validates maximum name length, allocates a UCS buffer with `GFP_NOFS`, converts the dentry name using the mount NLS table, and frees on conversion failure.

## Interactions

- Uses `JFS_SBI(dentry->d_sb)->nls_tab`.
- Produces `struct component_name` values consumed by directory code.
- Pairs with `free_UCSname()` from the header.

## Correctness Notes

Name conversion uses `GFP_NOFS` to avoid filesystem recursion. Without `iocharset`, non-Latin-1 names are lossy.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_unicode.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_unicode.h

## Role

Declares JFS Unicode conversion functions and provides inline UCS string utilities.

## Key Definitions

- Public functions: `get_UCSname()` and `jfs_strfromUCS_le()`.
- `free_UCSname()` frees a component name buffer.
- `UniStrcpy()` copies native `wchar_t` strings.
- `UniStrncpy_le()` copies/pads little-endian UCS strings.
- `UniStrncmp_le()` compares native `wchar_t` to little-endian UCS.
- `UniStrncpy_to_le()` and `UniStrncpy_from_le()` convert fixed-length strings to/from little-endian UCS.
- `UniToupper()` uppercases using Linux NLS Unicode case tables.
- `UniStrupr()` uppercases an entire native Unicode string.

## Design Notes

This header bridges JFS directory/name code with Linux NLS tables and little-endian on-disk name storage.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_unicode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_xattr.h

## Role

Defines JFS extended attribute on-disk list structures, iteration macros, xattr operation prototypes, handlers, and security initialization hook.

## Key Definitions

- `struct jfs_ea` describes one attribute: flag, name length, value length, and variable-length null-terminated name followed by value.
- `struct jfs_ea_list` stores overall list size plus a variable-length sequence of `struct jfs_ea`.
- `MAXEASIZE` and `MAXEALISTSIZE` are both 65535 bytes.
- `EA_SIZE`, `NEXT_EA`, `FIRST_EA`, `EALIST_SIZE`, and `END_EALIST` provide variable-length EA traversal.
- Declares internal set/get/list xattr functions and `jfs_xattr_handlers`.
- If `CONFIG_JFS_SECURITY` is disabled, `jfs_init_security()` is an inline no-op returning 0.

## Design Notes

The EA format keeps the name null terminator even though name length is explicit, preserving OS/2 compatibility expectations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_xattr.h -->