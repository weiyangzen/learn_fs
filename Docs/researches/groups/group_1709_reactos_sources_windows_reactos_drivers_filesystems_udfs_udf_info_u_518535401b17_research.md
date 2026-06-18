# Group Research: group_1709_reactos_sources_windows_reactos_drivers_filesystems_udfs_udf_info_u_518535401b17

Scope confirmed against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf_rel.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf_rel.h

This header defines core UDF filesystem in-memory structures shared by the UDF engine and, conditionally, console/user-mode tooling. It sits above ECMA-167 on-disk definitions and translates UDF disk concepts into driver-maintained state.

Key contents:
- `UDFTrackMap` describes optical/media track ranges, next writable address, packet/session data, addressing workaround flags, and fixed-packet/MRW offset fields.
- `UDFSparingData`, `UDFPartMap`, `UDF_VDS_RECORD`, VRS/VDS constants, and UDF revision constants model partition, sparing, volume descriptor sequence, and recognition state.
- `EXTENT_INFO` pairs user data length with an `EXTENT_MAP`, offset, modification flag, and allocation flags. The extent flags distinguish standard/sequential allocation, preallocation, verification, and 2K compatibility.
- Directory indexing is represented by `DIR_INDEX_HDR`, `DIR_INDEX_ITEM`, and hash entries. `DIR_INDEX_ITEM` caches names, file-entry locations, file-ident flags, system attributes, timestamps, size, allocation size, and optional opened `UDF_FILE_INFO`.
- `UDF_DATALOC_INFO` is the hardlink-aware “actual data location” object. It owns `DataLoc`, `AllocLoc`, `FELoc`, cached file-entry bytes, FE flags, link reference count, directory index, stream-directory info, and the paired NT FCB pointer.
- `UDF_FILE_INFO` is the path/tree instance object. It links an NT FCB, a shared data-location object, cached file-ident bytes, parent/index relationships, reference/open counters, hardlink list links, and an optional FE-list entry.
- `FE_LIST_ENTRY`, `UDF_DATALOC_INDEX`, `UDF_DIR_SCAN_CONTEXT`, `EXT_RELOCATION_ENTRY`, and `UDF_ALLOCATION_CACHE_ITEM` support file-entry lookup, directory scanning, relocation, and allocation descriptor caching.
- `UDF_VERIFY_CTX` stores verification bitmap/list state, lock/event synchronization, waiter/queued counts, and initialization state.

Notable design points:
- The header separates tree identity (`UDF_FILE_INFO`) from physical data identity (`UDF_DATALOC_INFO`) to support hardlinks and delayed cleanup.
- Directory entries are normalized into fixed-size in-memory index items because on-disk file-ident records are variable-size.
- Many memory tags and compile-time debugging/tracking switches are defined here, making this header part of the driver’s allocation and diagnostics contract.
- `UDF_NO_EXTENT_MAP` is a sentinel pointer value, so users of extent maps must distinguish sentinel, null, and valid maps.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf_rel.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udffs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udffs.h

This is the main include file for the ReactOS UDF filesystem driver. It centralizes compile-time feature switches, NT kernel dependencies, core UDF headers, public IOCTL definitions, debug helpers, resource wrappers, exception helpers, and file-specific bug-check IDs.

Key contents:
- Feature options include HDD support, extended attributes, sparse files, packed directories, hardlinks, delayed close, rename/move support, and optional security/read-only-related behavior.
- Default tuning constants cover directory packing, readahead granularity, sparse threshold, mount error threshold, bitmap/tree flush timeouts, and per-CPU FSP thread counts.
- `UDF_VALID_FILE_ATTRIBUTES` defines the supported Windows file attribute mask, including sparse-file support when enabled.
- Kernel includes pull in `ntifs.h`, ReactOS cross-NT support, mount manager definitions, physical I/O helpers, registry helpers, memory helpers, and UDF internals.
- Exports the global `UDFGlobalData` and `DefLetter`.
- Provides control-flow macros such as `try_return`, flag helpers, alignment helpers, and `UDFPanic`.
- `UdfIllegalFcbAccess` rejects write/security-style access on read-only volumes or when write-security is disabled.
- `UDFPrint`/`UDFPrintErr` and the resource/interlocked macros switch between direct kernel primitives and debug wrappers depending on `UDF_DBG`.
- `UDFRaiseStatus` and `UDFNormalizeAndRaiseStatus` save exception status in the IRP context before raising.
- Defines unique `UDF_FILE_*` bug-check IDs used by individual implementation files.

