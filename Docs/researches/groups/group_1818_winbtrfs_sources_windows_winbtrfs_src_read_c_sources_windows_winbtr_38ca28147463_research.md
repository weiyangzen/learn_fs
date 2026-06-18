# Group Research: group_1818_winbtrfs_sources_windows_winbtrfs_src_read_c_sources_windows_winbtr_38ca28147463

Scope verified against `Docs/research_subset_a.md`: `sources/windows/winbtrfs` is included in subset A. All four listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/read.c -->
# File Research: sources/windows/winbtrfs/src/read.c

## Purpose

`read.c` implements the WinBtrfs filesystem driver read path. It covers checksum calculation/verification, logical-to-physical reads across Btrfs chunk profiles, degraded and checksum-error recovery for mirrored and parity layouts, compressed extent handling, alternate data stream reads, cache manager integration, and the `IRP_MJ_READ` dispatch routine.

This file is central to correctness: it decides which devices to read from, validates returned data against Btrfs checksums and tree headers, repairs bad mirrors/parity members when possible, decompresses file data, fills holes with zeroes, and bridges Windows IRP/cache-manager behavior to Btrfs extent storage.

## Main Data Structures

- `enum read_data_status`: tracks each physical stripe request as pending, success, error, missing device, or skipped.
- `read_data_stripe`: per-stripe read state, including associated IRP, IOSB, MDL, stripe number, and physical stripe byte range.
- `read_data_context`: shared context for a logical read across devices; owns the completion event, stripe array, checksum pointer, target chunk/profile type, sector geometry, and optional temporary virtual address buffer.
- `read_part_extent`: describes one logical file extent segment inside a coalesced compressed read.
- `read_part`: queued physical read work for `read_file`; records disk address, chunk, checksum data, target buffer, compression, and one or more extent fragments.
- `comp_calc_job`: tracks asynchronous decompression jobs scheduled via the calculation thread infrastructure.

## Checksum Helpers

`check_csum` allocates a temporary checksum buffer, calls `do_calc_job`, and compares all sector checksums. It returns `STATUS_CRC_ERROR` on mismatch and propagates allocation failures.

`get_tree_checksum` and `check_tree_checksum` implement tree-block checksum support for CRC32C, XXHASH, SHA256, and BLAKE2. Tree checksum inputs begin at `tree_header.fs_uuid`, excluding the stored checksum field. `check_tree_checksum` logs expected/actual values for CRC32C and XXHASH and returns false for mismatch.

`get_sector_csum` and `check_sector_csum` perform the same checksum-family selection for one filesystem sector. These helpers are used when isolating which sector inside a larger read failed validation.

## Physical Read Completion

`read_data_completion` is the lower-device IRP completion routine. It copies `Irp->IoStatus` into the stripe state, maps success/failure to `ReadDataStatus_Success` or `ReadDataStatus_Error`, decrements the shared `stripes_left`, signals the event when all submitted reads complete, and returns `STATUS_MORE_PROCESSING_REQUIRED` so the caller retains control of associated IRP cleanup.

## Chunk Profile Read/Recovery Helpers

`read_data_dup` handles SINGLE, DUP, RAID1, RAID1C3, and RAID1C4-style mirrored reads. It selects the first successful stripe, verifies either tree metadata or file checksums, and if corrupted, attempts to reread alternate mirrors. On successful recovery it copies good data into the caller buffer and, when the volume and target device are writable, writes the good sector/tree back to the bad mirror. It logs Btrfs device stats for read, corruption, generation, and write errors.

`read_data_raid0` validates non-redundant striped reads. It cannot recover: stripe read errors or checksum/tree-header mismatches become hard failures. It maps failed sectors back to the physical RAID0 stripe with `get_raid0_offset` for device error accounting.

`read_data_raid10` combines RAID0 placement with mirrored substripes. It validates the selected mirror and, on checksum/tree-generation failure, rereads another mirror in the same substripe set. It can rewrite recovered tree blocks or sectors to the bad mirror when allowed.

