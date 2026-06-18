# Group Research: group_1704_reactos_sources_windows_reactos_drivers_filesystems_udfs_lockctrl_c_f49871fa7c6e

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/lockctrl.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/lockctrl.cpp

## Role

`lockctrl.cpp` implements byte-range lock handling for the ReactOS UDF filesystem driver. It covers the normal `IRP_MJ_LOCK_CONTROL` dispatch path plus Fast I/O callbacks for lock and unlock operations.

## Core Behavior

- `UDFLockControl()` is the top-level dispatch entry. It enters the filesystem, sets top-level IRP state, allocates a `UDFIrpContext`, calls `UDFCommonLockControl()`, and routes exceptions through the shared UDF exception filter/handler.
- `UDFCommonLockControl()` validates the file object, CCB, and FCB, rejects volume and directory FCBs, acquires the file's main resource exclusively, and delegates actual byte-range lock processing to `FsRtlProcessFileLock()`.
- If the main resource cannot be acquired in the current wait mode, the IRP is posted through `UDFPostRequest()` and returns pending.
- Fast I/O lock/unlock callbacks (`UDFFastLock`, `UDFFastUnlockSingle`, `UDFFastUnlockAll`, `UDFFastUnlockAllByKey`) decode the FCB/CCB, reject directories and volume opens, call the corresponding `FsRtlFast*` lock routines, and refresh `CommonFCBHeader.IsFastIoPossible`.

## Synchronization And State

Normal lock-control IRPs use `NtReqFcb->MainResource` exclusively around `FsRtlProcessFileLock()`. Fast unlock-all paths take the main resource shared, while the fast lock and fast unlock-single paths contain commented-out resource acquisition, so they rely mainly on the FsRtl file-lock package and surrounding Fast I/O assumptions.

The shared byte-range lock state lives in `NtReqFcb->FileLock`.

## Dependencies

This file depends on the UDF dispatch framework (`UDFAllocateIrpContext`, `UDFReleaseIrpContext`, `UDFPostRequest`, exception handling), FCB/CCB structures, resource wrappers, `UDFIsFastIoPossible()`, and Windows FsRtl file-lock routines.

## Notable Risks

- Fast lock and single-unlock paths do not currently acquire the FCB resource despite comments indicating that they should, which makes their safety depend on FsRtl lock internals and stable FCB lifetime from the caller.
- Directory and volume lock attempts complete as `STATUS_INVALID_PARAMETER`, so callers expecting long-path fallback receive a completed failure.
- `UDF_BUG_CHECK_ID` is set to `UDF_FILE_SHUTDOWN`, which appears inconsistent with the file's lock-control role.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/lockctrl.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/mem.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/mem.cpp

## Role

`mem.cpp` is a thin compilation unit that binds the UDF driver's memory-tool implementation into this build.

## Core Behavior

The file includes `udffs.h`, defines `UDF_BUG_CHECK_ID` as `UDF_FILE_MEM`, then includes `Include/mem_tools.cpp` directly. The actual allocator/debugging logic is therefore supplied by the included shared implementation, not by code physically written in this wrapper.

## Dependencies

It depends on `udffs.h` for driver-wide definitions and on `Include/mem_tools.cpp` for the memory allocation implementation.

## Notable Risks

Including a `.cpp` implementation file directly means compile-unit behavior depends on preprocessor state set before the include, especially `UDF_BUG_CHECK_ID` and any debug heap macros from `mem.h`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/mem.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/mem.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/mem.h

## Role

`mem.h` is the UDF driver's local memory-tool configuration header.

## Core Behavior

When `UDF_DBG` is enabled, it turns on memory-owner tracking, reference tracking, and allocation-bound checking with a two-`ULONG` guard size. It leaves optional nonpaged-only allocation and internal memory-manager modes commented out, then includes `Include/mem_tools.h`.

## Dependencies

The public allocation API comes from `Include/mem_tools.h`. Debug behavior is controlled by `UDF_DBG` and the `MY_HEAP_*` macros defined in this header before including the shared memory-tool header.

## Notable Risks

This header changes allocator instrumentation through macros, so include order matters. Production builds skip the debug heap tracking features entirely unless `UDF_DBG` is set.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/misc.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/misc.cpp

