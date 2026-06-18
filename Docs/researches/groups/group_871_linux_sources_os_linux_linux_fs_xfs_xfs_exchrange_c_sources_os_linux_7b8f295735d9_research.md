# Group Research: group_871_linux_sources_os_linux_linux_fs_xfs_xfs_exchrange_c_sources_os_linux_7b8f295735d9

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_exchrange.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_exchrange.c

Implements XFS range-exchange ioctls: `XFS_IOC_EXCHANGE_RANGE`, `XFS_IOC_START_COMMIT`, and `XFS_IOC_COMMIT_RANGE`. The core path validates two regular read/write files on the same mount, locks IO/MMAP state, flushes and unmaps page cache, cancels speculative CoW mappings, reserves quota, exchanges mappings via `xfs_exchmaps`, and updates timestamps/fsnotify.

Key logic:
- `xfs_exchrange_ilock` / `xfs_exchrange_iunlock` lock one or two inodes in a deadlock-safe order and optionally join them to a transaction.
- `xfs_exchrange_estimate` wraps `xfs_exchmaps_estimate` under inode locks.
- `xfs_exchrange_check_freshness` enforces commit-range optimistic concurrency by comparing file2 inode number, generation, ctime, and mtime against a prior snapshot.
- `xfs_exchrange_reserve_quota` computes net and gross data/realtime block deltas and reserves quota for both inodes, retrying after blockgc on `EDQUOT`/`ENOSPC`.
- `xfs_exchrange_mappings` builds an `xfs_exchmaps_req`, rounds realtime allocation units, estimates resources, allocates a write transaction, checks forks, handles dry-run, applies cmtime flags, calls `xfs_exchange_mappings`, commits synchronously when needed, and swaps incore sizes for whole-file-to-EOF exchanges.
- `xfs_exchange_range_checks` performs generic byte-range validation: immutable/swapfile rejection, EOF bounds, to-EOF length derivation, allocation-unit alignment, overflow checks, file size limits, same-file overlap rejection, and partial EOF-block safety.
- `xfs_exchrange_check_rtalign` handles non-power-of-two realtime allocation alignment with division-based checks.
- `xfs_exchrange_prep` enforces matching realtime/non-realtime status, performs generic prep, optional freshness check, quota attachment, range flush/unmap, and CoW cancellation.
- `xfs_exchange_range` is the VFS-facing dispatcher that checks file modes, append state, `remap_verify_area`, timestamp policy, write-start/end nesting, and fsnotify.
- `xfs_ioc_start_commit` samples file2 freshness into an opaque userspace blob containing fsid, inode identity, generation, ctime, and mtime.
- `xfs_ioc_commit_range` validates that blob and reruns exchange with the internal freshness-check flag.

Dependencies include `xfs_exchmaps`, quota, reflink, transaction/log, inode locking, realtime bitmap helpers, `remap_verify_area`, and fsnotify. The file is careful about ordering: freshness checks happen after metadata locks, data is flushed before mapping exchange, and cmtime updates are part of the transaction that exchanges extents.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_exchrange.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_exchrange.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_exchrange.h

Declares the internal state and entry points for XFS range exchange and commit-range operations.

Key contents:
- Private high-bit flags:
  - `__XFS_EXCHANGE_RANGE_UPD_CMTIME1`
  - `__XFS_EXCHANGE_RANGE_UPD_CMTIME2`
  - `__XFS_EXCHANGE_RANGE_CHECK_FRESH2`
  - `XFS_EXCHANGE_RANGE_PRIV_FLAGS`
- `struct xfs_exchrange`, carrying file pointers, byte offsets, length, public/private flags, and the file2 freshness snapshot used by commit-range.
- Ioctl entry points: `xfs_ioc_exchange_range`, `xfs_ioc_start_commit`, `xfs_ioc_commit_range`.
- Shared inode locking helpers and exchange-map resource estimation declaration.

This header is the narrow interface between ioctl handling, generic exchange validation, and lower-level `xfs_exchmaps` work.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_exchrange.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_export.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_export.c

Implements XFS NFS/exportfs operations.

