# Group Research: group_1701_reactos_sources_windows_reactos_drivers_filesystems_udfs_Include_us_0f0743db97c9

Scope checked against `Docs/research_subset_a.md`: these files are within `sources/windows/reactos`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/user_lib.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/user_lib.cpp

## Purpose
Implements user-mode helper routines shared by UDF/Optical tools around the ReactOS UDFS driver stack. It wraps Win32 service, registry, privilege, event, device-IOCTL, option lookup, and process-launch operations.

## Main Contents
- Defines `MediaTypeStrings[]` matching `JS_DEVICE_TYPE` values from `user_lib.h`.
- Provides small CRT-like helpers: `mymemchr`, `mystrrchr`, `mystrchr`, and `Exist`.
- Implements `MyMessageBox`, including resource-id handling and `FormatMessage` formatting.
- Implements service status lookup with `ServiceInfo`.
- Implements CD-ROM class upper-filter registration checks through `CheckCdrwFilter`.
- Provides registry helpers: `RegisterString`, `RegDelString`, `GetRegString`, `RegisterDword`, `GetRegUlong`, `SetRegUlong`.
- Implements `Privilege` for enabling/disabling token privileges and `IsWow64`.
- Creates globally accessible manual-reset events via `CreatePublicEvent`.
- Sends IOCTLs to a device handle through `UDFPhSendIOCTL`.
- Resolves optical device names with `UDFGetDeviceName`.
- Implements per-option read/write helpers from registry or disk config stream: `GetOptUlong`, `SetOptUlong`, and inherited lookup via `UDFGetOptUlongInherited`.
- Opens a volume with shared read fallback in `OpenOurVolume`.
- Converts drive letters to indexes with `drv_letter_to_index`.
- Launches configured tools with `LauncherRoutine2`.

## Dependencies and Interactions
- Heavy Win32 API use: SCM, registry, process, token, security descriptor, event, message box, file/device handle, and IOCTL APIs.
- Depends on UDFS/optical constants such as `CDROM_CLASS_PATH`, `REG_UPPER_FILTER_NAME`, `CDRW_SERVICE`, `UDF_CONFIG_STREAM_NAME`, `UDF_SERVICE_PARAM_PATH`, `UDF_KEY`, and `IOCTL_CDRW_GET_DEVICE_NAME`.
- Bridges user-mode tools to kernel/driver behavior through `DeviceIoControl`.

## Notable Details
- `UDFGetOptUlongInherited` applies option precedence: global service parameter, device-specific registry key, then disk-specific config stream.
- `UDFGetDeviceName` returns a pointer into a global `RealDeviceName` buffer, so callers must treat the result as non-reentrant shared state.
- `UDFPhSendIOCTL` returns `1` for success and `-1` for failure despite returning `ULONG`; the local `ret = GetLastError()` is not used.
- `GetRegString` opens/query registry data but does not close `hKey` on the success path.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/user_lib.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/user_lib.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/user_lib.h

## Purpose
Declares the user-mode utility API implemented by `user_lib.cpp`.

## Main Contents
- Defines `ODS` debug-output macro and `arraylen`.
- Defines optical media/device enum `JS_DEVICE_TYPE`.
- Declares `MediaTypeStrings`.
- Defines `JS_SERVICE_STATE`.
- Declares CRT-like helpers, message box wrapper, registry wrappers, service/filter helpers, privilege/WOW64/event helpers, IOCTL/device-name helpers, option helpers, volume-open helper, drive-letter conversion, and `LauncherRoutine2`.
- Defines option lookup depth constants:
  - `UDF_OPTION_GLOBAL`
  - `UDF_OPTION_MEDIASPEC`
  - `UDF_OPTION_DEVSPEC`
  - `UDF_OPTION_DISKSPEC`
  - `UDF_OPTION_MAX_DEPTH`

## Dependencies and Interactions
- Assumes Windows-style types are already available: `PCHAR`, `ULONG`, `HANDLE`, `HINSTANCE`, `HWND`, `LPCSTR`, `LPCTSTR`, `LPTSTR`, `WCHAR`, and related Win32 declarations.
- Used by user-mode UDF utilities that need shared registry, service, and device-control behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/user_lib.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/version.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/version.h

## Purpose
Central version macro header for UDF-related tools, libraries, resources, and driver components.

## Main Contents
Defines string and binary version macros for:
- `CHKUDF`: `0.2`
- `CDRW`: `0.69`
- `UDFFS`: `0.137`
- `UDFFMT`: `0.18`
- `UDFFORMAT`: `0.17`
- `UDFGUI`: `0.1`
- `JSSETUP`: `0.17`
- `LIBUDF`: `0.1`
- `JSREG`: `0.1`
- `BUGREPORT`: `0.1`
- `SHELLEXTUDF`: `0.6b`
- `COMMRES`: `0.1`

