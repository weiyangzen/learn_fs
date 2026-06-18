# Group Research: group_1703_reactos_sources_windows_reactos_drivers_filesystems_udfs_fastio_cpp_1f2ec4d76684

Scope: `Docs/research_subset_a.md` includes `sources/windows/reactos`, so all listed ReactOS UDFS files are in scope. Each source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/fastio.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/fastio.cpp

`fastio.cpp` implements UDFS fast I/O and Cache Manager/Memory Manager callback plumbing. It is not a normal read/write implementation; most routines either answer fast-I/O eligibility questions, serve cached metadata queries, or acquire/release FCB resources around section creation, lazy write, read-ahead, modified page writer, and `CcFlush`.

Key entry points:
- `UDFFastIoCheckIfPossible()` rejects volume and directory objects, then delegates byte-range lock checks to `FsRtlFastCheckLockForRead()` or `FsRtlFastCheckLockForWrite()`.
- `UDFIsFastIoPossible()` returns `FastIoIsNotPossible` if the volume is not mounted, `FastIoIsQuestionable` if file locks exist, otherwise `FastIoIsPossible`.
- `UDFFastIoQueryBasicInfo()`, `UDFFastIoQueryStdInfo()`, and `UDFFastIoQueryNetInfo()` call the corresponding `UDFGet*Information()` helpers from `fileinfo.cpp`; basic and network queries acquire `MainResource` shared unless this is a page file.
- `UDFFastIoAcqCreateSec()` and `UDFFastIoRelCreateSec()` acquire/release both `MainResource` and `PagingIoResource` exclusively and maintain `AcqSectionCount`.
- `UDFAcqLazyWrite()`/`UDFRelLazyWrite()` synchronize lazy writer activity on `PagingIoResource`, set `LazyWriterThreadID`, and temporarily set `FSRTL_CACHE_TOP_LEVEL_IRP`.
- `UDFAcqReadAhead()`/`UDFRelReadAhead()` acquire/release `MainResource` shared for Cache Manager read-ahead.
- `UDFFastIoAcqModWrite()`/`UDFFastIoRelModWrite()` gate modified-page writer operations with `PagingIoResource` and `AcqFlushCount`.
- `UDFFastIoAcqCcFlush()`/`UDFFastIoRelCcFlush()` acquire/release `PagingIoResource` exclusively around `CcFlush`.
- `UDFFastIoCopyWrite()` applies verify-queue backpressure and a 16 MiB-aligned cache-section heuristic before falling through to `FsRtlCopyWrite()`.

Notable behavior and dependencies:
- The file relies heavily on `UDFNTRequiredFCB` resources and state counters: `MainResource`, `PagingIoResource`, `AcqSectionCount`, `AcqFlushCount`, and `LazyWriterThreadID`.
- MDL fast I/O routines are present only as commented stubs, so MDL read/write fast paths are effectively unsupported here.
- Query fast paths use SEH wrappers and set `IoStatus` in finalizers, mirroring the IRP paths but with reduced dispatch overhead.
- Fast I/O is intentionally conservative for directories, volume objects, unmounted volumes, file locks, verify-cache pressure, and certain large cached writes.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/fastio.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/fileinfo.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/fileinfo.cpp

`fileinfo.cpp` implements `IRP_MJ_QUERY_INFORMATION` and `IRP_MJ_SET_INFORMATION` for UDFS file objects. It is the central bridge between NT file-information classes and UDF in-memory/on-disk metadata: timestamps, attributes, sizes, stream information, delete-on-close, rename/move, optional hard links, and file-ID reopen support.

Primary dispatch flow:
- `UDFFileInfo()` establishes filesystem/top-level IRP context and calls `UDFCommonFileInfo()`.
- `UDFCommonFileInfo()` validates `Ccb`/`Fcb`, rejects VCB-as-file queries, acquires the VCB shared, and dispatches query or set information classes.
- Query classes handled include `FileBasicInformation`, `FileStandardInformation`, `FileNetworkOpenInformation`, `FileInternalInformation`, `FileEaInformation`, `FileNameInformation`, `FileAlternateNameInformation`, `FilePositionInformation`, `FileStreamInformation`, and `FileAllInformation`.
- Set classes handled in writable builds include `FileBasicInformation`, `FilePositionInformation`, `FileDispositionInformation`, `FileRenameInformation`, optional `FileLinkInformation`, `FileAllocationInformation`, and `FileEndOfFileInformation`.

