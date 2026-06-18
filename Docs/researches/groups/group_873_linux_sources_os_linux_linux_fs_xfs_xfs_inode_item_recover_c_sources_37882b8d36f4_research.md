# Group Research: group_873_linux_sources_os_linux_linux_fs_xfs_xfs_inode_item_recover_c_sources_37882b8d36f4

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`; all listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_inode_item_recover.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_inode_item_recover.c

## Role
Implements log recovery for inode log items. During pass 2 recovery it readaheads inode cluster buffers, replays logged inode cores and fork data into on-disk dinodes, handles old 32-bit inode log formats, validates recovered metadata, and queues modified buffers for delayed writeback.

## Main Structures and Entry Points
- `xlog_recover_inode_ra_pass2` starts inode-buffer readahead from the inode log format record, handling native and 32-bit log item formats.
- `xlog_recover_inode_commit_pass2` is the core replay function for `XFS_LI_INODE` items.
- `xfs_recover_inode_owner_change` reconstructs a minimal in-core inode during recovery to reparent BMBT owners after extent swap operations.
- `xfs_log_dinode_to_disk`, timestamp helpers, and extent-count helpers convert the logged dinode representation to on-disk endian format.
- `xlog_recover_inode_dbroot` converts logged data-fork root blocks for normal BMBT and realtime metadata btrees.
- `xlog_inode_item_ops` registers the recovery operations.

## Behavior
The replay path first converts old format items if needed, skips replay if the target inode buffer was canceled, reads the inode buffer, verifies both existing disk inode magic and logged dinode magic, and uses inode LSN/flushiter rules to avoid replaying stale records. It validates logged fork format, fork offset, extent counts, large extent-count feature compatibility, and logged dinode size before copying core fields and optional fork payloads.

For v3 inodes, recovery writes the current transaction LSN to the dinode instead of trusting the logged LSN. It copies device numbers for special files, converts logged data and attr fork payloads according to the log flags, recomputes CRCs, runs full dinode verification, marks the buffer as log-recovery modified, and queues it to the caller's delwri list.

## Interactions
This file depends on bmap btree conversion, realtime rmap/refcount btree conversion, buffer recovery cancellation, inode verifiers, and the log recovery item dispatcher. It is tightly coupled to `xfs_inode_item` log format flags and to fork owner change semantics used by extent swap.

## Invariants and Error Handling
- Recovered regular files must have extent, btree, or meta-btree data forks; directories must have extents, btree, or local data forks.
- Large extent counts require the filesystem feature and zero padding.
- Total data and attr extent counts cannot exceed inode block count.
- Fork offsets and logged dinode sizes are bounded by inode size expectations.
- Owner change replay is skipped for deleted inodes but still attempted when disk inode LSN is newer than the replay item.
- Corruption is reported with `XFS_CORRUPTION_ERROR`/`xfs_alert`, and failures return `-EFSCORRUPTED` or allocation/read errors.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_inode_item_recover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_ioctl.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_ioctl.c

## Role
Provides the primary XFS file ioctl implementation and file attribute get/set operations. It is a major userspace boundary for bulk inode queries, filesystem geometry, extent maps, labels, reserve blocks, growfs, handles, scrub, health monitoring, media verification, exchange/commit range, EOF block freeing, and other XFS management operations.

## Main Structures and Entry Points
- `xfs_file_ioctl` dispatches native ioctls.
- `xfs_fileattr_get` and `xfs_fileattr_set` implement VFS fileattr operations for XFS flags, project IDs, and extent size hints.
- `xfs_ioc_fsbulkstat`, `xfs_ioc_bulkstat`, and `xfs_ioc_inumbers` adapt legacy and v5 inode bulk query APIs to `xfs_itable`.
- `xfs_ioc_fsgeometry`, `xfs_ioc_ag_geometry`, and `xfs_ioc_rtgroup_geometry` report filesystem, allocation group, and realtime group geometry.
- `xfs_ioc_getbmap` returns data/attr fork extent maps via `xfs_getbmap`.
- `xfs_ioc_swapext` validates two XFS file descriptors before invoking extent swap.
- `xfs_ioc_getlabel` and `xfs_ioc_setlabel` expose and update the filesystem label.

## Behavior
Legacy bulkstat/inumbers ioctls copy `xfs_fsop_bulkreq`, enforce `CAP_SYS_ADMIN`, validate count and output buffers, translate the historical `lastip` cursor semantics into internal `xfs_ibulk.startino`, call bulkstat/inumbers walkers, and copy back the updated cursor and output count. The v5 bulk request setup validates flags, reserved fields, special inode requests, AG-limited walks, large extent-count output, and metadata-directory visibility.

File attribute updates validate unsupported flags, project ID width, quota setup, DAX cache behavior, realtime flag transitions, extsize and cowextsize alignment, and v3 inode feature requirements. Updates run in inode-change transactions, adjust project quota ownership if needed, update on-disk diflags/diflags2 and VFS flags, clear setuid/setgid where required, record timestamps, and commit or release dquot references on failure.

The dispatcher consistently gates privileged administrative operations, checks shutdown/read-only state where relevant, uses `mnt_want_write_file` for mutating operations, performs explicit `copy_from_user`/`copy_to_user`, and delegates specialized functionality to XFS subsystems.

## Interactions
This file connects userspace ioctls to `xfs_itable`, `xfs_iwalk`, growfs, discard, quota, fsmap, scrub, health, reflink/exchange range, handle, realtime geometry, zoned allocation, and block garbage collection subsystems. It also shares formatters with `xfs_ioctl32.c` through declarations in `xfs_ioctl.h`.

## Invariants and Error Handling
- Many ioctls require `CAP_SYS_ADMIN`; mutating paths additionally require writable mounts/files.
- Bulk request reserved fields must be zero and unsupported flags are rejected.
- Metadata directory files are hidden from legacy bulkstat unless explicitly requested through v5 flags.
- Realtime flag changes are rejected if the inode already has file data or if DAX device compatibility is unsafe.
- Label changes update the primary superblock, backup superblocks, and invalidate relevant block-device caches.
- Removed allocation/free-space ioctls intentionally return `-ENOTTY` with a one-time warning.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_ioctl.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_ioctl.h

## Role
Declares the native XFS ioctl and file attribute interfaces used by the VFS and compat ioctl layer.

## Main Declarations
- Forward declarations for `struct xfs_bstat`, `struct xfs_ibulk`, and `struct xfs_inogrp`.
- `xfs_ioc_swapext` for extent swap ioctl execution.
- `xfs_fileattr_get` / `xfs_fileattr_set` for VFS file attribute operations.
- `xfs_file_ioctl` and `xfs_file_compat_ioctl` for native and compat ioctl dispatch.
- `xfs_fsbulkstat_one_fmt` and `xfs_fsinumbers_fmt` formatter helpers for bulk inode query output.

## Interactions
Included by the main ioctl implementation, compat ioctl implementation, and inode operation setup. It provides the shared function surface that lets `xfs_ioctl32.c` delegate native-compatible commands and reuse native bulk output formatters for x32/native-layout cases.

## Invariants
The header has no logic, but it establishes that native and compat ioctl dispatch remain separate while sharing common formatter and swapext/fileattr helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_ioctl32.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_ioctl32.c

## Role
Implements 32-bit compat handling for XFS ioctls whose argument layouts, pointer sizes, time fields, or x86 alignment differ from native 64-bit layout.

## Main Structures and Entry Points
- `xfs_file_compat_ioctl` dispatches compat commands and falls back to native dispatch when safe.
- `xfs_compat_ioc_fsbulkstat` handles compat legacy bulkstat and inumbers requests.
- `xfs_fsbulkstat_one_fmt_compat` and `xfs_fsinumbers_fmt_compat` serialize native internal results into compat output structures.
- `xfs_ioctl32_bstat_copyin` and timestamp helpers translate compat `xfs_bstat` input for swapext.
- `xfs_compat_handlereq_copyin` translates handle request structures.
- `xfs_compat_attrlist_by_handle` and `xfs_compat_attrmulti_by_handle` implement handle-based xattr compat ioctls.
- x86 alignment-only helpers handle geometry v1 and growfs structures under `BROKEN_X86_ALIGNMENT`.

## Behavior
Compat bulkstat follows the native legacy cursor semantics, but translates 32-bit user pointers through `compat_ptr`, enforces `CAP_SYS_ADMIN`, validates counts and buffers, and selects native output formatters for x32 syscalls where pointer arguments are compat but data structures use native 64-bit layout.

Compat handle operations copy in 32-bit pointer fields and call the shared handle helpers. Attribute list and multi operations resolve handles to dentries and call native xattr helpers, copying compat operation arrays back to userspace with per-operation error fields.

The compat dispatcher maps 32-bit ioctl numbers to native behavior where possible, wraps mutating operations with `mnt_want_write_file`, and delegates unsupported or native-layout-compatible requests to `xfs_file_ioctl`.

## Interactions
Depends on `xfs_ioctl32.h` for compat structs/ioctl numbers, `xfs_ioctl.h` for native helpers, `xfs_itable` for bulk walking, and `xfs_handle`/`xfs_attr` for handle-based attribute operations.

## Invariants and Error Handling
- Compat pointer values are never used directly; they are converted with `compat_ptr`.
- Administrative bulk and handle-attribute operations require `CAP_SYS_ADMIN`.
- Attribute multi operation arrays are bounded against integer overflow and capped at `16 * PAGE_SIZE`.
- `XFS_IOC_GETVERSION_32` is remapped to native ioctl encoding with `long` size.
- Swapext compat copies the fixed prefix and translates the embedded bstat field separately.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_ioctl32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_ioctl32.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_ioctl32.h

## Role
Defines compat XFS ioctl structures and ioctl command numbers for 32-bit userspace on 64-bit kernels, including x86-specific packed layouts for historical alignment differences.

## Main Declarations
- `XFS_IOC_GETVERSION_32` and compat bulkstat/inumbers ioctl numbers.
- `compat_xfs_bstime`, `compat_xfs_bstat`, and `compat_xfs_fsop_bulkreq`.
- Compat handle request, swapext, attrlist-by-handle, and attrmulti-by-handle structures.
- Under `BROKEN_X86_ALIGNMENT`, packed compat geometry v1, inogrp, and growfs data/realtime structures plus associated ioctl numbers.

## Behavior Encoded by Types
The definitions preserve 32-bit pointer fields as `compat_uptr_t`, old 32-bit timestamps as `old_time32_t`, and packed layouts when x86_64 native alignment would otherwise mismatch historical userspace ABI.

## Interactions
Consumed by `xfs_ioctl32.c` to copy fields to/from userspace and to dispatch compat command numbers. The header also documents which native APIs require translation rather than direct fallback.

## Invariants
The ABI structures intentionally mirror 32-bit userspace layout; fields and packing are compatibility contracts and must not be casually rearranged.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_ioctl32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iomap.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_iomap.c

## Role
Implements XFS mappings for the kernel iomap layer. It translates XFS bmbt extents into iomaps, allocates or reserves blocks for direct, buffered, DAX, reflink/COW, atomic, zoned, read, seek, xattr, zero, and truncate operations, and supplies the `iomap_ops` tables used throughout XFS I/O.

## Main Structures and Entry Points
- `xfs_bmbt_to_iomap` converts an XFS extent record into a generic `struct iomap`.
- `xfs_iomap_inode_sequence` and `xfs_iomap_valid` provide stale-map detection through data/attr/COW fork sequence cookies.
- `xfs_iomap_write_direct` performs transaction-backed direct-write block allocation or DAX conversion.
- `xfs_direct_write_iomap_begin`, `xfs_buffered_write_iomap_begin`, `xfs_zoned_buffered_write_iomap_begin`, `xfs_zoned_direct_write_iomap_begin`, and `xfs_atomic_write_cow_iomap_begin` are write mapping paths for different I/O modes.
- `xfs_iomap_prealloc_size` and `xfs_bmapi_reserve_delalloc` implement dynamic buffered delayed-allocation reservation and speculative preallocation.
- `xfs_iomap_write_unwritten` converts unwritten extents after I/O completion.
- `xfs_read_iomap_begin`, `xfs_seek_iomap_begin`, and `xfs_xattr_iomap_begin` map reads, seek-data/hole probing, and attr fork access.
- `xfs_zero_range` and `xfs_truncate_page` bridge truncate/zero helpers to DAX or buffered iomap operations.
- Exports several `const struct iomap_ops` and `const struct iomap_write_ops`.

## Behavior
Mapping conversion rejects invalid start blocks, reports holes, delalloc, unwritten, mapped extents, DAX offsets, integrity checksum flags, dirty inode-log state for datasync, and realtime-group merge boundaries. EOF allocation can be aligned to stripe/extent-size hints, and preallocation grows with file size but is throttled by global free space and user/group/project quota watermarks.

Direct writes first read the current mapping, decide if allocation or COW is needed, enforce nowait/overwrite-only constraints, support hardware atomic writes only when one naturally aligned extent spans the write, allocate blocks through transactions when needed, and return source maps for COW. DAX maps convert unwritten extents before data copy and complete COW at iomap end.

Buffered writes use delayed allocation unless extent-size hints or zoned allocation require other paths. They consider data fork and COW fork mappings together, handle unshare and zeroing specially, reserve delalloc blocks and quota, tag EOF/COW speculative preallocations, release unused new delalloc on short writes, and fill dirty folio batches to correctly zero ranges backed transiently by COW/pagecache state.

Atomic software writes allocate and convert COW fork mappings so data can be written out of place. Zoned buffered writes reserve from a caller-provided zone allocation context and map COW fork delalloc, while zoned direct writes report anonymous mappings whose actual extent recording is deferred to I/O completion.

## Interactions
This file is central to XFS I/O and interacts with bmap, reflink, quota, transaction reservation, realtime groups, zoned allocation, inode fork sequence counters, DAX, iomap writeback, pagecache invalidation, and inode operations (`xfs_iops.c` uses zero/truncate helpers and fiemap operations).

## Invariants and Error Handling
- Shutdown filesystems return `-EIO`; nowait paths return `-EAGAIN` rather than blocking on extent reads or allocations.
- Invalid block zero access marks the data fork sick and returns `-EFSCORRUPTED`.
- Atomic hardware writes require natural alignment, one covering extent, and size within the block device atomic write limit.
- Delalloc reservations update quota, free block/free realtime counters, `i_delayed_blks`, and delalloc accounting together, with rollback on failure.
- New delalloc mappings are flagged `IOMAP_F_NEW` so failed buffered writes can punch unused reservations.
- COW maps use `IOMAP_F_SHARED` and include validity cookies spanning data and COW fork sequences.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iomap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iomap.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_iomap.h

## Role
Declares XFS iomap helper functions and operation tables used by XFS file I/O, fiemap, xattr mapping, zeroing, and truncate code.

## Main Declarations
- Allocation/conversion helpers: `xfs_iomap_write_direct`, `xfs_iomap_write_unwritten`, `xfs_iomap_eof_align_last_fsb`.
- Mapping helpers: `xfs_iomap_inode_sequence`, `xfs_bmbt_to_iomap`.
- Zero/truncate helpers: `xfs_zero_range`, `xfs_truncate_page`.
- `xfs_aligned_fsb_count` inline helper expands a file-block count to satisfy extent-size alignment.
- Iomap ops tables for buffered write, direct write, zoned direct write, read, seek, xattr, DAX write, atomic-write COW, and write validation.

## Interactions
Included by inode operations and other XFS I/O code. It is the public boundary for `xfs_iomap.c` and advertises the set of iomap modes XFS supports.

## Invariants
`xfs_aligned_fsb_count` preserves the original requested span while extending start/end coverage to an extent-size multiple when a nonzero extent size hint is supplied.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iomap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iops.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_iops.c

## Role
Implements the Linux VFS inode operations for XFS. It handles inode creation, lookup, linking, unlinking, symlinks, renames, tmpfile creation, getattr/statx, setattr/truncate, timestamp updates, fiemap, security xattrs, DAX flag setup, and inode operation table initialization.

## Main Structures and Entry Points
- `xfs_generic_create` underpins create, mknod, mkdir, and tmpfile.
- `xfs_vn_lookup` and `xfs_vn_ci_lookup` implement normal and ASCII case-insensitive lookup.
- `xfs_vn_link`, `xfs_vn_unlink`, `xfs_vn_symlink`, and `xfs_vn_rename` map VFS namespace operations to XFS directory operations.
- `xfs_vn_getattr` fills `kstat`, including DIO alignment and atomic write statx fields.
- `xfs_vn_setattr`, `xfs_vn_setattr_size`, and `xfs_setattr_nonsize` implement size and non-size attribute changes.
- `xfs_vn_update_time` and `xfs_vn_sync_lazytime` log timestamp changes.
- `xfs_vn_fiemap` delegates data or attr fork extent reporting to iomap.
- `xfs_setup_inode`, `xfs_setup_iops`, and `xfs_diflags_to_iflags` initialize VFS inode state and operation tables.
- `xfs_get_atomic_write_min/max/max_opt` compute advertised atomic write limits.

## Behavior
Creation validates device numbers, prepares POSIX ACLs, pre-creates attr forks when ACL/security xattrs are likely, creates named or temporary inodes, initializes security xattrs and ACLs, installs inode operations, and cleans up created directory entries on post-create failure. Tmpfiles adjust link count to satisfy VFS `d_tmpfile` requirements while preserving XFS unlinked-list rules.

Lookup converts dentries to XFS names and uses `d_splice_alias`; case-insensitive lookup can return `d_add_ci` with the canonical name. Link/unlink/rename convert VFS names to XFS typed names and call XFS namespace helpers, invalidating negative dentries for case-insensitive unlink.

Getattr reports XFS disk size, block counts including delayed blocks, birth time for v3 inodes, immutable/append/nodump flags, block size hints, DIO alignment, COW write alignment, and atomic write limits. Setattr splits size changes from other changes: truncation locks out mmap faults/layouts, waits for direct I/O, zeroes exposed partial blocks, updates page cache size, writes needed ranges to avoid stale exposure, logs disk size before freeing extents, and marks truncated inodes for earlier flush. Non-size updates handle quota allocation/chown, VFS attribute copy, transaction logging, and ACL chmod follow-up.

## Interactions
This file sits between the VFS and XFS core subsystems: directory operations, inode allocation, symlinks, ACLs, xattrs, quota, iomap, file operations, DAX, stable writes, pagecache, block layout breaking, and transaction logging. It exports setup functions used when inodes are read or created.

## Invariants and Error Handling
- Directory inode locks use distinct lockdep classes from non-directories, with metadata directories separated.
- Internal metadata inodes are marked `S_PRIVATE` and stripped of normal xattr behavior.
- Page cache allocations are forced into no-FS reclaim context to avoid recursion.
- Size changes require regular files and exclusive IO/MMAP locks.
- Disk size is logged before block freeing on truncate down to avoid exposing freed/reallocated block contents after crash.
- Lazytime may only mark `I_DIRTY_TIME`; non-lazy nowait timestamp updates return `-EAGAIN`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iops.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_iops.h

## Role
Declares the XFS inode-operation functions and inode setup helpers used outside `xfs_iops.c`.

## Main Declarations
- `xfs_vn_listxattr` from the xattr subsystem.
- `xfs_vn_setattr_size` for explicit size-change handling.
- `xfs_inode_init_security` for LSM security xattr initialization.
- `xfs_setup_inode`, `xfs_setup_iops`, and `xfs_diflags_to_iflags` for VFS inode initialization.
- Atomic write stat helpers: `xfs_get_atomic_write_min`, `xfs_get_atomic_write_max`, and `xfs_get_atomic_write_max_opt`.

## Interactions
Used by inode allocation/read paths and by code that needs to query XFS atomic write capabilities without depending on the full inode operation implementation details.

## Invariants
The header separates setup/stat helper declarations from the private VFS operation tables, which remain internal to `xfs_iops.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_itable.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_itable.c