Key logic:
- `xfs_fileid_length` maps supported filehandle types to encoded word lengths and rejects invalid types.
- `xfs_fs_encode_fh` encodes inode and optional parent identity, selecting 32-bit or 64-bit inode formats depending on filesystem inode-number policy and available caller buffer space.
- `xfs_nfs_get_inode` retrieves an inode by inode number and generation with `XFS_IGET_UNTRUSTED`, translating stale/corrupt lookup errors to `ESTALE`, reloading incomplete unlinked state if needed, and rejecting generation mismatches or private inodes.
- `xfs_fs_fh_to_dentry` and `xfs_fs_fh_to_parent` decode filehandle records back into dentries.
- `xfs_fs_get_parent` resolves `..` through XFS directory lookup.
- `xfs_fs_nfs_commit_metadata` forces inode log metadata for NFS commit semantics.
- `xfs_export_operations` wires XFS into exportfs and optionally pNFS block operations.

The file’s central concern is stable cross-reboot inode identity while preserving XFS generation checks and safe handling of stale client filehandles.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_export.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_export.h

Defines XFS export/NFS filehandle formats and the exported inode lookup helper.

Key contents:
- Detailed comments describe five fileid encodings, including 32-bit and 64-bit inode-number variants with optional parent identity.
- `struct xfs_fid64` packs inode, generation, parent inode, and parent generation for 64-bit inode filehandles.
- `XFS_FILEID_TYPE_64FLAG` marks 64-bit inode filehandle formats and is wire-visible.
- Declares `xfs_nfs_get_inode`.

The header documents an important operational caveat: 64-bit inode exports interact poorly with NFS fsid fields unless exporting the mountpoint or using an explicit `fsid`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_export.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_extent_busy.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_extent_busy.c

Tracks freed extents that are still “busy” because their freeing transactions have not committed or discard is still in flight. Each group has a spinlock-protected rb-tree keyed by block number plus transaction/discard lists.

Key logic:
- `xfs_extent_busy_insert_list`, `xfs_extent_busy_insert`, and `xfs_extent_busy_insert_discard` allocate busy records, hold the group, insert non-overlapping ranges into the rb-tree, and append them to the caller’s list.
- `xfs_extent_busy_search` reports no overlap, exact overlap, or partial overlap for allocation decisions.
- `xfs_extent_busy_update_extent` lets allocator reuse safe portions of non-userdata busy extents by trimming/removing records; otherwise it forces the log and retries. It cannot split an immutable transaction/CIL busy-list record.
- `xfs_extent_busy_reuse` walks overlapping busy extents and applies safe reuse updates.
- `xfs_extent_busy_trim` trims allocation candidates away from busy ranges, records the busy generation for waiters, and prefers forward allocation patterns to reduce fragmentation.
- `xfs_extent_busy_clear` removes busy entries after commit, optionally marking them as undergoing discard instead of immediately unbusy, increments generation, and wakes waiters.
- `xfs_extent_busy_flush` forces the log and waits for generation changes while avoiding deadlocks with busy extents held by the current transaction.
- `xfs_extent_busy_wait_all` drains all AG and eligible realtime-group busy trees.
- `xfs_extent_busy_ag_cmp`, `xfs_extent_busy_list_empty`, and `xfs_extent_busy_alloc` provide sorting, state query, and tree allocation support.

The concurrency model hinges on `eb_lock`, `eb_gen`, and `eb_wait`: allocators can trim or wait on a generation, while commit/discard completion wakes them after clearing records.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_extent_busy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_extent_busy.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_extent_busy.h

Declares busy-extent structures and APIs.

Key contents:
- `struct xfs_extent_busy`: rb-tree node, list node, owning group, group-relative block range, and flags.
- Flags:
  - `XFS_EXTENT_BUSY_DISCARDED`: discard operation in progress.
  - `XFS_EXTENT_BUSY_SKIP_DISCARD`: do not discard.
- `struct xfs_busy_extents`: list plus work item and owner pointer for tracking discard completion batches.
- APIs for insertion, discard insertion, clearing, searching, reuse, trimming, flushing, global waiting, empty query, tree allocation, and sorting.
- `xfs_group_has_extent_busy` notes that zoned realtime groups skip busy extent tracking because zone reset orders transactions first.

