# Group Research: group_1817_winbtrfs_sources_windows_winbtrfs_src_fsctl_c_sources_windows_winbt_30674ceba519

Scope: `Docs/research_subset_a.md` includes `sources/windows/winbtrfs`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/fsctl.c -->
# File Research: sources/windows/winbtrfs/src/fsctl.c

## Purpose

`fsctl.c` is WinBtrfs' central filesystem-control dispatch and implementation file. It handles standard Windows FSCTLs, oplocks, volume lock/dismount flows, sparse/zero/range queries, object IDs, reparse-related delegation, and a large set of WinBtrfs private IOCTLs for subvolumes, snapshots, devices, balance/scrub control, xattrs, send/receive, resize, and checksum export.

## Main Entry Point

- `fsctl_request(PDEVICE_OBJECT DeviceObject, PIRP* Pirp, uint32_t type)`: dispatches FSCTL codes to local helpers or external subsystem functions.
- Performs an initial `FsRtlCheckOplock` for file-backed requests on filesystem VCBs.
- Uses `map_user_buffer()` for direct/output buffers where needed and updates `Irp->IoStatus.Information` for variable-length outputs.
- Unsupported Windows FSCTLs are deliberately stubbed with `STATUS_INVALID_DEVICE_REQUEST`; some are logged with `WARN`, while noisy `FSCTL_QUERY_VOLUME_CONTAINER_STATE` is only traced.

## Standard Windows FSCTL Behavior

Implemented or partially implemented:

- Oplocks: `fsctl_oplock()` validates file/directory cases, checks existing opens or file locks, rejects delete-pending handle oplocks, calls `FsRtlOplockFsctrl()`, and updates fast I/O state.
- Volume lifecycle: `lock_volume()`, `unlock_volume()`, `dismount_volume()`, `invalidate_volumes()`, `is_volume_mounted()`, `is_volume_dirty()`.
- Sparse/range operations: `set_sparse()`, `set_zero_data()`, `query_ranges()`.
- Retrieval pointers: `get_retrieval_pointers()` maps Btrfs extents and holes into Windows `RETRIEVAL_POINTERS_BUFFER`; compressed extents and holes report `LCN = -1`.
- Compression FSCTLs: `GET_COMPRESSION` reports `COMPRESSION_FORMAT_NONE`; `SET_COMPRESSION` only accepts `COMPRESSION_FORMAT_NONE`.
- Object IDs: `get_object_id()` synthesizes an object ID from inode and subvolume ID.
- Integrity: `get_integrity_information()` and `set_integrity_information()` are stubs that report sector-sized checksum/chunk sizes but do not enable Windows integrity streams.
- `FSCTL_FILESYSTEM_GET_STATISTICS` returns a minimal NTFS-like statistics block to avoid SMB breakage.

## WinBtrfs Private FSCTLs

Implemented private controls include:

- `FSCTL_BTRFS_GET_FILE_IDS`: returns subvolume ID, inode, and top-root flag.
- `FSCTL_BTRFS_CREATE_SUBVOL`: creates a new Btrfs root, root directory FCB, UUID tree entry, `..` inode ref, parent dir child, security descriptor, inherited mode/compression flags, and dirty markers.
- `FSCTL_BTRFS_CREATE_SNAPSHOT`: validates destination and source handles, flushes source data/metadata, creates a snapshot root, copies the source root tree block, updates extent references, links the snapshot into the destination directory, and marks source extents non-unique.
- `FSCTL_BTRFS_GET_INODE_INFO` / `SET_INODE_INFO`: exposes and mutates POSIX-like inode metadata, flags, ownership, mode, compression property, disk usage by compression type, sparse size, and extent count.
- `FSCTL_BTRFS_GET_DEVICES`: enumerates mounted/missing devices and device statistics.
- `FSCTL_BTRFS_GET_USAGE`: groups chunk usage by block group profile and reports per-device allocation.
- Balance/scrub control delegates to `start_balance`, `query_balance`, `pause_balance`, `resume_balance`, `stop_balance`, `start_scrub`, `query_scrub`, `pause_scrub`, `resume_scrub`, and `stop_scrub`.
- `FSCTL_BTRFS_ADD_DEVICE`: validates a target disk/partition, prevents adding an already-mounted Btrfs RAID member, checks writability and partition layout, creates `DEV_ITEM` and device stats items, clears the first MiB, registers PnP removal notification, removes drive letters, and updates superblock totals.
- `FSCTL_BTRFS_REMOVE_DEVICE`: delegated to `remove_device()`.
- `FSCTL_BTRFS_RESET_STATS`: zeroes in-memory per-device error counters and marks stats dirty.
- `FSCTL_BTRFS_MKNOD`: creates Unix-style file types including directories, regular files, symlinks, FIFOs, sockets, char devices, and block devices.
- `FSCTL_BTRFS_RECEIVED_SUBVOL`: records received-subvolume UUID/generation metadata for send/receive.
- `FSCTL_BTRFS_GET_XATTRS` / `SET_XATTR`: enumerates and mutates Btrfs xattrs, including special handling for NT security descriptors, DOS attributes, reparse xattr, Windows EAs, case-sensitive flag, and compression property.
- `FSCTL_BTRFS_RESERVE_SUBVOL`: privileged reservation of a readonly subvolume for write access by the current process.
- `FSCTL_BTRFS_FIND_SUBVOL`: resolves subvolume UUID or received UUID plus optional creation transaction ID to a path.
- `FSCTL_BTRFS_SEND_SUBVOL` / `READ_SEND_BUFFER`: delegated send-stream path.
- `FSCTL_BTRFS_RESIZE`: extends or shrinks a device; shrink can trigger a balance over the truncated range.
- `FSCTL_BTRFS_GET_CSUM_INFO`: exports checksum type, checksum length, sector count, and per-sector checksums, synthesizing sparse-sector checksums and using zero placeholders for compressed extents.