## Role
Implements bulk inode stat and inode-number table queries. It walks allocated inode records through `xfs_iwalk`/`xfs_inobt_walk`, formats internal v5 bulk result structures, and lets ioctl callers provide output formatters for legacy or native userspace ABI layouts.

## Main Structures and Entry Points
- `xfs_bulkstat_one` returns one inode's bulkstat data.
- `xfs_bulkstat` walks allocated inodes starting from a cursor and formats multiple records.
- `xfs_bulkstat_to_bstat` converts v5 `xfs_bulkstat` to legacy `xfs_bstat`.
- `xfs_inumbers` walks inode btree records and formats inode allocation groups.
- `xfs_inumbers_to_inogrp` converts v5 `xfs_inumbers` to legacy `xfs_inogrp`.
- Internal `xfs_bulkstat_one_int` gathers metadata for one inode.

## Behavior
Bulkstat uses `xfs_iget` with `XFS_IGET_DONTCACHE | XFS_IGET_UNTRUSTED`, skips missing/freed/internal private inodes, reloads incomplete unlinked-list state when needed, maps inode uid/gid through the mount idmap, fills size, timestamps, generation, mode, xflags, extent counts, fork offsets, health state, v3 birth time and CoW extent size, device fields, block size, and block counts. Metadata directory files can be minimally exposed when the request sets `XFS_IBULK_METADIR`.

