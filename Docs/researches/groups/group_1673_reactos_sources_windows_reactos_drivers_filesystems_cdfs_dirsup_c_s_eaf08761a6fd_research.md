# Group Research: group_1673_reactos_sources_windows_reactos_drivers_filesystems_cdfs_dirsup_c_s_eaf08761a6fd

Scope checked against `Docs/research_subset_a.md`: this group is within `sources/windows/reactos`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/dirsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/dirsup.c

## Purpose

`dirsup.c` implements CDFS directory-entry support. It maps ISO/HSG directory sectors, validates raw dirent boundaries, converts raw on-disk dirents into in-memory `DIRENT` structures, builds Unicode names, searches for files/directories, handles generated 8.3 aliases, and gathers multi-extent file metadata.

The file documents key ISO9660 directory behavior: dirents are sector-contained, zero padding may fill sector tails, like-named versioned files are contiguous and ordered by decreasing version, and a logical file can span multiple dirents/extents.

## Main Entry Points

- `CdLookupDirent`: starts a directory walk at a known dirent offset. It maps the containing sector with `CcMapData`, initializes `DIRENT_ENUM_CONTEXT`, truncates mapped length at EOF, and validates the raw dirent with `CdCheckRawDirentBounds`.
- `CdLookupNextDirent`: advances to the next valid dirent, possibly unpinning and mapping the next sector. It skips zero-length sector padding and all-zero sectors allowed by CDFS, then validates the found entry.
- `CdUpdateDirentFromRawDirent`: copies unaligned on-disk `RAW_DIRENT` fields into a normalized `DIRENT`, including file location, data length, timestamp pointer, dirent flags, interleave metadata, filename pointer/length, system-use offset, and default XA metadata.
- `CdUpdateDirentName`: converts raw on-disk file identifiers into `CD_NAME` values. It handles `.` and `..` constant entries, OEM-to-Unicode conversion for non-Joliet media, big-endian Unicode conversion for Joliet, filename/version splitting, trailing-dot trimming, legal-name validation, and optional upcase buffers.
- `CdFindFile`: scans a directory for a non-directory, non-associated file matching a `CD_NAME`; if the exact long name fails, it can match a generated short name keyed by dirent offset.
- `CdFindDirectory`: scans only directory entries and matches names without short-name fallback.
- `CdFindFileByShortName`: directly seeks the long file whose generated 8.3 name corresponds to the caller-provided short-name dirent-offset encoding.
- `CdLookupNextInitialFileDirent`: moves from one file’s first dirent to the next file’s first dirent, skipping remaining extents of the prior file when necessary.
- `CdLookupLastFileDirent`: gathers all dirents/extents for a file and computes aggregate file size, including CD-XA mode handling.
- `CdCleanupFileContext`: releases all mapped dirent contexts and allocated dirent name buffers in a `FILE_ENUM_CONTEXT`.
- `CdCheckRawDirentBounds`: validates raw dirent size, minimum length, file identifier capacity, and sector containment; returns the offset to the next dirent or zero for next-sector movement.
- `CdCheckForXAExtent`: parses the XA system-use area, recognizes XA signatures, audio extents, and Mode2 Form2 data, and stores XA attributes/file number.

## Data Flow

Directory walking centers on `DIRENT_ENUM_CONTEXT`, which stores the mapped sector, sector base offset, current offset, data length, BCB, and next-dirent offset. `COMPOUND_DIRENT` pairs this context with the normalized `DIRENT`. `FILE_ENUM_CONTEXT` keeps prior, initial, and current compound dirents so callers can scan files that may contain multiple extents.

Raw dirent lookup proceeds as:

1. Map a sector from the directory stream file.
2. Use the `CdRawDirent` macro to address the raw dirent at `Sector + SectorOffset`.
3. Validate bounds and derive the next offset.
4. Copy raw metadata into `DIRENT`.
5. Convert raw file ID bytes into exact-case and optionally case-folded `CD_NAME`.
6. Search or aggregate extents depending on caller.

## Name Handling

Self and parent entries are detected as one-byte directory file IDs `0` and `1` and mapped to fixed Unicode directory names. Non-special entries are converted based on media state:

- Non-Joliet: `RtlOemToUnicodeN`.
- Joliet: `CdConvertBigToLittleEndian`.