This header defines the allocator/log interface for preventing premature reuse of recently freed blocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_extent_busy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_extfree_item.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_extfree_item.c

Implements extent-free intent/done log items and deferred extent free operations. These are XFS’s crash-recoverable mechanism for ensuring extents that were scheduled for freeing are either completed or replayed after log recovery.

Key logic:
- EFI lifecycle:
  - `xfs_efi_init` allocates and initializes an EFI with two references.
  - `xfs_efi_item_format`, `xfs_efi_item_unpin`, `xfs_efi_item_release`, and `xfs_efi_item_match` implement log item behavior.
  - `xfs_efi_copy_format` converts recovered 32-bit, 64-bit, or native log formats.
- EFD lifecycle:
  - `xfs_extent_free_create_done` allocates the done item tied to an EFI.
  - `xfs_efd_item_format`, `xfs_efd_item_release`, and `xfs_efd_item_intent` implement done-item behavior.
  - `xfs_efd_from_efi` copies all EFI extents into an EFD when transaction rolling must cancel/relog remaining work.
- Deferred operation support:
  - `xfs_extent_free_defer_add` selects AG vs realtime-group ownership and queues the right defer type.
  - `xfs_extent_free_finish_item` calls `__xfs_free_extent`, fills EFD records, and handles `EAGAIN` by preserving all EFI extents.
  - `xfs_agfl_free_finish_item` frees AGFL blocks specially without busy-list insertion.
  - `xfs_rtextent_free_finish_item` handles realtime frees, including zoned filesystems via `xfs_zone_free_blocks`.
- Recovery:
  - `xfs_extent_free_recover_work` validates all recovered extents, reconstructs deferred work items, allocates a recovery transaction, and commits/captures continued deferred work.
  - `xfs_extent_free_relog_intent` relogs intents to move the log tail.
  - `xlog_recover_efi_commit_pass2`, `xlog_recover_rtefi_commit_pass2`, `xlog_recover_efd_commit_pass2`, and `xlog_recover_rtefd_commit_pass2` rebuild or cancel intents during log replay.
- Exports defer-op tables for normal frees, AGFL frees, and realtime frees, plus recover item ops for EFI/EFD and realtime EFI/EFD.

Important invariants: EFI extent slots must be fully populated before logging; EFDs release EFI references; recovered EFI extents must all validate and must not mix realtime and non-realtime semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_extfree_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_extfree_item.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_extfree_item.h

Defines kernel-only EFI/EFD log item structures and public helpers.

Key contents:
- `XFS_EFI_MAX_FAST_EXTENTS` and `XFS_EFD_MAX_FAST_EXTENTS` define cache-backed fast allocation thresholds.
- Extensive comments document EFI reference ownership: one reference for EFI AIL insertion and one held by the EFD path, preventing premature free across commit/unpin ordering.
- `struct xfs_efi_log_item` embeds `xfs_log_item`, refcount, next-extent counter, and variable EFI log format.
- `xfs_efi_log_item_sizeof` computes variable-sized EFI allocation.
- `struct xfs_efd_log_item` embeds `xfs_log_item`, points to its EFI, tracks next extent, and stores variable EFD format.
- Declares EFI/EFD slab caches, `xfs_extent_free_defer_add`, and log-space calculators.

This header is the structural contract for crash-recoverable deferred extent freeing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_extfree_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_file.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_file.c

Implements XFS regular-file and directory file operations, including fsync, reads, writes, fallocate, reflink remap, mmap faults, open/release, readdir, and seek.

Key areas:
- Alignment and fsync:
  - `xfs_is_falloc_aligned` checks allocation-unit alignment, including non-power-of-two realtime units.
  - `xfs_dir_fsync`, `xfs_fsync_flush_log`, and `xfs_file_fsync` flush data, force relevant log sequence numbers, and issue device cache flushes for separate data/log/realtime devices.
- Reads:
  - `xfs_file_read_iter` dispatches to DAX, direct I/O, or buffered reads.
  - Direct reads use iomap and optional bounce buffering for stable writes.
  - `xfs_file_splice_read` wraps page-cache splice reads under IOLOCK.
