# Group Research: ReactOS WinBtrfs read, registry, reparse, and resource files

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/read.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/read.c

## Purpose

`read.c` implements the WinBtrfs read path for ReactOS, spanning physical chunk reads, checksum validation, profile-specific redundancy recovery, extent decoding, cache manager integration, and the IRP dispatch handler for `IRP_MJ_READ`.

It is central to Btrfs data integrity: reads are not just block transfers, but profile-aware operations that may verify checksums, reconstruct data from mirrors/parity, repair corrupt copies, and translate Btrfs extents into Windows file reads.

## Main Responsibilities

- Issue physical read IRPs against one or more backing devices.
- Verify tree and data checksums using CRC32C, xxHash, SHA-256, or BLAKE2.
- Handle Btrfs chunk profiles:
  - single/duplicate/RAID1/RAID1C3/RAID1C4 via duplicate read logic
  - RAID0 striping
  - RAID10 mirrored striping
  - RAID5 parity reconstruction
  - RAID6 dual-parity reconstruction
- Recover from checksum or missing-device failures when possible.
- Write repaired data back to bad devices when the filesystem/device is writable.
- Read inline, regular, preallocated, sparse, compressed, and alternate data stream content.
- Integrate with Windows cache manager paths such as `CcCopyRead`, `CcCopyReadEx`, `CcMdlRead`, and direct noncached reads.
- Dispatch and complete filesystem read IRPs.

## Key Types

- `enum read_data_status`: tracks per-stripe state: pending, success, error, missing device, or skipped.
- `read_data_stripe`: records one physical stripe read, including IRP, MDL, status, stripe offset range, and completion status.
- `read_data_context`: shared state for a logical `read_data` operation: chunk, target address, checksum pointer, stripe list, sector size, read buffer, and synchronization event.
- `read_part`: describes a file extent fragment that must be read from disk, including checksum, compression, chunk pointer, buffer ownership, and extent slices.
- `read_part_extent`: records logical subranges inside merged compressed read parts.
- `comp_calc_job`: tracks asynchronous decompression jobs and the destination copy range.

## Important Functions

- `read_data_completion`: completion routine for physical stripe read IRPs. It stores `IoStatus`, marks success/error, decrements the shared stripe counter, and signals the event when all reads complete.
- `check_csum`: computes checksums over multiple sectors and compares them with supplied checksum bytes.
- `get_tree_checksum`, `check_tree_checksum`: compute and verify Btrfs tree block checksums for all supported checksum algorithms.
- `get_sector_csum`, `check_sector_csum`: compute and verify one sector checksum.
- `read_data_dup`: handles single, duplicate, RAID1, RAID1C3, and RAID1C4-like reads. It chooses a successful mirror, verifies it, then tries alternate mirrors for corrupt tree/data sectors and repairs the bad mirror if possible.
- `read_data_raid0`: validates striped reads. RAID0 has no redundancy, so checksum failures are logged as unrecoverable.
- `read_data_raid10`: verifies chosen mirror stripes and recovers from alternate sub-stripes when checksum validation fails.
- `read_data_raid5`: handles RAID5 verification and reconstruction from parity, including partial stripe overlays from in-memory write state.
- `raid6_recover2`: reconstructs RAID6 missing/corrupt stripes using P/Q parity and Galois field arithmetic.
- `read_data_raid6`: handles RAID6 verification, missing-device recovery, checksum recovery, and parity repair.
- `read_data`: top-level physical/logical chunk read routine. It finds the chunk, maps logical ranges to physical stripes, builds MDLs/IRPs, waits for completion, validates/reconstructs data, cleans up MDLs/IRPs, and returns status.
- `read_stream`: reads an alternate data stream stored in memory in `fcb->adsdata`.
- `read_file`: reads logical file contents from the extent list, handling sparse holes, inline extents, regular extents, preallocation, compression, checksum lookup, merged compressed reads, and decompression.
- `do_read`: handles one filesystem read IRP after locking, choosing cached, MDL, ADS, or noncached file-read paths.
- `drv_read`: registered `IRP_MJ_READ` dispatch entry point. It validates state/access, handles volume reads, oplocks, cache flushes, resource locking, pending work queue fallback, and IRP completion.

## Physical Read Flow

`read_data` first resolves the logical address to a Btrfs chunk. If the log-to-physical map is loaded, it uses `get_chunk_from_address`; during bootstrap it scans `Vcb->sys_chunks` and builds a temporary device array.

It normalizes chunk flags into a smaller set of read strategies:

- duplicate-like: single, duplicate, RAID1, RAID1C3, RAID1C4
- RAID0
- RAID10
- RAID5
- RAID6