After conversion, `CdConvertNameToCdName` splits the semicolon version suffix, trailing periods are removed from the filename portion, and `CdIsLegalName` validates the resulting Unicode filename. Ignore-case searches allocate or split a double-sized buffer so exact and upcased names can coexist.

## Short Name Support

Short-name matching is derived from `CdShortNameDirentOffset` and `CdGenerate8dot3Name`. The generated short name encodes `DirentOffset >> SHORT_NAME_SHIFT` after a tilde, reducing collision risk. `CdFindFile` first tries the disk name, then checks a generated 8.3 alias if the requested name looks like a short-name form and the target dirent offset matches.

## Multi-Extent and CD-XA Behavior

`CdLookupLastFileDirent` walks all dirents for a file until a dirent without `CD_ATTRIBUTE_MULTI` is reached. It sums file sizes across extents. For CD-XA media, it calls `CdCheckForXAExtent` and enforces consistent extent type across all extents. For XA data it validates sector alignment when logical block size is not 2048 and computes visible file size using RIFF header plus `XA_SECTOR_SIZE` per sector.

## Error Handling and Corruption Checks

The file raises `STATUS_FILE_CORRUPT_ERROR` for malformed dirents, zero-length file names, illegal converted names, invalid self/parent ordering with prior allocation, missing multi-extent continuation, inconsistent XA extent types, and invalid XA/interleave alignment. It uses cache-manager BCB unpin cleanup through helper routines rather than direct cleanup in each scan loop.

## Dependencies

Important dependencies include cache mapping (`CcMapData`, `CdUnpinData`), name helpers from `namesup.c`, volume state flags such as `VCB_STATE_JOLIET` and `VCB_STATE_CDXA`, dirent/path structures from CDFS headers, and allocation helpers such as `FsRtlAllocatePoolWithTag` and `CdFreePool`.

## Research Notes

This file is the core bridge between ISO9660/HSG on-disk directory records and CDFS higher-level create, enumeration, and query behavior. Its correctness depends heavily on sector-boundary invariants, BCB lifetime, and preserving dirent-offset identity for short-name synthesis.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/dirsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/fieldoff.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/fieldoff.c

## Purpose

`fieldoff.c` is a diagnostic/layout utility, not a filesystem runtime path. It includes `cdprocs.h` and prints field offsets and field sizes for the major CDFS in-memory and on-disk structures.

## Main Behavior

The file defines:

- `doit(a,b)`: prints the record type name, `FIELD_OFFSET(a,b)`, `sizeof(d.b)`, and field name.
- `main`: instantiates local variables of many CDFS structure types and invokes `doit` for each important field.

The output begins with:

`<Record> <offset> <size> <field>`

Then it prints grouped layout tables separated by blank lines.

## Structures Covered

The utility reports layout for:

- Mapping/name structures: `CD_MCB`, `CD_MCB_ENTRY`, `CD_NAME`, `NAME_LINK`, `PREFIX_ENTRY`.
- Global/volume structures: `CD_DATA`, `VCB`, `VOLUME_DEVICE_OBJECT`.
- FCB and CCB structures: `FCB_DATA`, `FCB_INDEX`, `FCB_NONPAGED`, `FCB`, `CCB`.
- Request and thread structures: `IRP_CONTEXT`, `IRP_CONTEXT_LITE`, `CD_IO_CONTEXT`, `THREAD_CONTEXT`.
- Path/dirent enumeration structures: `PATH_ENUM_CONTEXT`, `PATH_ENTRY`, `COMPOUND_PATH_ENTRY`, `DIRENT_ENUM_CONTEXT`, `DIRENT`, `COMPOUND_DIRENT`, `FILE_ENUM_CONTEXT`.
- CD-XA/media headers: `RIFF_HEADER`, `AUDIO_PLAY_HEADER`.
- Raw ISO/HSG structures: `RAW_ISO_VD`, `RAW_HSG_VD`, `RAW_DIRENT`, `RAW_PATH_ISO`, `RAW_PATH_HSG`, `SYSTEM_USE_XA`.

## Dependencies

It depends on all relevant CDFS type definitions being visible through `cdprocs.h`, and on `FIELD_OFFSET` being available. It also includes `<stdio.h>`, making it a host-style console program rather than kernel-driver code.

