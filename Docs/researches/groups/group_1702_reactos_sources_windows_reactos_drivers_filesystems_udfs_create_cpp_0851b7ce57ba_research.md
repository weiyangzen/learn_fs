# Group Research: group_1702_reactos_sources_windows_reactos_drivers_filesystems_udfs_create_cpp_0851b7ce57ba

Scope: `Docs/research_subset_a.md`

Files researched:
- `sources/windows/reactos/drivers/filesystems/udfs/create.cpp`
- `sources/windows/reactos/drivers/filesystems/udfs/devcntrl.cpp`
- `sources/windows/reactos/drivers/filesystems/udfs/dircntrl.cpp`
- `sources/windows/reactos/drivers/filesystems/udfs/dldetect.cpp`
- `sources/windows/reactos/drivers/filesystems/udfs/dldetect.h`
- `sources/windows/reactos/drivers/filesystems/udfs/env_spec.cpp`
- `sources/windows/reactos/drivers/filesystems/udfs/env_spec.h`
- `sources/windows/reactos/drivers/filesystems/udfs/errmsg.h`

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/create.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/create.cpp

## Purpose

`create.cpp` implements the ReactOS UDFS `IRP_MJ_CREATE` path. It handles all open/create forms for UDF volumes, root directories, regular files, directories, named streams, duplicate/reopen requests, and file-id opens. It also initializes FCB/CCB state for first opens and binds successful creates to NT `FILE_OBJECT` structures.

## Main Entry Points

- `UDFCreate(PDEVICE_OBJECT, PIRP)`: top-level create dispatch routine registered from `udfinit.cpp`. It enters the filesystem, handles direct opens of the filesystem control device object, creates an IRP context, calls `UDFCommonCreate`, and routes exceptions through the driver exception/logging path.
- `UDFCommonCreate(PtrUDFIrpContext, PIRP)`: central create/open implementation. It decodes create options/disposition, validates volume state, resolves paths, opens or creates the requested object, checks access/share rules, handles overwrite/supersede, completes the IRP, and unwinds intermediate open state on failure.
- `UDFReleaseResFromCreate(PERESOURCE*, PERESOURCE*, PERESOURCE*)`: cleanup helper that releases the paging I/O resource plus two ordinary resources if held.
- `UDFAcquireParent(PUDF_FILE_INFO, PERESOURCE*, PERESOURCE*)`: acquires parent/current FCB main resources and bumps references while path traversal is using a parent chain.
- `UDFFirstOpenFile(...)`: allocates and initializes an FCB and NT-required FCB state for a file info object that has not yet been opened through the FSD.
- `UDFOpenFile(PVCB, PFILE_OBJECT, PtrUDFFCB)`: allocates a CCB, attaches it to a `FILE_OBJECT`, links the CCB into the FCB, and increments reference counts.
- `UDFInitializeFCB(...)`: initializes FCB bookkeeping, resources, file lock, list links, name, flags, and VCB association.

## Create/Open Flow

`UDFCreate` first rejects no-op FSD-device opens by completing them as `FILE_OPENED`. For volume-device opens, it establishes top-level IRP state and delegates to `UDFCommonCreate`.

`UDFCommonCreate` performs the real work:

1. It decodes `FILE_OBJECT`, related file object, desired access, share access, allocation size, file attributes, create disposition, and create option flags.
2. It rejects unsupported early cases such as paging-file creation and nonzero EA length.
3. It obtains the VCB, flush-breaks pending work, denies creates during soft eject, denies foreign-PID access to locked volumes, verifies the VCB, and downgrades the VCB resource from exclusive to shared after verification.
4. It enforces read-only or dirty-open volume restrictions before any modifying operation.
5. It special-cases volume opens, root-directory opens, open-by-file-id, relative opens, duplicate-handle/reopen requests, stream paths, open-target-directory requests, missing-object creates, and existing-object opens.
6. It completes success by setting `FILE_OBJECT` flags, CCB flags, open counts, readonly counts, valid FCB flags, `IoStatus.Information`, and final IRP status.
7. It completes failure by removing share access when needed, cleaning CCB state, closing intermediate `UDF_FILE_INFO` chains, cleaning FCB chains, releasing resources, and freeing path buffers.

## Path Resolution

The routine constructs an absolute path from either the target name or a related directory object. Relative opens require the related object to be a directory and reject absolute target names. It normalizes leading double backslashes, trims trailing backslashes, validates total path and component lengths, and calls `UDFIsNameValid` to detect invalid characters and stream syntax.

Traversal uses `UDFDissectName` to split path components. Each component is opened through `UDFOpenFile__` for normal files/directories or `UDFOpenStreamDir__`/`UDFCreateStreamDir__` for stream directories. The loop keeps `LastGoodFileInfo`, `LastGoodName`, `LastGoodTail`, `OldRelatedFileInfo`, and `TreeLength` so it can distinguish a valid parent from a missing final component and unwind internal opens accurately.

`FILE_OPEN_BY_FILE_ID` is translated into an absolute path by `UDFGetOpenParamsByFileId`, after which the normal absolute open path is reused.

## Volume and Root Opens

Volume opens are identified by an empty file name with no non-volume related object. The code rejects invalid directory-only/delete/create semantics for volumes, checks whether the desired access/share combination implies read-only or read-write volume access, optionally flushes and closes delayed handles before exclusive-like opens, and may set `UDF_VCB_FLAGS_VOLUME_LOCKED`. It opens the VCB as the FCB, marks the CCB as `UDF_CCB_VOLUME_OPEN`, checks security/share access, forces no intermediate buffering, reports `FILE_OPENED`, and emits a volume event hook.