## Dependencies and Interactions
- Intended for resource/version metadata consumers.
- Contains only preprocessor constants; no include guard is present in this file.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/version.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/wcache_lib.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/wcache_lib.cpp

## Purpose
Implements the UDFS write/read cache library for block media. It supports ROM, rewritable, write-once, and RAM-like modes, including packet-sized read/modify/write behavior, cache eviction, direct cached-block access, flush/purge, bad-block policy flags, and limited async/chained I/O support.

## Main Contents
- Initializes cache metadata and backing tables in `WCacheInit__`.
- Maintains sorted lists of cached blocks, modified blocks, and cached frames.
- Uses frame-based cache organization where each frame contains per-block cache entries.
- Implements random/heuristic eviction through `WCacheFindLbaToRelease`, `WCacheFindModifiedLbaToRelease`, and `WCacheFindFrameToRelease`.
- Implements sorted-list helpers:
  - `WCacheGetSortedListIndex`
  - `WCacheInsertRangeToList`
  - `WCacheInsertItemToList`
  - `WCacheRemoveRangeFromList`
  - `WCacheRemoveItemFromList`
- Allocates/removes cache frames through `WCacheInitFrame` and `WCacheRemoveFrame`.
- Encodes modified flags in low pointer bits through `WCacheSetModFlag`, `WCacheClrModFlag`, `WCacheGetModFlag`, and `WCacheSectorAddr`.
- Implements packet update/writeback through `WCacheUpdatePacket` and `WCacheUpdatePacketComplete`.
- Enforces limits with mode-specific implementations:
  - `WCacheCheckLimitsRW`
  - `WCacheCheckLimitsRAM`
  - `WCacheCheckLimitsR`
- Implements read path in `WCacheReadBlocks__`, including direct large reads and caching newly read sectors.
- Implements write path in `WCacheWriteBlocks__`, including write-through optimization for aligned writes and modified-list tracking.
- Implements full flush/purge:
  - `WCacheFlushAll__`
  - `WCachePurgeAll__`
  - `WCacheFlushAllRW`
  - `WCachePurgeAllRW`
  - `WCacheFlushAllRAM`
  - `WCachePurgeAllRAM`
  - `WCachePurgeAllR`
- Implements range flush in `WCacheFlushBlocks__` and `WCacheFlushBlocksRW`.
- Implements direct cache access through `WCacheStartDirect__`, `WCacheDirect__`, `WCacheEODirect__`, and `WCacheIsCached__`.
- Implements WORM relocation-table synchronization through `WCacheSyncReloc__`.
- Implements cache discard through `WCacheDiscardBlocks__`.
- Implements async completion callback `WCacheCompleteAsync__`.
- Parses and mutates cache flags through `WCacheDecodeFlags` and `WCacheChFlags__`.

## Dependencies and Interactions
- Depends on callback APIs declared in `wcache_lib.h`: physical read/write, async read/write, block-used checks, relocation updates, and error handling.
- Uses kernel synchronization via `ERESOURCE` and resource acquire/release calls.
- Uses UDFS allocation/debug wrappers such as `MyAllocatePoolTag__`, `MyFreePool__`, `DbgAllocatePoolWithTag`, `DbgFreePool`, `DbgCopyMemory`, and `DbgMoveMemory`.
- Relies on caller-supplied `CheckUsedProc` to distinguish used, zero, and bad blocks.
- Relies on `UpdateRelocProc` for write-once media relocation behavior.

## Notable Details
- Async support exists structurally but comments say it is not completely implemented; initialization disables async write for WORM mode.
- Cache entries store flags in low pointer bits, requiring alignment assumptions and `WCACHE_ADDR_MASK`.
- `WCacheRelease__` frees many internal allocations, but its checks for `tmp_buff` and `reloc_tab` use `Cache->CachedFramesList` rather than the specific pointer fields.
- `WCacheDiscardBlocks__` loops using `while((List[i] < end) && (i < Cache->BlockCount))`, evaluating `List[i]` before checking bounds.
- The RAM path flushes contiguous modified sectors directly, while RW/ROM paths use packet update semantics.
- WORM mode packs modified blocks into relocation packets and writes through `WriteProc` with `NULL` LBA, relying on callback semantics.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/wcache_lib.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/wcache_lib.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/wcache_lib.h

## Purpose
Public header for the UDFS write-cache library implemented by `wcache_lib.cpp`.

