# Group Research: group_1832_windows_driver_samples_sources_windows_windows_driver_samples_files_2ec59ea431db

Scope confirmed against `Docs/research_subset_a.md`: `sources/windows/windows-driver-samples` is included. All seven listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/dirctrl.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/dirctrl.c

## Purpose

Implements CDFS directory-control handling for directory enumeration and directory change notification. This is the IRP_MJ_DIRECTORY_CONTROL worker used by both FSD and FSP paths.

## Main Entry Points

- `CdCommonDirControl`: validates that the handle decodes as `UserDirectoryOpen`, then dispatches on minor function.
- `CdQueryDirectory`: performs `IRP_MN_QUERY_DIRECTORY`.
- `CdNotifyChangeDirectory`: performs `IRP_MN_NOTIFY_CHANGE_DIRECTORY`.
- `CdInitializeEnumeration`: prepares persistent enumeration state from the CCB and request flags.
- `CdEnumerateIndex`: advances through directory entries until it finds the next matching visible entry.

## Key Behavior

`CdCommonDirControl` rejects non-directory handles with `STATUS_INVALID_PARAMETER`. It handles only `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`; other minor functions complete with `STATUS_INVALID_DEVICE_REQUEST`.

`CdQueryDirectory` supports these information classes:

- `FileDirectoryInformation`
- `FileFullDirectoryInformation`
- `FileIdFullDirectoryInformation`
- `FileNamesInformation`
- `FileBothDirectoryInformation`
- `FileIdBothDirectoryInformation`

It maps the user buffer, initializes a `FILE_ENUM_CONTEXT`, acquires the directory FCB shared, verifies the FCB, initializes enumeration state, then loops over matching entries. The buffer-fill rules are explicit: the first matching record may return a truncated name with `STATUS_BUFFER_OVERFLOW`; later records are either fully copied or not copied at all, preserving restart position for a later query.

Directory result entries use the dirent creation time for creation/write/change times. Directories report zero allocation and EOF and get `FILE_ATTRIBUTE_DIRECTORY`; files use the computed `FileContext.FileSize`, sector-aligned allocation, and `FILE_ATTRIBUTE_READONLY`. Hidden dirents set `FILE_ATTRIBUTE_HIDDEN`. ID directory classes receive a file ID via `CdSetFidFromParentAndDirent`.

For name output, it copies the Unicode file name and optionally appends `;` plus the version string. Version strings are returned when the search expression included a version, and also for directories with a version string. `FileBothDirectoryInformation` and `FileIdBothDirectoryInformation` also get a generated 8.3 short name when appropriate.

Enumeration state lives in the CCB. On a successful/non-error exit, after cleaning up the file context, it updates `Ccb->CurrentDirentOffset` and `CCB_FLAG_ENUM_RETURN_NEXT` under the FCB lock. Cleanup is intentionally done before acquiring the FCB mutex to avoid blocking against internal stream creation/purge paths that wait for mappings to release.

`CdNotifyChangeDirectory` supports notify requests even though CD media will not generate modifications. It verifies the VCB and calls `FsRtlNotifyFullChangeDirectory`, using the file object's name as the watched path and then completes only the IRP context while leaving the IRP pending.

## Enumeration Details

`CdInitializeEnumeration` handles restart and pattern setup. If `SL_RESTART_SCAN` includes a new pattern, it frees any previous search expression and clears initialization flags. It treats missing, empty, or single `*` names as match-all. Otherwise it converts the requested name into CDFS name/version components, records wildcard flags independently for name and version, uppercases for ignore-case searches, and stores the expression in the CCB. Root-directory enumeration suppresses constant `.` and `..` entries.

Positioning supports three modes:

- `SL_INDEX_SPECIFIED`: starts from the caller's file index and walks from the beginning to find a valid containing dirent.
- `SL_RESTART_SCAN`: starts from the directory stream offset.
- Otherwise: resumes from the CCB's saved offset and return-next flag.

`CdEnumerateIndex` skips associated files, root-suppressed constant entries, and duplicate lower versions when the search expression has no version component. It tests the long name first, then generates/tests an 8.3 short name when the long name is not 8.3 and the search has no version. On match, it calls `CdLookupLastFileDirent` so multi-extent files have complete size information.

## Dependencies

This file depends heavily on file object decoding, FCB/VCB locking, dirent walking and name conversion helpers from the rest of CDFS:

- `CdDecodeFileObject`
- `CdVerifyFcbOperation`
- `CdVerifyOrCreateDirStreamFile`
- `CdLookupInitialFileDirent`
- `CdLookupNextInitialFileDirent`
- `CdLookupLastFileDirent`
- `CdUpdateDirentName`
- `CdIsNameInExpression`
- `CdGenerate8dot3Name`
- `FsRtlNotifyFullChangeDirectory`
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/dirctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/dirsup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/dirsup.c

## Purpose

Provides low-level CDFS directory-entry support: mapping directory sectors, walking raw dirents, validating bounds, converting raw dirents into in-memory `DIRENT` structures, building Unicode names, searching for files/directories, grouping multi-extent entries, computing file sizes, detecting XA extents, and cleaning enumeration contexts.

## Main Entry Points

- `CdLookupDirent`
- `CdLookupNextDirent`
- `CdUpdateDirentFromRawDirent`
- `CdUpdateDirentName`
- `CdFindFile`
- `CdFindDirectory`
- `CdFindFileByShortName`
- `CdLookupNextInitialFileDirent`
- `CdLookupLastFileDirent`
- `CdCleanupFileContext`
- `CdCheckRawDirentBounds`
- `CdCheckForXAExtent`

## Directory Walking

Directories are treated as contiguous sectors. `CdLookupDirent` maps the sector containing a known dirent offset, truncating length at EOF, and validates the raw dirent with `CdCheckRawDirentBounds`.

`CdLookupNextDirent` finds the next possible dirent. It can reuse or remap a sector, advances by `NextDirentOffset`, skips all-zero sector tails, maps the next sector when needed, and validates each nonzero candidate. It supports `CurrentDirContext` and `NextDirContext` pointing to the same structure.

`CdCheckRawDirentBounds` rejects corrupt records when the raw dirent length exceeds remaining mapped bytes, is smaller than the minimum raw dirent size, or cannot contain the declared file-id length. A return of zero means the next search should move to the next sector.

## Raw Dirent Conversion

`CdUpdateDirentFromRawDirent` copies unaligned on-disk fields safely into `DIRENT`:

- `DirentOffset`
- raw dirent length
- starting logical block plus XAR length
- data length
- timestamp pointer
- dirent flags
- interleave fields
- file-name pointer and length
- possible system-use offset
- XA defaults

It rejects zero-length file names with `STATUS_FILE_CORRUPT_ERROR`.

`CdUpdateDirentName` turns raw ISO/HSG/Joliet bytes into CDFS Unicode name/version fields. It handles constant directory entries where a one-byte name of 0 or 1 maps to `.` or `..`. It allocates a larger buffer when embedded storage is insufficient, converts OEM names to Unicode for non-Joliet discs, converts big-endian Unicode for Joliet discs, splits name and version with `CdConvertNameToCdName`, strips a trailing period before a version string, validates legal names, and optionally builds an uppercase comparison name.

## Search Functions

`CdFindFile` searches only non-directory, non-associated entries. It compares long CDFS names first, then tries a generated 8.3 short name when the requested name can refer to a short-name offset and the candidate long name is not already 8.3. On success it calls `CdLookupLastFileDirent`.

`CdFindDirectory` searches directory entries only and does not use short-name equivalence.

`CdFindFileByShortName` uses the encoded short-name dirent offset. Since raw dirents are at least 34 bytes, one shifted 32-byte bucket can identify at most one dirent. It walks until the matching bucket, rejects associated and already-8.3 entries, generates the 8.3 name, compares, and collects all dirents on success.

## Multi-Extent and XA Handling

`CdLookupNextInitialFileDirent` advances to the first dirent of the next file, skipping any remaining multi-extent dirents for the current file. It rotates `PriorDirent`, `InitialDirent`, and `CurrentDirent` slots in `FILE_ENUM_CONTEXT`, clears file size and flags, and leaves the context positioned at the next file's initial dirent.

`CdLookupLastFileDirent` starts from a matching initial dirent and walks all `CD_ATTRIBUTE_MULTI` extents. It computes total file size. For CD-XA media, it calls `CdCheckForXAExtent`, verifies consistent extent type across all extents, enforces sector alignment when logical block size is not 2048 bytes, accounts for RIFF header size on first XA extent, and uses XA sector payload sizing for Mode2 Form2 data. Corrupt multi-extent chains raise `STATUS_FILE_CORRUPT_ERROR`.

`CdCheckForXAExtent` scans the system-use area for the XA signature and records audio, Mode2 Form2, XA attributes, and XA file number.

