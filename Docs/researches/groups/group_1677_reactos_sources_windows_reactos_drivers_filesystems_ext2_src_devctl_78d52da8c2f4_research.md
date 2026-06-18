# Group Research: group_1677_reactos_sources_windows_reactos_drivers_filesystems_ext2_src_devctl_78d52da8c2f4

Scope: `Docs/research_subset_a.md` includes `sources/windows/reactos`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/devctl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/devctl.c

This file implements Ext2Fsd device-control dispatch for app-facing IOCTLs and pass-through device IOCTLs. It handles volume/global property control, performance-stat queries, DOS mount-point symbolic links, and optional driver unload preparation.

Key responsibilities:
- Dispatch `IRP_MJ_DEVICE_CONTROL` requests by IOCTL code.
- Forward unrecognized device controls to the mounted volume's lower storage device.
- Apply or query global and per-volume Ext2Fsd properties.
- Expose driver version/build strings and performance counters.
- Add/delete `\DosDevices\Global\X:` symbolic links for mount points.
- Optionally transition the driver into an unload-ready state.

Important functions:
- `Ext2DeviceControl`: Top-level IOCTL switch for `IOCTL_APP_VOLUME_PROPERTY`, `IOCTL_APP_QUERY_PERFSTAT`, `IOCTL_APP_MOUNT_POINT`, optional `IOCTL_PREPARE_TO_UNLOAD`, and lower-driver forwarding.
- `Ext2DeviceControlNormal`: Validates the request is for a volume, copies the stack location to the next IRP stack slot, installs `Ext2DeviceControlCompletion`, and calls the target device.
- `Ext2ProcessGlobalProperty`: Handles global read/write policy, ext3 force-write policy, automount, hiding prefix/suffix patterns, codepage loading, and version query.
- `Ext2ProcessVolumeProperty`: Handles per-volume readonly/ext3-writable state, journal recovery attempt, hiding rules, drive letter, user id overrides, UUID, codepage, and automount query/set state.
- `Ext2ProcessUserProperty`: Validates property magic, routes requests to global versus volume property processors, and returns the full property buffer length on success.
- `Ex2ProcessUserPerfStat`: Returns global performance counters in v1 or v2 layout after validating magic, command, and buffer size.
- `Ex2ProcessMountPoint`: Creates or deletes a DOS-device symlink for a requested drive letter.
- `Ext2PrepareToUnload`: Under `EXT2_UNLOAD`, removes dismounted VCBs, refuses unload if mounted volumes remain, unregisters file-system devices, and sets `EXT2_UNLOAD_PENDING`.

Important interactions:
- Uses `Ext2Global->Resource` for global property/unload serialization and `Vcb->MainResource` for per-volume property changes.
- Calls `Ext2FlushFiles`, `Ext2FlushVolume`, and `Ext2RecoverJournal` when changing volume writability.
- Uses NLS `load_nls` to install global or volume codepage tables.
- Completes requests through `Ext2CompleteIrpContext`, except forwarded IOCTLs detach the IRP from the context.

Notable behavior and risks:
- Several property switch cases intentionally fall through from v3 to v2 to v1 handling.
- The ReactOS-specific code changes some original assignment-in-condition patterns for hiding flags into comparisons, which may alter upstream Ext2Fsd behavior.
- Per-volume codepage assignment stores the table pointer even if `load_nls` fails; label initialization is gated on a non-null page table.
- `Ex2ProcessMountPoint` trusts a single drive-letter character and constructs only `\DosDevices\Global\Z:`-style links.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/devctl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/dirctl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/dirctl.c

This file implements directory-control IRPs for Ext2Fsd. It converts ext2/ext3 directory entries into Windows directory-information records, supports wildcard query state, handles htree-indexed directories when enabled, registers change-notification IRPs, reports directory changes, and checks directory emptiness.

Key responsibilities:
- Serve `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`.
- Populate all supported Windows directory information classes.
- Maintain per-handle search pattern and enumeration position in the CCB.
- Hide configured names and skip `.`/`..` during enumeration.
- Translate OEM ext directory names to Unicode and apply Windows wildcard matching.
- Bridge ext3 htree readdir callbacks into the Windows output buffer.

Important functions:
- `Ext2GetInfoLength`: Returns the fixed prefix length for each supported `FILE_INFORMATION_CLASS`.
- `Ext2ProcessEntry`: Builds directory info records; loads inode data if no MCB is cached; follows symlink MCBs; sets attributes, sizes, times, file ids, and symlink reparse tags.
- `Ext2IsWearingCloak`: Applies per-volume hiding prefix/suffix filters while preserving `.` and `..`.
- `Ext2FillEntry`: Htree callback used by `ext3_dx_readdir`; converts names, filters them, matches search patterns, and calls `Ext2ProcessEntry`.
- `Ext2QueryDirectory`: Validates the target directory, acquires the FCB resource, initializes/reuses the search pattern, manages restart/index/single-entry flags, tries indexed-directory enumeration, and falls back to linear scanning.
- `Ext2NotifyChangeDirectory`: Registers a notify IRP with `FsRtlNotifyFullChangeDirectory` and leaves it pending.
- `Ext2NotifyReportChange`: Emits change notifications for an MCB path.
- `Ext2DirectoryControl`: Minor-function dispatcher.
- `Ext2IsDirectoryEmpty`: Delegates to `ext3_is_dir_empty`.