It then computes allowed missing devices, allocates per-stripe context, optionally locks RAID5/6 stripe ranges, and builds MDLs. For stripe profiles, the code constructs per-device MDLs by copying page frame numbers from a master MDL into stripe-specific MDLs. This is a deliberate Windows-kernel optimization to avoid extra data copying, but it relies on MDL layout assumptions noted by comments in the file.

After IRPs are submitted with `IoCallDriver`, `read_data` waits on the shared event and checks for user-induced errors. The profile-specific validator then verifies checksums and reconstructs or repairs as needed.

## Integrity and Recovery Behavior

Tree blocks are verified by checksum, logical address, and optionally generation. Data extents are verified sector-by-sector when checksums are available.

Recovery strategy depends on chunk profile:

- Duplicate/mirror profiles read alternate copies and copy good data into the output buffer.
- RAID10 tries alternate sub-stripes within the mirrored stripe set.
- RAID5 reconstructs missing or corrupt sectors by XORing remaining stripes.
- RAID6 reconstructs using P/Q parity and can handle two missing/corrupt stripes in supported cases.
- RAID0 cannot recover checksum failures.

When recovery succeeds and the filesystem is writable, the code attempts to write the repaired block or sector back to the bad device. It logs device statistics for read, write, corruption, and generation errors.

## File Extent Read Flow

`read_file` walks `fcb->extents` and materializes logical file contents into the caller buffer:

- Gaps are zero-filled.
- Inline uncompressed extents are copied directly.
- Inline compressed extents are decompressed from inline data.
- Regular extents become `read_part` entries, with sector alignment and checksum selection.
- Preallocated extents read as zeroes.
- Unsupported encryption or encoding returns `STATUS_NOT_IMPLEMENTED`.

For compressed regular extents, adjacent compatible read parts can be merged to reduce I/O. After disk reads complete, compressed buffers are decompressed through `add_calc_job_decomp` and `calc_thread_main`, then copied into the final destination.

Supported compression paths include zlib, LZO, and ZSTD. LZO has special page/block skipping logic for reads into the middle of compressed data.

## Windows Read Integration

`do_read` implements policy around Windows read semantics:

- Rejects directory reads except ADS reads.
- Enforces byte-range locks for non-paging I/O.
- Handles EOF and valid-data-length zero fill.
- Uses `CcMdlRead` for cached MDL reads.
- Uses `CcCopyReadEx` when available, falling back to `CcCopyRead`.
- Handles noncached reads through `read_stream` or `read_file`.
- Updates disk counters for user-visible reads when enabled.

`drv_read` wraps this with filesystem dispatch concerns: top-level IRP state, volume passthrough reads, MDL read completion, access checks, oplock checks, cache flushes for mapped sections, FCB resource locking, synchronous/asynchronous wait handling, pending job queue fallback, and final IRP completion.

## Notable Risks and Implementation Notes

- The RAID0/RAID10/RAID5/RAID6 MDL manipulation depends on PFNs following the MDL structure in memory. The code explicitly notes that MDLs are officially opaque and this could break on future Windows versions.
- Several cleanup paths rely on the common `exit:` block. Resource ownership is complex because `context.va`, stripe MDLs, dummy MDLs, IRPs, temporary device arrays, and RAID locks are conditionally allocated.
- SHA-256 and BLAKE2 tree checksum comparisons appear to compare computed hashes against `th` rather than `th->csum` in `check_tree_checksum`; this is worth auditing against upstream WinBtrfs history because it may be intentional only if structure layout makes it equivalent, but it reads suspiciously.
- RAID56 code overlays in-memory partial stripes before checksum validation, which is important for consistency with pending writes.
- Compression reads avoid decompressing directly into mmap-backed destination pages because Windows may use dummy pages that break decompressor backtracking.
- The path intentionally treats some user-induced device errors specially before attempting redundancy recovery.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/read.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/registry.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/registry.c

## Purpose

`registry.c` manages WinBtrfs registry-backed configuration. It loads global mount defaults, per-volume mount overrides, mounted/unmounted state, UID/GID SID mappings, debug logging settings, and registry-change notifications.

## Main Responsibilities

- Load per-volume options under a UUID-named registry key.
- Mark volumes mounted or unmounted.
- Reset stale mounted state for volume subkeys on startup.
- Load Windows SID to Unix UID mappings.
- Load Windows SID to Unix GID mappings, creating a default BUILTIN\Users to gid `100` mapping on first run.
- Read and normalize global mount defaults.
- In debug builds, read and hot-reload debug log file/device settings.
- Register registry change notifications through a work item.

## Key Functions