Query helpers:
- `UDFGetBasicInformation()` copies cached FCB times, updates directory-index time caches, composes NT attributes, and honors `FO_TEMPORARY_FILE`.
- `UDFGetStandardInformation()` reports link count, delete-pending state, directory flag, allocation size, and EOF.
- `UDFGetNetworkInformation()` combines basic timestamps, size/allocation fields, and attributes for network-open queries.
- `UDFGetInternalInformation()` computes a UDF-backed NT file ID and stores a path mapping in the VCB file-ID cache.
- `UDFGetEaInformation()` reports zero EA size.
- `UDFGetFullNameInformation()` returns `FileObject->FileName`; `UDFGetAltNameInformation()` synthesizes an 8.3/DOS name.
- `UDFGetFileStreamInformation()` walks the stream directory index and emits `FILE_STREAM_INFORMATION` records for non-deleted, non-internal streams.

Set and mutation helpers:
- `UDFSetBasicInformation()` updates UDF timestamps, FCB time caches, NT/UDF attributes, read-only and temporary flags, archive-related state, and directory-change notifications.
- `UDFSetDispositionInformation()` enforces read-only/root/non-empty/mapped-image checks, marks or unmarks delete-on-close, and delegates stream-tree marking to `UDFMarkStreamsForDeletion()`.
- `UDFMarkStreamsForDeletion()` opens the stream directory, validates image sections with `MmFlushImageSection()`, and recursively marks streams and stream directories with `UDF_FCB_DELETE_ON_CLOSE`/`UDF_FCB_DELETE_PARENT`.
- `UDFSetAllocationInformation()` and `UDFSetEOF()` coordinate file growth/truncation with free-space checks, `MmCanFileBeTruncated()`, `UDFResizeFile__()`, `PagingIoResource`, `CcSetFileSizes()`, archive-bit updates, and notify-change events.
- `UDFPrepareForRenameMoveLink()` converts VCB/resource ownership to a deadlock-avoiding state before rename/move/hard-link operations.
- `UDFRename()` validates source/target directories, stream-directory restrictions, open-reference safety, name length, replacement rules, performs `UDFRenameMoveFile__()`, updates parent/file references and FCB names, and emits remove/add/rename notifications.
- `UDFHardLink()` is compiled only with `UDF_ALLOW_HARD_LINKS`; it uses similar validation and notification logic around `UDFHardLinkFile__()`.

File-ID cache:
- `UDFFindFileId()`, `UDFFindFreeFileId()`, `UDFStoreFileId()`, `UDFRemoveFileId()`, `UDFReleaseFileIdCache()`, and `UDFGetOpenParamsByFileId()` maintain a VCB-side mapping from generated file IDs to full names and case-sensitivity state.

Notable behavior and dependencies:
- The file is highly synchronization-sensitive: VCB, parent FCB, current FCB, and paging resources are acquired differently for query, position-only set, rename/link, page-file mutation, and size-changing requests.
- Size updates intentionally handle recursive Cache Manager callbacks by using `AcqFlushCount`, temporary cache-map initialization, and `CcSetFileSizes()`.
- Many write paths are compiled out under `UDF_READ_ONLY_BUILD`.
- Rename/move code has extensive reference-count repair for CCB path chains when moving across directories.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/fileinfo.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/filter.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/filter.cpp

`filter.cpp` contains the small filter-attachment support used to attach UDFS above another CD-ROM filesystem device, especially CDFS-style stacks. It creates a filter device object, initializes its extension, and attaches it to the current top of the target filesystem device stack.

Key routines:
- `UDFCheckOtherFS()` acquires `UDFGlobalData.GlobalDataResource`, creates a `FILE_DEVICE_CD_ROM_FILE_SYSTEM` device with `FILTER_DEV_EXTENSION`, tags it as `UDF_NODE_TYPE_FILTER_DEVOBJ`, records the lower filesystem device, and attaches with `IoAttachDeviceByPointer()`.
- `UDFCheckOtherFSByName()` resolves a named device object via `IoGetDeviceObjectPointer()`, calls `UDFCheckOtherFS()`, then dereferences the file object.
- `UDFFsNotification()` is present but compiled out with `#if 0`; it would attach when a CD-ROM filesystem registers as active.