Important interactions:
- Calls into htree support through `ext3_dx_readdir` when directory-index features are present.
- Uses `Ext2ReadInode` for linear directory entry headers and `Ext2ProcessEntry` for Windows records.
- Directory change registration and reporting share `Vcb->NotifySync` and `Vcb->NotifyList`.

Notable behavior and risks:
- If htree enumeration returns `ERR_BAD_DX_DIR`, it clears `EXT3_INDEX_FL` in memory and scans linearly without marking the inode dirty.
- Linear scanning treats `rec_len == 0` as "skip to end of block", preventing an infinite loop but potentially masking malformed entries.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/dirctl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/dispatch.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/dispatch.c

This file is the central IRP dispatch and async work-queue bridge for Ext2Fsd. It builds IRP contexts, enters file-system critical regions, handles top-level IRP state, queues requests that must run later, and maps major IRP functions to operation-specific handlers.

Key responsibilities:
- Build and dispatch an `EXT2_IRP_CONTEXT` for each incoming IRP.
- Queue requests to a system work queue when the operation needs waitable context.
- Lock user buffers before pending queued requests.
- Resume operations after oplock completion.
- Wrap dispatch in structured exception handling.

Important functions:
- `Ext2OplockComplete`: Requeues the IRP context after successful oplock completion or completes it with the IRP error status.
- `Ext2LockIrp`: Locks user buffers for read/write, query-directory, query/set EA, and selected filesystem-control output buffers.
- `Ext2QueueRequest`: Sets wait/requeued flags, locks the IRP buffer, initializes the work item, queues it, and returns `STATUS_PENDING`.
- `Ext2DeQueueRequest`: Worker callback that enters the file system, sets top-level IRP if needed, dispatches, and handles exceptions.
- `Ext2DispatchRequest`: Major-function switch for create, close, read, write, flush, information, directory control, filesystem control, device control, locking, cleanup, shutdown, EA, and PnP.
- `Ext2BuildRequest`: Driver dispatch entry point.

Notable behavior and risks:
- `Ext2LockIrp` uses write parameters for both read and write lengths, relying on IRP stack layout compatibility.
- Queued work runs in `CriticalWorkQueue`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/dispatch.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ea.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ea.c

This file implements Windows extended-attribute query and set operations over ext4 xattr storage. It translates between Windows `FILE_FULL_EA_INFORMATION` buffers and `ext4_xattr_ref` items in the `EXT4_XATTR_INDEX_USER` namespace.

Key responsibilities:
- Enumerate all user xattrs, a single indexed xattr, or a caller-specified EA list.
- Format EA query results as linked Windows full-EA records.
- Validate EA names using Windows/FAT-compatible ANSI-name rules.
- Replace a file's user EA set from a caller-provided full-EA buffer.

Important functions:
- `Ext2IterateAllEa`: Copies one xattr item into a `FILE_FULL_EA_INFORMATION` record and tracks overflow/single-entry state.
- `Ext2QueryEa`: Parses query flags and buffers, obtains an xattr reference, handles named EA-list queries, index-based queries, or scans, updates `Ccb->EaIndex`, and reports output byte count.
- `Ext2IsEaNameValid`: Rejects empty or over-255-byte names and validates non-DBCS bytes.
- `Ext2SetEa`: Validates the caller EA buffer, purges existing xattr items, validates names, and adds each EA through `ext4_fs_set_xattr_ordered`.

Notable behavior and risks:
- `Ext2SetEa` purges existing EA items before validating and adding the new set; failure relies on clearing `xattr_ref.dirty` to discard uncommitted changes.
- `Ext2QueryEa` emits a change notification on successful query, which is unusual because queries do not modify EA state.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ea.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/except.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/except.c

This file centralizes structured exception filtering and recovery for Ext2Fsd IRP dispatch. It records exception status in the IRP context, distinguishes expected NTSTATUS exceptions from fatal bugs, handles verify/hard-error flows, and may requeue top-level operations.

Key responsibilities:
- Log exception records and context records.
- Validate the IRP context before using it.
- Convert expected exceptions into normal Ext2Fsd error handling.
- Bugcheck on unexpected exceptions without a valid IRP context.
- Complete, requeue, verify, or hard-error the active IRP as appropriate.

Important functions:
- `Ext2ExceptionFilter`: Prints diagnostics, validates `EXT2_IRP_CONTEXT`, sets wait/exception fields, catches expected exceptions and dismounted-volume cases, or frees the context when continuing search.
- `Ext2ExceptionHandler`: Converts the saved exception code into IRP completion status, checks VCB validity and mount state, requeues selected cases, handles user-induced errors, performs volume verification, and completes/frees the context.