## Research Notes

This utility is useful when comparing ReactOS/Microsoft-derived structure packing, validating ABI-sensitive offsets, or debugging generated structure documentation. It uses old-style K&R `main(argc, argv)` parameters and does not consume its arguments.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/fieldoff.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/fileinfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/fileinfo.c

## Purpose

`fileinfo.c` implements CDFS file-information query and set handlers, plus fast I/O query callbacks. Because CDFS is read-only, set-information support is intentionally narrow: it only accepts `FilePositionInformation` on user file opens.

## Main Dispatch Routines

- `CdCommonQueryInfo`: handles `IRP_MJ_QUERY_INFORMATION` for user file and directory opens. It acquires the FCB shared, initializes directory stream metadata if needed, verifies the FCB, dispatches by `FILE_INFORMATION_CLASS`, updates `IoStatus.Information`, releases the FCB, and completes the IRP.
- `CdCommonSetInfo`: handles `IRP_MJ_SET_INFORMATION`, but only for `FilePositionInformation` on `UserFileOpen`. It validates alignment for `FO_NO_INTERMEDIATE_BUFFERING`, then updates `FileObject->CurrentByteOffset` under the FCB lock.

## Supported Query Classes

`CdCommonQueryInfo` supports:

- `FileAllInformation`
- `FileBasicInformation`
- `FileStandardInformation`
- `FileInternalInformation`
- `FileEaInformation`
- `FilePositionInformation`
- `FileNameInformation`
- `FileAlternateNameInformation`
- `FileNetworkOpenInformation`

Name and alternate-name queries are rejected for handles opened by file ID. Unsupported classes return `STATUS_INVALID_PARAMETER`.

## Local Query Helpers

- `CdQueryBasicInfo`: zeroes `FILE_BASIC_INFORMATION`, sets creation/last-write/change time from `Fcb->CreationTime`, last access to zero, and attributes from the FCB.
- `CdQueryStandardInfo`: reports one link, not delete-pending, and returns zero allocation/EOF for directories; files use `Fcb->AllocationSize` and `Fcb->FileSize`.
- `CdQueryInternalInfo`: returns `Fcb->FileId` as the index number.
- `CdQueryEaInfo`: returns EA size zero because CDFS has no EAs.
- `CdQueryPositionInfo`: returns `FileObject->CurrentByteOffset`.
- `CdQueryNameInfo`: copies `FileObject->FileName` into `FILE_NAME_INFORMATION`, returning `STATUS_BUFFER_OVERFLOW` if only a prefix fits while preserving the required full length.
- `CdQueryAlternateNameInfo`: computes and returns a generated 8.3 alternate name for long-name files.
- `CdQueryNetworkInfo`: fills `FILE_NETWORK_OPEN_INFORMATION` with timestamps, attributes, and size fields.

## Fast I/O Query Callbacks

- `CdFastQueryBasicInfo`: fast path for basic info.
- `CdFastQueryStdInfo`: fast path for standard info.
- `CdFastQueryNetworkInfo`: fast path for network-open info.

All decode the file object, require initialized user file or directory opens, acquire the FCB resource shared with the caller’s `Wait` setting, verify the FCB, fill the output buffer, set `IoStatus`, and release the resource. If preconditions fail or the resource cannot be acquired, they return `FALSE` so the caller can use the IRP path.

## Alternate Name Lookup

`CdQueryAlternateNameInfo` is the most complex helper. It rejects root and version-specific opens, acquires the parent directory, ensures the parent stream exists, and then locates the original dirent:

- For directories, it resolves the child path-table entry and searches the parent by directory name.
- For files, it directly looks up the dirent offset encoded in the file ID.

It updates the dirent name, rejects names already legal 8.3, generates a short name with `CdGenerate8dot3Name`, copies it to the output buffer, and handles cleanup of dirent/path contexts.

## Error and Status Behavior

The file consistently uses length decrementing to compute `IoStatus.Information`. Several helper routines assume the caller provided enough fixed-structure space; variable-length name helpers explicitly return `STATUS_BUFFER_OVERFLOW` when only partial name data fits. Read-only unsupported set operations return `STATUS_INVALID_PARAMETER`.

## Dependencies