The cursor `breq->startino` advances past skipped or successfully emitted inodes so userspace can resume. Formatter `-ECANCELED` means the caller's output buffer filled; the public functions hide that from userspace when records were produced.

Inumbers formats inobt records as start inode, allocated count, allocation mask, and version. It similarly advances the cursor by one inode chunk and clears errors when at least one record was returned.

## Interactions
Called by native and compat ioctl code. Relies on `xfs_iwalk` for allocated inode iteration, `xfs_inobt_walk` for raw inode btree record iteration, inode cache lookup, health reporting, unlinked-list reload, and empty transactions for recursive buffer locking/cycle detection.

## Invariants and Error Handling
- Bulkstat is rejected inside idmapped mounts because the exported ABI cannot represent that safely.
- Start inode values that do not map into the filesystem are treated as already done.
- Private inodes and superblock inodes are not leaked through normal bulkstat.
- Errors after some output records are suppressed so the next call resumes at the problematic cursor and can report the error without partial output.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_itable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_itable.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_itable.h

## Role
Defines the internal bulk inode query request structure, flags, formatter callback types, and exported bulkstat/inumbers APIs.

## Main Declarations
- `struct xfs_ibulk` carries mount/idmap, user output buffer, start cursor, input/output counts, request flags, and iwalk flags.
- Flags `XFS_IBULK_NREXT64` and `XFS_IBULK_METADIR` request 64-bit extent counts and metadata directory visibility.
- `xfs_ibulk_advance` moves the userspace output pointer, increments output count, and returns `-ECANCELED` when full.
- Formatter typedefs `bulkstat_one_fmt_pf` and `inumbers_fmt_pf`.
- Bulk APIs and conversion helpers for v5 and legacy structs.