## Cleanup

`CdCleanupFileContext` unpins all mapped dirent contexts and frees allocated name buffers for all compound dirent slots in the file enumeration context.

## Dependencies

Key dependencies include cache manager mapping (`CcMapData`), CDFS unpin/cleanup helpers, raw ISO/HSG macros, name conversion helpers, short-name generation helpers, and VCB state flags such as `VCB_STATE_JOLIET` and `VCB_STATE_CDXA`.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/dirsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/fieldoff.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/fieldoff.c

## Purpose

A standalone diagnostic/layout utility, not runtime filesystem-driver logic. It includes `CdProcs.h` and `stdio.h`, defines a `doit` macro, and prints structure field offsets and field sizes.

## Main Behavior

`main` prints a header and then instantiates many CDFS structure types on the stack solely so the macro can compute:

- structure name
- `FIELD_OFFSET(type, field)`
- `sizeof(d.field)`
- field name

The output format is:

`<Record>  <offset>  <size>  <field>`

## Covered Structures

The utility reports offsets for core CDFS structures, including:

- `CD_MCB`, `CD_MCB_ENTRY`
- `CD_NAME`, `NAME_LINK`, `PREFIX_ENTRY`
- `CD_DATA`
- `VCB`, `VOLUME_DEVICE_OBJECT`
- `FCB_DATA`, `FCB_INDEX`, `FCB_NONPAGED`, `FCB`
- `CCB`
- `IRP_CONTEXT`, `IRP_CONTEXT_LITE`, `CD_IO_CONTEXT`, `THREAD_CONTEXT`
- `PATH_ENUM_CONTEXT`, `PATH_ENTRY`, `COMPOUND_PATH_ENTRY`
- `DIRENT_ENUM_CONTEXT`, `DIRENT`, `COMPOUND_DIRENT`, `FILE_ENUM_CONTEXT`
- `RIFF_HEADER`, `AUDIO_PLAY_HEADER`
- `RAW_ISO_VD`, `RAW_HSG_VD`, `RAW_DIRENT`
- `RAW_PATH_ISO`, `RAW_PATH_HSG`
- `SYSTEM_USE_XA`

## Notes

The function is K&R-style C with `VOID __cdecl main(argc, argv)`. It does not use `argc` or `argv`. There is no mutation of driver state, no IRP handling, and no filesystem behavior. Its value is build/debug support for verifying binary layout expectations across CDFS internal and on-disk structures.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/fieldoff.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/fileinfo.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/fileinfo.c

## Purpose

Implements CDFS file-information query/set handling and fast I/O query callbacks. Since CDFS is read-only, set support is limited to current file position.

## Main Entry Points

- `CdCommonQueryInfo`
- `CdCommonSetInfo`
- `CdFastQueryBasicInfo`
- `CdFastQueryStdInfo`
- `CdFastQueryNetworkInfo`
- `CdQueryBasicInfo`
- `CdQueryStandardInfo`
- `CdQueryInternalInfo`
- `CdQueryEaInfo`
- `CdQueryPositionInfo`
- `CdQueryNameInfo`
- `CdQueryAlternateNameInfo`
- `CdQueryNetworkInfo`

## Query Path

`CdCommonQueryInfo` decodes the file object and supports only `UserFileOpen` and `UserDirectoryOpen`. It acquires the FCB shared, initializes an uninitialized directory stream when needed, verifies the FCB, dispatches by information class, sets `IoStatus.Information` to bytes consumed, releases the FCB, and completes the IRP.

Supported query classes include:

- `FileAllInformation`
- `FileBasicInformation`
- `FileStandardInformation`
- `FileInternalInformation`
- `FileEaInformation`
- `FilePositionInformation`
- `FileNameInformation`
- `FileAlternateNameInformation`
- `FileNetworkOpenInformation`

Name-bearing classes are rejected for `CCB_FLAG_OPEN_BY_ID` because the handle cannot supply a normal path name. `FileAllInformation` also rejects open-by-ID handles.

## Returned Metadata

`CdQueryBasicInfo` sets creation, last-write, and change time from `Fcb->CreationTime`; last-access time is zero. Attributes come from `Fcb->FileAttributes`.

`CdQueryStandardInfo` reports one link, delete-pending false, directory flag based on attributes, zero sizes for directories, and FCB allocation/file size for files.

`CdQueryInternalInfo` returns `Fcb->FileId`.

