# Group Research: group_1685_reactos_sources_windows_reactos_drivers_filesystems_fastfat_create__e3f6b23de7d8

Scope: `Docs/research_subset_a.md` includes `sources/windows/reactos`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/create.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/create.c

This file implements the ReactOS FastFAT `IRP_MJ_CREATE` path: volume opens, root and directory opens, existing-file opens, new file/directory creation, overwrite/supersede handling, name lookup, oplock coordination, share/access checks, and create-time cleanup/rollback. It is a large Windows FastFAT-derived create implementation with ReactOS compatibility edits around SEH and pointer typing.

Key responsibilities:
- Dispatch `NtCreateFile`/`NtOpenFile` requests through `FatFsdCreate` and `FatCommonCreate`.
- Normalize create names, reject invalid path forms, enforce directory-vs-file options, and route empty/root names to volume/root opens.
- Walk the in-memory FCB/DCB prefix tree, fall back to on-disk directory-entry lookup, and create missing intermediate DCBs while parsing paths.
- Open existing volumes, root directories, directories, files, and target directories while updating file-object context, CCBs, share access, open counts, read-only counts, and cache flags.
- Create new FAT directory entries, long-name entries, FCB/DCB objects, EA handles, allocation, and change notifications for new files/directories.
- Perform supersede/overwrite by purging cached sections, truncating allocation, applying new allocation, updating attributes/timestamps/EA handles, and sending modify notifications.
- Coordinate create/open requests with oplocks, image sections, writable mapped sections, volume lock/write-protect state, paging-file restrictions, and optional stack expansion.

Important functions:
- `FatFsdCreate`: FSD dispatch wrapper for create IRPs; handles filesystem device-object short-circuit, top-level IRP state, `FsRtlEnterFileSystem`, exception processing, and final completion.
- `FatCommonCreateOnNewStack` / `FatCommonCreateCallout`: On newer NT targets, run `FatCommonCreate` on an expanded kernel stack and translate callout exceptions/status back to the caller.
- `FatCommonCreate`: Main create engine. It decodes options, acquires the VCB exclusively, verifies volume/FCBs, handles volume/root opens, parses names, looks up FCB/DCB prefixes and dirents, dispatches to existing/new open helpers, handles posting for oplocks, and performs broad error cleanup.
- `FatOpenVolume`: Opens DASD volume handles, optionally locks the volume for exclusive/non-write-shared opens, flushes/purges referenced objects, cleans the volume bit when safe, establishes direct-access share state, and records explicit device/manage-volume access in the CCB.
- `FatOpenRootDcb`: Opens the root directory after disposition/access/share checks and increments root/volume open accounting.
- `FatOpenExistingDcb`: Opens an already cached directory, checks `NoEaKnowledge`, disposition/access/share rules, optional handle-oplock breaks, directory oplock state, delete-on-close, and short-name-open flags.
- `FatOpenExistingFcb`: Opens an already cached file, applies implied access for overwrite/supersede, checks readonly/delete and hidden/system rules, handles share/oplock/image-section conflicts, purges cache for noncached opens when appropriate, and delegates overwrite/supersede to `FatSupersedeOrOverwriteFile`.
- `FatOpenTargetDirectory`: Implements `SL_OPEN_TARGET_DIRECTORY`; opens the parent DCB and rewrites `FileObject->FileName` to the final component, returning `FILE_EXISTS` or `FILE_DOES_NOT_EXIST`.
- `FatOpenExistingDirectory`: Builds a new DCB for an on-disk directory not already cached, performs EA/access/disposition checks, optional oplock setup, then installs the file object and open counts.
- `FatOpenExistingFile`: Builds a new FCB for an on-disk file not already cached, handles paging-file allocation lookup, create disposition, optional overwrite/supersede, and open accounting.
- `FatCreateNewDirectory`: Selects short/LFN names, allocates one or more dirents, handles LFN entries crossing a page boundary, creates a DCB, applies EA metadata, initializes `.`/`..`, reports directory-add notification, and contains extensive rollback for partial directory creation.
- `FatCreateNewFile`: Creates a new file dirent/FCB, uses the tunnel cache to restore short/long names and creation time, allocates initial file space, applies EA metadata, reports file-add notification, and unwinds dirents/allocation/FCB/CCB state on abnormal termination.
- `FatSupersedeOrOverwriteFile`: Implements `FILE_SUPERSEDE`, `FILE_OVERWRITE`, and `FILE_OVERWRITE_IF` for existing files, including section purge, allocation reset, EA replacement/deletion, dirent update, timestamp/attribute changes, and notification.
- `FatSetFullNameInFcb`: Fast path to synthesize `Fcb->FullFileName` from parent full name plus final component, preferring exact-case long names.
- `FatCheckSystemSecurityAccess`: Grants `ACCESS_SYSTEM_SECURITY` only when `SE_SECURITY_PRIVILEGE` is present.
- `FatCheckShareAccess`: Wraps `IoCheckShareAccess` and, on Vista+ targets, treats existing writable user mappings as sharing violations when write sharing is denied.
- `FatCallSelfCompletionRoutine`: Small event-signaling completion routine copied from NTFS for self-issued IRPs.