- Write setup:
  - `xfs_ilock_iocb` and `xfs_ilock_iocb_for_write` implement nowait-aware IOLOCK acquisition and upgrade when reflink remap is active.
  - `xfs_file_write_zero_eof` and `xfs_file_write_checks` handle generic write checks, layout breaking, privilege removal requirements, zeroing gaps beyond EOF, and modified-time setup.
  - Zoned filesystems reserve space before writes through `xfs_zoned_write_space_reserve`.
- Direct/DAX/buffered writes:
  - `xfs_dio_write_end_io` and `xfs_zoned_dio_write_end_io` handle completion, COW/unwritten conversion, stats, and EOF updates.
  - `xfs_file_dio_write_aligned`, `_unaligned`, `_zoned`, and `_atomic` cover sector/block alignment, COW fallback, zone allocation, and hardware/COW atomic write paths.
  - `xfs_file_dax_write` uses DAX iomap and updates size synchronously.
  - `xfs_file_buffered_write` and `_zoned` use iomap buffered writes, retrying after quota/space cleanup or writeback.
  - `xfs_file_write_iter` validates atomic constraints and dispatches the correct write path, allowing direct I/O to fall back only for reflink CoW.
- Fallocate and remap:
  - Handles punch hole, collapse range, insert range, zero range, unshare range, and allocate range.
  - Zoned fallocate pre-reserves edge-zeroing space.
  - `xfs_file_remap_range` implements reflink/dedupe remap with prep, block remap, destination update, optional cowextsize hint propagation, and sync-log handling.
- Open/release/readdir/seek:
  - `xfs_file_open` sets nowait, direct I/O, and atomic write capability.
  - `xfs_dir_open` performs directory data readahead.
  - `xfs_file_release` triggers early writeout after truncation and opportunistic EOF-block cleanup.
  - `xfs_file_readdir` delegates to XFS directory iteration with a buffer-size estimate.
  - `xfs_file_llseek` supports `SEEK_HOLE` and `SEEK_DATA` through iomap.
- mmap faults:
  - DAX read/write faults use `dax_iomap_fault`.
  - Buffered write faults use `iomap_page_mkwrite`.
  - Zoned write faults reserve space for the folio.
  - `xfs_file_mmap_prepare` validates DAX synchronous mapping support and installs XFS vm ops.
- Operation tables:
  - `xfs_file_operations` wires regular-file methods and flags such as mmap sync, async buffered IO, parallel DIO writes, and dontcache.
  - `xfs_dir_file_operations` wires directory methods.

The file is the main VFS integration point for XFS data I/O and carefully coordinates IOLOCK/MMAPLOCK ordering, DAX vs page cache behavior, reflink/COW semantics, zoned allocation, direct I/O completion, and persistent metadata ordering.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_file.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_file.h

Small public header for XFS file operations.

Key contents:
- Declares `xfs_file_operations` and `xfs_dir_file_operations`.
- Declares `xfs_is_falloc_aligned`, used by fallocate/range operations that must respect filesystem allocation units.

This is the VFS-facing declaration point for XFS regular and directory file operation tables.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_filestream.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_filestream.c

Implements filestream allocation-group selection, which tries to keep related file allocations in a chosen AG to improve locality and reduce fragmentation.

Key logic:
- `struct xfs_fstrm_item` stores an MRU-cache association from parent inode to per-AG.
- `xfs_fstrm_free_func` drops the association, decrements the AG filestream count, releases the perag reference, and frees the item.
- `xfs_filestream_pick_ag` scans AGs from a starting AG looking for an unused/suitable AG with enough free extent length or minimum free blocks, tracking the AG with most free space as fallback. It uses `pagf_fstrms` as both suitability guard and active association count.
- `xfs_filestream_get_parent` uses dentry aliases to find the parent directory inode.
- `xfs_filestream_lookup_association` checks the MRU cache for an existing parent-to-AG association, validates free extent availability unless in low-space mode, and returns a referenced perag.
- `xfs_filestream_create_association` removes stale associations, chooses a starting AG, calls the picker, and inserts a new MRU cache item if allocation succeeds.
- `xfs_filestream_select_ag` is the allocator entry point: find parent, reuse association if sufficient, otherwise create a new one.
- `xfs_filestream_deassociate`, `xfs_filestream_mount`, and `xfs_filestream_unmount` manage MRU entries and mount lifecycle.