`CdQueryEaInfo` always returns EA size zero.

`CdQueryPositionInfo` returns `FileObject->CurrentByteOffset`.

`CdQueryNameInfo` copies `FileObject->FileName` into a `FILE_NAME_INFORMATION` buffer and returns `STATUS_BUFFER_OVERFLOW` if the full name does not fit while still reporting the required length.

`CdQueryNetworkInfo` returns the same timestamp/attribute/size shape used by basic and standard queries.

## Alternate Name Handling

`CdQueryAlternateNameInfo` generates the 8.3 alternate name for long names. It returns `STATUS_OBJECT_NAME_NOT_FOUND` for the root FCB, handles opened with an explicit version, or names already in 8.3 form.

For directories, it finds the child dirent by reading the path-table entry, converting the path-entry name, and searching the parent directory. For files, it looks up the raw dirent offset from the FID and converts the dirent name. It then generates the short name from the long case-normalized name and dirent offset, copies as much as fits, and reports `STATUS_BUFFER_OVERFLOW` on truncation.

## Set Path

`CdCommonSetInfo` supports only `FilePositionInformation` on `UserFileOpen`. For `FO_NO_INTERMEDIATE_BUFFERING`, the requested byte offset must align to the VCB block mask. On success it updates `FileObject->CurrentByteOffset` under the FCB lock. All other set-info requests return `STATUS_INVALID_PARAMETER`.

## Fast I/O

The three fast query routines decode the file object with `CdFastDecodeFileObject`, allow user files and initialized user directories, acquire the FCB resource shared with the caller's wait preference, verify the FCB, fill the output buffer directly from FCB fields, set `IoStatus`, release the resource, and leave the filesystem critical region. If decode, initialized-directory checks, acquisition, or verification fail, they return `FALSE` so the caller can use the normal IRP path.

## Dependencies

This file depends on file-object decoding, FCB resource synchronization, directory stream creation, dirent/path lookup helpers, 8.3 name helpers, and standard NT file-information structures.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/fileinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/filobsup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/filobsup.c

## Purpose

Provides CDFS file-object context encoding and decoding helpers.

## Main Entry Points

- `CdSetFileObject`
- `CdDecodeFileObject`
- `CdFastDecodeFileObject`

## Key Behavior

CDFS stores the FCB pointer in `FileObject->FsContext`. It stores the CCB pointer in `FileObject->FsContext2`, with the low three bits used to encode `TYPE_OF_OPEN`. `TYPE_OF_OPEN_MASK` is `0x00000007`.

`CdSetFileObject` clears both context pointers for `UnopenedFileObject`. For real opens, it asserts that the CCB pointer is quad-aligned so the low three bits are free, stores the FCB and CCB, ORs the open type into `FsContext2`, and sets `FileObject->Vpb` from the FCB's VCB.

`CdDecodeFileObject` extracts the low-bit open type from `FsContext2`. If the type is `UnopenedFileObject`, it returns null FCB/CCB. Otherwise it returns `FsContext` as the FCB and `FsContext2` with the type bits cleared as the CCB.

`CdFastDecodeFileObject` is a lighter fast-I/O helper: it asserts a valid file object, returns `FsContext` as the FCB, and returns the low-bit open type. It does not return the CCB.

## Design Notes

The code asserts that `BeyondValidType <= 8`, preserving the low-three-bit encoding contract. This file is a central dependency for dispatch, directory control, file information, FSCTL, and fast I/O paths because most request validation begins by decoding the file object's open type.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/filobsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/fsctrl.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/fsctrl.c

## Purpose

Implements CDFS filesystem-control handling: mount, verify, user FSCTLs, oplocks, volume lock/unlock/dismount, dirty/mounted/path queries, volume invalidation, extended DASD reads, stale VCB cleanup, remount detection, and primary/Joliet volume descriptor scanning.

## Main Entry Points

- `CdCommonFsControl`
- `CdUserFsctl`
- `CdMountVolume`
- `CdVerifyVolume`
- `CdOplockRequest`
- `CdLockVolume`
- `CdUnlockVolume`
- `CdDismountVolume`
- `CdIsVolumeDirty`
- `CdIsVolumeMounted`
- `CdIsPathnameValid`
- `CdInvalidateVolumes`
- `CdAllowExtendedDasdIo`
- `CdScanForDismountedVcb`
- `CdFindPrimaryVd`
- `CdIsRemount`
- `CdFindActiveVolDescriptor`