## Main Contents
- Includes `platform.h`, and conditionally `env_spec_w32.h` for console builds.
- Defines callback types:
  - `PWRITE_BLOCK`
  - `PREAD_BLOCK`
  - `PWRITE_BLOCK_ASYNC`
  - `PREAD_BLOCK_ASYNC`
  - `PCHECK_BLOCK`
  - `PUPDATE_RELOC`
  - `PWC_ERROR_HANDLER`
- Defines block-state bits: `WCACHE_BLOCK_USED`, `WCACHE_BLOCK_ZERO`, `WCACHE_BLOCK_BAD`.
- Defines error context structure `WCACHE_ERROR_CONTEXT`.
- Defines cache entry, frame, and main `W_CACHE` structures.
- Defines cache modes:
  - `WCACHE_MODE_ROM`
  - `WCACHE_MODE_RW`
  - `WCACHE_MODE_R`
  - `WCACHE_MODE_RAM`
  - `WCACHE_MODE_EWR` planned but excluded by `WCACHE_MODE_MAX`
- Defines pointer/flag masks and cache flags such as whole-packet caching, no-compare, chained I/O, bad-block handling, and no-write-through.
- Declares public cache API functions for init, read, write, flush, purge, release, direct access, mode changes, relocation sync, discard, and flag mutation.
- Declares async completion callback `WCacheCompleteAsync__`.

## Dependencies and Interactions
- Exposes kernel-style types and synchronization fields, including `ERESOURCE`.
- Designed for inclusion from C++ while exporting C-compatible declarations via `extern "C"`.
- The `W_CACHE` struct is not opaque, so callers can inspect or mutate cache internals if they include this header.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/wcache_lib.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/zw_2_nt.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/zw_2_nt.h

## Purpose
Small compatibility header that maps selected `Zw*` native calls to `Nt*` names when building in `NT_NATIVE_MODE`.

## Main Contents
- Include guard `__Zw_to_Nt__NameConvert__H__`.
- Under `NT_NATIVE_MODE`, defines:
  - `ZwClose` as `NtClose`
  - `ZwOpenKey` as `NtOpenKey`
  - `ZwQueryValueKey` as `NtQueryValueKey`
- Contains commented-out pool allocation macro substitutions.

## Dependencies and Interactions
- Used where the same code may target kernel-style `Zw*` APIs or native-mode `Nt*` APIs.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/zw_2_nt.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/cleanup.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/cleanup.cpp

## Purpose
Handles IRP cleanup for the UDFS driver. Cleanup is where open handles are retired, share access is removed, byte-range locks are cleared, delete-on-close is processed, cache maps are flushed/uninitialized, timestamps and directory-index metadata are updated, and file-info chains are closed.

## Main Contents
- `UDFCleanup` is the dispatch entry point:
  - Handles cleanup against the filesystem device object directly.
  - Allocates IRP context for volume/file cleanup.
  - Uses top-level IRP tracking and structured exception handling.
- `UDFCommonCleanup` performs the main cleanup work:
  - Extracts `FileObject`, `Ccb`, `Fcb`, `Vcb`, and NT-required FCB data.
  - Handles volume cleanup separately, including handle counts, verify-volume flag, lock release, cache-map uninitialization, optional device reset, and share-access removal.
  - Acquires parent/current FCB resources for file cleanup.
  - Decrements open-handle and VCB-handle counts.
  - Processes `UDF_CCB_DELETE_ON_CLOSE` into `UDF_FCB_DELETE_ON_CLOSE`.
  - Unlocks all byte-range locks for non-directory files.
  - Handles stream deletion marking and parent deletion propagation.
  - Flushes/unlinks files on delete-on-close when last handle closes.
  - Issues directory/file/stream notifications for delete or modification.
  - Flushes/purges cache sections when needed.
  - Updates archive bit, write/access/change times, and directory-index file sizes.
  - Calls `CcUninitializeCacheMap`.
  - Releases resources and calls `UDFCloseFileInfoChain`.
  - Removes share access, recalculates fast-I/O possibility, and marks `FO_CLEANUP_COMPLETE`.
- `UDFCloseFileInfoChain` walks up a file-info parent chain:
  - Acquires parent/current resources.
  - Writes security when needed.
  - Calls `UDFCloseFile__` for each file info.
  - Releases resources as it climbs toward root.