Notable design points:
- This file is the driver’s compile-time configuration surface. Many later `.cpp` files change behavior through symbols defined here.
- Resource operations are abstracted so debug builds can track acquisition site and file bug-check ID without changing call sites.
- The header supports both kernel and `_CONSOLE` builds, but most included paths and dispatch prototypes target kernel-mode FSD operation.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udffs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udfinit.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udfinit.cpp

This file implements UDF driver initialization, dispatch table setup, filesystem device-object creation, optional forced dismount support, and filesystem registration-change handling.

Key functions:
- `DriverEntry`
  - Zeroes and initializes `UDFGlobalData`.
  - Initializes global and delayed-close resources.
  - Saves the driver object and registry path.
  - Initializes mounted VCB list, internal allocator, delayed-close queues/work item, zones/lookaside structures, and function pointers.
  - Creates the main UDF driver device object and Win32 symbolic link.
  - Creates and registers CD-ROM and, when `UDF_HDD_SUPPORT` is enabled, disk filesystem device objects.
  - Registers `UDFFsNotification` with `IoRegisterFsRegistrationChange`.
  - On failure, unwinds device objects, deadlock detector state, allocator state, zones, and resources.
- `UDFInitializeFunctionPointers`
  - Installs IRP major dispatch handlers for create, close, read, write, file info, volume info, directory control, FS control, device control, shutdown, locks, cleanup, EA, and optional security operations.
  - Initializes the fast I/O dispatch table with check/read/write/query/lock/unlock/section/mod-write/Cc-flush callbacks.
  - Installs cache manager callbacks for lazy write and read-ahead.
  - Sets `DriverObject->DriverUnload = UDFDriverUnload`.
- `UDFCreateFsDeviceObject`
  - Creates a filesystem device object with `UDFFS_DEV_EXTENSION`, zeroes it, and stamps node type/size.
- `UDFDismountDevice`
  - Opens a named device, queries filesystem attributes, skips if already a UDF title, otherwise locks, dismounts, sends CDRW media-change notification, unlocks, closes, and reopens.
- `UDFFsNotification`
  - When another CD-ROM filesystem registers, re-registers UDF’s filesystem device objects under the global resource so UDF can become top-level. It guards against recursive notification using `FsNotification_ThreadId`.

Notable design points:
- The driver registers separate filesystem device objects for CD and HDD-style UDF media.
- Initialization uses nested SEH and manual cleanup rather than RAII.
- Several legacy code paths are disabled with comments or `#if 0`, including broad remount scanning and dynamic NT export lookup.
- Fast I/O uses `FsRtlCopyRead` for read and `UDFFastIoCopyWrite` for write, while cache callbacks are UDF-specific.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udfinit.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udfpubl.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/udfpubl.h

This public header defines the IOCTL and data-structure interface between the UDF filesystem driver and user applications or cooperating drivers.

Key contents:
- Defines `IOCTL_UDFFS_BASE` and driver-specific IOCTLs:
  - enable/disable driver
  - invalidate volumes
  - get retrieval pointers
  - get/set file allocation mode
  - lock/unlock volume by PID
  - send license key
  - get special retrieval pointers
  - get version
  - set notification event
  - query just-mounted state
  - register autoformat
  - set options
- Defines input/output structs:
  - `UDF_GET_FILE_ALLOCATION_MODE_OUT`
  - `UDF_LOCK_VOLUME_BY_PID_IN`
  - optional `UDF_GET_SPEC_RETRIEVAL_POINTERS_IN`
  - `UDF_GET_VERSION_OUT`
  - `UDF_SET_OPTIONS_IN`
- Defines public device names:
  - kernel/DOS device `\\DosDevices\\DwUdf`
  - Win32 path `\\\\.\\DwUdf`
- Defines stream names used by UDF support tooling:
  - `UdfIsoBridgeStructure`
  - `DvdWriteNow.cfg`