This file depends on file-object decoding from `filobsup.c`, directory lookup/name support from `dirsup.c` and `namesup.c`, FCB/VCB verification helpers, resource acquisition helpers, and Windows `FILE_*_INFORMATION` structures.

## Research Notes

The implementation preserves Windows CDFS semantics: directories report zero logical size for standard/network information, access time is zero, delete-pending is always false, EA size is zero, and alternate names are synthetic rather than on-disk metadata.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/fileinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/filobsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/filobsup.c

## Purpose

`filobsup.c` implements CDFS file-object context encoding and decoding. It stores the FCB in `FILE_OBJECT.FsContext` and stores the CCB plus low-bit open-type tags in `FILE_OBJECT.FsContext2`.

## Main Functions

- `CdSetFileObject`: initializes a `FILE_OBJECT` for a CDFS open type. For `UnopenedFileObject`, it clears `FsContext` and `FsContext2`. Otherwise it asserts the CCB is sufficiently aligned, stores the FCB and CCB, ORs the `TYPE_OF_OPEN` value into the low three bits of `FsContext2`, and sets `FileObject->Vpb` from `Fcb->Vcb->Vpb`.
- `CdDecodeFileObject`: extracts the open type from the low three bits of `FsContext2`. For unopened objects it returns null FCB/CCB. Otherwise it returns `FsContext` as FCB and `FsContext2` with the type bits cleared as CCB.
- `CdFastDecodeFileObject`: fast callback helper that returns the FCB and open type without returning a CCB.

## Encoding Scheme

`TYPE_OF_OPEN_MASK` is `0x7`, so only three low bits are available. `CdSetFileObject` asserts `BeyondValidType <= 8` and that the CCB pointer has those low bits clear. This relies on pointer alignment to embed the open type in the CCB pointer value.

## Dependencies

This file depends on `TYPE_OF_OPEN`, `PFCB`, `PCCB`, file-object layout, CDFS assertion macros, and ReactOS-compatible lvalue handling around `SetFlag` and `ClearFlag`.

## Research Notes

This is a small but central convention file. Every dispatch path that needs to know whether a handle is a user file, directory, volume, stream, or unopened object depends on this low-bit tagging scheme being applied consistently.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/filobsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/fsctrl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/fsctrl.c

## Purpose

`fsctrl.c` implements CDFS file-system-control handling: mount, verify, user FSCTL dispatch, oplocks, volume lock/unlock/dismount, volume dirty/mounted/path queries, volume invalidation, extended DASD I/O, remount detection, and ISO/Joliet volume descriptor scanning.

It also defines global mount behavior flags:

- `CdDisable`: disables CDFS mounting.
- `CdNoJoliet`: disables Joliet supplementary descriptor selection.

## Top-Level Dispatch

- `CdCommonFsControl`: dispatches by FSCTL minor function:
  - `IRP_MN_USER_FS_REQUEST` -> `CdUserFsctl`
  - `IRP_MN_MOUNT_VOLUME` -> `CdMountVolume`
  - `IRP_MN_VERIFY_VOLUME` -> `CdVerifyVolume`
  - others -> `STATUS_INVALID_DEVICE_REQUEST`

- `CdUserFsctl`: dispatches user FSCTL codes:
  - Oplock FSCTLs -> `CdOplockRequest`
  - `FSCTL_LOCK_VOLUME` -> `CdLockVolume`
  - `FSCTL_UNLOCK_VOLUME` -> `CdUnlockVolume`
  - `FSCTL_DISMOUNT_VOLUME` -> `CdDismountVolume`
  - `FSCTL_IS_VOLUME_DIRTY` -> `CdIsVolumeDirty`
  - `FSCTL_IS_VOLUME_MOUNTED` -> `CdIsVolumeMounted`
  - `FSCTL_IS_PATHNAME_VALID` -> `CdIsPathnameValid`
  - `FSCTL_INVALIDATE_VOLUMES` -> `CdInvalidateVolumes`
  - `FSCTL_ALLOW_EXTENDED_DASD_IO` -> `CdAllowExtendedDasdIo`

## Mount Path

`CdMountVolume` verifies media, reads drive geometry, determines block factor, acquires global CDFS synchronization, creates a volume device object, initializes overflow queues, processes the CD TOC, initializes the VCB, reads primary and supplementary volume descriptors, optionally allocates the sector cache, detects remounts, initializes VCB fields from the volume descriptor, queries SCSI transfer limits, releases residual references, marks the VCB mounted, sends mount notification, and completes the IRP.