The file balances preferred locality with low-space fallbacks and metadata-preferred AG avoidance for user data.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_filestream.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_filestream.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_filestream.h

Declares filestream lifecycle and allocation selection APIs.

Key contents:
- Mount/unmount helpers for the filestream MRU cache.
- `xfs_filestream_deassociate` to remove an inode’s association.
- `xfs_filestream_select_ag` for allocator integration.
- `xfs_inode_is_filestream` tests mount-wide filestream mode or per-inode filestream flag.

This header is the allocator-facing interface for AG affinity decisions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_filestream.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_fsmap.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_fsmap.c

Implements `GETFSMAP`, translating XFS reverse/free-space metadata into generic `struct fsmap` records for userspace.

Key logic:
- Conversion helpers translate between public byte-addressed `fsmap` and internal basic-block `xfs_fsmap`.
- Owner conversion maps public special owners to rmap owners and vice versa.
- `struct xfs_getfsmap_info` holds query state: output head, record buffer, current AGF/group, next expected address, high/low rmap keys, missing-owner policy, device id, and last-record state.
- `xfs_getfsmap_helper` formats mappings, synthesizes gaps, counts records in count-only mode, checks shared extents through refcountbt when applicable, filters records before the continuation start, and marks flags such as prealloc, attr fork, extent map, and shared.
- Data device paths:
  - `__xfs_getfsmap_datadev` splits filesystem-wide keys into per-AG rmap/bnobt keys, iterates AGs, reads AGF, invokes a query function, and emits final gaps.
  - `xfs_getfsmap_datadev_rmapbt` uses rmapbt for privileged full mapping.
  - `xfs_getfsmap_datadev_bnobt` uses bnobt free-space records for fallback free/unknown ownership view.
- Log device path:
  - `xfs_getfsmap_logdev` fabricates a single log-owned mapping for an external log.
- Realtime paths under `CONFIG_XFS_RT`:
  - `xfs_getfsmap_rtdev_rtbitmap` reports free extents from the realtime bitmap.
  - `xfs_getfsmap_rtdev_rmapbt` reports full realtime mappings from rtrmapbt and handles zoned internal realtime volume offset padding.
- Device handling:
  - `xfs_getfsmap_device` returns synthetic internal device ids or encoded block-device ids.
  - `xfs_getfsmap_is_valid_device` and `xfs_getfsmap_check_keys` validate user query ranges.
- `xfs_getfsmap` configures handlers for data/log/realtime devices, chooses rmapbt only when the filesystem has rmapbt and the caller has `CAP_SYS_ADMIN`, sorts devices, iterates handlers, and sets output flags.
- `xfs_ioc_getfsmap` copies the userspace header, validates reserved fields, allocates an internal buffer up to 128 KiB with page fallback, loops to fill the caller’s record array, copies records out between lock-held queries, advances the low key using the last record, and sets `FMR_OF_LAST`.

The implementation’s subtlety is continuation semantics: physical keys are advanced for unshareable mappings, file offsets are advanced for shareable file data, and synthesized gaps must not duplicate or skip records.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_fsmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_fsmap.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_fsmap.h

Defines internal fsmap data structures and ioctl entry point.

Key contents:
- `struct xfs_fsmap`: internal mapping record with device, flags, physical offset, owner, owner offset, and length in filesystem units.
- `struct xfs_fsmap_head`: internal request/response header with flags, counts, and low/high keys.
- `struct xfs_fsmap_irec`: normalized internal record derived from rmap/free-space metadata, including start daddr, length, owner, offset, rmap flags, and original rmap startblock key.
- Declares `xfs_ioc_getfsmap`.

This header isolates the byte-to-basic-block conversion and internal record shape used by fsmap query backends.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_fsmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_fsops.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_fsops.c