## Interactions
Used by ioctl native/compat code and implemented by `xfs_itable.c`. Its callback design keeps inode walking independent from ABI-specific userspace copyout layouts.

## Invariants
`xfs_ibulk_advance` defines the shared buffer-full sentinel behavior: reaching `icount` returns `-ECANCELED`, which callers translate into successful partial completion as appropriate.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_itable.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iunlink_item.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_iunlink_item.c

## Role
Implements an in-memory-only log item used to order updates to the on-disk unlinked inode list. The item runs at transaction precommit to update a dinode's `di_next_unlinked` field in the correct buffer logging order.

## Main Structures and Entry Points
- `xfs_iunlink_cache` is the kmem cache for `struct xfs_iunlink_item`.
- `xfs_iunlink_log_inode` allocates and joins an iunlink item to a transaction.
- `xfs_iunlink_item_precommit` updates the dinode before commit and releases the item.
- `xfs_iunlink_log_dinode` reads the inode cluster buffer, verifies the old pointer, writes the new pointer, updates CRC, and logs the precise buffer range.
- `xfs_iunlink_item_ops` provides release, sort, and precommit callbacks.

## Behavior
The public function validates the new and old AG inode pointers, treats a no-op NULL-to-NULL transition as success, rejects a non-NULL self-transition as corruption, saves the inode, perag, new pointer, and old pointer into a dirty log item, and marks the transaction dirty. At precommit, the item maps the inode buffer and updates `di_next_unlinked` unless the buffer is stale because the transaction may be freeing the inode cluster.