Root opens are identified by an absolute path length of one backslash. The code rejects file-only, supersede, overwrite, and delete-on-close requests; opens `Vcb->RootDirFCB`; references the root file info; checks access/share; and returns `FILE_OPENED`.

## Create, Stream, Overwrite, and Supersede Behavior

If traversal fails on the final object with `STATUS_OBJECT_NAME_NOT_FOUND` or `STATUS_OBJECT_PATH_NOT_FOUND`, `UDFCommonCreate` creates only for `FILE_CREATE`, `FILE_OPEN_IF`, `FILE_OVERWRITE_IF`, or `FILE_SUPERSEDE`. It checks volume writability, delete-on-close with readonly attributes, parent add-file/add-subdirectory access, target-name validity, and directory-versus-stream restrictions.

New objects are created with `UDFCreateFile__`, optionally converted into directories with `UDFRecordDirectory__`, assigned NT archive attributes for files, opened through `UDFFirstOpenFile`, initialized to zero length, and passed through `UDFSetAccessRights`. Notify events report file, directory, or stream additions.

Named stream creation can involve three phases: open/create the base file, create/open the stream directory, then create/open the stream entry. The code marks the underlying FCB valid between phases and updates `LocalPath` and `TreeLength` for unwind.

Existing objects go through `AlreadyOpened`. `FILE_CREATE` returns `STATUS_OBJECT_NAME_COLLISION`. Directory-only/file-only mismatches are rejected. Delete-on-close rejects readonly files and non-empty directories. Existing-object overwrite/supersede checks delete or write permissions, verifies system/hidden attribute compatibility, rejects mapped-file truncation via `MmCanFileBeTruncated`, synchronizes with `PagingIoResource`, truncates using `UDFResizeFile__`, updates allocation/file/valid lengths, calls `CcSetFileSizes`, adjusts attributes, and emits modify notifications.

## FCB/CCB Initialization

`UDFFirstOpenFile` allocates a UDF FCB and object name, links the FCB to `UDF_FILE_INFO`, attaches or allocates the shared `UDFNTRequiredFCB` stored in the file's `Dloc->CommonFcb`, seeds sizes/timestamps from on-disk metadata for new common FCBs, inserts the FCB under `Vcb->FcbListResource`, initializes readonly/directory flags, appends the final on-disk name, and optionally calls `UDFOpenFile`.

`UDFInitializeFCB` initializes `FSRTL_COMMON_FCB_HEADER` resource pointers, main and paging resources, file locks, common reference count, CCB list resource, VCB FCB list link, CCB list head, counters, flags, name pointer, and owning VCB.

`UDFOpenFile` allocates a CCB, stores the FCB and file object, fills `FsContext`, `FsContext2`, `Vpb`, and `SectionObjectPointer`, clears delayed-close state, links the CCB into `NextCCB`, and increments FCB/common reference counts.

## Synchronization and State

The create path uses `Vcb->VCBResource`, FCB `MainResource`, and, for truncation, `PagingIoResource`. It carefully tracks `Res1`, `Res2`, and `PagingIoRes` to avoid leaking locks across early exits. It temporarily increments `VCBOpenCount` around flush/close-all operations that release the VCB resource.

Successful opens update `VCBHandleCount`, per-FCB `OpenHandleCount`, `CachedOpenHandleCount`, `VCBOpenCount`, and optionally `VCBOpenCountRO`. CCB flags record delete-on-close, case-sensitive opens, readonly opens, volume opens, and tree length. File-object flags are set for write-through, sequential I/O, no buffering, cache support, execute fast I/O, case sensitivity, and stream opens.

## Integration Points

This file depends heavily on:

- `udf_info` primitives: `UDFOpenFile__`, `UDFCreateFile__`, `UDFCloseFile__`, `UDFCreateStreamDir__`, `UDFOpenStreamDir__`, `UDFRecordDirectory__`, `UDFResizeFile__`, `UDFUnlinkFile__`.
- Access/security helpers: `UDFCheckAccessRights`, `UDFSetAccessRights`, `UdfIllegalFcbAccess`.
- VCB and volume helpers: `UDFVerifyVcb`, `UDFFlushTryBreak`, `UDFFlushLogicalVolume`, delayed-close cleanup helpers, lock/eject state.
- Cache/memory manager APIs: `CcIsFileCached`, `CcSetFileSizes`, `CcFlushCache`, `CcPurgeCacheSection`, `MmFlushImageSection`, `MmCanFileBeTruncated`.
- Notification helpers from `env_spec.h`: `UDFNotifyFullReportChange`, `UDFNotifyVolumeEvent`.

## Notable Risks and Edge Cases

- The routine is long and stateful; many early exits depend on correct `TreeLength`, `LastGoodFileInfo`, and resource pointer maintenance.
- Stream creation has multi-phase partial state and complex cleanup paths; failed stream directory or stream entry creation can leave metadata to flush/unlink.
- Duplicate-handle/reopen handling simulates normal traversal by backing up to the parent, which depends on parent references and FCB links being valid.
- Some fields and comments preserve historical NT behavior, including allowing create of readonly files with write access before later denial.
- Several paths are conditionally compiled around `UDF_READ_ONLY_BUILD` and `IFS_40`, so write behavior can differ materially by build.
- Volume locking and flush behavior relies on open/share counts and delayed close cleanup; incorrect counts can affect dismount/lock correctness.