## Key Internal Helpers

- `snapshot_tree_copy()`: reads a tree block, allocates a new metadata address, rewrites header fields, increments data or child tree-block references, recalculates checksum, and writes the cloned block.
- `flush_subvol_fcbs()` / `flush_fcb_caches()`: flush cache manager state for open FCBs before snapshot, lock, invalidate, or dismount operations.
- `zero_data()`: rewrites partial ranges for inline, compressed, or regular extent layouts; used by `set_zero_data()` for unaligned boundaries.
- `duplicate_extents()`: implements reflink/clone semantics. It copies data for ADS, inline, compressed-inline, or unaligned cases; otherwise creates shared extent records, copies checksums, updates extent refs, excises destination ranges, and purges cached destination pages.
- `mark_subvol_dirty()`: adds roots to `dirty_subvols` and sets `Vcb->need_write`.
- `get_csum_info()` and `add_csum_sparse_extents()`: package checksum data for callers across CRC32C, xxhash, SHA256, and BLAKE2 checksum sizes.

## Locking and State Discipline

- `Vcb->tree_lock` guards most metadata mutations and global filesystem state.
- FCB resource locks guard inode/extents/xattrs per file.
- `fileref_lock`, `dir_children_lock`, `dirty_subvols_lock`, `chunk_lock`, and global loading locks are used for narrower state.
- Rollback lists are used for snapshot, zeroing, and clone paths that touch extent/tree metadata.
- Volume lock/dismount paths flush cache manager state, write dirty metadata, free cached trees, and update VPB state under the VPB spin lock.

## Dependencies

- Driver core structures and helpers from `btrfs_drv.h`.
- Public/private IOCTL definitions from `btrfsioctl.h`.
- Checksum support via `crc32c.h` and general checksum helpers.
- Windows kernel APIs: `FsRtl*`, `Cc*`, `Io*`, `Se*`, VPB manipulation, mount manager/device IOCTLs.
- Cross-file subsystem functions: balance, scrub, send, remove-device, reparse point helpers, tree insertion/deletion, extent ref updates, security descriptor helpers, cache/read/write helpers.

## Research Notes

- This is a high-blast-radius file: user-mode IOCTL inputs directly drive metadata mutation, device topology changes, and subvolume operations.
- Many handlers include explicit privilege checks, readonly/subvolume-readonly checks, user-mode access checks, and 32-bit process handle handling.
- Snapshot and clone paths carefully clear extent uniqueness because shared extents may now be referenced by multiple files/subvolumes.
- Several Windows FSCTLs are intentionally stubs; compatibility behavior is selective rather than full NTFS emulation.
- `mknod()` deserves focused review: after computing or validating the desired inode, the code assigns `fcb->inode = inode`, where `inode` is the lookup output from `find_file_in_dir()` after a not-found result. That looks potentially fragile and may be a real bug depending on surrounding helper semantics.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/fsctl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/fsrtl.c -->
# File Research: sources/windows/winbtrfs/src/fsrtl.c

## Purpose

`fsrtl.c` provides a compatibility implementation of `FsRtlValidateReparsePointBuffer` for environments where the Vista+ FsRtl API is unavailable or not exported.

