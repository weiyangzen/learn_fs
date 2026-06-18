# Group Research: group_1113_linux_stable_sources_os_linux_linux_stable_fs_xfs_xfs_exchrange_c_s_23c28157d834

Scope verified against `Docs/research_subset_a.md`: `sources/os/linux/linux-stable` is included. All 20 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_exchrange.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_exchrange.c

## Purpose

Implements XFS file range exchange and commit-range ioctls. This file validates user requests, prepares both files, coordinates locking/writeback/quota reservation, and invokes the lower exchange-mapping engine.

## Main Responsibilities

- Provides inode lock/join helpers for exchange-map operations: `xfs_exchrange_ilock`, `xfs_exchrange_iunlock`, and `xfs_exchrange_estimate`.
- Validates exchange requests for same mount, regular files, read/write access, append/immutable/swapfile exclusions, non-overlap on same inode, EOF bounds, file-size limits, and supported flags.
- Enforces allocation-unit alignment, including realtime extent sizes that are not powers of two.
- Flushes direct I/O and pagecache ranges, unmaps cached state, attaches dquots, and cancels speculative CoW preallocations.
- Reserves quota for net and gross mapping changes, with a one-time retry after quota/blockgc cleanup.
- Implements `XFS_IOC_EXCHANGE_RANGE`, `XFS_IOC_START_COMMIT`, and `XFS_IOC_COMMIT_RANGE`.

## Important Invariants

- Both files must be on the same mount and both realtime or both non-realtime.
- Start offsets must align to the file allocation unit; non-EOF lengths must be allocation-unit aligned.
- Partial EOF allocation units cannot be exchanged into the middle of another file.
- Commit-range freshness compares file2 inode number, generation, ctime, and mtime while inode metadata is locked.
- `XFS_EXCHANGE_RANGE_TO_EOF` can swap unequal sizes and updates in-core sizes after committed mapping updates.

## Research Notes

This is the policy and correctness wrapper around `xfs_exchange_mappings`. The sensitive areas are alignment/EOF validation, freshness-token handling, quota retry behavior, and ordering of IO/MMAP locks, metadata locks, pagecache flushing, transaction joins, and privilege/fsnotify updates.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_exchrange.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_exchrange.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_exchrange.h

## Purpose

Declares the internal exchange-range state and APIs used by the XFS exchange/commit range implementation.

## Main Contents

- Private high-bit flags for timestamp updates and file2 freshness checks.
- `XFS_EXCHANGE_RANGE_PRIV_FLAGS`, grouping internal-only flags that userspace cannot set.
- `struct xfs_exchrange`, containing both files, offsets, length, flags, and file2 freshness metadata.
- Ioctl entry declarations for exchange, start-commit, and commit-range.
- Exchange-map helper declarations for inode locking and resource estimation.

## Research Notes

The header is intentionally narrow: it exposes the VFS-facing exchange state and the small helper surface needed by exchange-map code without exposing implementation details of lower mapping exchange.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_exchrange.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_export.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_export.c

## Purpose

Implements XFS `exportfs` operations for NFS and block export users. It encodes XFS inode identities into file handles and resolves file handles back to dentries/inodes.

## Main Responsibilities

- Chooses 32-bit or 64-bit file handle formats, with optional parent information.
- Encodes inode and parent identity in `xfs_fs_encode_fh`.
- Resolves NFS file handles with `xfs_nfs_get_inode`.
- Provides `fh_to_dentry`, `fh_to_parent`, `get_parent`, and NFS commit metadata operations.
- Optionally exposes pNFS block export callbacks under `CONFIG_EXPORTFS_BLOCK_OPS`.

## Important Invariants

- Generation zero is valid in XFS, so handle lengths must be explicit.
- Inode zero is rejected as stale.
- `XFS_IGET_UNTRUSTED` is used because client-supplied handles can be arbitrary.
- Invalid or corrupt inode references are translated to `-ESTALE` for NFS semantics.
- Private/internal inodes are not exportable.

## Research Notes

This file bridges stable XFS inode identity with VFS exportfs. It deliberately treats many invalid handle outcomes as stale file handles rather than surfacing ordinary filesystem errors to NFS clients.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_export.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_export.h

