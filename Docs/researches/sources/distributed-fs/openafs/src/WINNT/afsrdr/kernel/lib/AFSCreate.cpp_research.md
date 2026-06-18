# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSCreate.cpp

## Purpose

`AFSCreate.cpp` implements the Windows redirector library's `IRP_MJ_CREATE` handling. It is the central open/create path for the AFS redirector device, volume roots, ordinary files and directories, special pseudo-files such as `_._AFS_IOCTL_._`, and special share names. It converts a Windows create IRP into redirector object lookup, AFS service authorization, FCB/CCB construction, share-access registration, cache-manager setup, and persistent in-memory reference state.

## Important APIs, types, and functions

- `AFSCreate(PDEVICE_OBJECT, PIRP)` is the dispatch entry. It handles control-device opens when the file object or filename is missing, rejects use before `AFSRDRDeviceObject` is initialized, delegates real file-system opens to `AFSCommonCreate`, catches exceptions, and completes the IRP.
- `AFSCommonCreate(PDEVICE_OBJECT, PIRP)` is the main router. It retrieves `AFSDeviceExt`, create disposition/options, desired access, auth group, parses the pathname with `AFSParseName`, handles global-root opens, performs name lookup with `AFSLocateNameEntry`, and dispatches to root/open/create/overwrite/target-directory/special-file paths.
- `AFSOpenAFSRoot` and `AFSOpenRoot` open the synthetic AFS global root and a volume root. `AFSOpenRoot` validates/enumerates the root, calls `AFSProcessRequest(AFS_REQUEST_TYPE_OPEN_FILE)`, initializes the root FCB, checks share access, allocates a CCB, and marks the object held by the service.
- `AFSProcessCreate` creates a new child by calling `AFSCreateDirEntry`, evaluating the new node, initializing its FCB/CCB, reporting directory notifications, setting share access, updating parent child-open counts, and rolling back the directory entry on failure.
- `AFSOpenTargetDirectory` supports `SL_OPEN_TARGET_DIRECTORY` for rename-style operations. It opens the parent directory, rewrites `FileObject->FileName` to the target component, and reports whether the target exists.
- `AFSProcessOpen` opens an existing object. It validates the entry, handles pending delete and delete-on-close, checks image-section conflicts for write/delete opens, asks the service for granted access, validates that access with `AFSCheckAccess`, builds a CCB, updates share access and open counts, and records service-held state.
- `AFSProcessOverwriteSupersede` handles `FILE_OVERWRITE`, `FILE_OVERWRITE_IF`, and `FILE_SUPERSEDE`. It rejects read-only volumes/files, validates and initializes the FCB, checks truncation safety with `MmCanFileBeTruncated`, zeros sizes under paging I/O synchronization, trims extents, calls `AFSUpdateFileInformation`, updates attributes, and calls `CcSetFileSizes`.
- `AFSControlDeviceCreate` allows kernel-mode control-device opens and rejects user-mode direct opens.
- `AFSOpenIOCtlFcb` creates/opens the per-directory PIOCtl pseudo FCB and sends `AFS_REQUEST_TYPE_PIOCTL_OPEN` to the service.
- `AFSOpenSpecialShareFcb` opens special-share pipe-like entries and sends `AFS_REQUEST_TYPE_PIPE_OPEN`.

## Control flow

The create path first separates control-device opens from file-system opens. File-system opens require a global root and a non-shutdown redirector device. `AFSCommonCreate` obtains the caller auth group, ensures the global root is enumerated, and parses the name into a root-relative file name, parsed-name state, root filename, volume, parent directory entry, and name array.

If no volume is returned, the request targets the synthetic `\\Server\\GlobalRoot` layer. The code strips leading/trailing separators, permits only the root itself, `_._AFS_IOCTL_._`, or a special-share name under an already located special parent, and otherwise returns name-not-found.

For real volumes, the code validates the path format, then performs lookup. Reparse handling has two modes. Without a reparse policy override, lookup either substitutes target names normally or, if `FILE_OPEN_REPARSE_POINT` is set, disables mount-point, symlink, and DFS-link target evaluation. With `AFSIgnoreReparsePointToFile()` in effect, the code clones the name array and may run a first lookup that ignores the reparse-open flag, then reruns lookup with target evaluation disabled if the policy does not apply. Lookup can also return `STATUS_REPARSE`, in which case the IRP information is set to `IO_REPARSE`.