ReactOS-specific branches allow disk-backed ISO mounting through `CdData.HddFileSystemDeviceObject`, using disk IOCTLs instead of CDROM IOCTLs where appropriate.

The mount path supports:
- Normal ISO/HSG/Joliet data discs.
- Audio disc fallback when no valid PVD is found but audio tracks exist and the data track is not first.
- Remounting a prior `VcbNotMounted` VCB by swapping VPB/device state.
- Single-track sector-cache allocation for directory acceleration.

## Verify Path

`CdVerifyVolume` reacquires the mounted VCB and checks whether media is still the same. It:

1. Runs `IOCTL_CDROM_CHECK_VERIFY`.
2. Uses media change count when available.
3. Re-reads and compares the TOC.
4. For data discs, finds the primary VD, optionally finds active Joliet VD, compares serial number, and compares volume label.
5. Marks the volume mounted and clears the verify bit if successful.
6. On wrong volume, marks the VCB not mounted, frees XA and directory cache state, and may trigger dismount if no user handles remain.
7. Sends remount notification when `VCB_STATE_NOTIFY_REMOUNT` is set.

## Volume Locking and Dismount

- `CdLockVolumeInternal`: purges the volume, waits for lazy writer activity, reacquires the VCB exclusively, runs delayed close processing, and succeeds only if cleanup/user-reference counts show no other user handles. It sets `VCB_STATE_LOCKED`, `VPB_LOCKED`, and records the locking file object.
- `CdUnlockVolumeInternal`: clears explicit lock state if the caller matches `VolumeLockFileObject`.
- `CdLockVolume`: accepts only `UserVolumeOpen`, sends lock notification, acquires the VCB exclusive, verifies it, calls the internal lock helper, and sends lock-failed notification on failure.
- `CdUnlockVolume`: accepts only `UserVolumeOpen`, calls the internal unlock helper, and sends unlock notification on success.
- `CdDismountVolume`: accepts only `UserVolumeOpen`, sends dismount notification, makes the request waitable, acquires global/Vcb synchronization, marks the VCB invalid and dismounted, sets `CCB_FLAG_DISMOUNT_ON_CLOSE`, and completes. On newer NTDDI it calls `FsRtlDismountComplete`.

## Oplocks

`CdOplockRequest` allows oplocks only on `UserFileOpen`. It forces a waitable IRP context, acquires the FCB exclusive for oplock requests or shared for break acknowledgements, verifies the FCB, calls `FsRtlOplockFsctrl`, updates `IsFastIoPossible`, releases the FCB, and lets the oplock package complete the IRP when appropriate.

For level 2 oplocks it checks current or in-progress byte-range locks; for other request oplocks it uses `FcbCleanup` as the open count.

## Miscellaneous FSCTLs

- `CdIsVolumeDirty`: validates a user volume open and output buffer, always reports clean state for mounted CDFS volumes.
- `CdIsVolumeMounted`: decodes the file object, disables popups, verifies the VCB if present, and returns success if no verification error is raised.
- `CdIsPathnameValid`: always succeeds.
- `CdAllowExtendedDasdIo`: accepts only user volume opens and sets `CCB_FLAG_ALLOW_EXTENDED_DASD_IO`.
- `CdInvalidateVolumes`: privileged operation requiring `SeTcbPrivilege`; obtains a file object from an input handle, finds all VCBs on the same real device, swaps VPB state if necessary, marks volumes invalid, purges, and checks for dismount.
- `CdScanForDismountedVcb`: opportunistically walks the global VCB queue and calls `CdCheckForDismount` on invalid, dismounting, or low-reference not-mounted volumes.

## Volume Descriptor Scanning