## Purpose

Defines XFS-specific NFS export file handle formats and declares handle-to-inode lookup.

## Main Contents

- Documents the supported wire formats for empty, 32-bit inode, 32-bit inode plus parent, 64-bit inode, and 64-bit inode plus parent handles.
- Defines packed `struct xfs_fid64`.
- Defines `XFS_FILEID_TYPE_64FLAG`, the on-wire flag for 64-bit inode handles.
- Declares `xfs_nfs_get_inode`.

## Research Notes

The key compatibility warning is that NFS fsid inode fields can still be 32-bit outside XFS control; filesystems with 64-bit inode numbers should export mountpoints or use the `fsid` export option.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_export.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_extent_busy.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_extent_busy.c

## Purpose

Tracks extents that have been freed in memory but cannot yet be safely reused because the freeing transaction has not reached stable log state or discard processing is active.

## Main Responsibilities

- Maintains per-group busy extent rbtrees with generation counters and waitqueues.
- Inserts busy extents from transactions and discard paths.
- Searches for exact or partial allocation conflicts.
- Trims allocation candidates around busy ranges.
- Allows carefully constrained reuse for non-userdata allocations by removing or shrinking busy records.
- Clears busy extents after commit/discard, wakes waiters, and supports wait-all behavior across AGs and realtime groups.

## Important Invariants

- Busy extents in a group rbtree must not overlap.
- Transaction/CIL busy lists are immutable, so busy records cannot be split in place.
- Fully consumed busy records are removed from the rbtree and marked invalid by setting length to zero; list cleanup happens later.
- User allocations cannot reuse busy extents; the log must be forced and allocation retried.
- Discarded extents are marked `XFS_EXTENT_BUSY_DISCARDED` and cause retry.
- Zoned realtime groups skip busy tracking because zone reset ordering handles safe freeing.

## Research Notes

This is a core allocator safety mechanism. It prevents stale freed blocks from being reallocated too early while still giving metadata allocation paths a limited way to make progress under low-space pressure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_extent_busy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_extent_busy.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_extent_busy.h

## Purpose

Declares busy extent structures and APIs used by the XFS allocator and transaction code.

## Main Contents

- `struct xfs_extent_busy`, containing rbtree linkage, transaction list linkage, group reference, block range, and flags.
- Busy flags for discard-in-progress and discard skipping.
- `struct xfs_busy_extents`, used to track related busy extents through discard completion.
- APIs for insertion, clearing, searching, reuse, trimming, flushing, wait-all, empty checks, tree allocation, and sorting.
- `xfs_group_has_extent_busy`, which disables busy tracking for zoned realtime groups.

## Research Notes

The header shows the two ownership dimensions of busy extents: fast overlap lookup through the group rbtree and lifetime tracking through transaction/discard lists.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_extent_busy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_extfree_item.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_extfree_item.c

## Purpose

Implements XFS deferred extent-free intent/done log items: EFI records describe extents that must be freed, and EFD records acknowledge completion or cancellation.

## Main Responsibilities

- Allocates, formats, releases, and recovers EFI and EFD log items.
- Provides log-space accounting for EFI/EFD records.
- Supports normal data extent frees, AGFL frees, and realtime extent frees.
- Integrates with the deferred operation framework through `xfs_extent_free_defer_type`, `xfs_agfl_free_defer_type`, and `xfs_rtextent_free_defer_type`.
- Handles transaction roll/retry by copying unprocessed EFI extents into an EFD.
- Validates recovered extents and replays incomplete frees from the log.
- Supports relogging intent items to push the log tail forward.

## Important Invariants

- EFI items carry two references: one for EFI AIL insertion and one for EFD completion.
- EFD items release the EFI reference when committed or aborted.
- EFI extent slots must be fully populated before formatting.
- Recovered EFI extents must validate as all realtime or all non-realtime according to item type.
- AGFL blocks are freed through special reserve accounting and are not inserted into the busy extent list.
- Realtime frees use rtgroup locks and either rtbitmap or zoned free paths depending on filesystem mode.

## Research Notes