## Testing Signals

Useful tests would cover volume/root opens, relative opens, duplicate-handle opens, file-id opens, case-sensitive opens, create/open/open-if dispositions, delete-on-close, readonly media and readonly-file denial, stream creation/open, target-directory opens for rename, noncached opens with existing cache sections, mapped-file overwrite denial, and unwind after injected failures in `UDFCreateFile__`, `UDFFirstOpenFile`, and `UDFSetAccessRights`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/create.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/devcntrl.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/devcntrl.cpp

## Purpose

`devcntrl.cpp` implements the UDFS `IRP_MJ_DEVICE_CONTROL` dispatch path. It accepts private UDF IOCTLs, selected storage/CD/DVD/CDRW IOCTLs, volume-control requests, and file allocation-mode requests, and forwards unsupported/default requests to the lower storage device.

## Main Entry Points

- `UDFDeviceControl(PDEVICE_OBJECT, PIRP)`: top-level device-control dispatch wrapper. It enters filesystem context, allocates an IRP context, calls `UDFCommonDeviceControl`, and routes exceptions through the standard UDF exception handler.
- `UDFCommonDeviceControl(PtrUDFIrpContext, PIRP)`: central IOCTL dispatcher. It validates the target object, classifies IOCTL safety, handles local IOCTLs, forwards default IOCTLs to `Vcb->TargetDeviceObject`, and completes or passes through the IRP.
- `UDFDevIoctlCompletion(PDEVICE_OBJECT, PIRP, VOID*)`: completion routine retained for an older forwarding path. It marks pending IRPs and releases the IRP context.
- `UDFGetFileAllocModeFromICB(PtrUDFIrpContext, PIRP)`: returns the file's current ICB allocation mode.
- `UDFSetFileAllocModeFromICB(PtrUDFIrpContext, PIRP)`: flushes the file and converts away from in-ICB allocation mode when allowed.

## IOCTL Target Validation

The dispatcher distinguishes filesystem device object requests from volume/file requests:

- Filesystem device object requests are limited to private control operations such as disabling the driver, invalidating volumes, registering a mount notification event, sending a license key in write builds, and registering autoformat.
- Volume opens accept broad IOCTL handling because the FCB node is the VCB.
- Regular file/directory opens are limited to retrieval pointers and file allocation mode IOCTLs.

The code derives `Fcb`, `Ccb`, and `Vcb` from the file object when possible. Most VCB operations acquire `Vcb->VCBResource` shared; `IOCTL_CDROM_DISK_TYPE` uses exclusive acquisition because it verifies volume/media state.

## Safe Versus Unsafe IOCTLs

`UnsafeIoctl` defaults to true and is cleared for read-only, query, geometry, verify, media-type, audio, CDRW query, UDF query, and dirty-status operations. Before forwarding an unsafe IOCTL, the driver flushes the logical volume with `UDFFlushLogicalVolume`; after handling/defaulting it marks `UDF_VCB_FLAGS_UNSAFE_IOCTL`.

Direct SCSI pass-through is inspected at the CDB level. Write, format, blank, close-track/session, reserve-track, cue-sheet, DVD-structure send, streaming, and write-parameter mode-select commands are treated as direct media modification. If the volume is mounted, the driver closes delayed/system handles, runs `UDFDoDismountSequence`, clears mounted/write-security state, stops the eject waiter, decrements the serial number to defeat quick remount, and then forwards the IOCTL.

## Locally Handled IOCTLs

Important local cases include:

- `IOCTL_UDF_REGISTER_AUTOFORMAT`: stores a single file-object owner in `UDFGlobalData.AutoFormatCount` or returns sharing violation.
- `IOCTL_UDF_DISABLE_DRIVER`: unregisters and deletes the UDF filesystem device object, destroys zones, and tears down global resources.
- `IOCTL_UDF_INVALIDATE_VOLUMES`: releases VCB resource if held and delegates to `UDFInvalidateVolumes`.
- `IOCTL_UDF_SET_NOTIFICATION_EVENT`: references or dereferences a user-provided event handle in `UDFGlobalData.MountEvent`.
- `IOCTL_UDF_IS_VOLUME_JUST_MOUNTED`: returns and clears `Vcb->IsVolumeJustMounted`.
- `IOCTL_UDF_GET_RETRIEVAL_POINTERS` and `IOCTL_UDF_GET_SPEC_RETRIEVAL_POINTERS`: delegate to `UDFGetRetrievalPointers`.
- `IOCTL_UDF_GET_FILE_ALLOCATION_MODE`: delegates to `UDFGetFileAllocModeFromICB`.
- `IOCTL_UDF_SET_FILE_ALLOCATION_MODE`: delegates to `UDFSetFileAllocModeFromICB` in write builds.
- `IOCTL_UDF_LOCK_VOLUME_BY_PID` and `IOCTL_UDF_UNLOCK_VOLUME_BY_PID`: delegate to lock/unlock helpers with the current PID.
- `IOCTL_UDF_GET_VERSION`: fills `UDF_GET_VERSION_OUT` with driver build fields, UDF revision, user FS flags, readonly/raw/media/driver flags, compatibility flags, and config version.
- `IOCTL_UDF_SET_OPTIONS`: accepts temporary config bytes, updates registry-derived VCB options, increments config version, and toggles verify-on-write infrastructure.
- `FSCTL_ALLOW_EXTENDED_DASD_IO`: no-op success.
- `FSCTL_IS_VOLUME_DIRTY`: delegates to `UDFIsVolumeDirty`.
- Eject/media-removal/door-lock controls: either notify an eject waiter, maintain `MediaLockCount`, or forward while normalizing local lock state.
- `IOCTL_CDROM_DISK_TYPE`: verifies media, checks output size, reports data track, and sets audio-track bit if track metadata indicates audio.