`read_data_raid5` validates and reconstructs RAID5 data. It first overlays in-memory `partial_stripe` data from the chunk when present, protecting reads that overlap pending parity-stripe updates. On checksum failure or degraded mode, it reconstructs missing/bad tree blocks or sectors by XORing all other stripes. It supports repair writeback to the failed/corrupt device when writable.

`raid6_recover2` reconstructs two missing RAID6 stripes using P/Q parity and Galois-field math. It supports the case where one missing stripe is P parity, and the general case using P and Q equations.

`read_data_raid6` extends RAID5 logic to dual-parity layouts. It overlays partial stripes, validates checksums/tree metadata, reconstructs with XOR when possible, falls back to Q-parity-assisted two-error recovery, identifies parity versus data corruption, and writes repaired data/parity back to devices when allowed. It permits up to two missing devices.

## `read_data` Logical-to-Physical Read Engine

`read_data` is the main block-layer read function. Inputs include a logical address, length, optional checksums, tree/read flags, output buffer, optional known chunk, optional parent IRP, expected tree generation, whether the destination is a file-read buffer, and MDL mapping priority.

Important behavior:

- Resolves the containing chunk either from `Vcb->log_to_phys_loaded` chunk mapping or bootstrap `Vcb->sys_chunks`.
- Classifies the chunk profile into DUP/SINGLE/RAID1/RAID1C3/RAID1C4, RAID0, RAID10, RAID5, or RAID6 and sets `allowed_missing`.
- Allocates `read_data_context.stripes`.
- Locks RAID5/RAID6 chunk ranges with `chunk_lock_range` to coordinate with partial stripe state.
- Builds per-stripe MDLs and byte ranges differently for RAID0, RAID10, DUP/mirrors, RAID5, and RAID6.
- Uses a temporary `context.va` for file reads when direct deinterlacing or checksum validation cannot safely operate against caller MDLs.
- Uses dummy pages for parity stripes in long RAID5/RAID6 reads so MDL layouts remain valid while skipping parity data.
- Marks absent devices or empty stripe ranges as `ReadDataStatus_MissingDevice` and fails if missing count exceeds redundancy.
- Allocates lower read IRPs or associated IRPs, sets buffered/direct/neither I/O fields according to the lower device flags, installs `read_data_completion`, submits all active stripes, and waits for completion.
- Updates disk counters when `diskacc` is enabled.
- Short-circuits user-induced lower-device errors before attempting checksum recovery.
- Dispatches post-read validation/recovery to the profile-specific helper.
- Copies temporary file-read buffers back to the caller after successful validation.
- Cleans up RAID locks, dummy MDL/page, per-stripe MDLs/IRPs, temporary bootstrap device arrays, and stripe context.

A notable implementation detail is the use of MDL page-frame manipulation for RAID0/RAID10/RAID5/RAID6 deinterlacing. Comments acknowledge that MDLs are officially opaque and this could break on future Windows versions.

## File and Stream Reads

`read_stream` handles alternate data streams stored in-memory in `fcb->adsdata`. It checks EOF and zero-length reads, copies the available range, and reports bytes read.

`read_file` handles normal Btrfs file extents:

- Rejects reads starting beyond `inode_item.st_size`.
- Walks `fcb->extents` fully in logical order.
- Fills holes between extents with zeroes.
- Rejects unsupported encryption and nonzero encoding.
- Handles inline extents:
  - Raw inline data is copied directly.
  - ZLIB, LZO, and ZSTD inline data are decompressed, with an intermediate buffer when reading from a nonzero offset.
- Handles regular extents:
  - Builds `read_part` entries with physical address, aligned read length, checksum pointer, target copy offset, compression type, and chunk pointer.
  - Uses direct target buffers only for uncompressed sector-aligned reads; otherwise allocates a temporary buffer.
- Handles preallocated extents by returning zeroes.
- Merges adjacent compressed `read_part` entries when they are contiguous, same compression, same chunk, adjacent destination, and compatible checksum state. The merged structure carries multiple `read_part_extent` fragments and may allocate a combined checksum buffer.
- Calls `read_data` for every queued physical read part.
- Copies uncompressed temporary buffers back to the destination when needed.
- For compressed regular extents, prepares decompression jobs using `add_calc_job_decomp`; LZO handling skips page-compressed chunks until the requested offset.
- Runs queued decompression jobs with `calc_thread_main`, waits on their events, copies decompressed slices into the output, and frees temporary buffers.
- Zero-fills trailing sparse data up to file size.
- Cleans all pending read parts and decompression jobs on exit.