- `CdFindPrimaryVd`: scans for a primary volume descriptor. It may make two passes: first using last-session information for multisession discs, then from sector zero. It recognizes ISO and HSG standard IDs, rejects wrong versions/terminators, and records VCB volume type, base sector, VD sector offset, and primary VD offset when not in verify mode.
- `CdFindActiveVolDescriptor`: searches for a supported Joliet secondary descriptor unless `CdNoJoliet` is set. It accepts known Joliet escape sequences, switches VCB state from ISO to Joliet, records the active descriptor offset, computes serial number, and stores a trimmed Unicode volume label in the VPB. If no supplementary descriptor is found, it restores the saved primary descriptor.
- `CdIsRemount`: compares a new VCB against not-mounted VCBs on the same real device. Audio discs compare TOC contents; data discs compare serial number, TOC, and volume label.
- `CdReMountOldVcb`: moves the old VCB to the new target device/VPB, updates condition/media-change count, clears VPB-not-on-device state, and transfers sector-cache buffer ownership from the new VCB.

## Error Handling and Cleanup

The mount and verify paths use structured try/finally cleanup heavily. They free TOC and volume descriptor buffers, restore verify state on failed mounts, delete temporary device objects, dismount partially initialized VCBs, release global resources, and dereference notification file objects. Several status codes are deliberately normalized to `STATUS_WRONG_VOLUME` to allow RAW or other filesystem handling.

## Dependencies

This file depends on CDFS VCB lifecycle helpers, low-level device IOCTL helpers, TOC processing, cache purge/dismount helpers, VPB spin-lock manipulation, CDFS volume descriptor macros, name endian conversion, notification APIs, oplock APIs, privilege checks, and ReactOS-specific filesystem-device branching.

## Research Notes

`fsctrl.c` is the central lifecycle file for CDFS volumes. Its most important invariants are global mount/verify serialization, VCB exclusive ownership during state transitions, careful VPB manipulation under spin lock, and consistency checks between TOC, serial number, and volume label during verify/remount.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/fsctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/fspdisp.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/fspdisp.c

## Purpose

`fspdisp.c` implements the CDFS filesystem process worker dispatch routine. Posted IRP contexts enter `CdFspDispatch`, which runs them in a filesystem worker context and dispatches by major IRP function.

## Main Function

`CdFspDispatch` receives an `IRP_CONTEXT` as `Context`, extracts its IRP and stack location, optionally derives the `VOLUME_DEVICE_OBJECT`, and enters a processing loop.

For each request it:

1. Marks the IRP context with FSP flags.
2. Enters the filesystem with `FsRtlEnterFileSystem`.
3. Sets thread context with `CdSetThreadContext`.
4. Runs the major-function switch inside SEH.
5. Handles exceptions through `CdExceptionFilter` and `CdProcessException`.
6. Retries if the status is `STATUS_CANT_WAIT` after cleaning the IRP context for more processing.
7. Exits the filesystem.
8. Services the volume overflow queue if present.

## IRP Major Functions Dispatched

The worker dispatches:

- `IRP_MJ_CREATE` -> `CdCommonCreate`
- `IRP_MJ_READ` -> `CdCommonRead`
- `IRP_MJ_QUERY_INFORMATION` -> `CdCommonQueryInfo`
- `IRP_MJ_SET_INFORMATION` -> `CdCommonSetInfo`
- `IRP_MJ_QUERY_VOLUME_INFORMATION` -> `CdCommonQueryVolInfo`
- `IRP_MJ_DIRECTORY_CONTROL` -> `CdCommonDirControl`
- `IRP_MJ_FILE_SYSTEM_CONTROL` -> `CdCommonFsControl`
- `IRP_MJ_DEVICE_CONTROL` -> `CdCommonDevControl`
- `IRP_MJ_LOCK_CONTROL` -> `CdCommonLockControl`
- `IRP_MJ_CLEANUP` -> `CdCommonCleanup`
- `IRP_MJ_PNP` -> asserts false, then calls `CdCommonPnp`
- defaults -> completes `STATUS_INVALID_DEVICE_REQUEST`

`IRP_MJ_CLOSE` asserts false, indicating close should not normally be handled through this FSP dispatch path.

## Overflow Queue Handling

After each request, if a volume device object was associated with the original file object, the routine checks `VolDo->OverflowQueue` under `OverflowQueueSpinLock`. If queued work exists, it decrements the overflow count, removes the next IRP context, updates `Irp` and `IrpSp`, and continues processing in the same worker invocation. If no queued work remains, it decrements `PostedRequestCount` and returns to the executive worker thread.

## Error Handling