## Forwarding Behavior

Default handling calls `IoSkipCurrentIrpStackLocation` and `IoCallDriver(Vcb->TargetDeviceObject, Irp)`. When the IRP is forwarded without local completion, the IRP context is released immediately because no completion routine is currently installed. Local completions set `Irp->IoStatus.Status`, leave or set `Information`, complete the IRP, and release the context in the `finally` block.

## File Allocation Mode Helpers

`UDFGetFileAllocModeFromICB` validates the output buffer, returns `UDFGetFileICBAllocMode__(Fcb->FileInfo)`, and sets `IoStatus.Information`.

`UDFSetFileAllocModeFromICB` validates the input buffer, flushes the file via `UDFFlushAFile`, and refuses conversion to `ICB_FLAG_AD_IN_ICB`. If the current mode is in-ICB and the requested mode is another allocation mode, it calls `UDFConvertFEToNonInICB`; otherwise it permits only no-op mode matches. A notable defect is visible: the function computes `RC` but returns `STATUS_SUCCESS` unconditionally at the end.

## Integration Points

This file is connected to storage/media management code in `fscntrl.cpp`, `verfysup.cpp`, `phys_eject.cpp`, and `Include/phys_lib.cpp` through shared IOCTL helpers and VCB state. It also interacts with user-visible UDF private structures such as `UDF_GET_VERSION_OUT`, `UDF_SET_OPTIONS_IN`, `UDF_GET_FILE_ALLOCATION_MODE_OUT`, and `UDF_SET_FILE_ALLOCATION_MODE_IN`.

## Notable Risks and Edge Cases

- Pass-through CDB inspection assumes the system buffer and CDB data offsets are valid for the expected SCSI structures.
- Unsafe IOCTLs can cause dismount-like local state changes before being forwarded to lower drivers.
- `IOCTL_UDF_DISABLE_DRIVER` tears down global driver state from an IOCTL path; concurrency assumptions are important.
- Event-handle registration allows only one global mount event and relies on user-mode handle referencing/dereferencing correctness.
- The unconditional success return in `UDFSetFileAllocModeFromICB` can hide conversion or flush errors from callers.
- Some private IOCTLs are accepted on the filesystem device object while others require mounted volume context; misuse returns `STATUS_INVALID_PARAMETER`.

## Testing Signals

Useful tests include FS-device IOCTL filtering, file-handle IOCTL rejection, volume-handle version/options queries, safe versus unsafe forwarding, pass-through write CDB media invalidation, eject waiter behavior, media-lock count transitions, output-buffer length validation, and allocation-mode conversion error propagation.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/devcntrl.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/dircntrl.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/dircntrl.cpp

## Purpose

`dircntrl.cpp` implements UDFS directory-control handling for `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`. It formats directory entries into NT query-directory information classes, maintains per-CCB enumeration state, supports wildcard/case-insensitive matching, and queues directory change notifications.

## Main Entry Points

- `UDFDirControl(PDEVICE_OBJECT, PIRP)`: top-level `IRP_MJ_DIRECTORY_CONTROL` dispatch wrapper. It creates an IRP context, calls `UDFCommonDirControl`, handles exceptions, and restores top-level IRP state.
- `UDFCommonDirControl(PtrUDFIrpContext, PIRP)`: validates file-object context, acquires the VCB shared, and dispatches to query-directory or notify-change handling by minor function.
- `UDFQueryDirectory(...)`: implements directory enumeration and output-buffer formatting.
- `UDFFindNextMatch(...)`: scans a UDF directory index for the next undeleted, non-internal entry matching a pattern/hash.
- `UDFNotifyChangeDirectory(...)`: queues or completes directory-change notification requests using FsRtl notify support.

## Query Directory Flow

`UDFQueryDirectory` validates that the target FCB is a directory and not a VCB, determines whether it can block, and posts the request if not. It derives the VCB, NT-required FCB, CCB, directory `UDF_FILE_INFO`, requested buffer length, requested information class, and caller search flags.

Supported information classes are:

- `FileDirectoryInformation`
- `FileFullDirectoryInformation`
- `FileNamesInformation`
- `FileBothDirectoryInformation`

The routine computes the fixed base length for the requested class, acquires the FCB main resource shared, maps either the MDL or user buffer, normalizes a trailing NUL in the search pattern, and chooses the active enumeration pattern.

## Search Pattern and Enumeration State

Each directory handle stores search state in its CCB:

- `DirectorySearchPattern` stores the first or overridden non-match-all pattern.
- `CurrentIndex` stores the last returned directory index.
- `UDF_CCB_MATCH_ALL`, `UDF_CCB_WILDCARD_PRESENT`, and `UDF_CCB_CAN_BE_8_DOT_3` describe how matching should work.
- `hashes` caches UDF name hashes for non-wildcard patterns.

The code supports:

- `SL_INDEX_SPECIFIED`: start from `FileIndex + 1`, ignore the pattern, and match all.
- `SL_RESTART_SCAN`: restart at index 0.
- Continued scans: start at `Ccb->CurrentIndex + 1`.
- Case-insensitive opens: upcase the supplied pattern and set the ignore-case flag unless the CCB marks a case-sensitive open.