Global toggles:

- `CdDisable`: disables mounting.
- `CdNoJoliet`: disables Joliet secondary volume descriptor selection.

## Dispatch and User FSCTLs

`CdCommonFsControl` handles `IRP_MN_USER_FS_REQUEST`, `IRP_MN_MOUNT_VOLUME`, and `IRP_MN_VERIFY_VOLUME`. Other minor functions complete with `STATUS_INVALID_DEVICE_REQUEST`.

`CdUserFsctl` dispatches these user controls:

- oplock request/ack controls
- `FSCTL_LOCK_VOLUME`
- `FSCTL_UNLOCK_VOLUME`
- `FSCTL_DISMOUNT_VOLUME`
- `FSCTL_IS_VOLUME_DIRTY`
- `FSCTL_IS_VOLUME_MOUNTED`
- `FSCTL_IS_PATHNAME_VALID`
- `FSCTL_INVALIDATE_VOLUMES`
- `FSCTL_ALLOW_EXTENDED_DASD_IO`

Unknown controls return `STATUS_INVALID_DEVICE_REQUEST`.

## Mount Path

`CdMountVolume` expects a CD-ROM real device and a waitable IRP context. It updates `IrpContext->RealDevice`, honors `CdDisable` and shutdown state, performs `IOCTL_CDROM_CHECK_VERIFY` to collect media change count, optionally queries drive geometry to determine block factor, acquires global CDFS data, scans for removable stale VCBs, creates a volume device object, initializes overflow queue state, reads the TOC, and initializes a new VCB.

For data discs it allocates a sector-sized descriptor buffer and calls `CdFindPrimaryVd`. If no valid PVD is found but the TOC indicates suitable audio content, it may mount as an audio/CD-XA disk. When a PVD is found, it preserves it, then calls `CdFindActiveVolDescriptor` to select a supported Joliet secondary descriptor when present.

It allocates a directory sector cache only for non-audio single-track media. It then checks `CdIsRemount`; on remount, it transfers the new device object and sector cache to the old VCB through `CdReMountOldVcb` and may issue mount notification if the old VCB requested it. New mounts call `CdUpdateVcbFromVolDescriptor`, capture SCSI transfer limits, drop residual references, dereference the target device object, mark the VCB mounted, and send mount notification.

Failure cleanup is extensive: unowned TOC and descriptor buffers are freed, verify is restored when appropriate, partially installed VPBs are detached, incomplete VCBs are dismounted, leftover device objects are deleted, and the global resource is released.

## Verify Path

`CdVerifyVolume` reacquires global state and the VCB exclusively, rejects invalid/dismounting VCBs, performs check-verify, compares media change count, rereads and compares TOC when needed, and for data discs rereads descriptors. It reselects the active descriptor, compares serial number and volume label against the VPB, and returns `STATUS_WRONG_VOLUME` on mismatch.

On success it marks the VCB mounted and clears the real-device verify bit. On wrong volume it marks the VCB not mounted, frees XA and directory cache state, may purge the volume, and checks for dismount if no cleanup handles remain. It updates media change count regardless of outcome.

## Volume Locking and Dismount

`CdLockVolumeInternal` purges the volume, waits for lazy writer activity, forces waitable reacquire of the VCB, drains FSP closes, and sets `VCB_STATE_LOCKED` plus `VPB_LOCKED` only if user references match the allowed residual counts. Explicit locks record the locking file object.

`CdUnlockVolumeInternal` clears `VCB_STATE_LOCKED`, `VPB_LOCKED`, and `VolumeLockFileObject` only when the unlock caller matches the recorded lock file object.

`CdLockVolume` accepts only `UserVolumeOpen`, sends `FSRTL_VOLUME_LOCK`, acquires the VCB exclusive, verifies it, calls the internal lock helper, and sends lock-failed notification on failure.

`CdUnlockVolume` accepts only `UserVolumeOpen`, calls the internal unlock helper, and sends `FSRTL_VOLUME_UNLOCK` on success.

`CdDismountVolume` accepts only `UserVolumeOpen`, sends `FSRTL_VOLUME_DISMOUNT`, acquires global data and VCB exclusive, invalidates mounted volumes, sets `VCB_STATE_DISMOUNTED`, marks the CCB with `CCB_FLAG_DISMOUNT_ON_CLOSE`, and calls `FsRtlDismountComplete` on Windows 8+.

## Other User Controls