## Interactions
Used by unlinked inode list update code to coordinate dinode logging with transaction ordering. Holds a passive perag reference until release. Uses inode buffer mapping, transaction buffer logging, inode verifier errors, tracepoints, and log item sorting by inode number.

## Invariants and Error Handling
- The on-disk old pointer must match the in-core saved old pointer; mismatch is `-EFSCORRUPTED`.
- Stale inode buffers are not relogged because doing so would clear stale state incorrectly.
- Precommit always removes the log item from the transaction and frees it after attempting the dinode update.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iunlink_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iunlink_item.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_iunlink_item.h

## Role
Declares the in-memory iunlink log item structure and the helper for logging unlinked-list pointer changes.

## Main Declarations
- `struct xfs_iunlink_item` embeds `struct xfs_log_item`, points to the inode and perag, and records new and old next-agino values.
- `xfs_iunlink_cache` exposes the item kmem cache.
- `xfs_iunlink_log_inode` joins an iunlink update to a transaction.

## Interactions
Consumed by unlinked inode list maintenance and implemented by `xfs_iunlink_item.c`. The structure records exactly the state needed to verify and update `di_next_unlinked` during precommit.

## Invariants
The item is not a persistent log replay item; it is an in-memory transaction ordering helper whose state must be consumed before commit.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iunlink_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iwalk.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_iwalk.c