This file is crash-recovery infrastructure for block freeing. Its correctness depends on pairing every logged intent with a done record, preserving enough information across transaction rolls, and validating recovered extents before replay.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_extfree_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_extfree_item.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_extfree_item.h

## Purpose

Declares in-core EFI/EFD log item structures and extent-free deferred operation entry points.

## Main Contents

- Fast allocation limits for EFI and EFD items.
- `struct xfs_efi_log_item`, with log item header, refcount, next-extent counter, and on-disk format payload.
- `struct xfs_efd_log_item`, with log item header, paired EFI pointer, next-extent counter, and done payload.
- Size helpers for variable-length EFI/EFD items.
- Global EFI/EFD slab cache declarations.
- `xfs_extent_free_defer_add` and EFI/EFD log space helpers.

## Research Notes

The header documents the EFI/EFD reference model clearly: after an EFI commits, an EFD is required even if unrelated later work fails, because the EFI must eventually be released from recovery-visible state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_extfree_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_file.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_file.c

## Purpose

Implements XFS regular-file and directory file operations: read/write, fsync, llseek, mmap faults, fallocate, reflink remap, fadvise, open/release, and readdir.

## Main Responsibilities

- Implements direct, DAX, buffered, and splice read paths with shutdown checks and IOLOCK protection.
- Implements buffered, direct, DAX, zoned, and atomic write paths.
- Handles pre-write checks, layout breaking, privilege stripping, EOF zeroing, direct-I/O draining, and timestamp updates.
- Handles direct-I/O completion for CoW, unwritten extent conversion, file size updates, and write accounting.
- Supports zoned filesystem reservations for buffered writes, direct writes, faults, and fallocate zero-edge cases.
- Implements `fallocate` modes: punch hole, collapse range, insert range, zero range, unshare range, and allocate range.
- Implements reflink/dedupe remap and destination metadata updates.
- Implements mmap fault handlers for buffered and DAX mappings, including huge faults and write faults.
- Exposes `xfs_file_operations` and `xfs_dir_file_operations`.

## Important Invariants

- Writes fail after filesystem shutdown.
- Direct I/O must be aligned to the device logical sector size; filesystem-block unaligned writes take special serialization paths.
- Reflink remapping can force write locks to upgrade from shared to exclusive.
- DAX writes and faults require stronger serialization than ordinary buffered I/O.
- Extending writes beyond EOF must zero the gap while preventing concurrent EOF update races.
- Atomic writes must meet XFS min/max limits and may fall back from hardware atomic to CoW atomic handling.
- Zoned writes reserve space before taking locks and return unused reservations after completion.

## Research Notes

This is the main VFS integration surface for XFS file data. The risky areas are lock mode transitions, direct-I/O fallback/retry behavior, EOF size updates from async completion, zoned reservations, and interactions among reflink, CoW, unwritten extents, mmap faults, and sync semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_file.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_file.h

## Purpose

Declares XFS file operation tables and a fallocate alignment helper.

## Main Contents

- `xfs_file_operations` for regular files.
- `xfs_dir_file_operations` for directories.
- `xfs_is_falloc_aligned`, used to verify fallocate range alignment against the file allocation unit.

## Research Notes

This header is small but marks the public internal entry points from inode/VFS setup into the large file operation implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_filestream.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_filestream.c

## Purpose

Implements filestream allocation group selection, which tries to keep related file allocations near a parent directory while avoiding allocation group contention and fragmentation.

## Main Responsibilities

- Maintains an MRU cache mapping parent directory inode numbers to preferred AGs.
- Selects AGs with enough free space and minimal current filestream use.
- Falls back to the AG with the most free space under low-space conditions.
- Reuses existing parent-directory associations when still suitable.
- Creates new associations after removing stale ones and rotating inode32 allocation starts when needed.
- Provides mount/unmount cache lifecycle and explicit inode deassociation.

## Important Invariants

- Cached AG associations hold active perag references and increment `pagf_fstrms`.
- Selection prefers AGs not already used by another filestream.
- Metadata-preferred AGs are avoided for userdata unless low-space behavior allows them.
- If a cached AG no longer has a sufficiently long free extent, the association can be replaced.
- Allocation can still proceed even if the MRU cache item allocation fails, as long as a referenced AG was selected.