- Defines user-visible filesystem flags for read-only/raw/media/write-protection states.
- Defines damaged-partition policy constants and option-scope flags for temporary, disk, drive, and global settings.

Notable design points:
- Packing is forced with `#pragma pack(push, 8)` to keep the user/kernel ABI stable.
- Some IOCTLs use `FILE_ANY_ACCESS`, while several operational controls use `FILE_READ_ACCESS`.
- The header is guarded so definitions can coexist with environments that already define CTL_CODE or related filesystem control definitions.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/udfpubl.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/unload.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/unload.cpp

This file defines `UDFDriverUnload`.

Behavior:
- Logs unload.
- Sets `UDF_DATA_FLAGS_BEING_UNLOADED` in `UDFGlobalData.UDFFlags` to prevent further mount operations.
- Enters an infinite loop sleeping for 10 seconds at a time while printing `Poll...`.
- Symbolic link deletion and device-object deletion code is present only as comments.

Notable design points:
- The unload routine does not actually complete. It intentionally waits forever after marking the driver as unloading.
- Because the cleanup code is commented out, this driver cannot unload cleanly through this path as written.
- The unload flag is still meaningful because verification/comparison code checks `UDF_DATA_FLAGS_BEING_UNLOADED` and can reject volumes as wrong-volume during teardown-like states.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/unload.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/verfysup.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/verfysup.cpp

This file implements UDF volume verification, media-change handling, quick remount support, dismount checks, VCB teardown, and old/new VCB comparison.

Key functions:
- `UDFVerifyVcb`
  - Rejects VCBs being dismounted.
  - For removable media, sends `IOCTL_STORAGE_CHECK_VERIFY` unless media is locked and no unsafe IOCTL was seen.
  - Sets `DO_VERIFY_VOLUME` when media-change count changes, raw/no-media states appear, or unsafe IOCTL state forces verification.
  - Raises `STATUS_VERIFY_REQUIRED`, `STATUS_WRONG_VOLUME`, or `STATUS_FILE_INVALID` through the IRP context as needed.
- `UDFVerifyVolume`
  - Handles `IRP_MN_VERIFY_VOLUME`.
  - Checks media, allocates a temporary `NewVcb`, reads disk info, initializes read-only write-cache state, and compares physical then logical media identity.
  - Supports raw-disk handling, mount-error thresholds, and quick-remount cache reinitialization.
  - Clears `DO_VERIFY_VOLUME` on successful verification and restarts eject waiter/cache state if the old VCB remains mounted.
  - Cleans temporary VCB/cache state before returning and completes the verify IRP.
- `UDFPerformVerify`
  - Called from exception handling when a request encountered `STATUS_VERIFY_REQUIRED`.
  - Avoids recursive verify during mount/verify FSCTLs.
  - Calls `IoVerifyVolume`, normalizes wrong-volume cases when the VCB is already mounted, can dismount unreferenced VCBs, reparses absolute creates after remount, and posts the original request on success.
- `UDFCheckForDismount`
  - Tests open/reference counts under global and VCB resources.
  - Starts dismount when only residual filesystem references remain.
  - Releases the VCB when teardown is underway and VPB references drain.
- `UDFDismountVcb`
  - Marks the VCB as being dismounted.
  - Allocates a replacement VPB when needed.
  - Closes residual references, swaps or clears VPB state under the VPB spinlock, stops eject waiter, and releases the VCB on final reference.
- `UDFCompareVcb`
  - Physical comparison checks media LBA ranges, track numbers, NWA, possible last LBA, physical serial/type/erasable state, media class, target device object, last session, and per-track ranges/parameters.
  - Logical comparison checks VAT count, volume creation time, serial number, volume identifier, and root file identity.
  - Uses a simplified logical check if the old volume is modified, avoiding root directory inspection.

Notable design points:
- Verification is two-phase: physical identity first, logical UDF identity second.
- Temporary VCB/cache state is used to inspect current media without mutating the mounted VCB until identity is confirmed.
- Raw/blank media and bad-volume cases are explicitly handled.
- Dismount code carefully coordinates VCB resources, VPB spinlock state, residual references, and eject waiter shutdown.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/verfysup.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/volinfo.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/volinfo.cpp