## Role

`misc.cpp` is a central support module for the ReactOS UDF filesystem driver. It owns global allocation zones, object/CCB/FCB/IRP-context lifecycle helpers, exception handling, deferred IRP dispatch, VCB initialization and teardown, media/configuration option handling, registry/config parsing, EA rejection, resource reacquisition helpers, and write-cache error accounting.

## Allocation And Object Lifecycle

- `UDFInitializeZones()` sizes object-name, CCB, and IRP-context lookaside zones according to `MmQuerySystemSize()` and NT server/workstation classification. It also sets delayed-close and write-cache sizing defaults.
- `UDFDestroyZones()` frees the global zone backing allocations and clears the initialized flag.
- `UDFAllocateObjectName()`/`UDFReleaseObjectName()` and `UDFAllocateCCB()`/`UDFReleaseCCB()` allocate from zones first, then fall back to pool with flags marking non-zone allocations.
- `UDFCleanUpCCB()` removes a CCB from the FCB CCB list, frees directory search-pattern storage, and releases the CCB.
- `UDFAllocateFCB()` allocates and initializes FCB signatures. `UDFCleanUpFCB()` frees the FCB name, unlinks the FCB from the VCB list, deletes its CCB-list resource if initialized, and releases the FCB.
- `UDFAllocateIrpContext()` creates per-request context, copies major/minor functions from the IRP, sets blocking capability for synchronous/file-object-less requests, and records whether the request is not top-level.
- `UDFReleaseIrpContext()` returns contexts to the zone or frees pool fallback allocations.

## Dispatch And Exception Flow

`UDFIsIrpTopLevel()` manages `IoGetTopLevelIrp()`/`IoSetTopLevelIrp()` for dispatch entry points. `UDFExceptionFilter()` records expected exception status into the IRP context and uses `FsRtlIsNtstatusExpected()` to decide whether to handle or continue searching. `UDFExceptionHandler()` completes or posts IRPs for saved exception statuses, with special handling for `STATUS_VERIFY_REQUIRED`, user-induced errors, hard-error popups, and pending/cant-wait retry paths.

`UDFPostRequest()` marks IRPs pending and queues contexts to a per-VCB worker system. It limits active work by `FSP_PER_DEVICE_THRESHOLD` and uses an overflow queue when too many requests are already posted. `UDFCommonDispatch()` runs in a worker thread, restores top-level IRP state, forces blocking capability, dispatches by major function to common handlers, processes overflow-queue entries, and decrements the posted-request count when the worker exits.

## VCB And Configuration

`UDFInitializeVCB()` zeroes and signs the VCB, initializes all major resources, allocates per-CPU filesystem statistics, stores target/volume/VPB pointers, initializes FCB/notify/open/overflow lists, allocates the VCB `NTRequiredFCB`, sets initial cache and open-count fields, links the VCB into global state, and discovers a target device name through an IOCTL with fallback to a nameless-device registry name.

`UDFReleaseVCB()` waits for posted work to drain, releases logical-volume state and write cache, removes the VCB from the global list, deletes resources, uninitializes notify state, performs residual VCB cleanup, and deletes the volume device object.

`UDFGetMediaClass()` maps device/media flags to UDF media classes such as CD-ROM, CD-R, CD-RW, DVD writable/read-only classes, floppy, removable disk, or HDD. `UDFReadRegKeys()` reads registry or config-file options into the VCB, including allocation descriptor defaults, UID/GID defaults, flush periods, delayed update behavior, sparse thresholds, verify-on-write, compatibility flags, forced read-only handling, cache sizing, eject-button handling, damaged/dirty-volume behavior, and removable-media write-through behavior.

`UDFGetRegParameter()` delegates registry lookup to `UDFRegCheckParameterValue()`. `UDFGetCfgParameter()` parses simple `name=value` numeric configuration data with comments and decimal/hex values. `UDFRegCheckParameterValue()` checks global defaults, media-class defaults, and device-specific parameter keys.

## Other Helpers