## Directory Matching

`UDFFindNextMatch` iterates through `UDFDirIndex(hDirIndex, EntryNumber)`, skips entries without names, deleted entries, and internal file-info entries, optionally prefilters by long/POSIX/DOS hash, then calls `UDFIsNameInExpression`. Matching flags indicate whether the pattern can be 8.3, whether matching ignores case, and whether it contains wildcards. Entries 0 and 1 are treated specially through the final `EntryNumber < 2` argument, consistent with dot/dotdot behavior.

## Output Buffer Formatting

For each match, `UDFFileDirInfoToNT` creates a temporary `FILE_BOTH_DIR_INFORMATION` representation. The routine copies the fixed base fields needed by the requested information class into the caller buffer, copies the Unicode file name bytes, sets `FileIndex`, `FileNameLength`, `NextEntryOffset`, and tracks `IoStatus.Information`.

If the next entry cannot fit:

- after at least one successful entry, it returns `STATUS_SUCCESS`;
- for the first entry, it returns `STATUS_BUFFER_OVERFLOW` and truncates the filename length to the available space policy used here;
- it decrements `NextMatch` so the oversized entry is not lost on the next call.

When no more matches are found, it returns `STATUS_SUCCESS` if at least one entry was returned, `STATUS_NO_SUCH_FILE` for an empty first query, or `STATUS_NO_MORE_FILES` for later continuation queries.

## Notify Change Flow

`UDFNotifyChangeDirectory` validates that the target is a directory, acquires the FCB main resource shared or posts if it cannot wait, rejects delete-pending directories, extracts the completion filter and tree-watch flag, and calls `FsRtlNotifyFullChangeDirectory` with the VCB notify mutex/list, CCB context, directory name, watch-tree flag, completion filter, and IRP. Successful notify setup returns `STATUS_PENDING` and releases the IRP context without completing the IRP.

## Integration Points

The file depends on:

- UDF directory indexes through `UDFDirIndex`, `PDIR_INDEX_HDR`, and `PDIR_INDEX_ITEM`.
- Name helpers: `UDFIsMatchAllMask`, `FsRtlDoesNameContainWildCards`, `UDFBuildHashEntry`, `UDFCanNameBeA8dot3`, `UDFIsNameInExpression`.
- NT output conversion: `UDFFileDirInfoToNT`.
- FCB/CCB fields initialized by create/open paths.
- FsRtl notification APIs and `UDFNotifyFullReportChange` calls elsewhere that wake queued notifications.

## Notable Risks and Edge Cases

- Search state is stored per CCB, so callers that change masks mid-enumeration reset/replace CCB state.
- The function writes `NextEntryOffset` by storing a `ULONG` at `Buffer + LastOffset`; the first entry writes zero initially and previous entries are patched on later iterations.
- Buffer-overflow handling intentionally rewinds `NextMatch`, but truncating `FileNameBytes` on the first oversized entry may produce partial-name semantics that consumers must tolerate.
- Directory validation depends on both FCB flags and `UDFIsADirectory(DirFileInfo)`.
- Posting nonblocking requests requires locking the caller buffer before worker-thread processing.

## Testing Signals

Useful tests include match-all enumeration, wildcard masks, exact masks with hash prefiltering, case-sensitive versus case-insensitive opens, 8.3-compatible masks, restart scans, index-specified scans, single-entry queries, each supported information class, small output buffers, no-match first/later queries, deleted/internal entry skipping, and notify requests on valid, invalid, and delete-pending directories.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/dircntrl.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/dldetect.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/dldetect.cpp

## Purpose

`dldetect.cpp` implements a debug deadlock detector for UDFS ERESOURCE acquisition. It wraps resource acquisition paths, records which thread is waiting for which resource, walks owner/waiter chains after repeated wait timeouts, and breaks into debug code when a cycle appears likely.

## Main Data

- `MaxThreadCount`: maximum number of tracked thread slots, supplied by `DLDInit`.
- `DLDThreadTable`: fixed array of `THREAD_STRUCT` entries mapping thread IDs to currently awaited resources plus source bug-check id/line.
- `DLDpTimeout`: four-second relative wait timeout used for periodic deadlock checks.
- `DLDpResourceTimeoutCount`: number of timed-out waits before graph inspection; initialized to `0x2`.
- `DLDThreadAcquireChain[DLD_MAX_REC_LEVEL]`: recursion trace for reported acquisition chains.

The detector is explicitly written for uniprocessor assumptions; `DLDInit` prints and breaks if `KeNumberProcessors > 1`.

## Initialization and Tracking

`DLDInit(ULONG MaxThrdCount)` initializes the timeout, stores the maximum table size, allocates `DLDThreadTable` from nonpaged pool, and zeros it.

`DLDFree()` frees the thread table.

`DLDAllocFindThread(ULONG ThreadId)` finds an existing table entry or reuses the first empty entry. If the table is full it prints a diagnostic and calls `BrutePoint`.

`DLDFindThread(ULONG ThreadId)` returns an existing tracked thread entry or `NULL`.

## Deadlock Detection Algorithm

`DLDpWaitForResource` waits on the resource's exclusive event or shared semaphore in four-second intervals. On each timeout, it increments a local wait counter. After the threshold, it calls `DLDProcessResource` while holding the resource spin lock.

`DLDProcessResource` inspects the supplied `ERESOURCE`:

- If the resource is not active, it returns no deadlock.
- If it is exclusively owned, or has a single shared owner in `OwnerThreads[1]`, it finds that owner thread and calls `DLDProcessThread`.
- If it has many owners, it iterates `OwnerTable` and processes every tracked owner.

`DLDProcessThread` checks whether the owner is the original waiter or appears in the current acquisition chain. If so, it prints a cycle diagnostic with bug-check id and source line data. Otherwise, if the owner thread is itself waiting on another resource, it recursively processes that resource.

The recursion limit is `DLD_MAX_REC_LEVEL` (40).

## Resource Acquisition Wrappers

`DLDAcquireExclusive(PERESOURCE, ULONG BugCheckId, ULONG Line)` manually acquires `Resource->SpinLock`, handles free resources, recursive exclusive acquisition by the same thread, and otherwise delegates to `DLDpAcquireResourceExclusiveLite`.

`DLDpAcquireResourceExclusiveLite(...)` allocates the `ExclusiveWaiters` event if needed, increments exclusive waiters, records the current thread's waiting resource and source location, releases the spin lock while waiting, then clears the waiting record and marks exclusive ownership after the wait returns.

`DLDAcquireShared(PERESOURCE, ULONG BugCheckId, ULONG Line, BOOLEAN WaitForExclusive)` manually handles free resources, recursive exclusive owner cases, shared owner table lookup/allocation, shared acquisition when no exclusive waiters are present, and waiting on `SharedWaiters` when necessary.

`DLDpFindCurrentThread(PERESOURCE, ERESOURCE_THREAD)` finds or allocates an owner entry for a thread in `OwnerThreads[0]`, `OwnerThreads[1]`, or the dynamically allocated `OwnerTable`. It can grow the owner table by allocating a new tagged table and copying old entries.

## Integration Points

`udfinit.cpp` initializes and frees the detector under debug/deadlock-detection configuration. `udf_dbg.cpp` routes debug resource acquisition wrappers to `DLDAcquireShared` and `DLDAcquireExclusive`. The public prototypes and helper structs are in `dldetect.h`.

## Notable Risks and Edge Cases

- This code directly reads and writes internal `ERESOURCE` fields and even writes to a hard-coded offset in the current thread object (`CurrentThread + 0x136`). That is highly version-specific and fragile outside the intended NT/ReactOS layout.
- The source only defines `DLDAcquireExclusive` and `DLDAcquireShared`; `dldetect.h` also declares `DLDAcquireSharedStarveExclusive` and `DLDUnblock`, which are not implemented in this file.
- The detector is explicitly not multiprocessor-safe by design, even though it uses spin locks around resource structures.
- Some diagnostic loop output in `DLDProcessThread` indexes `DLDThreadAcquireChain[i]` inside a loop over `j`, which appears suspicious for producing repeated or incorrect diagnostic rows.
- If allocation of waiter events/semaphores or owner tables fails, the code does not consistently propagate errors because the wrappers have `VOID` signatures.

## Testing Signals

Useful debug tests would deliberately create two-thread resource cycles, recursive exclusive acquisition, shared acquisition with and without exclusive waiters, owner-table growth beyond the two inline owner slots, timeout-only nondeadlock waits, and table-full conditions. Any modern port should also validate assumptions about `ERESOURCE` and thread-object layout.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/dldetect.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/dldetect.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/dldetect.h

## Purpose

`dldetect.h` declares the UDFS deadlock detector API and the small tracking structures used by `dldetect.cpp`. It is intended for NT kernel-mode debug/resource-acquisition instrumentation.

## Public API

- `DLDInit(ULONG MaxThrdCount)`: initialize the detector with a maximum number of tracked threads.
- `DLDAcquireExclusive(PERESOURCE Resource, ULONG BugCheckId, ULONG Line)`: acquire an ERESOURCE exclusively with deadlock tracking.
- `DLDAcquireShared(PERESOURCE Resource, ULONG BugCheckId, ULONG Line, BOOLEAN WaitForExclusive)`: acquire shared with deadlock tracking.
- `DLDAcquireSharedStarveExclusive(PERESOURCE Resource, ULONG BugCheckId, ULONG Line)`: declared but not implemented in the paired source file.
- `DLDUnblock(PERESOURCE Resource)`: declared but not implemented in the paired source file.
- `DLDFree()`: free detector state.

## Macros and Constants

- `DLDAllocatePool(size)` and `DLDFreePool(addr)` wrap UDFS pool allocation helpers using nonpaged pool.
- `DLDGetCurrentResourceThread()` casts `PsGetCurrentThread()` to `ERESOURCE_THREAD`.
- `ResourceOwnedExclusive` is defined as `0x80` if absent.
- `ResourceDisableBoost` is defined as `0x08`.

## Structures

- `THREAD_STRUCT`: stores a tracked thread id, the resource it is currently waiting on, and the bug-check id/source line for the acquisition point.
- `THREAD_REC_BLOCK`: stores a thread plus the resource it holds while reporting or walking a wait chain.

## Integration Points

The declarations are consumed by debug wrappers in `udf_dbg.cpp` and initialization in `udfinit.cpp`. The detector source depends on these structures and macros exactly.

## Notable Risks

The header exposes APIs that model old `ERESOURCE` internals rather than opaque resource APIs. The two unimplemented declarations should be checked before enabling code paths that call them. The memory macros assume UDFS allocation helpers are available through `udffs.h` or prior includes.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/dldetect.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/env_spec.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/env_spec.cpp

## Purpose