This file implements UDF query/set volume information dispatch paths.

Key functions:
- `UDFQueryVolInfo`
  - Top-level IRP wrapper for `IRP_MJ_QUERY_VOLUME_INFORMATION`.
  - Enters filesystem context, allocates IRP context, calls `UDFCommonQueryVolInfo`, handles exceptions, completes or posts.
- `UDFCommonQueryVolInfo`
  - Reads query class and output length.
  - Optionally checks access under `UDF_ENABLE_SECURITY`.
  - Zeroes the system buffer.
  - Dispatches to volume, size, device, attribute, and full-size query helpers.
  - Acquires `VCBResource` shared for label-copying in `FileFsVolumeInformation`.
- `UDFQueryFsVolumeInfo`
  - Returns volume creation time, physical serial number, `SupportsObjects = FALSE`, and volume label with overflow handling.
- `UDFQueryFsSizeInfo`
  - Returns total/free allocation units, sectors per allocation unit, and bytes per sector.
  - Recomputes space when `BitmapModified` is set and updates `LowFreeSpace`.
- `UDFQueryFsFullSizeInfo`
  - Same space model as size info, filling caller and actual available units.
- `UDFQueryFsDeviceInfo`
  - Returns target device type and characteristics.
  - Clears read-only/write-once characteristics for non-CD/DVD target devices.
- `UDFQueryFsAttributeInfo`
  - Reports case sensitivity/preservation, named streams when supported, sparse-file support, optional persistent ACLs, read-only volume state, and Unicode-on-disk.
  - Chooses a filesystem title based on device type, raw/blank state, CDR mode, and media class.
- `UDFSetVolInfo`
  - Top-level wrapper for `IRP_MJ_SET_VOLUME_INFORMATION` when not read-only build.
- `UDFCommonSetVolInfo`
  - Allows only volume-label changes, rejects non-volume objects and raw disks, checks security when enabled, and posts when VCB acquisition cannot block.
- `UDFSetLabelInfo`
  - Validates label length, reallocates `Vcb->VolIdent`, copies the new label, null-terminates it, and marks the volume modified.

Notable design points:
- Free-space values are cached in the VCB and refreshed only when bitmap state says they are stale.
- The filesystem name returned to callers is media-sensitive rather than always a single `UDF` string.
- Label setting updates in-memory state and marks modified; actual persistence is delegated to later flush/update paths.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/volinfo.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/wcache.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/wcache.cpp

This file is a thin compilation unit for the UDF write-cache implementation.

Key contents:
- Includes `udffs.h`.
- Sets this file’s bug-check ID to `UDF_FILE_WCACHE`.
- Includes `Include/wcache_lib.cpp` directly.

Notable design points:
- The cache implementation is compiled into this module by textual inclusion of the shared library `.cpp`, not by linking a separately compiled object.
- The bug-check ID is set before inclusion so code inside `wcache_lib.cpp` can inherit the UDF file identity for diagnostics.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/wcache.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/wcache.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/wcache.h

This header wraps the shared write-cache library header for the UDF driver.

Key contents:
- Include guard `__CDRW_WCACHE_H__`.
- Includes `Include/wcache_lib.h`.

Notable design points:
- This file provides the UDF-local include name for the reusable write-cache library.
- No types or functions are declared directly here; all public cache API comes from `wcache_lib.h`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/wcache.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/write.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/write.cpp

This file implements the UDF `IRP_MJ_WRITE` dispatch path, deferred write callback, and cache purge helper. It is excluded when `UDF_READ_ONLY_BUILD` is defined.

Key functions:
- `UDFWrite`
  - Top-level write dispatch wrapper.
  - Enters filesystem context, sets top-level IRP state, allocates IRP context, calls `UDFCommonWrite`, handles exceptions, and exits filesystem context.
