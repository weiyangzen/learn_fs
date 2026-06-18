# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSGeneric.cpp lines 8316-10150

## Purpose

This chunk contains Windows kernel redirector utility paths for object status lookup, directory-name validation, default security descriptor setup, authentication-group recovery, object invalidation, reparse policy, target-file metadata probing, and share-name detection.

The largest behavioral surfaces are:

- `AFSGetObjectStatus`, which resolves an object either by AFS FID or by `\afs`-rooted name and copies cached object metadata to an `AFSStatusInfoCB`.
- `AFSCreateDefaultSecurityDescriptor`, which builds the driver's process-wide default self-relative security descriptor.
- `AFSRetrieveValidAuthGroup`, which chooses a usable PAG/authentication GUID from open CCBs or from the current process/thread.
- `AFSPerformObjectInvalidate`, which reacts to delete and data-version invalidations by tearing down extents, purging cache sections, and setting verification/purge flags.

Smaller helpers support failed symlink access reporting, final/parent component parsing, filename character validation, reparse-point policy checks, file-info reads for reparse targets, and share-name parsing.

## Important APIs, Types, And Functions

- `AFSGetObjectStatus(AFSGetStatusInfoCB*, ULONG, AFSStatusInfoCB*, ULONG*)` maps either `GetStatusInfo->FileID` or `GetStatusInfo->FileName` to an `AFSObjectInfoCB`, then returns file id, target id, expiration, data version, type, flags, times, attributes, EOF, allocation, EA size, and link count.
- `AFSCheckSymlinkAccess(AFSDirectoryCB*, UNICODE_STRING*)` looks up a child name in case-sensitive, case-insensitive, and optional short-name indexes, then returns `STATUS_REPARSE_POINT_NOT_RESOLVED` for the unresolved symlink object.
- `AFSRetrieveFinalComponent` and `AFSRetrieveParentPath` are `UNICODE_STRING` slicing helpers based on `FsRtlDissectName` or backward slash scanning; they return views into the original buffer, not allocated copies.
- `AFSValidNameFormat` rejects `:`, `*`, `?`, `"`, `<`, and `>` in a file name.
- `AFSCreateDefaultSecurityDescriptor` allocates a World SID, optional low-integrity mandatory-label SACL, absolute security descriptor, then converts it to a page-sized self-relative descriptor stored in global `AFSDefaultSD`.
- `AFSRetrieveValidAuthGroup(AFSFcb*, AFSObjectInfoCB*, BOOLEAN, GUID*)` scans open `AFSCcb` entries for write or read access and falls back to `AFSRetrieveAuthGroupFnc(PID,TID,...)`.
- `AFSPerformObjectInvalidate(AFSObjectInfoCB*, ULONG)` handles `AFS_INVALIDATE_DELETED` and `AFS_INVALIDATE_DATA_VERSION`.
- `AFSIgnoreReparsePointToFile` reads `pDeviceExt->Specific.RDR.ReparsePointPolicy`.
- `AFSRetrieveTargetFileInfo` opens a kernel-handle target with `ZwCreateFile(FILE_READ_ATTRIBUTES)` and fills `AFSFileInfoCB` from `FILE_NETWORK_OPEN_INFORMATION`.
- `AFSIsShareName` returns true only for a path of the form `\Share` with no later slash.

Core structures and state touched here include `AFSDeviceExt`, `AFSVolumeCB`, `AFSObjectInfoCB`, `AFSDirectoryCB`, `AFSFcb`, `AFSCcb`, `AFSNameArrayHdr`, `AFSExtent`, `AFSByteRange`, global `AFSRDRDeviceObject`, `AFSGlobalRoot`, `AFSServerName`, and `AFSDefaultSD`.

## Control Flow

`AFSGetObjectStatus` has two resolution paths. When all FID fields are nonzero, it takes `VolumeTreeLock`, locates the volume by `AFSCreateHighIndex`, increments the volume with `AFS_VOLUME_REFERENCE_GET_OBJECT`, and either uses the volume object's embedded `ObjectInformation` for a volume FID or locates a child object by `AFSCreateLowIndex` in the volume `ObjectInfoTree`. Non-volume FID lookup takes the object-tree lock exclusive, increments `AFS_OBJECT_REFERENCE_STATUS`, and updates `LastAccessCount`.

When no full FID is supplied, `AFSGetObjectStatus` validates the variable input buffer, requires the first path component to match `AFSServerName`, initializes a name array from `AFSGlobalRoot`, references the root volume and directory entry, and calls `AFSLocateNameEntry` with mount-point and symlink target evaluation disabled. It transfers any returned volume and parent-directory references, rejects reparse status, then references `pDirectoryEntry->ObjectInformation`. Both paths converge on copying cached `AFSObjectInfoCB` fields into the output. The cleanup block decrements directory-entry references, object references, volume references, and frees the name array.