Once lookup is complete, `SL_OPEN_TARGET_DIRECTORY` routes to `AFSOpenTargetDirectory`; create dispositions route to `AFSProcessCreate`; missing final components route to PIOCtl or name-not-found; volume roots route to `AFSOpenRoot`; overwrite/supersede dispositions route to `AFSProcessOverwriteSupersede`; all other existing objects route to `AFSProcessOpen`. Successful opens then bind `FileObject->FsContext` and `FsContext2`, set section object pointers for file/PIOCtl FCBs, mark cacheability or no-buffering, set fast I/O read for execute opens, update last access time, insert the CCB on the FCB, and transfer the parsed full name/name array into the CCB.

## State and persistence behavior

This file owns the lifetime-sensitive state transitions for open objects. It increments and decrements volume references with explicit reference reasons, directory-entry `DirOpenReferenceCount`, FCB `OpenReferenceCount` and `OpenHandleCount`, parent `ChildOpenHandleCount` and `ChildOpenReferenceCount`, and CCB insertion/removal. It sets durable in-memory flags such as `AFS_OBJECT_HELD_IN_SERVICE`, `AFS_DIR_ENTRY_PENDING_DELETE`, `AFS_OBJECT_FLAGS_DIRECTORY_ENUMERATED`, `AFS_FCB_FLAG_FILE_MODIFIED`, and `CCB_FLAG_MASK_OPENED_REPARSE_POINT`.

State persisted outside the kernel library is mediated through service calls. Open/create access is held with `AFS_REQUEST_FLAG_HOLD_FID`; failed post-service opens release service access via `AFS_REQUEST_TYPE_RELEASE_FILE_ACCESS`; overwrite/supersede pushes changed file size/timestamps/attributes through `AFSUpdateFileInformation`; PIOCtl and pipe opens notify the service with dedicated request types.

## Dependencies and integration points

The implementation depends on WDK IRP and file-system APIs (`IoGetCurrentIrpStackLocation`, `IoCheckShareAccess`, `IoSetShareAccess`, `IoUpdateShareAccess`, `MmFlushImageSection`, `MmCanFileBeTruncated`, `CcSetFileSizes`, section object pointers, file object flags, and create dispositions/options). It also depends on redirector-local infrastructure declared in `AFSCommon.h`: name parsing/location, auth-group retrieval, volume/object/Fcb/Ccb initialization, directory enumeration/validation, service request callbacks, extent trimming, notification reporting, debug tracing, exception filtering, and custom pool allocation/free routines.

It integrates with `AFSDirControl.cpp` through `AFSFsRtlNotifyFullReportChange` after create operations, with cache and extent code through FCB section/extents state, with service/user-mode communication through `AFSProcessRequest`, and with the framework through global callback pointers defined in `AFSData.cpp`.

## Risks and edge cases

- Reference balancing is complex. Many paths switch `pVolumeCB`, `pParentDirectoryCB`, `pDirectoryCB`, and `pNameArray` ownership after `AFSLocateNameEntry`; missed ownership transitions can leak or prematurely free live objects.
- The two-pass reparse policy path clones and restores name arrays and root names. Bugs here can produce wrong target semantics, stale substituted names, or pool misuse.
- Create and overwrite paths make local object state changes before or around service calls. Rollback paths must keep directory trees, FCB sizes, extents, and service-held access synchronized.
- Section object operations are protected by exception handlers, but failures map to sharing, delete, or user-mapped-file errors. These paths are important for executable files and memory-mapped files.
- Control-device create permits only kernel callers. Any future relaxation needs to preserve the model that user-mode access goes through the file-system/security component.

## Test signals

Useful tests include root open before and after initialization, shutdown-mode create rejection, full global-root enumeration, exact PIOCtl and special-share opens, create/open/open-if/overwrite/supersede matrix coverage, delete-on-close on files/directories/root, `SL_OPEN_TARGET_DIRECTORY` rename preparation, share-access conflicts, read-only volume and read-only attribute rejection, symlink/mountpoint/DFS reparse policy behavior, service open denial and access-mask denial, memory-mapped overwrite rejection, image-section write/delete conflicts, failure-injection for CCB/FCB/name-array allocation, and leak/reference-count tracing around all failure exits.