- `UDFCommonWrite`
  - Handles MDL write completion and DPC-posting cases.
  - Resolves CCB, FCB, VCB, and NT-required FCB state.
  - Rejects deleted files, read-only media/volumes, directories, shutdown volumes, and file-lock conflicts.
  - Supports raw volume writes only when the volume is locked; flushes logical state, locks caller buffer, marks unsafe IOCTL/serial change, and writes through `UDFTWrite`.
  - Applies verification back pressure using `VerifyCtx` queue/item counts.
  - Uses `CcCanIWrite`/`CcDeferWrite` for cached-write throttling.
  - Handles page-file writes as noncached I/O.
  - Interprets `FILE_WRITE_TO_END_OF_FILE` and `FILE_USE_FILE_POINTER_POSITION`.
  - Truncates paging writes beyond EOF and prevents paging I/O from extending file size.
  - Maintains cached/noncached coherency by flushing and purging cache for overlapping noncached writes.
  - Acquires `MainResource`, `PagingIoResource`, and sometimes `VCBResource` according to cached, noncached, paging, lazy-writer, and extension cases.
  - Extends allocation via `UDFResizeFile__`, updates common FCB header sizes, calls `CcSetFileSizes`, and zeroes new gaps with `UDFZeroDataEx`.
  - Initializes system cache maps for first cached writes and uses `CcCopyWrite` for cached writes.
  - Performs direct physical writes through `UDFWriteFile__` for noncached writes.
  - Updates current byte offset, CCB/FO modified flags, file-size-changed state, directory-index file size, and valid data length on success.
  - Posts pending requests with locked buffers and preserved resource-acquired flags where needed.
- `UDFDeferredWriteCallBack`
  - Called by the cache manager to repost deferred write IRPs to UDF’s worker path.
- `UDFPurgeCacheEx_`
  - Purges cache ranges after sparse/unrecorded updates.
  - Optionally uses `CcCopyWrite` with `Vcb->ZBuffer` to zero partial page fragments before purging.
  - Processes large ranges in `PURGE_BLOCK_SZ` chunks and advances valid data length when appropriate.

Notable design points:
- The write path has separate behavior for raw volume writes, cached file writes, noncached file writes, paging I/O, lazy-writer recursion, and write-through recursion.
- File extension is done before cache-manager size publication so allocation failures can still be reported.
- Verification pressure can force waiting before more writes enter the system cache.
- MDL write is effectively unsupported in the cached path: the code returns `STATUS_INVALID_PARAMETER`.
- Raw volume writes deliberately mark the mounted volume unsafe for future quick verification and decrement the serial number to force remount behavior for tools such as check utilities.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/write.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/CMakeLists.txt -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/CMakeLists.txt

This CMake file defines the ReactOS VFAT filesystem driver build.

Key contents:
- Appends all VFAT source files to `SOURCE`, including block I/O, cleanup, close, create, directory, FAT, fast I/O, FCB, flush, FSCTL, PNP, read/write, shutdown, string, volume, and `vfat.h`.
- Adds `-DKDBG` when the `KDBG` option is enabled.
- Builds `vfatfs` as a module with `vfatfs.rc`.
- Sets module type to `kernelmodedriver`.
- Links against `${PSEH_LIB}`.
- Imports `ntoskrnl` and `hal`.
- Uses `vfat.h` as the precompiled header source.
- For Xbox architecture, installs the driver to `reactos/system32/drivers` and registers `vfatfs_reg.inf`.

Notable design points:
- The file is the module-level source manifest for the VFAT FSD.
- The build is kernel-specific and depends on ReactOS kernel/hal imports and PSEH support.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/blockdev.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/blockdev.c

This file implements VFAT low-level block-device read, write, partial-MDL I/O, and IOCTL helpers.

Key functions:
- `VfatReadWritePartialCompletion`
  - Completion routine for partial read/write IRPs.
  - Frees the IRP’s MDL chain, propagates failure status to the original IRP, tracks pending-returned state, decrements `IrpContext->RefCount`, signals the context event when the last pending partial completes, frees the partial IRP, and returns `STATUS_MORE_PROCESSING_REQUIRED`.
- `VfatReadDisk`
  - Builds a synchronous `IRP_MJ_READ` with `IoBuildSynchronousFsdRequest`.
  - Optionally sets `SL_OVERRIDE_VERIFY_VOLUME`.
  - Waits on pending I/O and retries after successful `IoVerifyVolume` on `STATUS_VERIFY_REQUIRED`.