## Main Entry Point

- `compat_FsRtlValidateReparsePointBuffer(ULONG BufferLength, PREPARSE_DATA_BUFFER ReparseBuffer)`

It validates Windows reparse point buffer shape, length consistency, tag class, and selected Microsoft tag payloads.

## Behavior

- Rejects buffers smaller than `REPARSE_DATA_BUFFER_HEADER_SIZE` or larger than `MAXIMUM_REPARSE_DATA_BUFFER_SIZE`.
- Accepts either normal `REPARSE_DATA_BUFFER` sizing or GUID reparse buffer sizing if the `ReparseDataLength` matches exactly.
- Requires non-Microsoft tags to use GUID reparse buffers.
- Rejects null GUIDs for non-Microsoft GUID reparse buffers.
- Rejects GUID buffer use for mount-point and symlink tags.
- Validates Microsoft mount point buffers:
  - substitute name must begin at offset 0,
  - print name must follow the substitute string plus null,
  - total data length must match fields plus two null terminators.
- Validates Microsoft symlink buffers:
  - substitute and print lengths must be nonzero,
  - offsets and lengths must be even UTF-16 byte counts,
  - both strings must fit inside the provided data length.
- Accepts other non-reserved Microsoft tags without detailed payload validation.
- Returns `STATUS_IO_REPARSE_DATA_INVALID` for malformed payloads and `STATUS_IO_REPARSE_TAG_INVALID` for invalid tag classes.

## Helpers

- `IsNullGuid()`: checks for all-zero GUID.
- `IsEven()`: validates UTF-16 byte alignment.

## Dependencies

- Includes `ntifs.h` and `ntdef.h`.
- Uses Windows reparse constants/macros such as `IsReparseTagMicrosoft`, `IO_REPARSE_TAG_MOUNT_POINT`, and `IO_REPARSE_TAG_SYMLINK`.

## Research Notes

- Header comment identifies this as ReactOS-derived Vista+ FsRtl compatibility code under LGPL-2.1-or-later.
- The function is security-sensitive because reparse data can cross user/kernel and filesystem boundary paths.
- The implementation focuses on structural validation, not semantic target validation.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/fsrtl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/galois.c -->
# File Research: sources/windows/winbtrfs/src/galois.c

## Purpose

`galois.c` implements finite-field arithmetic used by WinBtrfs RAID-6 parity generation and recovery.

## Core Data

- `glog[]`: exponent-to-field-value lookup table for GF(2^8).
- `gilog[]`: inverse log lookup table mapping field values to exponents.

These tables support fast multiply/divide by converting operations into exponent arithmetic modulo 255.

## Entry Points

- `galois_divpower(uint8_t* data, uint8_t div, uint32_t len)`: divides every byte in a buffer by `2^div`.
- `gpow2(uint8_t e)`: returns `2^e` in the field.
- `gmul(uint8_t a, uint8_t b)`: multiplies two GF(2^8) elements, returning zero if either operand is zero.
- `gdiv(uint8_t a, uint8_t b)`: divides two GF(2^8) elements; returns `0xff` for divide-by-zero as a should-not-happen sentinel.
- `galois_double(uint8_t* data, uint32_t len)`: multiplies every byte by 2 using the RAID-6 primitive polynomial reduction constant `0x1d`.

## Implementation Details

- `galois_double()` has 64-bit fast path on AMD64/ARM64 and 32-bit fast path elsewhere.
- Wide-word doubling masks high bits and applies `0x1d` reduction per byte.
- Remaining bytes are processed individually.
- Comments credit H. Peter Anvin's "The mathematics of RAID-6" for the derived algorithm.

## Dependencies

- Includes `btrfs_drv.h`.
- Called from RAID/parity paths in read, write, scrub, and flush-thread code.

## Research Notes

- This file is small but critical for RAID-6 correctness. Arithmetic mistakes here would affect parity reconstruction and scrub repair.
- No allocation or locking occurs here; callers own buffer lifetime and synchronization.
- There is a `FIXME - SIMD?` note, indicating known optimization headroom for parity-heavy workloads.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/galois.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/mkbtrfs/mkbtrfs.c -->
# File Research: sources/windows/winbtrfs/src/mkbtrfs/mkbtrfs.c

## Purpose

`mkbtrfs.c` is the command-line Btrfs formatting utility for WinBtrfs. It parses user options, loads `ubtrfs.dll`, configures format feature flags and checksum type through exported setter functions, then invokes the DLL's `FormatEx` entry point.