`env_spec.cpp` provides NT-kernel environment-specific physical I/O helpers for UDFS. It builds lower-level read, write, and IOCTL IRPs against the target device, waits for completion, bridges completion status back to UDFS callers, implements optional debug/performance instrumentation, and supplies debug notification wrappers.

## Main Entry Points

- `UDFAsyncCompletionRoutine(PDEVICE_OBJECT, PIRP, PVOID)`: completion routine for asynchronous read/write IRPs built at elevated IRQL. It copies I/O status, unlocks and frees MDLs, frees the IRP, signals the context event, and returns `STATUS_MORE_PROCESSING_REQUIRED`.
- `UDFSyncCompletionRoutine(PDEVICE_OBJECT, PIRP, PVOID)`: completion routine that copies I/O status into the context and returns success. It is currently not active in the IOCTL path.
- `UDFPhReadSynchronous(PDEVICE_OBJECT, PVOID, SIZE_T, LONGLONG, PSIZE_T, ULONG)`: reads bytes from the physical target device, using synchronous or asynchronous FSD request construction depending on current IRQL.
- `UDFPhWriteSynchronous(PDEVICE_OBJECT, PVOID, SIZE_T, LONGLONG, PSIZE_T, ULONG)`: writes bytes to the physical target device, using synchronous or asynchronous FSD request construction depending on current IRQL.
- `UDFTSendIOCTL(ULONG, PVCB, PVOID, ULONG, PVOID, ULONG, BOOLEAN, PIO_STATUS_BLOCK)`: serializes a target-device IOCTL through `Vcb->IoResource` and delegates to `UDFPhSendIOCTL`.
- `UDFPhSendIOCTL(ULONG, PDEVICE_OBJECT, PVOID, ULONG, PVOID, ULONG, BOOLEAN, PIO_STATUS_BLOCK)`: builds and sends a device IOCTL request to a physical device and waits for completion if pending.
- `UDFNotifyFullReportChange(...)` and `UDFNotifyVolumeEvent(...)`: debug-build notification wrappers; non-debug builds use inline/macro definitions from `env_spec.h`.

## Physical Read Behavior

`UDFPhReadSynchronous` sets `*ReadBytes` to zero, optionally uses the caller buffer directly when `PH_TMP_BUFFER` is set, otherwise allocates a nonpaged temporary buffer. It allocates a `UDF_PH_CALL_CONTEXT`, initializes a notification event, builds either an asynchronous or synchronous `IRP_MJ_READ` request, sets `SL_OVERRIDE_VERIFY_VOLUME`, calls the lower driver, and waits when the status is `STATUS_PENDING`.

On success, it copies the completed byte count from the context status block, copies temporary-buffer contents back to the caller buffer when used, optionally mirrors reads into `UDFVRead` for browse/debug builds, records performance counters when enabled, frees context and temporary buffer, and returns normalized status. `STATUS_DATA_OVERRUN` is treated as success after completion.

## Physical Write Behavior

`UDFPhWriteSynchronous` is analogous to read but sends `IRP_MJ_WRITE`. In debug builds, `UDF_SIMULATE_WRITES` can short-circuit writes by pretending all bytes were written. The current active implementation writes directly from the caller buffer rather than copying to a temporary buffer. It sets `SL_OVERRIDE_VERIFY_VOLUME`, waits for pending completion, updates `*WrittenBytes`, optionally mirrors writes into `UDFVWrite`, records performance counters, and logs write failures.

`UDFPhWriteVerifySynchronous` exists only inside `#if 0`; the public header maps write-verify to ordinary write.

## IOCTL Behavior

`UDFTSendIOCTL` acquires `Vcb->IoResource` exclusively with a check helper, then calls `UDFPhSendIOCTL` against `Vcb->TargetDeviceObject`, releasing the resource in `finally`.

`UDFPhSendIOCTL` allocates a context, initializes an event, builds an IOCTL IRP with `IoBuildDeviceIoControlRequest`, optionally sets `SL_OVERRIDE_VERIFY_VOLUME`, calls the driver, waits for pending completion, normalizes `STATUS_DATA_OVERRUN` to success, copies the completion IOSB to the optional caller-supplied IOSB, frees context, and returns the final status. If waiting above passive level, it uses a short timeout that doubles until completion.

## Notification Helpers

In debug builds, `UDFNotifyFullReportChange` wraps `FsRtlNotifyFullReportChange`, computing the parent prefix length differently for root versus non-root objects. `UDFNotifyVolumeEvent` is stubbed to return because the ReactOS FIXME indicates `FsRtlNotifyVolumeEvent` is effectively unavailable or intentionally disabled.

## Instrumentation

`MEASURE_IO_PERFORMANCE` enables global counters for read time, write time, written data, and relative write time, with `PerfPrint` timing output. Debug builds expose `UDF_SIMULATE_WRITES`.

## Integration Points

These helpers are used broadly by physical/media code under `Include/phys_lib.cpp`, format support, verify support, eject handling, close/reset paths, and filesystem control paths. They are declared by `env_spec.h`, while a Win32 user-mode analogue exists under `Include/env_spec_w32.cpp`.

## Notable Risks and Edge Cases