- `VfatReadDiskPartial`
  - Builds an asynchronous read IRP against `DeviceExt->StorageDevice`.
  - Creates a partial MDL from the original request’s MDL at `BufferOffset`.
  - Installs the shared completion routine.
  - Either waits for completion or increments the context reference count for async aggregation.
  - Retries after successful volume verification.
- `VfatWriteDisk`
  - Synchronous write counterpart to `VfatReadDisk`, including optional verify override and retry after media verification.
- `VfatWriteDiskPartial`
  - Partial-MDL asynchronous write counterpart to `VfatReadDiskPartial`.
- `VfatBlockDeviceIoControl`
  - Builds synchronous device I/O control requests, optionally overrides verify, waits on pending I/O, retries after volume verification, and returns output length through `OutputBufferSize`.

Notable design points:
- Media-change handling is centralized in every block helper: on `STATUS_VERIFY_REQUIRED`, the code obtains the thread’s verify device, clears it, calls `IoVerifyVolume`, and reissues the original request on success.
- Partial I/O uses independent child IRPs and MDLs but reports final failure back through the parent IRP context.
- The write partial setup assigns length/offset through `Parameters.Read`, relying on the read/write union layout.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/blockdev.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/cleanup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/cleanup.c

This file implements VFAT `IRP_MJ_CLEANUP` handling, which runs when a handle is closed but before the final file-object close release.

Key functions:
- `VfatCleanupFile`
  - Retrieves the FCB from `FileObject->FsContext`.
  - For volume opens, decrements FCB/device open-handle counts and removes share access when other opens remain.
  - For file/directory opens:
    - Acquires FCB main and paging resources exclusively.
    - Converts CCB delete-on-close into `FCB_DELETE_PENDING`.
    - Calls `FsRtlNotifyCleanup`.
    - Decrements open-handle counts.
    - Releases byte-range locks held by the requestor process.
    - Updates the directory entry when `FCB_IS_DIRTY`.
    - For delete-pending last opens, rejects deletion of non-empty directories; otherwise uninitializes the cached stream, clears sizes, and later deletes the directory entry.
    - Calls `CcUninitializeCacheMap` for the current file object.
    - Reports file/directory removal notifications when deletion succeeds.
    - Removes share access when handles remain.
    - Marks `FO_CLEANUP_COMPLETE` and, in KDBG builds, `FCB_CLEANED_UP`.
  - Contains disabled delayed-close logic because comments say it caused filesystem corruption and test failures.
  - Optionally checks for dismount under `ENABLE_SWAPOUT`.
- `VfatCleanup`
  - Returns success immediately for the global filesystem device object.
  - Acquires the volume directory resource, calls `VfatCleanupFile`, releases it unless the device was deleted, clears IRP information, and returns success.

Notable design points:
- Cleanup is where delete-on-close becomes actual deletion if the final open handle is gone.
- Cache uninitialization is deliberately done even if caching may not have been initialized.
- The active implementation avoids delayed close in cleanup; delayed close is handled in the close path instead.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/cleanup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/close.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/close.c

This file implements VFAT `IRP_MJ_CLOSE`, FCB release, and delayed-close worker support.

Key functions:
- `VfatCommonCloseFile`
  - No-ops for FAT metadata and volume FCBs.
  - If the last open handle is gone and cache remains initialized, uninitializes the cache map for the FCB’s stored file object, clears `FCB_CACHE_INITIALIZED`, and dereferences the file object.
  - Marks `FCB_CLOSED` in KDBG builds.
  - Releases the FCB, potentially deleting it.
- `VfatCloseWorker`
  - Processes global delayed-close list entries under `CloseMutex`.
  - Removes close contexts, decrements `CloseCount`, acquires the VCB directory resource, and closes FCBs still marked `FCB_DELAYED_CLOSE`.
  - Handles concurrent deletion by leaving context freeing to the other owner.
  - Clears `CloseWorkerRunning` when the list drains.
- `VfatPostCloseFile`
  - Allocates a close context from a paged lookaside list.
  - Stores VCB/FCB, links context to the FCB, inserts it into the global close list, increments `CloseCount`, and queues the close worker when more than 16 delayed closes accumulate and no worker is running.