## Entry Points

- `main(int argc, char** argv)`: full CLI flow.
- `print_string(FILE* f, int resid, ...)`: loads localized strings from resources, formats them, and prints to stdout/stderr.

## CLI Arguments

Required:

- `device`: drive letter such as `D:` or a device path such as `\Device\Harddisk0\Partition2`.

Optional:

- `label`: filesystem label.

Supported flags:

- `/sectorsize:num`
- `/nodesize:num`
- `/csum:crc32c|xxhash|sha256|blake2`
- `/mixed` / `/notmixed`
- `/extiref` / `/notextiref`
- `/skinnymetadata` / `/notskinnymetadata`
- `/noholes` / `/notnoholes`
- `/freespacetree` / `/notfreespacetree`
- `/blockgrouptree` / `/notblockgrouptree`

## Defaults and Feature Logic

- Default incompat flags include extended inode refs, skinny metadata, and no-holes.
- Default compat-ro flags include free-space cache.
- Default checksum type is CRC32C.
- Enabling block-group-tree forces free-space-tree and no-holes, matching the Linux-side constraint noted in the source comment.
- Enabling free-space-tree also sets the valid free-space-cache compat-ro bit.

## DLL Interface

Loads `ubtrfs.dll`, with debug fallback paths for x86/x64 builds. It resolves and calls:

- `SetSizes`
- `SetIncompatFlags`
- `SetCompatROFlags`
- `SetCsumType`
- `FormatEx`

`FormatEx` receives undocumented format-style structures matching the Windows formatter interface expectations.

## Device and Label Handling

- Drive letters are normalized to `\??\X:`.
- Device paths are converted from OEM code page to UTF-16.
- Labels are converted from OEM code page to UTF-16 if provided.
- Invalid drive syntax prints a localized error and exits.

## Dependencies

- Windows user-mode headers: `windef.h`, `winbase.h`, `winternl.h`, `devioctl.h`, `ntdddisk.h`, string conversion APIs.
- Local `resource.h` for message IDs.
- `../btrfs.h` for Btrfs feature and checksum constants.

## Research Notes

- The utility is intentionally thin; actual filesystem creation lives in `ubtrfs.dll`.
- Error handling is mostly fail-fast with localized messages.
- The `FORMAT_FLAG_*` definitions are present but the parsed CLI does not currently set most of them in `opts`.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/mkbtrfs/mkbtrfs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/mkbtrfs/mkbtrfs.rc.in -->
# File Research: sources/windows/winbtrfs/src/mkbtrfs/mkbtrfs.rc.in

## Purpose

`mkbtrfs.rc.in` is the CMake-templated Windows resource script for `mkbtrfs.exe`. It provides version metadata and localized strings used by the formatting utility.

## Resource Content

- Includes `resource.h` through a CMake-expanded path.
- Includes `winresrc.h`.
- Defines English (United Kingdom) resources with code page 1252.
- Defines `VS_VERSION_INFO` with CMake project version substitutions:
  - `FILEVERSION`
  - `PRODUCTVERSION`
  - `FileVersion`
  - `ProductVersion`
- Version strings identify:
  - file description: Btrfs formatting utility,
  - internal name: `mkbtrfs`,
  - original filename: `mkbtrfs.exe`,
  - product name: WinBtrfs,
  - copyright range through 2024.

## String Table

Defines user-facing strings consumed by `mkbtrfs.c`, including:

- usage header and extended help text,
- multibyte conversion errors,
- invalid drive recognition,
- DLL/function loading failures,
- format failure and success messages,
- invalid or missing argument messages,
- checksum option validation messages.

The long `IDS_USAGE2` string documents device path syntax and all supported formatting flags.

## Dependencies

- `sources/windows/winbtrfs/src/mkbtrfs/resource.h` for numeric IDs.
- CMake variables:
  - `@CMAKE_CURRENT_SOURCE_DIR@`
  - `@PROJECT_VERSION_MAJOR@`
  - `@PROJECT_VERSION_MINOR@`
  - `@PROJECT_VERSION_PATCH@`

## Research Notes

- This file is build-time templated, not a final checked-in `.rc`.
- String IDs match the usage in `mkbtrfs.c`; changes here must stay synchronized with `resource.h`.
- The embedded help text is the authoritative CLI documentation for the standalone formatter.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/mkbtrfs/mkbtrfs.rc.in -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/mkbtrfs/resource.h -->
# File Research: sources/windows/winbtrfs/src/mkbtrfs/resource.h