Notable behavior and dependencies:
- The filter path distinguishes filter device extensions by `NodeIdentifier` values used later in mount handling.
- Failed filter-device creation or attachment cleans up immediately and releases the global resource.
- The active filesystem notification path is disabled, so callers must invoke the name/device attachment helpers through other initialization logic.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/filter.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/flush.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/flush.cpp

`flush.cpp` implements `IRP_MJ_FLUSH_BUFFERS` plus internal recursive flush helpers for files, directories, stream directories, volume metadata, and the write cache. It coordinates NT Cache Manager flushing with UDF metadata persistence and lower-device flush forwarding.

Primary dispatch flow:
- `UDFFlush()` creates an IRP context, manages top-level IRP state, and delegates to `UDFCommonFlush()`.
- `UDFCommonFlush()` posts non-waitable flushes, distinguishes volume/root flushes from single-file flushes, acquires VCB/FCB resources, and completes or forwards the IRP.
- Volume/root flushes acquire `VCBResource` exclusively and call `UDFFlushLogicalVolume()`.
- Regular file flushes acquire VCB shared and FCB `MainResource` exclusive, then call `UDFFlushAFile()`.

Flush helpers:
- `UDFFlushAFile()` writes security metadata, flushes stream directories, calls `CcFlushCache()` when the cached file is modified or not yet marked flushed, updates modify time/archive state, syncs allocation size in the directory index, and calls `UDFFlushFile__()`.
- `UDFFlushADirectory()` writes directory security, recurses into stream directories, scans directory entries, flushes child directories/files, checks for break requests, and flushes the directory file itself.
- `UDFFlushLogicalVolume()` skips raw, read-only, or unmounted volumes; otherwise it flushes from the root, optionally performs verify writes, unmounts internal UDF structures, flushes `FastCache`, and clears modified state unless this is a lite flush.
- `UDFFlushCompletion()` preserves pending state and converts `STATUS_INVALID_DEVICE_REQUEST` from lower drivers into success.
- `UDFFlushTryBreak()` sets a flush-break request flag; `UDFFlushIsBreaking()` currently returns `FALSE` before checking flags, so break requests are effectively advisory/disabled in this build.

Notable behavior and dependencies:
- The file uses UDF-specific cache APIs such as `WCacheFlushBlocks__()`, `WCacheFlushAll__()`, `UDFVFlush()`, `UDFUmount__()`, `UDFPreClrModified()`, and `UDFClrModified()`.
- Lower-device flush forwarding is conditional on `Vcb->FlushMedia`; otherwise the IRP is completed locally.
- Flush updates are tied to `FO_FILE_MODIFIED`, `FO_FILE_SIZE_CHANGED`, `UDF_CCB_WRITE_TIME_SET`, compatibility flags, and archive-bit policy.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/flush.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/fscntrl.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/fscntrl.cpp

`fscntrl.cpp` implements `IRP_MJ_FILE_SYSTEM_CONTROL` for UDFS. It handles user FSCTLs, mount, verify delegation, blank/raw mount fallback, root FCB construction, eject-waiter startup, VCB cleanup, volume lock/unlock/dismount, volume bitmaps, retrieval pointers, dirty checks, and invalidation.

Dispatch and FSCTL handling:
- `UDFFSControl()` allocates IRP context and delegates to `UDFCommonFSControl()`.
- `UDFCommonFSControl()` dispatches `IRP_MN_USER_FS_REQUEST`, `IRP_MN_MOUNT_VOLUME`, and `IRP_MN_VERIFY_VOLUME`; verify is delegated to `UDFVerifyVolume()`.
- `UDFUserFsCtrlRequest()` rejects oplock FSCTLs, supports `FSCTL_INVALIDATE_VOLUMES`, `FSCTL_IS_VOLUME_DIRTY`, `FSCTL_ALLOW_EXTENDED_DASD_IO`, `FSCTL_DISMOUNT_VOLUME`, `FSCTL_IS_VOLUME_MOUNTED`, `FSCTL_FILESYSTEM_GET_STATISTICS`, `FSCTL_LOCK_VOLUME`, `FSCTL_UNLOCK_VOLUME`, `FSCTL_IS_PATHNAME_VALID`, `FSCTL_GET_VOLUME_BITMAP`, and `FSCTL_GET_RETRIEVAL_POINTERS`.