The decompression code intentionally avoids decompressing directly into final mmap-backed destinations because Windows may use dummy pages that can break algorithms requiring backtracking, especially ZSTD.

## Windows Read Path

`do_read` is the core IRP read implementation after `drv_read` has validated the file object and acquired locks.

It rejects directory reads except ADS reads, checks byte-range locks for non-paging I/O, handles zero-length and EOF reads, and maps the user buffer. It respects `ValidDataLength`: reads beyond valid data are zero-filled, and reads crossing VDL append zeroes for the tail.

For cached reads, it initializes the cache map when needed and uses `CcMdlRead`, `CcCopyReadEx`, or `CcCopyRead`. If the cache manager cannot wait, the IRP is marked pending. For noncached reads, it requires synchronous wait, then calls `read_stream` for ADS or `read_file` for regular file data. It updates `Irp->IoStatus.Information` and process disk counters when enabled.

`drv_read` is the `IRP_MJ_READ` dispatch entry point. It:

- Enters the filesystem with `FsRtlEnterFileSystem` and top-level IRP tracking.
- For volume device objects, delegates to `vol_read`.
- Handles `IRP_MN_COMPLETE` by calling `CcMdlReadComplete`.
- Validates `fcb`, `ccb`, and `FILE_READ_DATA` access for user-mode callers.
- Passes reads against the volume FCB through to the real device.
- Checks oplocks for non-paging I/O.
- Forces synchronous handling for paging I/O to avoid deadlocks in `CcCopyRead`.
- Flushes mapped cached data before non-paging reads when a data section exists.
- Acquires the FCB resource shared if not already held.
- Calls `do_read`, updates synchronous file-object current byte offset, completes non-pending IRPs, or queues pending work with `add_thread_job` and falls back to `do_read_job`.
- Restores top-level IRP state and exits the filesystem.

## Dependencies and Cross-File Interactions

This file depends heavily on declarations and helpers from `btrfs_drv.h`, checksum code from `crc32c.h`, XXHASH from the bundled ZSTD sources, compression helpers (`zlib_decompress`, `lzo_decompress`, `zstd_decompress`), Btrfs chunk geometry helpers (`get_raid0_offset`, `get_raid56_lock_range`), lower-device I/O helpers (`sync_read_phys`, `write_data_phys`), device error accounting (`log_device_error`), cache initialization, calculation-thread jobs, and worker-thread queuing.

It also interacts with FCB/CCB state, file extents, chunk/device mappings, partial-stripe tracking, Windows Cache Manager, MDLs, IRPs, oplocks, byte-range locks, and process disk counters.

## Error Handling and Safety Notes

Most allocation and lower-I/O failures return NTSTATUS codes directly after logging. Redundant profiles aggressively attempt checksum recovery and repair writeback, while RAID0 and SINGLE without alternate copies cannot recover. The code distinguishes corruption errors from generation mismatches for metadata reads.

Cleanup is centralized in `read_data` and `read_file`, but the paths are complex. Important invariants include correct MDL lock/unlock handling, freeing temporary file-read buffers exactly once, preserving RAID locks around parity reads, and not dereferencing absent devices in degraded paths.

## Research Notes

This file should be studied with the write path and chunk/extent-tree code because read recovery can write repaired data back to devices and must coordinate with partial stripe state. It is also a useful map of how WinBtrfs adapts Btrfs extent/chunk semantics to Windows IRP, MDL, and cache-manager mechanics.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/read.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/registry.c -->
# File Research: sources/windows/winbtrfs/src/registry.c

## Purpose

`registry.c` manages WinBtrfs driver configuration stored in the Windows registry. It loads global mount defaults, per-volume mount options, mounted/unmounted volume markers, SID-to-UID and SID-to-GID mappings, debug logging settings, and registry change notifications.