## Research Notes

This file is an allocation locality heuristic. It trades strict exclusivity for practical low-space fallback while preserving reference accounting around cached AG choices.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_filestream.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_filestream.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_filestream.h

## Purpose

Declares filestream lifecycle and AG selection APIs.

## Main Contents

- Mount and unmount hooks for the filestream MRU cache.
- `xfs_filestream_deassociate` for deleting an inode’s cached association.
- `xfs_filestream_select_ag` for allocator AG selection.
- `xfs_inode_is_filestream`, which checks mount-wide filestream support or the inode filestream flag.

## Research Notes

The header isolates filestream policy behind a small allocator-facing interface.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_filestream.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_fsmap.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_fsmap.c

## Purpose

Implements the XFS `GETFSMAP` ioctl, reporting physical filesystem mappings across data, log, and realtime devices.

## Main Responsibilities

- Converts between VFS `struct fsmap` byte units and XFS internal basic-block/block units.
- Converts owners between fsmap owner IDs and XFS rmap owner IDs.
- Queries data device mappings through rmapbt when available and privileged, or bnobt otherwise.
- Queries external log mappings by fabricating log-owner records.
- Queries realtime mappings through rtrmapbt or rtbitmap depending on configuration and privileges.
- Synthesizes gaps as free or unknown owner records.
- Marks shared file data extents by consulting refcount btrees.
- Batches records in kernel memory before copying to userspace.

## Important Invariants

- Low/high keys must be valid, ordered, and refer to known devices.
- Continuation is driven by a nonzero low-key length from the last returned record.
- For shareable file data, continuation advances owner offset; for unshareable metadata, continuation advances physical position.
- Counting mode increments entries without formatting records.
- `-ECANCELED` means the internal buffer filled and the ioctl should continue if userspace has room.
- The last returned record is marked with `FMR_OF_LAST` only when the result set is exhausted.

## Research Notes

This file is a multi-backend query engine for filesystem physical layout. Its core complexity is key normalization and continuation across devices, AGs, rtgroups, rmap ordering, and synthetic gaps.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_fsmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_fsmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_fsmap.h

## Purpose

Defines internal fsmap structures and declares the getfsmap ioctl entry point.

## Main Contents

- `struct xfs_fsmap`, the internal mapping record in device/basic-block units.
- `struct xfs_fsmap_head`, the internal request/response header with low/high keys.
- `struct xfs_fsmap_irec`, the internal record format used by backends before final fsmap formatting.
- Declaration of `xfs_ioc_getfsmap`.

## Research Notes

The header separates userspace `struct fsmap` layout from internal XFS query units and rmap-derived record state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_fsmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_fsops.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_fsops.c

## Purpose

Implements filesystem-level operations for growfs, reserve pools, user-triggered shutdown, and AG/metafile reservation setup.

## Main Responsibilities

- Initializes new AG headers during data-section grow operations.
- Handles data grow and limited shrink scaffolding, including perag initialization and superblock counter updates.
- Updates inode maximum percentage independently from physical grow.
- Rejects log grow/move operations with `-ENOSYS`.
- Implements reservation pool resizing for free-space counters.
- Implements `XFS_IOC_GOINGDOWN` behavior for default, logflush, and nologflush shutdown modes.
- Performs force-shutdown reporting and health monitor notification.
- Initializes and frees per-AG and metafile metadata reservations.

## Important Invariants

- Growfs requires `CAP_SYS_ADMIN` and `m_growlock`.
- Data-section changes are rejected when an internal realtime section exists.
- Shrinking below two AGs is rejected; full AG shrink is still not completed.
- New AG headers are written non-transactionally before the grow transaction is committed.
- Superblock size/count changes are committed transactionally and synchronously.
- Force shutdown is atomic; only the first caller performs full shutdown reporting.

## Research Notes

This file controls coarse filesystem geometry and shutdown state. Its most important correctness boundary is making new geometry live only after required on-disk AG setup and transactional superblock updates.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_fsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_fsops.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_fsops.h

## Purpose

Declares XFS filesystem operation entry points.

## Main Contents

- Data grow and log grow functions.
- Reserve pool resizing API.
- Filesystem going-down ioctl handler.
- AG/metafile reservation init and free APIs.