`AFSCheckSymlinkAccess` searches the parent directory's case-sensitive tree first, then case-insensitive tree, then short-name tree when short names are enabled and the component is legal DOS 8.3. A case-insensitive match with an ambiguous list returns `STATUS_OBJECT_NAME_COLLISION`. A found entry is temporarily open-referenced and then immediately decremented before returning `STATUS_REPARSE_POINT_NOT_RESOLVED`.

`AFSCreateDefaultSecurityDescriptor` is an initialization-time builder. It creates a World SID, optionally creates a low mandatory-label ACE/SACL if `AFSRtlSetSaclSecurityDescriptor` is available, creates an absolute descriptor, installs the SACL, group, and owner, validates the descriptor, converts it to a self-relative descriptor, and publishes it as `AFSDefaultSD`. Temporary allocations are freed on exit; the self-relative descriptor is retained only on success.

`AFSRetrieveValidAuthGroup` first normalizes a missing `Fcb` through `ObjectInfo->Fcb`. It then scans the FCB CCB list under `CcbListLock`, preferring a CCB with `FILE_WRITE_DATA` for write access and otherwise accepting a `FILE_READ_DATA` CCB. If none is found, it calls the configured auth-group callback for the current process and thread. A zero GUID is treated as no PAG and returns `STATUS_ACCESS_DENIED`.

`AFSPerformObjectInvalidate` branches by invalidation reason. Deleted file invalidation marks pending extent requests `STATUS_FILE_DELETED`, signals `ExtentsRequestComplete`, tears down FCB extents when service I/O is not direct, and sets `ObjectInfo->Links` to zero. Data-version invalidation either purges the full cache section in direct-service-I/O mode, or in cached mode reasons over extent dirtiness: no clean extents means no purge; clean extents with no open references can be torn down; clean extents with open references purge the full file; dirty extents trigger clean-range construction and range purging. Fallback code walks extents while holding the extent lock if a clean byte-range list cannot be allocated. On failure or exceptions, it sets `AFS_FCB_FLAG_PURGE_ON_CLOSE` and/or `AFS_OBJECT_FLAGS_VERIFY_DATA`. The caller's invalidation reference is always dropped at the end via `AFS_OBJECT_REFERENCE_INVALIDATION`.

## State And Persistence Behavior

This chunk mostly manipulates in-memory redirector state; it does not write durable on-disk records itself.

- Status lookup temporarily pins volumes, directory entries, and object-info blocks, then releases them in a central cleanup path.
- Object status output is a snapshot of cached object metadata already stored in `AFSObjectInfoCB`.
- `AFSCreateDefaultSecurityDescriptor` publishes process-global `AFSDefaultSD`; ownership transfers to global driver lifetime after successful self-relative conversion.
- Auth-group retrieval observes active open CCBs and current process/thread PAG mapping but does not persist credentials.
- Invalidation changes cached runtime state: FCB extent lists, extent request status/event, cache-manager section state, `Links`, `AFS_FCB_FLAG_PURGE_ON_CLOSE`, and `AFS_OBJECT_FLAGS_VERIFY_DATA`.
- Target-file info retrieval reads metadata from another file object through NT I/O manager APIs and copies it into an AFS file-info structure.

Reference accounting is central. The code uses `AFSVolumeIncrement/Decrement`, `AFSObjectInfoIncrement/Decrement`, and `DirOpenReferenceCount` increments/decrements with trace logging and assertions. Locking is done with ERESOURCE wrappers such as `AFSAcquireShared`, `AFSAcquireExcl`, and `AFSReleaseResource`.

## Dependencies And Integration Points