The file is kernel-mode registry plumbing around `ZwCreateKey`, `ZwOpenKey`, `ZwQueryValueKey`, `ZwEnumerateValueKey`, `ZwSetValueKey`, `ZwDeleteValueKey`, and `ZwNotifyChangeKey`.

## Per-Volume Mount Options

`registry_load_volume_options` builds a per-volume registry path by appending the filesystem UUID to `registry_path`. It initializes `Vcb->options` from global `mount_*` defaults, then opens the UUID key and enumerates values.

Recognized per-volume values include:

- `Ignore`
- `Compress`
- `CompressForce`
- `CompressType`
- `Readonly`
- `ZlibLevel`
- `FlushInterval`
- `MaxInline`
- `SubvolId`
- `SkipBalance`
- `NoBarrier`
- `NoTrim`
- `ClearCache`
- `AllowDegraded`
- `ZstdLevel`
- `NoRootDir`
- `NoDataCOW`

It clamps compression type to valid Btrfs compression IDs, clamps max inline data to the node-size-derived maximum, limits zlib level to 9, limits ZSTD level to `ZSTD_maxCLevel()`, and restores a default flush interval if the registry value is zero.

## Mounted State Tracking

`registry_mark_volume_mounted` creates or opens the per-UUID volume key and writes `Mounted=1`.

`registry_mark_volume_unmounted_path` opens a volume key, enumerates its values, and decides whether to clear or delete it. If any option other than `Mounted` exists, it writes `Mounted=0`; otherwise it deletes the key completely. This preserves user options while removing empty transient volume keys.

`registry_mark_volume_unmounted` builds the UUID path and calls `registry_mark_volume_unmounted_path`.

`is_uuid` validates registry subkey names with the canonical 36-character UUID shape and hyphen positions.

`reset_subkeys` enumerates UUID-shaped subkeys, copies their names into a temporary list, then calls `registry_mark_volume_unmounted_path` for each. This is used during non-refresh startup to mark previous mount records as unmounted without modifying non-volume registry subkeys.

## User and Group Mapping Reads

`read_mappings` loads `registry_path\Mappings`. It first clears `uid_map_list`, freeing SIDs and mapping nodes, then opens/creates the key and enumerates REG_DWORD values. Each value name is interpreted as a SID string and the DWORD data as a UID, passed to `add_user_mapping`.

`read_group_mappings` mirrors this for `registry_path\GroupMappings` and `gid_map_list`. If the group mapping key is newly created, it adds a default mapping for `S-1-5-32-545` (`BUILTIN\Users`) to GID `100`, writes it into the registry, and calls `add_group_mapping`.

Both mapping lists are protected by `mapping_lock` in `read_registry`.

## Generic Registry Defaulting

`get_registry_value` queries a named value. If the value exists with the expected type and sufficient length, it copies the data into the caller-provided storage. If the type or length is wrong, it deletes and recreates the value with the current in-memory default. If the value is missing, it creates it from the current in-memory default.

This makes `read_registry` both a reader and a registry default materializer.

## Global Registry Load

`read_registry` is the main global configuration loader. It:

- Acquires `mapping_lock`, refreshes UID/GID mappings, then releases it.
- Creates/opens the root driver registry key.
- Calls `reset_subkeys` on initial load, not refresh.
- Reads or initializes global values:
  - `Compress`
  - `CompressForce`
  - `CompressType`
  - `ZlibLevel`
  - `FlushInterval`
  - `MaxInline`
  - `SkipBalance`
  - `NoBarrier`
  - `NoTrim`
  - `ClearCache`
  - `AllowDegraded`
  - `Readonly`
  - `ZstdLevel`
  - `NoRootDir`
  - `NoDataCOW`
  - `NoPNP` on initial load only
- Ensures `mount_flush_interval` is not zero.

In `_DEBUG` builds it also manages debug logging values:

- Reads `DebugLogLevel`.
- Reads `LogDevice` and, on refresh or state transitions, resets `comfo`, `comdo`, and `log_handle` under `log_lock`, then tries `IoGetDeviceObjectPointer` when device logging is enabled.
- Reads or creates `LogFile`, defaulting to `\??\C:\btrfs.log`.
- Reopens the log file with `ZwCreateFile` when debug logging state changes and no log device is active.