- `VfatCloseFile`
  - Destroys the CCB if present.
  - If shutdown is active, delayed close is not requested, or delayed posting fails, closes immediately; otherwise leaves the FCB for delayed worker release.
  - Clears the file object’s filesystem contexts and section-object pointer.
  - Optionally checks dismount for volume closes under `ENABLE_SWAPOUT`.
- `VfatClose`
  - Returns success for the global filesystem device object.
  - Acquires the volume directory resource, calls `VfatCloseFile`, releases the resource, clears IRP information, and returns status. If the resource cannot be acquired in the current wait mode, it queues the IRP context.

Notable design points:
- The close path separates cleanup-time handle semantics from final object/FCB release.
- Delayed close is global and threshold-driven; it batches work until more than 16 entries are queued.
- Reopen logic in `create.c` can cancel delayed close and reuse the FCB before the worker processes it.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/close.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/create.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/create.c

This file implements VFAT file creation/opening, 8.3 name conversion, directory lookup, volume opens, target-directory opens, create disposition handling, overwrite/supersede behavior, paging-file rules, share checks, and notifications.

Key functions:
- `vfat8Dot3ToString`
  - Converts an on-disk FAT 8.3 short name into a Unicode string.
  - Handles deleted-entry first-byte remapping from `0x05` to `0xe5`.
  - Applies base/ext lowercase flags and inserts the dot for non-volume entries with extensions.
- `FindFile`
  - Searches a directory for a file name or wildcard.
  - Builds a full path and first checks the in-memory FCB table for non-wildcard names.
  - Uppercases the search expression for `FsRtlIsNameInExpression`.
  - Iterates directory entries with `VfatGetNextDirEntry`, skips volume entries, detects corrupt missing names, compares long and short names, and optionally refreshes directory-entry data from an existing FCB.
  - Frees pinned directory pages and allocated strings on exit.
- `VfatOpenFile`
  - Resolves related-file parent state.
  - Checks removable-media verify with `IOCTL_DISK_CHECK_VERIFY`.
  - Gets or creates the FCB for the requested path.
  - Rejects invalid overwrite/delete cases, including existing directories, delete-pending FCBs, read-only overwrite/delete-on-close, root, and dot/dotdot.
  - Cancels delayed close if the FCB was queued for delayed release, including removal from the global close list and reference/context cleanup.
  - Attaches the FCB to the file object.
- `VfatCreateFile`
  - Unpacks create disposition/options, paging-file and open-target-directory flags.
  - Rejects unsupported file-id opens and invalid option combinations.
  - Denies opens when the volume is locked.
  - Handles volume opens, enforcing allowed dispositions/options, share access, FCB attachment, and open-handle counts.
  - Validates path syntax for illegal characters, illegal dot-only path components, double backslashes, absolute names with related file objects, target-root directory opens, and trailing backslashes.
  - Implements `SL_OPEN_TARGET_DIRECTORY` by resolving the target then opening/attaching the parent directory and trimming file-object name state.
  - On not-found paths, creates files/directories for `FILE_CREATE`, `FILE_OPEN_IF`, `FILE_OVERWRITE_IF`, or `FILE_SUPERSEDE` using `VfatAddEntry`, sets allocation size and extended attributes, and marks paging files.
  - On existing files, enforces `FILE_CREATE` collision, directory/non-directory option constraints, trailing-backslash rules, mapped-image write/delete checks, paging-file rules, hidden/system overwrite constraints, supersede/overwrite attributes and timestamps, allocation-size updates, and final information status.
  - Updates share access, delete-on-close CCB flag, directory-change notifications, open-handle counts, and create statistics.
- `VfatCreate`
  - Returns success for opens on the filesystem control device.
  - Acquires the volume directory resource, calls `VfatCreateFile`, releases the resource, and sets priority boost on success.

Notable design points:
- Create/open is serialized under `DeviceExt->DirResource`.
- The function supports both long and short names and checks both during directory searches.
- Delayed-close reuse is handled during open to avoid discarding an FCB that is immediately needed again.
- Delete-on-close is stored in the CCB during create and consumed later by cleanup.
- Existing file overwrite/supersede updates FAT timestamps and attributes before resizing allocation.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/create.c -->