- `registry_load_volume_options`: initializes `Vcb->options` from global defaults, then overlays values from the registry key for the filesystem UUID.
- `registry_mark_volume_mounted`: creates/opens the UUID key and writes `Mounted = 1`.
- `registry_mark_volume_unmounted_path`: either writes `Mounted = 0` if the key has other options, or deletes the UUID key if `Mounted` is the only value.
- `registry_mark_volume_unmounted`: builds the UUID registry path and delegates to `registry_mark_volume_unmounted_path`.
- `is_uuid`: validates UUID-shaped registry subkey names.
- `reset_subkeys`: enumerates UUID subkeys and marks them unmounted or deletes them.
- `read_mappings`: loads `Mappings` values into `uid_map_list`.
- `read_group_mappings`: loads `GroupMappings` into `gid_map_list`, and creates a default group mapping if the key is new.
- `get_registry_value`: helper that queries a value, copies it if type/size match, or writes the supplied default if missing or malformed.
- `read_registry`: primary global registry loader. It refreshes mappings, creates/opens the root key, optionally resets volume subkeys, loads mount defaults, and handles debug-only logging options.
- `registry_work_item`: worker callback invoked after registry changes; reloads settings and rearms notification.
- `watch_registry`: installs the initial `ZwNotifyChangeKey` callback.

## Configuration Values

Global and per-volume options include:

- `Compress`
- `CompressForce`
- `CompressType`
- `ZlibLevel`
- `ZstdLevel`
- `FlushInterval`
- `MaxInline`
- `SkipBalance`
- `NoBarrier`
- `NoTrim`
- `ClearCache`
- `AllowDegraded`
- `Readonly`
- `NoRootDir`
- `NoDataCOW`
- `SubvolId` for per-volume selection
- `Ignore` for per-volume ignore behavior
- `NoPNP` globally during non-refresh reads

The loader clamps some values:

- Compression type above ZSTD becomes `0`.
- `MaxInline` is capped to fit within the filesystem node layout.
- zlib level is capped at `9`.
- zstd level is capped at `ZSTD_maxCLevel()`.
- zero flush interval falls back to a default/global value.

## Registry Path Construction

Per-volume registry paths are built by appending a canonical UUID string to `registry_path`. The UUID formatter inserts hyphens after byte positions matching the standard `8-4-4-4-12` UUID display layout.

The same path construction is repeated in load, mounted, and unmounted functions.

## Mapping Behavior

`read_mappings` clears the current UID mapping list, opens or creates `\Mappings`, and enumerates `REG_DWORD` values. Each value name is treated as a SID string and the DWORD is treated as the mapped Unix UID.

`read_group_mappings` mirrors this for `\GroupMappings`. If the key is newly created, it writes a default `S-1-5-32-545 = 100`, corresponding to BUILTIN\Users as a conventional Unix `users` group.

Both mapping loaders are called under `mapping_lock` in `read_registry`.

## Debug Build Behavior

When `_DEBUG` is enabled, `read_registry` also manages:

- `DebugLogLevel`
- `LogDevice`
- `LogFile`

It compares old and new settings during refresh, closes/dereferences stale logging handles or device objects, and opens the new log target if needed. The default log file is `\??\C:\btrfs.log`.

## Notable Risks and Implementation Notes

- `get_registry_value` calls `ZwClose(h)` on allocation failure even though ownership remains with the caller; that helper should be audited because closing the caller’s handle inside a query helper is surprising.
- Registry string/path buffers are manually sized and not NUL-terminated in several places, which is valid for `UNICODE_STRING` but requires all consumers to respect explicit lengths.
- The mounted/unmounted logic preserves option-bearing UUID keys but deletes keys that only hold transient mounted state.
- `read_registry(refresh=false)` resets all UUID subkeys that look like volume IDs, which makes driver startup treat prior mounted state as stale.
- Registry notification is rearmed after each callback, using a global `WORK_QUEUE_ITEM`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/registry.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/reparse.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/reparse.c

## Purpose

`reparse.c` implements reparse point support for WinBtrfs, especially translation between Btrfs symlinks and Windows reparse buffers. It supports querying, setting, and deleting reparse points for symlinks, files, directories, and certain special file types.

## Main Responsibilities