Old `UNICODE_STRING` buffers for log device/file are freed after refresh transitions.

## Registry Watcher

`registry_work_item` is a delayed work queue callback. It reloads the registry with `refresh=true`, then re-arms `ZwNotifyChangeKey` for `REG_NOTIFY_CHANGE_LAST_SET`.

`watch_registry` initializes the global `WORK_QUEUE_ITEM wqi` and registers the first `ZwNotifyChangeKey` notification.

## Dependencies and Shared State

The file uses global configuration variables declared elsewhere, including `registry_path`, `mount_*` defaults, `no_pnp`, `uid_map_list`, `gid_map_list`, `mapping_lock`, and debug-only log handles/device pointers. It depends on helper functions such as `hex_digit`, `add_user_mapping`, and `add_group_mapping`.

## Error Handling and Notes

Most registry errors are logged and either returned or cause the relevant optional section to stop. Some mapping enumeration loops ignore intermediate errors other than `STATUS_NO_MORE_ENTRIES`, so malformed individual values are skipped rather than fatal. Registry strings and key paths are manually allocated with pool memory and freed in local cleanup paths.

The mounted-state logic is intentionally conservative: per-volume keys containing user options persist after unmount, but optionless keys are deleted.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/registry.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/reparse.c -->
# File Research: sources/windows/winbtrfs/src/reparse.c

## Purpose

`reparse.c` implements WinBtrfs reparse point operations: reading reparse data, setting reparse points, converting certain reparse points into native Btrfs symlinks, storing other reparse payloads, and deleting reparse points.

It bridges Windows reparse semantics with Btrfs inode types, file data, and extended attributes.

## Reparse Buffer Handling

The file defines `REPARSE_DATA_BUFFER_LX_SYMLINK`, a small structure used for Linux subsystem symlink reparse data. It also imports `fFsRtlValidateReparsePointBuffer` for system validation of incoming buffers.

## Getting Reparse Points

`get_reparse_point` takes a file object, caller buffer, buffer length, and returned length pointer. It acquires the tree lock shared and the FCB resource shared.

Behavior by file type/state:

- Native Btrfs symlink:
  - For LXSS callers (`ccb->lxss`), returns an `IO_REPARSE_TAG_LX_SYMLINK` buffer with a fixed integer payload.
  - Otherwise reads symlink target bytes from file data, converts UTF-8 to UTF-16, converts `/` to `\`, and returns an `IO_REPARSE_TAG_SYMLINK` buffer using relative symlink flags. Substitute and print names are identical.
- File with `FILE_ATTRIBUTE_REPARSE_POINT`:
  - Reads the stored reparse buffer from file data through `read_file`.
- Directory with `FILE_ATTRIBUTE_REPARSE_POINT`:
  - Copies `fcb->reparse_xattr` into the caller buffer.
- Other cases return `STATUS_NOT_A_REPARSE_POINT`.

It supports partial result behavior by setting as much header information as the buffer can hold and returning `STATUS_BUFFER_OVERFLOW` when needed.

## Setting Native Symlinks

`set_symlink` handles `IO_REPARSE_TAG_SYMLINK` and `IO_REPARSE_TAG_LX_SYMLINK` when they should become Btrfs symlink inodes.

For Windows symlink tags, it validates minimum length and substitute name length, converts the substitute name from UTF-16 to UTF-8, and normalizes `\` to `/`.

For LX symlink tags, it treats the LX payload name bytes as the target.

It then:

- Changes `fcb->type` to `BTRFS_TYPE_SYMLINK`.
- Rewrites inode mode bits from regular-file to symlink.
- Updates inode generation to the current superblock generation.
- Updates directory cache type when present.
- Truncates existing file data.
- Writes the target path into file data with `write_file2`.
- Updates ctime/mtime unless the CCB indicates user-specified timestamps.
- Updates subvolume root ctransid/ctime.
- Marks inode and file reference dirty.

## Setting Reparse Points

`set_reparse_point2` is the core setter. It rejects existing symlink inodes, rejects nonempty directories, validates buffer length, and calls `fFsRtlValidateReparsePointBuffer`.

Special cases:

- Mount points must target directories.
- Relative Windows symlinks on files and LX symlinks on files become native Btrfs symlinks through `set_symlink`.
- Directory, char device, and block device reparse data is stored in `fcb->reparse_xattr`.
- Other file reparse data is stored as file data after truncating the file.

After storing non-symlink reparse data, it sets `FILE_ATTRIBUTE_REPARSE_POINT`, marks attributes changed, updates timestamps and inode generation, updates subvolume root metadata, and marks the FCB dirty.

There are explicit FIXME notes for rejecting existing `FILE_ATTRIBUTE_REPARSE_POINT` and validating file/directory type more strictly.

`set_reparse_point` is the IRP-facing wrapper. It validates `FileObject`, rejects unexpected `Irp->UserBuffer`, checks `ccb`, checks caller write privileges, resolves ADS operations to the parent file, acquires tree shared and FCB exclusive resources, initializes rollback, calls `set_reparse_point2`, queues file-change notification on success, and either clears or applies rollback before releasing locks.

## Deleting Reparse Points

`delete_reparse_point` validates `FileObject`, `fcb`, `ccb`, caller privileges, and `fileref`, then acquires tree shared and FCB exclusive locks. It rejects too-short buffers, nonzero `ReparseDataLength`, and ADS deletion.

Behavior by file type:

- Native symlink:
  - Requires `IO_REPARSE_TAG_SYMLINK`.
  - Converts the inode back to regular file type/mode.
  - Clears `FILE_ATTRIBUTE_REPARSE_POINT`.
  - Updates timestamps, generation, sequence, directory cache type, subvolume root metadata, and dirty flags.
- File:
  - Truncates file data to zero.
  - Clears `FILE_ATTRIBUTE_REPARSE_POINT`.
  - Updates timestamps, inode metadata, and dirty flags.
- Directory:
  - Clears `FILE_ATTRIBUTE_REPARSE_POINT`.
  - Frees `fcb->reparse_xattr.Buffer`.
  - Marks reparse xattr changed.
  - Updates timestamps, inode metadata, and dirty flags.
- Unsupported file types return `STATUS_INVALID_PARAMETER`.

On success it queues a last-write/attributes notification. Rollback is cleared on success and applied on failure.

There are FIXME notes asking whether delete should verify the requested tag matches the stored reparse tag for file and directory reparse points.

## Dependencies and Shared State

This file depends on FCB/CCB/file-ref structures, tree locks, rollback helpers, file truncation and write helpers, UTF conversion helpers, timestamp conversion, dirty marking, and notification queuing. It calls `read_file` from `read.c` to materialize symlink targets and file-stored reparse payloads.

## Error Handling and Notes

The implementation carefully updates Btrfs inode state and Windows file attributes together. It uses rollback for mutating set/delete paths, but symlink conversion is broad: it changes inode type, mode, data, timestamps, directory-cache type, and root metadata in one operation. Reparse payload storage differs by type: native symlinks use file data as a target path, directories/devices use xattr storage, and generic file reparse points use file data.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/reparse.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/resource.h -->
# File Research: sources/windows/winbtrfs/src/resource.h

## Purpose

`resource.h` is a small Microsoft Visual C++ generated resource header used by `btrfs.rc`.

It contains no runtime filesystem logic. Its only active definitions are guarded by `APSTUDIO_INVOKED` and `!APSTUDIO_READONLY_SYMBOLS`, providing default next IDs for Visual Studio resource editing:

- `_APS_NEXT_RESOURCE_VALUE` = `101`
- `_APS_NEXT_COMMAND_VALUE` = `40001`
- `_APS_NEXT_CONTROL_VALUE` = `1001`
- `_APS_NEXT_SYMED_VALUE` = `101`

## Dependencies and Impact

The file is consumed by the resource compiler/editor workflow, not by the driver read, registry, or reparse logic. It is relevant to Windows build resources but has no effect on Btrfs behavior, IRP handling, registry configuration, or on-disk format handling.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/resource.h -->