Implements filesystem-level operations: growfs, reserve-block tuning, forced shutdown, going-down ioctl behavior, and per-AG/metafile reservations.

Key logic:
- `xfs_resizefs_init_new_ags` initializes new AG headers with delayed-write buffers before the grow transaction is committed; it can also extend the previous last AG.
- `xfs_growfs_data_private` validates target block count, probes new device end, checks realtime geometry, computes AG deltas, rejects unsupported shrink cases, initializes perag structures, initializes new AGs or shrinks the last AG, transactionally updates superblock counters, commits synchronously, updates mount geometry thresholds, reserves AG metadata, and recomputes realtime btree maxlevels.
- `xfs_growfs_log_private` validates requested log size but returns `ENOSYS` for log moving/resizing.
- `xfs_growfs_imaxpct` updates inode allocation percentage transactionally.
- `xfs_growfs_data` and `xfs_growfs_log` enforce `CAP_SYS_ADMIN` and serialize with `m_growlock`.
- `xfs_reserve_blocks` changes reserve-pool targets under `m_sb_lock`, releasing surplus reserve space or trying to fill a larger reserve from free counters without dipping into reserved space.
- `xfs_fs_goingdown` implements user-requested shutdown modes: freeze/thaw default, logflush, and nologflush.
- `xfs_do_force_shutdown` atomically transitions the mount to shutdown, shuts down the log, reports a reason/tag, emits diagnostics, reports to `fserror`, and notifies health monitoring.
- `xfs_fs_reserve_ag_blocks` initializes per-AG metadata reservations and realtime/metafile reservations, forcing shutdown on unexpected reservation errors.
- `xfs_fs_unreserve_ag_blocks` releases metafile and per-AG reservations.

This file is a mount-wide administrative control point and must keep superblock, perag, reservation, and health/shutdown state coherent.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_fsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_fsops.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_fsops.h

Declares filesystem-level operation entry points.

Key contents:
- Grow data/log APIs.
- Free-counter reserve-block tuning API.
- Filesystem going-down API.
- Per-AG metadata reservation init/free APIs.

This is the ioctl/mount-facing interface to growfs, reserve management, and administrative shutdown operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_fsops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_globals.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_globals.c

Defines global tunables and runtime defaults for XFS.

Key contents:
- `xfs_params` exposes min/default/max ranges for panic mask, error level, sync daemon timer, stats clear, inherited inode flags, rotor step, filestream timer, and blockgc timer. Most timers are centiseconds except `blockgc_timer`, which is seconds.
- `xfs_globals` sets defaults for log recovery delay, mount delay, assert behavior, debug-only parallel work threads and logged-attribute replay flag, and btree bulk-load slack for leaf/node blocks.

This file centralizes tunable defaults used even when sysctl support is disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_globals.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_handle.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_handle.c

Implements XFS handle-based ioctls: path/fd to handle, open/readlink by handle, legacy attr list/multi operations by handle, and parent-pointer retrieval.

Key logic:
- Handle construction:
  - `xfs_filehandle_init` and `xfs_fshandle_init` fill filesystem and file handles from fixed fsid, inode number, and generation.
  - `xfs_find_handle` supports path-to-fshandle, fd-to-handle, and path-to-handle, requiring XFS regular/dir/symlink targets.
- Handle lookup/open:
  - `xfs_khandle_to_dentry` decodes a copied handle through exportfs under a directory file.
  - `xfs_khandle_to_inode` retrieves an inode directly via `xfs_nfs_get_inode`, avoiding exportfs dentry tree reconstruction.
  - `xfs_handle_to_dentry` copies userspace handle data and decodes it.
  - `xfs_open_by_handle` requires `CAP_SYS_ADMIN`, restricts to regular files/directories, checks append/immutable/write rules, opens via `dentry_open`, and suppresses atime/cmtime for regular files.
  - `xfs_readlink_by_handle` requires symlink target and copies link text to userspace.