- `UDFInitializeIrpContextLite()` and `UDFInitializeIrpContextFromLite()` preserve enough context for queued close-style work and reconstruct a full IRP context later.
- `UDFQuerySetEA()` completes EA query/set IRPs with `STATUS_EAS_NOT_SUPPORTED`.
- `UDFIsResourceAcquired()`, `UDFAcquireResourceExclusiveWithCheck()`, and `UDFAcquireResourceSharedWithCheck()` avoid reacquiring resources already held by the current thread.
- `UDFWCacheErrorHandler()` increments the VCB I/O error counter and returns the underlying write-cache error status.
- The file ends by including shared implementations `Include/misc_common.cpp` and `Include/regtools.cpp`.

## Dependencies

This module is tightly coupled to nearly every UDF subsystem: global driver state, VCB/FCB/CCB/IRP context structures, resource wrappers, delayed close, read/write/create/cleanup/close/dir/fileinfo/volume/security handlers, cache manager callbacks, physical I/O helpers, registry helpers, write cache, and Windows kernel exception, work-item, VPB, notify, and resource APIs.

## Notable Risks

- `UDFCommonDispatch()` assumes common handlers consume or release the IRP context; incorrect ownership in a handler would leak or double-free.
- VCB initialization has many partially initialized resources and allocations; the failure cleanup is explicit and must stay aligned with new fields.
- Worker queue draining in `UDFReleaseVCB()` waits by polling `PostedRequestCount`, so stuck worker accounting can stall teardown.
- Registry/config parsing is permissive and mostly silent on malformed values, falling back to defaults.
- `UDFLogEvent()` is effectively a stub and does not write the event log despite callers using it after internal errors.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/misc.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/namesup.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/namesup.cpp

## Role

`namesup.cpp` implements filename parsing, validation, wildcard matching, and 8.3-name eligibility helpers for the UDF driver.

## Core Behavior

- `UDFDissectName()` skips leading backslashes, handles leading stream-colon syntax, and returns the next component boundary while reporting component length. It has an x86/MSVC inline-assembly implementation and a generic C fallback.
- `UDFIsNameValid()` rejects empty and too-long names, rejects Windows-disallowed characters and control characters, detects a single stream separator, forbids nested stream paths, and disallows trailing space or dot before separators and at the end.
- `UDFIsNameInExpression()` first compares a long filename against a search pattern using either `FsRtlIsNameInExpression()` or `RtlCompareUnicodeString()`. If that fails and an 8.3 name is possible, it generates a DOS name through `UDFDOSName()` and retries, setting `DosOpen` when the short-name path matched.
- `UDFIsMatchAllMask()` recognizes match-all patterns: Win32 `*`, DOS all-question-mark `????????.???`, and DOS `*.*`, also identifying DOS-open semantics.
- `UDFCanNameBeA8dot3()` checks whether a name fits a single-dot, 8-character basename, 3-character extension shape.

## Dependencies

The code depends on Windows Unicode strings, FsRtl wildcard matching, RTL string comparison, UDF DOS-name generation, UDF path-length constants, and DOS wildcard character constants.

## Notable Risks

- `UDFIsNameValid()` uses `c0` to validate separators and trailing characters after the first character; malformed first-character edge cases are worth testing carefully when changing validation.
- The x86 inline-assembly and generic C versions of `UDFDissectName()` must remain behaviorally identical.
- Alternate stream syntax is accepted through `:`, but sub-streams and stream directories are deliberately rejected.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/namesup.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/namesup.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/namesup.h

## Role

`namesup.h` declares the UDF filename support API implemented by `namesup.cpp`.

## Interface

It exposes helpers for component dissection, wildcard expression matching, wildcard detection, name validity checks with stream-open reporting, match-all-mask detection, and 8.3-name eligibility.

## Dependencies

The declarations depend on UDF driver types such as `PVCB`, Windows `UNICODE_STRING`, and the DOS/open reporting conventions used by directory lookup and create paths.

## Notable Risks

The prototypes use `__fastcall` on selected helpers, so callers and definitions must agree on calling convention.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/namesup.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/ntifs_ex.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/ntifs_ex.h

## Role

`ntifs_ex.h` is a compatibility header that fills in NTIFS/DDK definitions, prototypes, macros, and constants needed by this UDF driver across Windows/ReactOS build environments.

## Core Contents