## Role
Implements inode and inode-btree record walkers for XFS. It iterates allocated inodes or raw inobt records in increasing inode order, starting from an inode cursor, with optional single-AG limitation and optional threaded per-AG execution.

## Main Structures and Entry Points
- `struct xfs_iwalk_ag` stores per-AG walk state, cached inobt records, callbacks, transaction/perag references, flags, and optional parallel work state.
- `xfs_iwalk` walks allocated inodes with a caller callback.
- `xfs_iwalk_threaded` queues one work item per allocation group for parallel inode walking.
- `xfs_inobt_walk` walks inobt records directly.
- Internal helpers allocate record caches, start btree cursors at the correct point, run callbacks safely, and compute prefetch sizes.

## Behavior
The walker reads inobt records under an AGI btree cursor but does not call arbitrary callbacks while holding cursor state. Instead it caches inobt records in memory, tears down the cursor and AGI buffer, runs callbacks over cached records, then recreates the cursor at the next inode record. This avoids holding btree state across callbacks that may perform filesystem operations.

For inode walks, free bits in each inobt record are used to skip free inodes, and allocated inode clusters are readaheaded before callbacks. When starting in the middle of a chunk, earlier bits are marked free so records are not returned twice. Empty records can be skipped for inode walks. The code detects non-forward cursor progress and marks the btree sick on corruption.