## Research Notes

This header exposes the filesystem-level operation surface used by ioctl and mount/unmount paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_fsops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_globals.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_globals.c

## Purpose

Defines global XFS tunables and runtime defaults.

## Main Contents

- `xfs_params`, containing min/default/max values for panic mask, error level, sync timer, stats clearing, inherited inode flags, rotor step, filestream timer, and blockgc timer.
- `xfs_globals`, containing defaults for recovery/mount delay, assert behavior, debug worker settings, log attribute replay, and btree bulk-load slack.

## Important Notes

- Tunable timer units are centiseconds except `blockgc_timer`, which is in seconds.
- `xfs_params` exists even without sysctl support because other XFS code consumes these values.
- Assert behavior depends on `XFS_ASSERT_FATAL`.
- Some fields are compiled only under `DEBUG`.

## Research Notes

This file is configuration data, not control flow. It centralizes default behavior that other XFS subsystems consult.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_globals.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_handle.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_handle.c

## Purpose

Implements XFS handle-based ioctls for file handle creation, privileged open/readlink by handle, legacy attribute operations by handle, and parent-pointer enumeration.

## Main Responsibilities

- Builds filesystem handles and file handles from paths or file descriptors.
- Converts user handles back to dentries or inodes using exportfs/NFS handle resolution.
- Implements privileged `open_by_handle` and `readlink_by_handle`.
- Implements legacy attr list and attrmulti operations, including namespace filtering and cursor handling.
- Implements `GETPARENTS` and `GETPARENTS_BY_HANDLE` for parent pointer enumeration.
- Formats parent records with parent file handles and names into a user-provided buffer.

## Important Invariants

- Handle operations are privileged where required with `CAP_SYS_ADMIN`.
- Handles can only be generated for XFS regular files, directories, and symlinks.
- Handle opens are restricted to directories and regular files; symlink reads are restricted to symlinks.
- Handle resolution requires a directory file as the parent context.
- Attribute namespace flags cannot request root and secure namespaces simultaneously.
- Parent pointer corruption marks the inode parent metadata sick.

## Research Notes

This file ties XFS-specific handles to exportfs identity and administrative userspace tools. Its sensitive paths are user buffer/cursor validation, capability checks, and avoiding expensive or unsafe directory-tree reconstruction for parent-pointer queries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_handle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_handle.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_handle.h

## Purpose

Declares handle-based ioctl helpers and legacy attribute operation entry points.

## Main Contents

- Attribute list and attrmulti by-handle declarations.
- Path/fd-to-handle, open-by-handle, and readlink-by-handle declarations.
- Single attrmulti operation helper.
- Generic attr list helper.
- User handle to dentry conversion.
- Parent pointer query declarations.

## Research Notes

The header exposes the administrative handle API surface used by XFS ioctl handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_handle.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_health.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_health.c

## Purpose

Tracks and reports XFS metadata health state for filesystem-wide, allocation-group, realtime-group, and inode metadata.

## Main Responsibilities

- Warns at unmount if unfixed metadata corruption was detected.
- Marks filesystem, group, and inode metadata sick, corrupt, or healthy.
- Samples sick and checked masks under the correct locks.
- Reports metadata errors through `fserror` and XFS health monitor hooks.
- Keeps sick inodes from being dropped with `I_DONTCACHE`.
- Converts internal health masks to ioctl-visible geometry and bulkstat masks.
- Marks bmap, btree, dir, attr, and da metadata sick from lower-level detection paths.

## Important Invariants

- Sick masks are validated against the object type before mutation.
- Primary/secondary sick-bit relationships are maintained when marking healthy.
- FS counters are treated specially at unmount to avoid conflicting dirty-log recovery behavior with repair advice.
- Internal/constructing/reclaiming inodes report metadata errors at the filesystem level rather than file level.
- Bmap btrees map to inode fork health; non-ephemeral non-bmap btrees map to group health.

## Research Notes

This file is the health-state registry for XFS online checking and reporting. It does not repair metadata itself; it records observations, exposes them through ioctl-facing structures, and notifies health monitoring/reporting systems.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_health.c -->