- Provides `MmGetSystemAddressForMdlSafer()`, which maps an MDL safely by setting `MDL_MAPPING_CAN_FAIL` around `MmMapLockedPages()` when the MDL is not already system-mapped or nonpaged.
- Defines `FULL_SECURITY_INFORMATION` and declares security descriptor/SID RTL routines used by UDF security support.
- Defines `IsFileObjectReadOnly()`.
- Supplies missing `FSCTL_*` codes, filesystem capability flags, file attribute flags, `FileFs*Information` enum values, `IRP_MN_SURPRISE_REMOVAL`, `VPB_REMOVE_PENDING`, and volume notification event codes when the platform headers do not provide them.
- Declares `ZwFsControlFile()`, `ZwDeviceIoControlFile()`, and `ZwQueryVolumeInformationFile()`.
- Provides fallback definitions for `IoCopyCurrentIrpStackLocationToNext()` and `IoSkipCurrentIrpStackLocation()`.
- Defines a `ptrFsRtlNotifyVolumeEvent` function pointer type and includes `Include/ntddk_ex.h`.

## Dependencies

The header sits between platform DDK/NTIFS headers and the UDF codebase. It depends on MDL, security descriptor, SID, IRP, VPB, FSCTL, and Zw/Nt kernel types being available.

## Notable Risks

- Several blocks are disabled with `#if 0`, so this header documents old compatibility definitions without enabling them.
- The local `MmGetSystemAddressForMdlSafer()` uses older `MmMapLockedPages()` plus temporary MDL flag mutation rather than newer `MmGetSystemAddressForMdlSafe()` semantics.
- Fallback IRP stack macros must match platform behavior exactly; subtle differences can affect pass-through PnP and device-control flows.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/ntifs_ex.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/pnp.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/pnp.cpp

## Role

`pnp.cpp` implements Plug and Play IRP handling for UDF volume device objects, especially query-remove, surprise-remove, and remove-device flows.

## Dispatch Flow

`UDFPnp()` is the top-level dispatch routine. It enters the filesystem, sets top-level IRP state, allocates an IRP context, and calls `UDFCommonPnp()`, using the shared exception filter/handler on errors. The routine contains an unconditional `ASSERT(FALSE)`, suggesting this path may not be expected in normal builds or remains diagnostic.

`UDFCommonPnp()` verifies the target is a VCB, forces blocking mode, and switches on the PnP minor function:

- `IRP_MN_QUERY_REMOVE_DEVICE` -> `UDFPnpQueryRemove()`.
- `IRP_MN_SURPRISE_REMOVAL` -> `UDFPnpSurpriseRemove()`.
- `IRP_MN_REMOVE_DEVICE` -> `UDFPnpRemove()`.
- Other minor functions are skipped down the stack with `IoSkipCurrentIrpStackLocation()` and `IoCallDriver()`.

## Remove Handling

`UDFPnpQueryRemove()` acquires global and VCB resources, closes delayed/system delayed objects, runs `UDFDoDismountSequence()`, stops the eject waiter, forwards the query remove down the device stack with a completion event, and if successful forces dismount through `UDFCheckForDismount()`. It then completes the original IRP.

`UDFPnpRemove()` acquires global and VCB resources, closes delayed objects, clears any volume lock state, forwards the remove down the stack and waits, marks the real device for verify, runs dismount, clears mounted/write-security flags, stops the eject waiter, checks for dismount, releases resources, frees the media-removal buffer, and completes the IRP.

`UDFPnpSurpriseRemove()` follows the same broad structure as remove but is used for unplanned device disappearance. It forwards the surprise-remove IRP first, then marks verify, dismounts, clears mounted/write-security flags, stops the eject waiter, checks for dismount, and completes.

`UDFPnpCompletionRoutine()` signals the supplied event and returns `STATUS_MORE_PROCESSING_REQUIRED` so the caller can finish processing synchronously.

## Dependencies

The file depends on VCB state, delayed close, dismount sequencing, eject waiter control, `UDFCheckForDismount()`, global/VCB resource ordering, IRP stack forwarding helpers, and lower storage-stack PnP behavior.

## Notable Risks