The dispatch loop uses SEH around the common routine call. `STATUS_CANT_WAIT` triggers a retry path where `IRP_CONTEXT_FLAG_MORE_PROCESSING` is set and `CdCleanupIrpContext` prepares the context for another attempt.

## Dependencies

This file depends on all common IRP handlers, exception-processing helpers, CDFS thread context helpers, and volume overflow queue fields.

## Research Notes

This is a compact but central asynchronous dispatch bridge. It keeps worker-thread entry, retry-on-cannot-wait behavior, and per-volume overflow queue draining in one place.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/fspdisp.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/lockctrl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/lockctrl.c

## Purpose

`lockctrl.c` implements byte-range lock control for CDFS, including IRP-based lock handling and fast I/O lock/unlock callbacks.

## Main IRP Path

`CdCommonLockControl` handles `IRP_MJ_LOCK_CONTROL`. It decodes the file object and accepts only `UserFileOpen`. It checks oplock state with `FsRtlCheckOplock`, verifies the FCB, creates an `FsRtl` file lock if needed, calls `FsRtlProcessFileLock`, recomputes `Fcb->IsFastIoPossible`, completes the request, and returns the status.

## Fast I/O Lock/Unlock Functions

- `CdFastLock`: validates `UserFileOpen`, verifies the FCB, requires fast oplock eligibility, creates a file lock if needed, calls `FsRtlFastLock`, and updates fast I/O state when a lock is granted.
- `CdFastUnlockSingle`: validates `UserFileOpen`, returns `STATUS_RANGE_NOT_LOCKED` if no file lock exists, checks oplock fast-I/O eligibility, calls `FsRtlFastUnlockSingle`, and recomputes fast I/O state when no current locks remain.
- `CdFastUnlockAll`: validates `UserFileOpen`, returns `STATUS_RANGE_NOT_LOCKED` if no file lock exists, checks oplock fast-I/O eligibility, calls `FsRtlFastUnlockAll`, and recomputes fast I/O state.
- `CdFastUnlockAllByKey`: same structure as unlock-all, but calls `FsRtlFastUnlockAllByKey`.

All fast callbacks enter and exit the filesystem around protected work and return `FALSE` when the fast path cannot safely complete, letting the caller fall back to the IRP path.

## Locking Semantics

Only user file opens can use byte-range locks. Directory, volume, stream, or unopened objects are rejected with `STATUS_INVALID_PARAMETER`. The implementation relies on `FsRtl` lock packages for actual range conflict and unlock semantics.

## Fast I/O State

After lock state changes, the file’s `IsFastIoPossible` state is recomputed with `CdIsFastIoPossible`. This ensures cached/fast I/O observes lock and oplock restrictions.

## Dependencies

This file depends on file-object decoding from `filobsup.c`, FCB verification, oplock helpers from `fsctrl.c`/FCB state, `CdCreateFileLock`, `CdGetFcbOplock`, `CdLockFcb`, `CdUnlockFcb`, and Windows `FsRtl` file-lock APIs.

## Research Notes

The file is mostly a thin validation and synchronization layer over `FsRtl` byte-range locking. Its correctness depends on rejecting non-file opens, keeping file-lock allocation synchronized, and updating fast-I/O eligibility after any successful lock-state mutation.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/lockctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/namesup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/namesup.c

## Purpose

`namesup.c` implements CDFS name manipulation: splitting ISO version suffixes, endian conversion for Joliet names, uppercasing, path component dissection, legal-name checks, 8.3 validation/generation, wildcard matching, short-name offset extraction, and direct lexical comparison.

## Main Functions