- Return Windows reparse buffers for Btrfs symlinks.
- Support LX symlink behavior for LXSS-style callers.
- Convert Btrfs symlink target data between UTF-8 with `/` separators and Windows UTF-16 with `\` separators.
- Store non-symlink reparse data either as file data or directory/special-file xattrs.
- Convert regular files into symlinks for relative Windows symlink tags or LX symlink tags.
- Delete reparse points and restore symlink files to regular files.
- Update inode metadata, timestamps, attributes, subvolume root metadata, and dirty flags.
- Use rollback lists for mutating operations.

## Key Functions

- `get_reparse_point`: handles FSCTL-style reparse point retrieval.
- `set_symlink`: converts a supplied Windows or LX symlink reparse buffer into Btrfs symlink file contents and updates inode type/mode.
- `set_reparse_point2`: validates and applies a reparse point to an FCB.
- `set_reparse_point`: IRP wrapper for setting reparse data, including access checks, ADS handling, resource locking, rollback, and notifications.
- `delete_reparse_point`: removes reparse data or converts symlinks back to regular files, with metadata updates and rollback.

## Query Behavior

For `BTRFS_TYPE_SYMLINK`:

- If the CCB is marked `lxss`, it returns an `IO_REPARSE_TAG_LX_SYMLINK` buffer with a small generic payload.
- Otherwise, it reads the symlink target using `read_file`, converts UTF-8 to UTF-16, replaces `/` with `\`, duplicates the target as both substitute and print name, and marks the symlink as relative.

For files with `FILE_ATTRIBUTE_REPARSE_POINT`:

- Regular files read reparse bytes from file data using `read_file`.
- Directories return `fcb->reparse_xattr`.
- Other types return `STATUS_NOT_A_REPARSE_POINT`.

The function holds both `tree_lock` and the FCB resource shared while querying.

## Set Behavior

`set_reparse_point2` rejects attempts to set a reparse point on an existing Btrfs symlink and rejects non-empty directories. It validates the buffer via `fFsRtlValidateReparsePointBuffer`.

Special cases:

- Mount-point tags require a directory.
- A regular file with a relative `IO_REPARSE_TAG_SYMLINK`, or an `IO_REPARSE_TAG_LX_SYMLINK`, is converted into a Btrfs symlink using `set_symlink`.
- Directories, character devices, and block devices store reparse data in `fcb->reparse_xattr`.
- Other file types store the raw reparse buffer as file data after truncating the file.

`set_symlink` truncates existing file data, writes the symlink target bytes, changes inode mode to `__S_IFLNK`, updates generation/transid/sequence/timestamps, marks FCB and fileref dirty, and updates directory cache type if present.

## Delete Behavior

`delete_reparse_point` validates the request buffer, requires zero `ReparseDataLength`, rejects ADS targets, and then branches by file type:

- Symlinks require `IO_REPARSE_TAG_SYMLINK`, then are converted back to regular files by updating type and mode and clearing `FILE_ATTRIBUTE_REPARSE_POINT`.
- Regular files are truncated to zero and have the reparse attribute cleared.
- Directories clear `FILE_ATTRIBUTE_REPARSE_POINT`, free `reparse_xattr`, and mark the xattr changed.
- Unsupported types return `STATUS_INVALID_PARAMETER`.

All successful mutations update inode transaction metadata, sequence, timestamps unless user-set timestamps suppress them, and subvolume root change metadata. They also queue last-write/attribute notifications.

## Locking and Rollback

Set and delete wrappers acquire:

- `fcb->Vcb->tree_lock` shared
- `fcb->Header.Resource` exclusive

They initialize a rollback list, clear it on success, and call `do_rollback` on failure. This keeps truncate/write mutations recoverable if a later step fails.

## Notable Risks and Implementation Notes

- `set_reparse_point2` has FIXME comments for rejecting preexisting reparse attributes and validating allowed file/directory targets more strictly.
- Deletion has FIXME comments about checking that supplied reparse tags match stored tags for non-symlink file and directory cases.
- `set_symlink` only converts Windows symbolic links when `SYMLINK_FLAG_RELATIVE` is set; absolute Windows symlink behavior is not treated as a Btrfs symlink conversion here.
- LX symlink handling stores raw bytes after a small unknown header, matching the local `REPARSE_DATA_BUFFER_LX_SYMLINK` structure.
- Querying normal symlinks always reports `SYMLINK_FLAG_RELATIVE`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/reparse.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/resource.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/resource.h

## Purpose

`resource.h` is a Visual C++ generated resource include used by `btrfs.rc`.

## Contents

The file contains only default AP Studio resource ID definitions guarded by `APSTUDIO_INVOKED` and `APSTUDIO_READONLY_SYMBOLS`:

- `_APS_NEXT_RESOURCE_VALUE`
- `_APS_NEXT_COMMAND_VALUE`
- `_APS_NEXT_CONTROL_VALUE`
- `_APS_NEXT_SYMED_VALUE`

## Role in the Source Tree

This is not filesystem logic. It is build/resource metadata for Windows resource editing and compilation.

## Notable Notes

- No runtime behavior is defined here.
- No dependencies beyond the resource compiler/editor convention are present.
- The file is safe to treat as generated boilerplate unless resource IDs are added to `btrfs.rc`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/resource.h -->