Threaded walking uses `xfs_pwork` to allocate per-AG work state, hold perag references for async execution, allocate an empty transaction per worker for recursive buffer locking, and support polling/abort.

## Interactions
Used by `xfs_itable.c` for bulkstat/inumbers and by other filesystem scans that need safe inode iteration. Depends on ialloc/inobt btree cursor APIs, perag iteration, inode buffer readahead, transaction buffer locking, health marking, and parallel work helpers.

## Invariants and Error Handling
- Callback return values propagate; `-ECANCELED` is reserved as a caller-controlled stop sentinel.
- Start flags are limited to `XFS_IWALK_SAME_AG`.
- Inobt record cache size is at least two records to simplify mid-record starts and cursor restart.
- Prefetch is capped to avoid excessive memory or readahead.
- Cursor and AGI buffer are always released through `xfs_iwalk_del_inobt`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iwalk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iwalk.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_iwalk.h

## Role
Declares XFS inode walking and inode-btree walking APIs plus callback types and flags.

## Main Declarations
- `xfs_iwalk_fn` callback receives mount, transaction, inode number, and caller data for allocated inode walks.
- `xfs_iwalk` performs single-threaded allocated inode walking.
- `xfs_iwalk_threaded` performs per-AG threaded allocated inode walking.
- `XFS_IWALK_SAME_AG` restricts iteration to the allocation group containing `startino`.
- `xfs_inobt_walk_fn` callback receives mount, transaction, AG number, inobt record, and caller data.
- `xfs_inobt_walk` walks raw inode btree records.

## Interactions
Used by bulkstat/inumbers and any XFS code that must scan allocated inodes or inode allocation records without embedding btree traversal details.

## Invariants
Callbacks return 0 to continue or any nonzero value to stop and propagate. `-ECANCELED` is documented as a safe sentinel because the walkers do not generate it internally.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_iwalk.h -->