- `UDFPnp()` asserts false unconditionally, so debug builds will break on any PnP dispatch.
- `UDFPnpQueryRemove()` allocates `Buf` but does not free it in its finally block, unlike remove and surprise-remove paths.
- `UDFPnpRemove()` and `UDFPnpSurpriseRemove()` declare `VcbDeleted` and `VcbAcquired` without explicit initializers before complex control flow, so any early path must set them before finally uses them.
- Cancel-remove support is present only as commented-out code, so query-remove recovery is not implemented here.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/pnp.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/protos.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/protos.h

## Role

`protos.h` is the main cross-module prototype header for the ReactOS UDF filesystem driver. It declares dispatch entry points, common IRP handlers, Fast I/O callbacks, filesystem-control helpers, metadata/query/set helpers, security routines, verification/dismount functions, read/write helpers, and miscellaneous infrastructure APIs.

## Interface Coverage

The header groups prototypes by implementation file:

- `create.cpp`: create dispatch, common create, first-open/open-file, and FCB initialization.
- `cleanup.cpp` and `close.cpp`: cleanup/close dispatch, file-info chain cleanup, delayed close queue handling, and delayed close worker.
- `dircntrl.cpp`: directory control, query directory, and change notification.
- `devcntrl.cpp`: device control, completion, and query-path handling.
- `fastio.cpp`: Fast I/O read/write/query/device-control callbacks plus cache-manager acquire/release callbacks.
- `fileinfo.cpp`: query/set file information, rename, hardlink, file ID cache, allocation/EOF/disposition/basic/stream information helpers.
- `flush.cpp`: file, directory, and logical-volume flush operations and completion/break helpers.
- `fscntrl.cpp`: filesystem control, mount, volume lock/unlock/dismount, bitmap/retrieval pointer queries, statistics, path validation, eject waiter, VCB cleanup, and volume mounted/dirty checks.
- `lockctrl.cpp`: normal and Fast I/O byte-range locking APIs.
- `misc.cpp`: zones, exception handling, object/FCB/CCB/IRP-context lifecycle, posting, VCB init/release, registry/config parameters, EA rejection, resource helpers, and write-cache error handling.
- `namesup.cpp`: included through `namesup.h`.
- `pnp.cpp`: PnP dispatch.
- `read.cpp`: read dispatch, stack-overflow read posting, common read, buffer locking/unlocking, caller buffer lookup, and MDL completion.
- `SecurSup.cpp`: query/set security, ACL assignment/deassignment, security read/write, access checks.
- `Shutdown.cpp`, `Udf_dbg.cpp`, `UDFinit.cpp`, `verify.cpp`, `VolInfo.cpp`, and `write.cpp`: shutdown, debug resource wrappers, driver entry/init, verify/dismount comparison, volume information, write, deferred write, and cache purge/zero-data APIs.

## Compile-Time Shaping

The header uses build flags to expose or hide behavior:

- `UDF_READ_ONLY_BUILD` removes write/set-information/set-security/set-volume prototypes in several sections.
- `_WIN32_WINNT >= 0x0400` enables newer Fast I/O callback prototypes.
- `UDF_ENABLE_SECURITY` and `UDF_HANDLE_EAS` condition security/EA-related dispatch exposure elsewhere in the codebase.
- A large physical I/O prototype block is disabled under `#if 0`, but includes the active `UDFReadSectors` macro that chooses write-cache reads when available and falls back to `UDFTRead()`.

## Dependencies

`protos.h` includes `mem.h` and `namesup.h`, and depends on nearly all UDF driver types (`VCB`, `UDFFCB`, `UDFCCB`, `UDFIrpContext`, file-info structures, write-cache types) plus Windows kernel IRP, device, file object, security, Fast I/O, and cache manager types.

## Notable Risks

- Because this is a broad global prototype header, changes can ripple across almost every UDF compilation unit.
- It contains inline/macro behavior, not just declarations, including `UDFReleaseFCB`, `UDFRemoveFromDelayedQueue`, `UDFReadSectors`, and cache purge/zero-data aliases.
- Some declarations are inconsistent in style or type spelling, such as `extern OSSTATUS NTAPI UDFRead()` while the implementation returns `NTSTATUS`.
- Disabled prototype blocks preserve stale declarations and even malformed text, so enabling them would require cleanup.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/protos.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/read.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/read.cpp

## Role