## Purpose

`resource.h` assigns numeric resource IDs for strings used by the `mkbtrfs` resource script and loaded at runtime by `mkbtrfs.c`.

## Defined IDs

- `IDS_USAGE` through `IDS_INVALID_CSUM_TYPE`, values 101 through 116.
- IDs cover usage text, conversion errors, drive recognition, DLL/function lookup failures, format result messages, argument errors, and checksum validation messages.

## Build Tool Metadata

The file includes standard Visual C++ resource-editor defaults under `APSTUDIO_INVOKED`:

- `_APS_NEXT_RESOURCE_VALUE`
- `_APS_NEXT_COMMAND_VALUE`
- `_APS_NEXT_CONTROL_VALUE`
- `_APS_NEXT_SYMED_VALUE`

## Dependencies

- Used by `mkbtrfs.rc.in`.
- Referenced by `mkbtrfs.c` through `print_string()` calls.

## Research Notes

- This is a coordination header: no executable logic, but changes can break resource lookup if not mirrored in the RC string table and C source references.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/mkbtrfs/resource.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/pnp.c -->
# File Research: sources/windows/winbtrfs/src/pnp.c

## Purpose

`pnp.c` implements WinBtrfs Plug and Play IRP handling for filesystem volumes, the root bus device, volume PDOs, and volume filter/device wrappers.

## Main Entry Point

- `drv_pnp(PDEVICE_OBJECT DeviceObject, PIRP Irp)`: dispatch routine for `IRP_MJ_PNP`.

It enters the filesystem context, manages top-level IRP state, routes by device extension type, completes handled requests, or forwards unhandled requests down the stack.

## Filesystem VCB PnP Paths

- `pnp_query_remove_device()`: checks for open root children, flushes dirty metadata with `do_write()`, frees cached trees, and returns denial or unsuccessful status.
- `pnp_remove_device()`: sends dismount notification for mounted volumes, clears `mounted_device`, marks the VCB removing, and calls `uninit()` if no files are open.
- `pnp_surprise_removal()`: marks mounted volume state as removing without flush, clears mounted-device linkage, and uninitializes if possible.
- `pnp_device_usage_notification()`: tracks paging/hibernation/dump-file usage through `Vcb->page_file_count`, then forwards to the real device.

## Bus Device Handling

- `bus_pnp()` handles bus-level PnP minor functions.
- Query/remove/start/cancel/surprise/remove are mostly success or refusal as appropriate.
- `bus_query_capabilities()` sets `UniqueID` and `SilentInstall`.
- `bus_query_device_relations()` enumerates global `pdo_list` under `pdo_list_lock`, skips `dont_report` PDOs, references each child PDO, and returns `BusRelations`.
- `bus_query_hardware_ids()` returns `ROOT\btrfs`.

## PDO Handling

- `pdo_pnp()` handles PDO-specific PnP requests.
- `pdo_query_device_id()` formats `Btrfs\{uuid}` from the PDO UUID.
- `pdo_query_hardware_ids()` returns `BtrfsVolume`.
- `pdo_query_id()` routes `BusQueryDeviceID` and `BusQueryHardwareIDs`.
- `pdo_query_device_relations()` returns a single-object `TargetDeviceRelation` for the PDO.
- `pdo_device_usage_notification()` propagates usage notifications to all child backing devices by allocating nested PnP IRPs, setting a completion routine, waiting for completion when pending, and returning the first failure.

## Locking and Lifetime

- Global PDO enumeration uses `pdo_list_lock`.
- Per-PDO child enumeration uses `pdode->child_lock`.
- Mounted filesystem state changes use `Vcb->tree_lock`.
- Device relation outputs reference returned device objects as required by PnP manager contracts.
- Nested device usage notifications use an event-backed completion context to synchronize with lower drivers.

## Dependencies

- Includes `btrfs_drv.h`.
- Uses external globals `pdo_list_lock` and `pdo_list`.
- Calls core filesystem helpers such as `has_open_children()`, `do_write()`, `free_trees()`, `uninit()`, `is_top_level()`, and logging macros.
- Uses Windows kernel PnP, IRP, device relation, and paging path APIs.

## Research Notes

- PnP support is split by device extension type: bus, volume, PDO, and actual filesystem VCB.
- Query-remove behavior is conservative and refuses removal if open children exist.
- Surprise removal intentionally avoids metadata writeback and transitions to removal state.
- Device usage propagation is important for pagefile/hibernation/dump-file correctness across multi-device Btrfs volumes.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/pnp.c -->