- `CdConvertNameToCdName`: splits a `CD_NAME` file name at `;`. The filename portion remains in `FileName`; bytes after the semicolon become `VersionString` when present.
- `CdConvertBigToLittleEndian`: converts a big-endian Unicode byte stream into little-endian form. Odd byte counts raise `STATUS_DISK_CORRUPT_ERROR`.
- `CdUpcaseName`: upcases both filename and version string portions, inserting a semicolon separator into the destination buffer when copying into a separate `CD_NAME`.
- `CdDissectName`: removes the first path component from `RemainingName` and returns it in `FinalName`, advancing past a backslash if more components remain.
- `CdIsLegalName`: checks Unicode characters against HPFS legality while explicitly allowing `"`, `<`, `>`, and `|` for CDFS behavior.
- `CdIs8dot3Name`: validates whether a Unicode name is legal 8.3/FAT-style form, rejecting spaces, excess length, excess dots, dots past the base-name limit, and names that cannot convert to legal OEM DBCS FAT names.
- `CdGenerate8dot3Name`: creates a synthetic short name from a long Unicode name and dirent offset.
- `CdIsNameInExpression`: matches a current `CD_NAME` against a search expression, using `FsRtlIsNameInExpression` when wildcard flags are set and exact memory comparison otherwise. It can optionally match version strings.
- `CdShortNameDirentOffset`: parses a tilde plus hexadecimal offset string from a name before any dot; returns `MAXULONG` if not found or invalid.
- `CdFullCompareNames`: performs fast case-sensitive lexical comparison via `RtlCompareMemory`, resolving equal prefixes by shorter length.

## 8.3 Generation Details

`CdGenerate8dot3Name` first calls `RtlGenerate8dot3Name` to obtain a generic Unicode short name. It then biases the base name by inserting `~` plus the hexadecimal representation of `DirentOffset >> SHORT_NAME_SHIFT`. It carefully accounts for DBCS lead bytes in the OEM representation so the generated name remains within the 8-character base limit. The extension portion, if present, is copied after the biased base.

## Wildcard and Version Matching

`CdIsNameInExpression` independently checks file name and version string portions. Version matching occurs only when requested, when the search expression contains a version, and when the wildcard flags do not indicate version-match-all. Wildcards are delegated to `FsRtlIsNameInExpression`; non-wildcard paths use direct length and byte comparison.

## Endian and Joliet Support

Joliet directory and volume strings are big-endian Unicode on disk. `CdConvertBigToLittleEndian` is the shared primitive used by both name conversion and volume-label handling. It treats odd byte counts as corrupt media.

## Dependencies

This file depends on Windows RTL string conversion and name routines, `FsRtl` wildcard/FAT-name helpers, CDFS name structures, wildcard flags in CCB state, and short-name constants such as `BYTE_COUNT_8_DOT_3` and `SHORT_NAME_SHIFT`.

## Research Notes

This file defines the name semantics used by create, directory enumeration, alternate-name queries, and volume verification. The generated short-name scheme is deterministic and tied to dirent offset, not stored on disk.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/namesup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/nodetype.h -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/nodetype.h

## Purpose

`nodetype.h` defines CDFS node type codes and bugcheck file IDs. It establishes the convention that major CDFS structures begin with a `NODE_TYPE_CODE` followed by a `NODE_BYTE_SIZE`.

## Node Type Definitions

The header defines:

- `NODE_TYPE_CODE` as `USHORT`
- `NODE_BYTE_SIZE` as `CSHORT`
- `NTC_UNDEFINED`
- CDFS node codes for:
  - data header
  - VCB
  - path-table FCB
  - index FCB
  - data FCB
  - nonpaged FCB
  - CCB
  - IRP context
  - lite IRP context

It also defines:

- `NodeType(P)`: returns the first node type code or `NTC_UNDEFINED` for null.
- `SafeNodeType(Ptr)`: directly reads the node type code.

## Bugcheck IDs

The header assigns file-specific high-word IDs such as:

- `CDFS_BUG_CHECK_DIRSUP`
- `CDFS_BUG_CHECK_FILEINFO`
- `CDFS_BUG_CHECK_FILOBSUP`
- `CDFS_BUG_CHECK_FSCTRL`
- `CDFS_BUG_CHECK_FSPDISP`
- `CDFS_BUG_CHECK_LOCKCTRL`
- `CDFS_BUG_CHECK_NAMESUP`

and many other CDFS modules.

`CdBugCheck(A,B,C)` calls `KeBugCheckEx(CDFS_FILE_SYSTEM, BugCheckFileId | __LINE__, A, B, C)`, combining the module’s `BugCheckFileId` with the source line.

## Dependencies

The header assumes kernel types such as `USHORT`, `CSHORT`, and `KeBugCheckEx` are available from included Windows/ReactOS headers.

## Research Notes

This header is a diagnostic and structural identity foundation. Runtime validation and debugging can quickly identify CDFS object kinds through the first two fields, while bugchecks include both module identity and line number.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/nodetype.h -->