- The functions wait for I/O even when they may be called above passive level; read/write use asynchronous FSD requests at elevated IRQL, while IOCTL waits assert below dispatch level and uses timeout polling above passive.
- `UDFAsyncCompletionRoutine` frees the IRP and MDLs itself and returns `STATUS_MORE_PROCESSING_REQUIRED`; callers must not touch the IRP afterward.
- Read uses a temporary buffer unless `PH_TMP_BUFFER` is set, while write currently writes directly from caller memory; buffer lifetime and nonpaged residency matter.
- `IoBuildSynchronousFsdRequest` usually signals the event itself; the sync completion routine is mostly unused/commented.
- `UDFPhSendIOCTL` does not install a completion routine in the active path, relying on the built IOCTL request event and IO status block.
- Optional `_BROWSE_UDF_` behavior overloads the byte-count pointer as a VCB carrier when `PH_VCB_IN_RETLEN` is set.

## Testing Signals

Useful tests would mock lower-device completion for immediate success, pending success, `STATUS_DATA_OVERRUN`, failure, missing IRP allocation, temporary read-buffer copyback, simulated writes, override-verify flag propagation, serialized `UDFTSendIOCTL`, and elevated-IRQL asynchronous read/write completion cleanup.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/env_spec.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/env_spec.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/env_spec.h

## Purpose

`env_spec.h` declares NT-kernel environment-specific UDFS helper APIs and macros for physical I/O, lower-device IOCTLs, notifications, statistics, thread/PID lookup, and completion routines.

## Declared I/O APIs

- `UDFPhReadSynchronous(...)`: physical-device read helper.
- `UDFPhWriteSynchronous(...)`: physical-device write helper.
- `UDFPhWriteVerifySynchronous`: defined as an alias to `UDFPhWriteSynchronous`; the real verify implementation is disabled in the `.cpp`.
- `UDFTSendIOCTL(...)`: VCB-target IOCTL helper that serializes through VCB I/O resource.
- `UDFPhSendIOCTL(...)`: physical-device IOCTL helper.

Commented-out declarations for asynchronous/background writes remain present but inactive.

## Notification APIs and Macros

Under `UDF_DBG`, the header declares debug implementations of:

- `UDFNotifyFullReportChange(PVCB, PUDF_FILE_INFO, ULONG, ULONG)`
- `UDFNotifyVolumeEvent(PFILE_OBJECT, ULONG)`

Outside debug builds, `UDFNotifyFullReportChange` is an inline wrapper around `FsRtlNotifyFullReportChange` using the file's FCB object name and a parent-prefix length when present. `UDFNotifyVolumeEvent` is a no-op macro with the underlying FsRtl call commented out.

## Statistics Macros

The header defines per-processor statistics increment helpers:

- `CollectStatistics(VCB, Field)`: increments `Statistics[processor].Common.Field`.
- `CollectStatisticsEx(VCB, Field, a)`: adds to `Statistics[processor].Common.Field`.
- `CollectStatistics2(VCB, Field)`: increments `Statistics[processor].Fat.Field`.
- `CollectStatistics2Ex(VCB, Field, a)`: adds to `Statistics[processor].Fat.Field`.

These macros rely on `KeGetCurrentProcessorNumber()` and field-token concatenation.

## Completion and Environment Helpers

Declared completion routines:

- `UDFAsyncCompletionRoutine`
- `UDFSyncCompletionRoutine`
- `UDFSyncCompletionRoutine2`

Small environment macros:

- `UDFGetDevType(DevObj)`: returns `DeviceType`.
- `OSGetCurrentThread()`: maps to `PsGetCurrentThread()`.
- `GetCurrentPID()`: maps to `HandleToUlong(PsGetCurrentProcessId())`.

## Integration Points

This header is included through `udffs.h` into core UDFS dispatch and media code. `create.cpp`, `read.cpp`, `write.cpp`, `fileinfo.cpp`, `cleanup.cpp`, and security support use notification/statistics helpers. Physical read/write/IOCTL helpers are used by verification, mount, formatting, eject, and low-level physical library code.

## Notable Risks

- The notification inline casts `UNICODE_STRING` pointers to `PSTRING`, matching FsRtl's byte-string convention but requiring correct lengths.
- The statistics macros use token-pasting syntax in a macro body; portability depends on the compiler accepting this historical style.
- `UDFNotifyVolumeEvent` is effectively disabled in non-debug builds.
- `GetCurrentPID()` returns a 32-bit `ULONG` handle value, which matches the surrounding lock-owner code but truncates in environments where process IDs are wider.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/env_spec.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/errmsg.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/errmsg.h

## Purpose

`errmsg.h` defines event-log message constants for the UDFS driver. It is generated or kept in message-compiler style from an `errmsg.msg` source, with comments documenting NTSTATUS bit layout and severity values.

## Contents

The file defines severity constants:

- `STATUS_SEVERITY_WARNING`
- `STATUS_SEVERITY_SUCCESS`
- `STATUS_SEVERITY_INFORMATIONAL`
- `STATUS_SEVERITY_ERROR`

It defines one UDFS event id:

- `UDF_ERROR_INTERNAL_ERROR ((ULONG)0xE004A001L)`: message text indicates the UDF FSD encountered an internal error and log data should be checked.

## Integration Points

Dispatch wrappers such as `UDFCreate`, `UDFDeviceControl`, and `UDFDirControl` call `UDFLogEvent(UDF_ERROR_INTERNAL_ERROR, RC)` from exception handlers. This constant is the common event-code hook used when unexpected kernel exceptions are caught.

## Notable Risks

The comments instruct message IDs to begin at `0xA000` for UDFS errors and avoid `%1` insertion strings. Only one message constant is present, so any more specific event reporting must be defined elsewhere or added to this message set.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/errmsg.h -->