Mount path:
- `UDFMountVolume()` validates target device type and registry policy, handles removable-media check-verify/test-unit-ready spin-up, optionally locks media removal, creates the volume device object, initializes the VCB, reads disk geometry/UDF structures, initializes the write cache, and performs `UDFVInit()` plus disk verification.
- On normal media it selects cache mode based on media class/read-only/write mode, completes mount with `UDFCompleteMount()`, starts the eject waiter for writable media, fills VPB serial/label fields, marks `UDF_VCB_FLAGS_VOLUME_MOUNTED`, registers shutdown notification, and signals mount events.
- On failed UDF recognition it may attempt raw/blank mount unless ISO9660 is present; `UDFBlankMount()` creates a synthetic root containing a `Blank.CD` entry.
- Failure cleanup unlocks removable media, resets the device driver when needed, restores verify state, dismounts partial VCBs, deletes temporary volume devices, or passes the mount IRP down to a lower filesystem filter device.

Mount completion and residual cleanup:
- `UDFCompleteMount()` allocates the root FCB/name/file info, opens the root directory, initializes root NT FCB state, opens system stream directory and special files such as non-allocatable space and UID mapping, reads disk-specific config stream data, clears mount-time modified flags, initializes root common FCB header, and assigns ACLs.
- `UDFBlankMount()` builds a minimal root directory index for blank/raw media and disables fast I/O.
- `UDFCloseResidual()` releases special mount-time references such as non-allocatable file info, UID map, VAT, system stream directory, and root FCB chains.
- `UDFCleanupVCB()` frees VCB-owned caches, allocation bitmaps, statistics, labels, target names, buffers, write parameters, errors, and track maps.
- `UDFScanForDismountedVcb()` walks global VCBs and calls `UDFCheckForDismount()` for dismounting or unmounted residual VCBs.

Volume control helpers:
- `UDFStartEjectWaiter()` locks removable writable media, allocates an eject wait context, and queues `UDFEjectReqWaiter()`.
- `UDFIsVolumeMounted()` validates the open, verifies the VCB unless raw/locked, and returns success.
- `UDFGetStatistics()` copies per-processor filesystem statistics from the VCB.
- `UDFIsPathnameValid()` walks each path component, enforcing UDF name length and `UDFIsNameValid()`.
- `UDFLockVolume()` closes delayed files, verifies the VCB, flushes the logical volume, and locks only when open/reference counts indicate no other users.
- `UDFUnlockVolume()` clears VPB/UDFS lock state when the locker matches; the non-locked branch assigns multiple statuses and ultimately returns `STATUS_VOLUME_DISMOUNTED`.
- `UDFDismountVolume()` requires a locked volume with only residual references, runs `UDFDoDismountSequence()`, clears mounted/write-security state, and stops the eject waiter.
- `UDFGetVolumeBitmap()` validates user buffers, reports `VOLUME_BITMAP_BUFFER` data from `FSBM_Bitmap`, and protects access with `VCBResource`.
- `UDFGetRetrievalPointers()` validates/probes buffers and converts UDF extent mappings from `UDFReadFileLocation__()` into NT retrieval-pointer extents.
- `UDFIsVolumeDirty()` reports `VOLUME_IS_DIRTY` when the original integrity type is open.
- `UDFInvalidateVolumes()` requires `SeTcbPrivilege`, swaps in a fresh VPB for the target device, finds matching mounted VCBs, disables delayed close, dismounts them, stops eject waiting, and scans for final VCB teardown.

Notable behavior and dependencies:
- This file is tightly coupled to lower storage IOCTLs, VPB state, removable-media locking, UDF registry/config policy, UDF_INFO mount helpers, write-cache setup, delayed-close queues, and global VCB management.
- It supports both direct UDFS filesystem device objects and filter-device mount forwarding to a lower filesystem.
- The mount path contains several recovery/fallback paths: retry check-verify, raw mount, blank mount, device-driver reset, and lower-driver handoff.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/fscntrl.cpp -->