Important interactions:
- Relies on VCB exclusive acquisition for create serialization and sets `VCB_STATE_FLAG_CREATE_IN_PROGRESS` around cache purge paths to prevent teardown races.
- Uses FCB/DCB splay trees for cached-name lookup and `FatLocateDirent` for on-disk lookup; `FileNameOpenedDos` tracks short-name hits for CCB flags.
- Uses `FatSelectNames`, `FatConstructDirent`, `FatCreateNewDirent`, `FatPrepareWriteDirectoryFile`, and LFN dirent counting to build FAT short/LFN directory records.
- Interacts with FAT EA support through `FatCreateEa`, `FatDeleteEa`, `FatGetNeedEaCount`, and dirent `ExtendedAttributes`, while Fat32 paths bypass EA storage.
- Uses `FsRtlCheckOplock`, `FsRtlCheckOplockEx`, `FsRtlOplockBreakH`, and `FsRtlOplockFsctrl` for create/open oplock semantics and atomic `FILE_OPEN_REQUIRING_OPLOCK`.
- Uses cache/MM calls such as `CcPurgeCacheSection`, `CcFlushCache`, `CcSetFileSizes`, `MmFlushImageSection`, `MmCanFileBeTruncated`, and `MmDoesFileHaveUserWritableReferences`.
- Sends namespace/content notifications via `FatNotifyReportChange` after successful create or overwrite operations.
- Maintains volume/device state through write-protect hard-error setup, dirty-volume cleaning, media eject disable for paging files, and direct-access volume locking.

Notable behavior and risks:
- The main create path is intentionally exception-heavy; failed creates rely on nested cleanup to undo BCB pins, dirent bitmap bits, file allocation, stream file cache maps, share state, counts, FCB/DCB/CCB allocations, and partial EA work.
- New directory/file LFN sequences may cross a page boundary; the code copies through a temporary pool dirent array and has special rollback logic for each page.
- `FatCommonCreate` mutates incoming file-name buffers to collapse leading double backslashes and to remove a trailing backslash before validation.
- Open-by-file-id is explicitly unsupported because FAT file IDs are not reversible.
- FAT32 rejects any EA buffer at the top of create processing, while non-FAT32 still honors `NoEaKnowledge` and Need-EA checks.
- Overwrite/supersede temporarily augments desired access for conflict checks, then removes added bits before recording real share access.
- Paging-file opens have special restrictions: an existing non-paged-pool FCB cannot be converted to a paging FCB, allocation is looked up eagerly, media eject can be disabled, and a reserve MDL is allocated.
- Several cleanup comments note dangling DCB branches can remain in rare failure paths, favoring correctness of live cache/allocation teardown over complete tree pruning.
- ReactOS-specific casts are present for `FatPrepareWriteDirectoryFile` output pointers and `InterlockedCompareExchangePointer` on `FatReserveMdl`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/create.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/devctrl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/devctrl.c

This file implements FastFAT `IRP_MJ_DEVICE_CONTROL` handling. It accepts device-control requests only on user volume opens, performs limited filesystem-side policy for snapshot, disk-copy, and SCSI pass-through IOCTLs, and otherwise forwards requests to the lower storage device.

Key responsibilities:
- Dispatch device-control IRPs through `FatFsdDeviceControl`.
- Validate that the file object decodes as `UserVolumeOpen`.
- Intercept `IOCTL_VOLSNAP_FLUSH_AND_HOLD_WRITES` to flush the FAT volume and hold file resources while the lower driver processes the request.
- Deny `IOCTL_DISK_COPY_DATA` unless the volume is locked, forced direct write is requested, or the handle completed a dismount.
- Detect SCSI `FORMAT_UNIT` pass-through commands and mark the CCB/file object so close-time verification can occur.
- Forward all accepted IOCTLs to `Vcb->TargetDeviceObject`.

Important functions:
- `FatFsdDeviceControl`: FSD wrapper that enters the filesystem, establishes top-level IRP state, creates an IRP context with waitability from `CanFsdWait`, calls `FatCommonDeviceControl`, and routes exceptions through `FatProcessException`.
- `FatCommonDeviceControl`: Main IOCTL handler. It decodes the user volume open, switches on `IoControlCode`, performs special handling for snapshot flush/hold, direct disk copy, and SCSI pass-through format commands, forwards the IRP to the target device, and completes or detaches the IRP as appropriate.
- `FatDeviceControlCompletionRoutine`: Completion routine used by the synchronous snapshot path; signals an event and returns `STATUS_MORE_PROCESSING_REQUIRED` when an event context is supplied.

Important interactions:
- Uses `FatDecodeFileObject` to reject file/directory opens for device-control requests.
- Uses `FatAcquireExclusiveVolume`, `FatFlushAndCleanVolume`, and `FatReleaseVolume` for `IOCTL_VOLSNAP_FLUSH_AND_HOLD_WRITES`.
- Copies the current IRP stack location and installs a completion routine only for the snapshot hold path; most IOCTLs use `IoSkipCurrentIrpStackLocation`.
- Forwards accepted IOCTLs with `IoCallDriver(Vcb->TargetDeviceObject, Irp)`.
- Checks `VCB_STATE_FLAG_LOCKED`, `SL_FORCE_DIRECT_WRITE`, and `CCB_FLAG_COMPLETE_DISMOUNT` before allowing `IOCTL_DISK_COPY_DATA`.
- Parses `SCSI_PASS_THROUGH`, `SCSI_PASS_THROUGH_DIRECT`, `SCSI_PASS_THROUGH_EX`, and `SCSI_PASS_THROUGH_DIRECT_EX` buffers, including Wow64 32-bit structure variants when enabled.

Notable behavior and risks:
- The snapshot flush-and-hold path forces wait semantics, holds the volume exclusively, waits for lower-driver completion when pending, then releases the volume and completes the IRP itself.
- Non-snapshot forwarded IOCTLs set `Irp = NULL` before `FatCompleteRequest`, so completion belongs to the lower driver while the IRP context is still freed.
- SCSI format-unit detection is best-effort and only runs when the system buffer is present and the input buffer is large enough for the relevant pass-through structure.
- Only user volume opens can issue these device controls; other open types fail with `STATUS_INVALID_PARAMETER`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/devctrl.c -->