## Dependencies and Interactions
- Uses Windows filesystem APIs: `FsRtlEnterFileSystem`, `IoCompleteRequest`, `FsRtlFastUnlockAll`, `FsRtlNotifyCleanup`, `FsRtlNotifyFullChangeDirectory`, `CcFlushCache`, `CcPurgeCacheSection`, `CcUninitializeCacheMap`, and `IoRemoveShareAccess`.
- Coordinates tightly with UDFS FCB/CCB/VCB lifetime, delete-on-close, stream directory handling, delayed/system close queues, and notification logic.
- Calls many UDFS helpers: `UDFFlushFile__`, `UDFUnlinkFile__`, `UDFMarkStreamsForDeletion`, `UDFPretendFileDeleted__`, `UDFCloseFileInfoChain`, `UDFSetFileXTime`, `UDFSetFileSizeInDirNdx`, and `UDFCloseFile__`.

## Notable Details
- Cleanup and close are split: cleanup handles handle-visible semantics and cache/share cleanup; close handles object lifetime.
- Delete-on-close has special stream and linked-file behavior; multi-link files avoid forced cache purge.
- The function carefully releases and reacquires resources around deletion and close-chain operations to avoid holding incompatible locks.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/cleanup.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/close.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/close.cpp

## Purpose
Handles IRP close for the UDFS driver. Close is responsible for freeing CCBs, decrementing open/reference counts, queueing or executing delayed close, cleaning FCB/file-info chains, processing final volume close/dismount checks, and flushing/purging delayed-close objects in directories.

## Main Contents
- `UDFClose` is the close dispatch entry:
  - Handles filesystem-device-object closes directly.
  - Allocates IRP context.
  - Invokes `UDFCommonClose` under top-level IRP and exception handling.
- `UDFCommonClose`:
  - Extracts `FileObject`, `Ccb`, `Fcb`, and `Vcb` for normal IRP close, or uses saved FCB/tree length for queued close.
  - Cleans and detaches the CCB.
  - Attempts delayed close when enabled and eligible.
  - Posts recursive/not-top-level close work when needed.
  - Decrements CCB count and VCB open counts.
  - Handles volume close specially, including global/Vcb resource ordering, write-status reset IOCTL, and dismount checks.
  - For file closes, calls `UDFCleanUpFcbChain`.
  - Completes IRP and releases IRP context unless posted.
- `UDFCleanUpFcbChain`:
  - Walks from a file-info node toward the root.
  - Decrements references for the open path.
  - Flushes files before final cleanup.
  - Handles delete-parent propagation.
  - Clears `fi->Fcb` and common-FCB links before lower-level cleanup.
  - Frees NT-required FCB resources, byte-range lock structures, ACL state, FCBs, and file-info allocations when safe.
  - Stops when it reaches referenced objects.
- Delayed-close machinery:
  - `UDFDoDelayedClose` converts a lite context back to a full IRP context and calls `UDFCommonClose`.
  - `UDFDelayedClose` drains file and directory delayed-close queues down to configured minimums.
  - `UDFCloseAllDelayed` drains all delayed closes for a VCB.
  - `UDFQueueDelayedClose` creates lite close contexts, inserts them into file or directory queues, tracks thresholds, and queues worker work.
- Directory subtree delayed-close support:
  - `UDFBuildTreeItemsList` recursively walks stream directories and directory indexes, avoiding repeated linked objects.
  - `UDFIsInDelayedCloseQueue` and `UDFIsLastClose` are selection callbacks.
  - `UDFCloseAllXXXDelayedInDir` finds delayed or system-cache-backed objects under a directory, then either flushes/purges system cache sections or removes internal delayed-close queue entries.

## Dependencies and Interactions
- Uses filesystem and memory-manager/cache-manager APIs such as `CcFlushCache`, `CcPurgeCacheSection`, `MmFlushImageSection`, and worker queue APIs.
- Coordinates with global delayed-close queues in `UDFGlobalData`.
- Calls UDFS-specific object lifetime helpers such as `UDFCleanUpCCB`, `UDFCleanUpFCB`, `UDFCleanUpFile__`, `UDFCloseFile__`, `UDFFlushFile__`, `UDFUnlinkFile__`, `UDFCheckForDismount`, and IRP-context lite conversion helpers.
- Uses `IOCTL_CDRW_RESET_WRITE_STATUS` on final volume close.

## Notable Details
- Close always returns success to the I/O manager, as expected for filesystem close dispatch.
- Delayed close is suppressed for delete-on-close and posted-rename FCBs.
- `UDFBuildTreeItemsList` allocates growing arrays in `TREE_ITEM_LIST_GRAN` chunks and avoids repeated traversal of linked file-info objects.
- `UDFCloseAllXXXDelayedInDir` can operate in “system” mode to flush/purge cache sections, or internal mode to drain delayed-close queue entries.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/close.cpp -->