`read.cpp` implements read dispatch for the UDF filesystem driver, including normal cached reads, noncached/direct reads, volume reads, paging I/O resource handling, stack-overflow read posting, user-buffer MDL management, and MDL read-completion support.

## Dispatch And Stack-Overflow Handling

`UDFRead()` is the top-level `IRP_MJ_READ` handler. It enters the filesystem, establishes top-level IRP state, allocates a `UDFIrpContext`, calls `UDFCommonRead()`, and delegates exceptions to the shared UDF exception path.

`UDFCommonRead()` checks top-level IRP markers, handles `IRP_MN_COMPLETE` by calling `UDFMdlComplete()`, returns pending for DPC reads, decodes file object/CCB/FCB/VCB, rejects deleted FCBs, and posts through `UDFPostStackOverflowRead()` when remaining kernel stack is below `OVERFLOW_READ_THRESHHOLD`. The overflow helper uses `FsRtlPostStackOverflow()` and `UDFStackOverflowRead()` to retry in a safer context while holding the relevant file resource shared.

## File And Volume Read Behavior

For volume FCB reads, the code forces blocking mode, performs delayed-close and flush work when IRP context flags request it, acquires the VCB resource shared, locks/maps the caller buffer, and reads through either `UDFReadData()` for mounted volumes or `UDFTRead()` for raw/unmounted access.

For file reads, it handles `FILE_USE_FILE_POINTER_POSITION`, rejects directory reads, checks byte-range locks for nonpaging reads, validates/truncates reads against file size, refreshes Fast I/O possibility, and updates access notifications for cached non-volume reads.

Cached reads initialize the cache map on first use with current FCB sizes and UDF cache callbacks, set read-ahead granularity, reject MDL-read requests with `STATUS_INVALID_PARAMETER`, then use `CcCopyRead()`.

Noncached reads flush cached data when needed for coherency, acquire paging I/O resources, lock and map the caller buffer, and call `UDFReadFile__()` with cache-lock awareness. If data is already locked in the driver's fast cache and the request initially cannot wait, it temporarily allows waiting and releases the direct cache lock afterward through `WCacheEODirect__()`.

## Buffer And MDL Helpers

- `UDFGetCallersBuffer()` maps an existing IRP MDL, maps a driver-created MDL from the IRP context, returns a transition buffer when that optional mode is enabled, or falls back to `Irp->UserBuffer`.
- `UDFLockCallersBuffer()` allocates an MDL for the user buffer when one is not present, probes and locks pages with read/write access inverted according to I/O direction, stores the MDL on the IRP, and marks the IRP context as buffer-locked.
- `UDFUnlockCallersBuffer()` flushes I/O buffers and clears context-owned MDL state, relying on I/O completion to unlock/free the MDL in the normal path.
- `UDFMdlComplete()` releases Cache Manager MDLs with `CcMdlReadComplete()` or `CcMdlWriteComplete()`, clears `Irp->MdlAddress`, releases the IRP context, and completes the IRP.

## Completion Semantics

The finalizer releases acquired resources, posts pending work when blocking/resource acquisition was not possible, advances `FileObject->CurrentByteOffset` for successful synchronous nonpaging reads, marks successful nonpaging reads as fast-I/O reads and accessed CCBs, fills `IoStatus`, releases the IRP context, and completes the IRP.

## Dependencies

This file depends on core UDF FCB/CCB/VCB structures, byte-range lock state, resource wrappers, cache manager APIs, MDL/page-locking APIs, UDF physical/logical read helpers, write cache helpers, delayed-close/flush flags, notification helpers, and the shared exception/posting infrastructure.

## Notable Risks

- MDL read support is explicitly disabled by returning `STATUS_INVALID_PARAMETER` for `IRP_MN_MDL` cached reads, while MDL completion support still exists.
- Buffer locking and unlocking rely on IoCompleteRequest to finish MDL cleanup for context-owned MDLs; ownership mistakes can leak or corrupt MDL state.
- Noncached cache coherency depends on targeted `CcFlushCache()` calls and paging-resource serialization, with several older synchronization blocks commented out.
- The read path has many pending/posting exits, so resource-acquisition flags and `PtrIrpContext` ownership must remain exact when changing the function.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/read.cpp -->