Notable behavior and risks:
- The filter unconditionally calls `DbgBreak()` after printing exception details.
- Verify-required handling may complete root creates with `STATUS_REPARSE` and `IO_REMOUNT`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/except.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/generic.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/generic.c

This file provides the broad ext2/ext3/ext4 metadata support layer used by the Windows driver. It loads/saves superblocks, group descriptors, inodes, and buffers; manages block and inode allocation bitmaps; updates directory entries and link counts; initializes uninitialized ext4 bitmaps; computes group-descriptor checksums; and exposes ext3/ext4 helper accessors.

Key responsibilities:
- Load, refresh, save, and flush volume metadata.
- Manage buffer-head caches for group descriptors and metadata blocks.
- Translate raw ext3 inodes to/from in-memory `struct inode`.
- Allocate and free blocks and inodes while maintaining bitmaps, group descriptors, and superblock counts.
- Add/remove directory entries and update parent/file type metadata.
- Support ext4-style 64-bit descriptor fields, huge-file block counts, metadata checksums, sparse-super/meta-bg layouts, and uninitialized bitmaps.

Important functions:
- `Ext2LoadSuper`, `Ext2SaveSuper`, `Ext2RefreshSuper`: Superblock I/O and root inode refresh.
- `Ext2LoadGroup`, `Ext2LoadGroupBH`, `Ext2DropGroupBH`, `Ext2PutGroup`: Group-descriptor discovery, loading, validation, and release.
- `Ext2GetInodeLba`, `Ext2LoadInode`, `Ext2SaveInode`, `Ext2ClearInode`: Inode table addressing and raw inode persistence.
- `Ext2DecodeInode`, `Ext2EncodeInode`: Convert mode, flags, uid/gid, size, acl, times, blocks, and extra inode size.
- `Ext2NewBlock`, `Ext2FreeBlock`: Allocate/free block runs using group bitmaps.
- `Ext2NewInode`, `Ext2FreeInode`, `Ext2UpdateGroupDirStat`: Allocate/free inode bitmap bits and update directory counts.
- `Ext2AddEntry`, `Ext2RemoveEntry`, `Ext2SetFileType`, `Ext2SetParentEntry`: Higher-level directory mutations around ext3 helpers.
- `ext4_get_group_desc`, `ext4_init_inode_bitmap`, `ext4_init_block_bitmap`, `ext4_check_descriptors`: Descriptor access, lazy bitmap initialization, and validation.

Notable behavior and risks:
- Allocation code sometimes repairs stale free-count metadata by setting a group's free count to zero and retrying another group.
- `Ext2SaveInode` reads the existing raw inode before encoding, preserving fields not represented in memory.
- `Ext2LoadInodeXattr` reads the raw inode and then calls `Ext2EncodeInode` into the same buffer, combining current core inode fields with raw tail data.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/generic.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/htree.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/htree.c

This file implements ext3 directory helper logic, including htree indexed directory hashing, lookup, readdir, insertion, splitting, linear fallback, deletion, and empty-directory checks. It is Linux ext3 code adapted to the Ext2Fsd/ReactOS buffer-head and IRP-context environment.

Key responsibilities:
- Provide ext3 directory hash functions and htree index traversal under `EXT2_HTREE_INDEX`.
- Read metadata directory blocks through Ext2Fsd mapping paths.
- Add, find, delete, and validate ext3 directory entries.
- Convert one-block linear directories into indexed htree directories.
- Split full directory leaf/index blocks during insertion.
- Feed htree directory results to Windows directory enumeration in stable hash order.

Important functions:
- `ext3_dirhash`: Implements ext3 legacy, half-MD4, and TEA filename hashes.
- `ext3_bread`: Maps a directory logical block through extents or indirect mapping and reads it into a buffer head.
- `ext3_append`: Extends a directory by one filesystem block via `Ext2ExpandFile`.
- `add_dirent_to_buf`: Inserts a dirent, checks duplicates, updates directory times/version, marks inode and buffer dirty.
- `dx_probe`, `dx_release`, `ext3_htree_next_block`: Validate and traverse htree root/node entries.
- `ext3_dx_readdir`: Delivers hash-sorted htree entries through a `filldir` callback.
- `ext3_dx_find_entry`, `ext3_find_entry`: Lookup names through htree or linear scan.
- `ext3_dx_add_entry`, `do_split`, `make_indexed_dir`, `ext3_add_entry`: Indexed and linear directory insertion.
- `ext3_delete_entry`, `ext3_is_dir_empty`: Removal and rmdir emptiness checks.

Notable behavior and risks:
- `dx_probe` returns `ERR_BAD_DX_DIR` for unsupported/corrupt htree formats; callers must not surface that directly to user mode.
- `ext3_find_entry` disables htree lookup for create IRPs.
- `add_dirent_to_buf` releases the buffer on all outcomes except `-ENOSPC`, so callers must follow that ownership convention.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/htree.c -->