- Device and global redirector state: `AFSRDRDeviceObject`, `AFSDeviceExt`, `AFSGlobalRoot`, `AFSServerName`, and redirector policy flags.
- Namespace lookup: `AFSLocateHashEntry`, `AFSCreateHighIndex`, `AFSCreateLowIndex`, `AFSIsVolumeFID`, `AFSInitNameArray`, `AFSLocateNameEntry`, and `AFSFreeNameArray`.
- Directory indexes: `AFSGenerateCRC`, `AFSLocateCaseSensitiveDirEntry`, `AFSLocateCaseInsensitiveDirEntry`, `AFSLocateShortNameDirEntry`, and case-insensitive collision list flags.
- Windows kernel runtime: `FsRtlDissectName`, `RtlCompareUnicodeString`, SID/ACL/security-descriptor routines, `ZwCreateFile`, `ZwQueryInformationFile`, `ZwClose`, `CcPurgeCacheSection`, `KeSetEvent`, `KeQueryTickCount`, `PsGetCurrentProcessId`, and `PsGetCurrentThreadId`.
- Cache and extent subsystem: `AFSTearDownFcbExtents`, `AFSConstructCleanByteRangeList`, `AFSReleaseCleanExtents`, extent list heads/counts, dirty flags, and FCB section-object resources.
- Authentication: `AFSRetrieveAuthGroupFnc` and open CCB `AuthGroup`/`GrantedAccess` fields.
- Worker/cleanup integration: call sites in cleanup and worker code invoke `AFSPerformObjectInvalidate`; device-control code invokes `AFSGetObjectStatus`; initialization invokes `AFSCreateDefaultSecurityDescriptor`; extent paths invoke `AFSRetrieveValidAuthGroup`.

## Risks And Edge Cases

- The requested line range begins inside `AFSGetObjectStatus`; the full function signature and first local declarations begin just above the chunk at line 8306.
- In name-based `AFSGetObjectStatus`, after `AFSLocateNameEntry` returns failure or `STATUS_REPARSE`, the code sets `pVolumeCB = NULL` before cleanup. This relies on `AFSLocateNameEntry` and its returned-reference contract to avoid leaking or double-releasing references.
- The cleanup path decrements both `pDirectoryEntry` and `pParentDirEntry`; callers changing `AFSLocateNameEntry` reference semantics must preserve these assumptions.
- `AFSRetrieveValidAuthGroup` assigns `pFcb` from `ObjectInfo->Fcb`, but uses `Fcb->NPFcb` and `Fcb->CcbListHead` inside the later `if (pFcb != NULL)` block. If this is not guarded elsewhere, calling with `Fcb == NULL` and `ObjectInfo->Fcb != NULL` appears vulnerable to null dereference.
- `AFSCheckSymlinkAccess` manually releases the directory tree lock before `try_return` on case-insensitive collision; this is correct only because the common cleanup does not also release that lock.
- The security descriptor builder uses fixed ACE slack and a page-sized self-relative buffer. Changes to descriptor contents must keep `ulSDLength` sizing and cleanup ownership correct.
- `AFSPerformObjectInvalidate` has complex lock ordering across FCB resource, section-object resource, and extents resource. The fallback path explicitly notes possible deadlock when it cannot allocate a byte-range list and must walk extents under the extent lock.
- Cache purge calls are wrapped in SEH, but many failure paths degrade to purge-on-close or verify-data flags; tests should check that stale clean data cannot be consumed after purge failures.
- `AFSConstructCleanByteRangeList` returns a list pointer that is advanced/mutated during purge processing; ownership and release behavior must be verified in the implementation of that helper.
- `AFSValidNameFormat` rejects only a subset of Windows-invalid characters and does not reject slash, backslash, control characters, or trailing-dot/space forms in this helper alone; callers must layer additional validation where required.

## Test Signals

Useful validation for this chunk includes:

- IOCTL/status tests for FID-based lookup of volume and non-volume objects, invalid FID rejection, name-based lookup under `\afs`, invalid server component rejection, and output field parity with cached `AFSObjectInfoCB`.
- Reference-count tracing around `AFSGetObjectStatus` success, invalid-parameter, allocation-failure, and reparse paths to catch leaked volume, object, directory-entry, or name-array references.
- Directory lookup tests for unresolved symlink components covering exact case, case-insensitive unique match, case-insensitive collision, short-name lookup enabled/disabled, and missing names.
- Name helper tests for final component and parent path with root, trailing slash, single-component, and multi-component `UNICODE_STRING` inputs.
- Security descriptor initialization tests checking success when optional `AFSRtlSetSaclSecurityDescriptor`/group callbacks exist or are absent, descriptor validity, self-relative output, and cleanup on allocation/API failures.
- Auth-group tests with write CCB, read-only CCB fallback, no CCB plus valid current PAG, no CCB plus zero GUID, and the `Fcb == NULL`/`ObjectInfo->Fcb != NULL` case.
- Invalidation tests for deleted files, direct-service-I/O data-version purge, cached data-version purge with no dirty extents, all dirty extents, mixed dirty/clean extents, no open references, open references, byte-range-list allocation failure, and `CcPurgeCacheSection` failure/exception paths.
- Reparse policy tests for `AFS_REPARSE_POINT_TO_FILE_AS_FILE`, target-file-info tests for open/query failure and metadata-copy success, and share-name tests for `\share` versus `\share\child`.