- Attribute list/multi:
  - `xfs_ioc_attr_list` validates namespace flags and cursor, uses an internal buffer, and formats legacy `xfs_attrlist` entries through `xfs_ioc_attr_put_listent`.
  - `xfs_attrlist_by_handle` lists attrs for a handle target.
  - `xfs_ioc_attrmulti_one` handles get/set/remove operations with namespace filtering and mount write protection for mutating operations.
  - `xfs_attrmulti_by_handle` copies a bounded operation array, applies each operation, stores per-op errors, and copies results back.
- Parent pointers:
  - `xfs_getparents_put_listent` filters parent-pointer attrs, decodes parent ino/gen/name, marks inode parent sickness on corruption, and formats `xfs_getparents_rec` records.
  - `xfs_getparents` validates buffer/flags/cursor, allocates an internal records buffer, iterates parent attrs, expands the last record to fill remaining buffer space, updates cursor and output flags, and copies records out.
  - `xfs_ioc_getparents` retrieves parents of the current file.
  - `xfs_ioc_getparents_by_handle` retrieves parents of a file identified by handle without exportfs path reconstruction.

The file is privilege-sensitive. Most handle operations require `CAP_SYS_ADMIN`, validate handle size/generation, and avoid copying to userspace while internal iteration state is unstable.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_handle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_handle.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_handle.h

Declares XFS handle, attribute-by-handle, and parent-pointer ioctl helpers.

Key contents:
- Attribute list and multi-attribute operations by handle.
- Handle creation/open/readlink helpers.
- Single attrmulti operation helper and attr list helper.
- Userspace handle-to-dentry decoder.
- GETPARENTS entry points for current file and by handle.

This header exposes privileged handle-based functionality used by XFS ioctl dispatch.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_handle.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_health.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_health.c

Implements XFS health/sickness state tracking for filesystem-wide metadata, AG/realtime-group metadata, and per-inode metadata, plus translation to ioctl and health-monitor masks.

Key logic:
- Unmount reporting:
  - `xfs_health_unmount` scans AGs, realtime groups, and filesystem-wide sickness, warns about unfixed corruption, and clears `FS_COUNTERS` sickness in the special case where a dirty-log repair recommendation would be harmful.
- Filesystem health:
  - `xfs_fs_mark_sick`, `xfs_fs_mark_corrupt`, `xfs_fs_mark_healthy`, and `xfs_fs_measure_sickness` update `m_fs_sick`/`m_fs_checked` under `m_sb_lock`, report metadata errors, and emit health-monitor events.
- Group health:
  - `xfs_agno_mark_sick`, `xfs_rgno_mark_sick`, `xfs_group_mark_sick`, `xfs_group_mark_corrupt`, `xfs_group_mark_healthy`, and `xfs_group_measure_sickness` manage `xg_sick`/`xg_checked` under group state locks with AG vs realtime-group mask validation.
- Inode health:
  - `xfs_inode_mark_sick`, `xfs_inode_mark_corrupt`, `xfs_inode_mark_healthy`, and `xfs_inode_measure_sickness` manage `i_sick`/`i_checked`, clear `I_DONTCACHE` so sickness reports are retained, report file metadata errors when possible, and notify health monitoring.
- Ioctl mask translation:
  - Static maps translate internal sick masks to `XFS_FSOP_GEOM`, `XFS_AG_GEOM`, `XFS_RTGROUP_GEOM`, and bulkstat sick/checked masks.
  - `xfs_fsop_geom_health`, `xfs_ag_geom_health`, `xfs_rtgroup_geom_health`, and `xfs_bulkstat_health` fill public health fields.
  - `xfs_healthmon_fs_mask`, `xfs_healthmon_perag_mask`, `xfs_healthmon_rtgroup_mask`, and `xfs_healthmon_inode_mask` translate masks for event reporting.
- Corruption classification helpers:
  - `xfs_bmap_mark_sick` maps data/attr/COW fork bmap corruption to inode sickness.
  - `xfs_btree_mark_sick` marks inode bmap or group btree sickness depending on cursor type.
  - `xfs_dirattr_mark_sick` and `xfs_da_mark_sick` classify directory vs xattr btree corruption.

This file is the central state machine for “observed corrupt”, “checked corrupt”, and “healthy” metadata status, bridging internal error detection, fsnotify/fserror, userspace geometry/bulkstat reporting, and health monitor events.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_health.c -->