`CdOplockRequest` allows oplocks only on `UserFileOpen`. It makes the IRP context waitable, acquires the FCB exclusive for new oplock requests or shared for break acknowledgements, verifies the FCB, calls `FsRtlOplockFsctrl`, updates `IsFastIoPossible`, and lets the oplock package complete the IRP.

`CdIsVolumeDirty` requires a system output buffer large enough for `ULONG`, accepts only `UserVolumeOpen`, rejects dismounted volumes, and always returns a clean state because CDFS is read-only.

`CdIsVolumeMounted` decodes the file object, verifies the VCB if an FCB is available, and otherwise succeeds.

`CdIsPathnameValid` always succeeds.

`CdAllowExtendedDasdIo` accepts only `UserVolumeOpen` and sets `CCB_FLAG_ALLOW_EXTENDED_DASD_IO`.

`CdInvalidateVolumes` is restricted to the filesystem device object and requires `SeTcbPrivilege`. It accepts a file-object handle, extracts the underlying device object, walks all VCBs for that real device, swaps VPBs off the device when needed, marks matching volumes invalid, purges them, and checks for dismount.

`CdScanForDismountedVcb` walks the global VCB queue and calls `CdCheckForDismount` on VCBs already dismounting, invalid, or not mounted with only residual references.

## Descriptor and Remount Helpers

`CdFindPrimaryVd` searches at most two passes: first using last-session/multisession information when available, then from sector zero. It skips audio-only VCBs, reads descriptors starting at `FIRST_VD_SECTOR`, recognizes ISO and HSG identifiers, rejects invalid versions and terminators, and records VCB volume type, base sector, current descriptor offset, and primary descriptor offset when not in verify mode.

`CdIsRemount` scans existing VCBs on the same real device in `VcbNotMounted` state. Audio disks match by TOC. Data disks match by serial number, TOC, volume label length/content, and real device.

`CdFindActiveVolDescriptor` scans ISO descriptors for supported Joliet secondary descriptors unless `CdNoJoliet` is set. It recognizes the supported Joliet escape sequences, updates VCB state and descriptor offset when not verifying, restores the saved PVD if no secondary descriptor is selected, and on mount computes the VPB serial number and Unicode volume label with trailing spaces/nulls stripped.

## Dependencies

This file coordinates most global CDFS state and uses VPB spin locks, CDFS VCB/FCB resources, TOC processing, low-level device I/O controls, sector reads, descriptor macros, purge/dismount helpers, FsRtl volume notifications, oplock helpers, and optional telemetry.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/fsctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/fspdisp.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/fspdisp.c

## Purpose

Implements the CDFS FSP worker-thread dispatcher. Posted IRP contexts enter here and are routed to the common worker for their major function.

## Main Entry Point

- `CdFspDispatch`

## Key Behavior

`CdFspDispatch` receives an `IRP_CONTEXT`, extracts the IRP and current stack location, and identifies the associated `VOLUME_DEVICE_OBJECT` when the request has a file object. It then enters a processing loop.

For each IRP context it:

- sets `IRP_CONTEXT_FSP_FLAGS`
- enters the filesystem critical region
- sets CDFS thread context
- initializes exception status and IRP status/information
- dispatches by major function
- handles exceptions through `CdExceptionFilter` and `CdProcessException`
- retries internally on `STATUS_CANT_WAIT`
- exits the filesystem critical region

Supported dispatch targets include:

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
- `IRP_MJ_PNP` -> assertion plus `CdCommonPnp`
- default -> complete with `STATUS_INVALID_DEVICE_REQUEST`

`IRP_MJ_CLOSE` asserts false; close processing is not expected through this FSP dispatch path.

## Retry and Overflow Queue Handling

When processing returns `STATUS_CANT_WAIT`, the dispatcher marks `IRP_CONTEXT_FLAG_MORE_PROCESSING`, cleans the IRP context for retry, and runs the request again.

After a request finishes, if there is an associated volume device object, it checks the volume overflow queue under `OverflowQueueSpinLock`. If queued work exists, it decrements `OverflowQueueCount`, dequeues the next IRP context, and continues processing it in the same worker thread. If no overflow work remains, it decrements `PostedRequestCount` and returns to the executive worker thread.

## Dependencies

This file is the bridge from posted asynchronous work to the common CDFS request routines. It relies on IRP context flags, CDFS exception handling, thread-context setup, completion helpers, and the volume overflow queue fields initialized during mount.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/fspdisp.c -->