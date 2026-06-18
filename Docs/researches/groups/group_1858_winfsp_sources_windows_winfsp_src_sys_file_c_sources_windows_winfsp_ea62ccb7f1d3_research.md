# Group Research: group_1858_winfsp_sources_windows_winfsp_src_sys_file_c_sources_windows_winfsp_ea62ccb7f1d3

Scope: `Docs/research_subset_a.md` includes `sources/windows/winfsp`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/file.c -->
# File Research: sources/windows/winfsp/src/sys/file.c

## Role

Core WinFsp file-node and file-description implementation. This file manages the kernel in-memory representation of opened filesystem objects: lifetime, context-table membership, share access, ERESOURCE locking, cache metadata, named stream coordination, cleanup/close, rename propagation, notifications, byte-range locks, and helper opens of main files.

## Main Structures And State

The central object is `FSP_FILE_NODE`, stored in `FILE_OBJECT->FsContext` elsewhere in the driver. It owns or references:

- `FSRTL_ADVANCED_FCB_HEADER Header`, with file sizes, section object pointers, and main/paging resources.
- `FSP_FILE_NODE_NONPAGED`, allocated separately for resources, fast mutex, spin lock, section pointers, and nonpaged metadata-cache handles.
- Context-table entries keyed both by user context and by file name.
- Share-access counters and extra WinFsp counters: `ActiveCount`, `OpenCount`, `HandleCount`, delete-pending state, stream delete-denial counters, POSIX-delete state, and cache change numbers.
- Cached basic/file info plus cached security, directory, stream, and EA blobs in volume-level `FspMetaCache` instances.

`FSP_FILE_DESC`, stored in `FILE_OBJECT->FsContext2`, tracks per-handle state such as granted access, user context2, directory enumeration pattern/marker, delete-on-close/POSIX delete, disposition retry status, metadata flags, and optional main-file handle/object.

## Important Entry Points

- `FspFileNodeCreate` / `FspFileNodeDelete`: allocate and tear down file nodes, resources, file locks, oplocks, per-stream contexts, volume references, and metadata-cache entries.
- `FspFileNodeAcquire*F`, `TryAcquire*F`, `Release*F`, `ReleaseOwner*F`: wrapper layer around main and paging I/O ERESOURCE acquisition, with top-level IRP flag tracking to assert lock state.
- `FspFileNodeOpen`: inserts or finds a node in the volume name table, enforces delete-pending and share-access rules, handles main-file/named-stream delete sharing behavior, and bumps active/open/handle counts.
- `FspFileNodeCleanup`, `CleanupFlush`, `CleanupComplete`, `Close`: drive delete-on-close, POSIX delete, cache uninitialization, context-table removal, share-access removal, count decrements, and final dereference.
- `FspFileNodeFlushAndPurgeCache`: wraps cache manager flush/purge paths, using `CcCoherencyFlushAndPurgeCache` when available and falling back to `CcFlushCache`/`CcPurgeCacheSection`.
- `FspFileNodeOverwriteStreams`, `CheckBatchOplocksOnAllStreams`, `RenameCheck`, `Rename`: handle named stream invalidation and recursive rename behavior across descendants.
- `FspFileNodeGet/TryGet/Set/TrySet/InvalidateFileInfo`: maintain cached WinFsp file info and synchronize Cc file sizes.
- `FspFileNodeReference/Set/TrySet/InvalidateSecurity`, `DirInfo`, `StreamInfo`, `Ea`: per-node metadata-cache handles protected by the node lock and, for invalidation races, `NpInfoSpinLock`.
- `FspFileNodeNotifyChange` and `FspFileNodeInvalidateCachesAndNotifyChangeByName`: translate file vs stream notifications, invalidate relevant caches, and report changes.
- `FspFileNodeProcessLockIrp`: delegates byte-range locking to `FsRtlProcessFileLock`.
- `FspFileDescCreate/Delete/ResetDirectory/SetDirectoryMarker`: handle per-open directory enumeration state.
- `FspMainFileOpen/Close`: opens the main file for stream operations using an ECP GUID and `IoCreateFileEx`.
- `FspFileNodeOplockPrepare/Complete`: support oplock break work-item handoff.

## Control Flow And Algorithms

The file-node open path first locks the volume context table. It may insert the new node or reuse an existing node with the same name. It performs special named-stream vs main-file sharing checks, checks delete-pending, asks the I/O manager share-access routines to validate or update `ShareAccess`, and then increments WinFsp’s own active/open/handle counters. On first active use it links the node into the volume active list.

Cleanup is split into decision, optional flush, and completion phases. `FspFileNodeCleanup` computes whether delete or truncate-on-close should happen. `FspFileNodeCleanupComplete` removes share access, possibly deletes the file node from the name table, propagates deletion to open stream nodes, updates file sizes for delete/truncate, resets truncate-on-close, calls `CcUninitializeCacheMap`, and dereferences nodes removed from the context table.

Rename is descendant-aware. `GATHER_DESCENDANTS` enumerates name-table entries under a prefix, optionally references them, and grows from a 16-entry stack array to heap allocation when needed. `FspFileNodeRenameCheck` blocks unsafe renames: it checks replaced targets, image sections, cleaned-up-but-open mapped files, descendant handles, POSIX rename exceptions, and batch/handle oplocks. `FspFileNodeRename` then removes each descendant from the name table, rewrites its file name by replacing the old prefix with the new one, reinserts it, and handles collisions with replaced open nodes.

Metadata caching uses volume-level meta caches. File info has expiration timestamps and change numbers; security/dir/stream/EA caches store opaque buffers by cache item id in `NonPaged`. Try-set functions compare the saved change number from request preparation to detect intervening mutations before accepting a user-mode response.

## Concurrency And Locking

The main synchronization layers are:

- Volume context-table lock for name/context lists and open/handle counters.
- `Header.Resource` for main file-node state.
- `Header.PagingIoResource` for paging I/O coordination.
- Volume rename resource, held externally during rename operations.
- `NpInfoSpinLock` for cache-handle invalidation races against setters.
- FSRTL file locks and oplocks.

Lock wrappers normalize stream nodes to their main file when needed and store lock flags in the current top-level IRP. Owner-based release is used for IRPs posted to user mode, allowing request finalizers to release locks even on cancellation or retry.

## Integration Points

This file is foundational for `create.c`, `cleanup.c`, `dirctl.c`, `fileinfo.c`, `flush.c`, `fsctl.c`, `read.c`, `write.c`, and `security.c`. It depends heavily on helpers from the WinFsp sys layer: context-table APIs, IOQ/request APIs, Cc wrappers, notify helpers, file-name helpers, meta-cache helpers, and volume parameters.

## Edge Cases And Risks

- Many behaviors intentionally emulate NTFS/FastFat and are documented as experimentally derived, especially main-file/named-stream share violations and POSIX rename behavior.
- Rename completion can block by design, which is unusual for IRP completion paths but documented here as intentional.
- `FspFileNodeSetFileInfo` has a complex recovery path when `CcSetFileSizes` fails; it flushes, purges, uninitializes cache maps, and waits for cache teardown while holding the file-node lock.
- Metadata invalidation invalidates cache items but does not always clear the stored item id; correctness relies on meta-cache semantics and reference failures after invalidation.
- The descendant macros store low-bit flags in file-node pointers, relying on pointer alignment.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/file.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/fileinfo.c -->
# File Research: sources/windows/winfsp/src/sys/fileinfo.c

## Role

Implements `IRP_MJ_QUERY_INFORMATION`, `IRP_MJ_SET_INFORMATION`, and fast I/O query paths for WinFsp filesystem volumes. It translates Windows `FILE_INFORMATION_CLASS` requests into local cached responses or user-mode WinFsp transactions, updates file-node state on completion, and handles disposition and rename semantics.

## Query Information

The query side supports:

- `FileAllInformation`
- `FileAttributeTagInformation`
- `FileBasicInformation`
- `FileEaInformation`
- `FileInternalInformation`
- `FileNameInformation`
- `FileNormalizedNameInformation`
- `FileNetworkOpenInformation`
- `FilePositionInformation`
- `FileStandardInformation`
- `FileStreamInformation`
- `FileStatInformation` and `FileStatLxInformation` when WSL features are enabled

Unsupported or rejected classes include compression, hard links, alternate short names, and invalid defaults.

The small `FspFsvolQuery*Information` helpers write specific Windows structures into the caller buffer, handling buffer-too-small/overflow behavior. `FileAllInformation` has a two-phase path: first validates/fills name data, then later overlays cached or returned file info.

For most metadata classes, `FspFsvolQueryInformation` first validates output space, acquires the file node, and tries `FspFileNodeTryGetFileInfo`. If cached file info is valid, it fills the buffer synchronously. Otherwise it posts `FspFsctlTransactQueryInformationKind` to user mode, saves request context including the file node and all-information state, and releases owner locks on completion.

`FileStreamInformation` has a separate stream-info cache. `FspFsvolQueryStreamInformationCopy` converts WinFsp `FSP_FSCTL_STREAM_INFO` records into Windows `FILE_STREAM_INFORMATION`, appending `:$DATA`, setting `NextEntryOffset`, and returning overflow when only partial stream names fit.

`FileStatLxInformation` also queries Linux metadata EAs `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV` through `FspSendQueryEaIrp` when extended attributes are enabled.

## Set Information

The set side supports:

- `FileAllocationInformation`
- `FileBasicInformation`
- `FileEndOfFileInformation`
- `FilePositionInformation`
- `FileDispositionInformation`
- `FileDispositionInformationEx`
- `FileRenameInformation`
- `FileRenameInformationEx`

It rejects hard links, valid data length, unsupported POSIX variants when the volume does not advertise support, and invalid lengths.

Allocation and EOF setters validate truncation with `MmCanFileBeTruncated`, populate the user-mode request, and on successful response update file info, mark `FO_FILE_MODIFIED`, and notify size changes.

Basic information validates attributes, strips/forces normal and directory bits appropriately, maps `-1` timestamp values to “do not update” zero fields in the WinFsp request, and on completion updates file info, per-handle metadata flags, `FO_TEMPORARY_FILE`, and change notifications.

Position information is handled locally by setting `FileObject->CurrentByteOffset` under the main resource.

Disposition handling performs delete-pending setup. It supports classic and extended disposition flags, rejects root deletion, blocks already POSIX-deleted nodes, checks oplocks, checks image sections with `MmFlushImageSection`, optimizes repeated Windows 10/11 POSIX-delete retry patterns through `FileDesc->DispositionStatus`, and can avoid posting to user mode when `PostDispositionWhenNecessaryOnly` allows a local readonly/cached check. Successful completion updates file-node and file-object delete-pending state and notifies delete-pending directories.

Rename handling validates target names, rejects root and stream rename, optionally captures a subject security context for replace-if-exists, acquires the volume rename resource and file-node resources, uses `FspFileNodeRenameCheck` for old and new names, posts the rename to user mode, and on success emits old/new rename notifications and calls `FspFileNodeRename` to rewrite in-memory descendant names.

`FspFsvolSetInformationPrepare` converts a captured replace-if-exists subject context into a user-mode impersonation token handle and packs the originating process id plus handle into the request. The request finalizer closes this token in the correct process context, releases subject contexts, file-node locks, and the volume rename resource.

## Completion And Retry Model

Query and stream-query completions validate response buffers, save current cache change numbers, release owner-held file-node resources, then try to reacquire exclusive access. If reacquisition fails, they save the response in the IRP request and ask the IOQ to retry completion later. If reacquisition succeeds, they set file/stream info only when the change number still matches; otherwise they use existing cache or response data without overwriting newer state.

Set completions special-case failed disposition requests to store retry status. Successful disposition and rename use dedicated completion helpers; allocation/basic/EOF use the same helper triplets as preparation, with `Response` non-null.

## Fast I/O

`FspFastIoQueryBasicInfo`, `FspFastIoQueryStandardInfo`, and `FspFastIoQueryNetworkOpenInfo` opportunistically answer from valid file-node cached info when the main resource can be acquired. `FspFastIoQueryOpen` supports kernel-mode opens only when `AllowOpenInKernelMode` is set, rejects relative opens, and looks up cached file info by name with access checks.

## Integration Points

This file is the metadata bridge between Windows IRPs and user-mode filesystem transactions. It relies on `file.c` for node locks, cached metadata, rename checks, notifications, and file-info mutation; on `iop.c` for request creation/retry/finalization; on `security.c`/send helpers for security and EA queries; and on volume parameters for feature switches.

## Edge Cases And Risks

- Several information classes are identified by numeric constants `68` and `70`, indicating compatibility with headers where names may not exist.
- Rename and disposition semantics mirror NTFS/FastFat behavior with documented Windows quirks around POSIX delete retries and readonly deletion documentation mismatches.
- User-mode response buffers are bounds-checked before use; stream responses are also copied into cache only when change numbers still match.
- Request finalization is critical: many paths hold file-node resources or captured security/token handles across user-mode transactions.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/fileinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/flush.c -->
# File Research: sources/windows/winfsp/src/sys/flush.c

## Role

Implements `IRP_MJ_FLUSH_BUFFERS` for WinFsp filesystem volumes. It flushes kernel cache state locally, then posts a flush transaction to the user-mode filesystem so backing storage can be synchronized.

## Main Flow

`FspFlushBuffers` dispatches only for `FspFsvolDeviceExtensionKind`; other device kinds return `STATUS_INVALID_DEVICE_REQUEST`.

`FspFsvolFlushBuffers` has two modes:

- Volume/root flush: if `FileObject->FsContext` is not a valid file node or the file node is the root directory, this is treated as a whole-volume flush.
- File flush: for regular file nodes, it flushes that file’s cache and posts a per-file user-mode flush.

For a whole-volume flush, the code copies the list of open file nodes using `FspFileNodeCopyOpenList`, clears the top-level IRP to avoid resource deadlocks, flushes non-directory file cache sections in reverse list order, restores the top-level IRP, deletes the copied list, then creates a request with a null user context. The null context is the protocol signal for “flush whole volume.” It records the local flush result in request context.

For a file flush, directories succeed immediately because there is no meaningful directory cache flush. Regular files are acquired exclusive with full locking, `FspCcFlushCache` is called on the file object section pointers, and a `FspFsctlTransactFlushBuffersKind` request is posted with both user contexts. The file node is marked as owner-held by the request so cancellation/finalization can release it.

## Completion

`FspFsvolFlushBuffersComplete` combines two result sources:

- The user-mode response status.
- The local cache flush result saved in request context for whole-volume flushes.

If both succeed and this is a real file node rather than volume/root, it updates file info from `Response->Rsp.FlushBuffers.FileInfo` with truncate-on-close enabled.

`FspFsvolFlushBuffersRequestFini` releases owner-held file-node locks when a posted per-file request is canceled or otherwise finalized before normal completion.

## Integration Points

This file uses `file.c` for open-list copying, full-resource acquisition, owner release, and file-info updates. It uses `iop.c` request creation/finalization and the WinFsp transaction kind consumed by user-mode dispatch.

## Edge Cases And Risks

- Whole-volume flush intentionally resets `IoSetTopLevelIrp(0)` during local cache flushes to avoid recursive resource deadlocks.
- Reverse-order volume flush is intended to flush children before containing directories, although directories are skipped.
- Directory flush returns success without posting to user mode.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/flush.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/fsctl.c -->
# File Research: sources/windows/winfsp/src/sys/fsctl.c

## Role

Implements `IRP_MJ_FILE_SYSTEM_CONTROL` dispatch for both the WinFsp control device and mounted filesystem volume devices. It routes private WinFsp FSCTLs, mount/volume operations, reparse point operations, oplocks, statistics, persistent volume state, and retrieval pointers.

## Control Device Path

`FspFsctlFileSystemControl` handles the fsctl/control device:

- Mount-device and mount-manager setup.
- Volume name and volume list queries.
- Transaction FSCTLs: normal, batch, and internal.
- Stop/stop0 shutdown sequencing.
- Notifications.
- Driver unload.
- Extension-provider FSCTLs in the private control-code range.
- Mount-volume minor function.

The STOP/STOP0 comment documents an important protocol change: `FSP_FSCTL_STOP0` stops the IOQ without canceling active IRPs, allowing dispatcher threads to drain before `FSP_FSCTL_STOP` cancels remaining IRPs.

## Volume Device Path

`FspFsvolFileSystemControl` handles mounted volume FSCTLs:

- Work queue FSCTLs: `FSP_FSCTL_WORK`, `FSP_FSCTL_WORK_BEST_EFFORT`.
- Query WinFsp / `FSCTL_IS_VOLUME_MOUNTED`.
- Reparse point get/set/delete.
- Oplock requests and acknowledgements.
- `FSCTL_QUERY_PERSISTENT_VOLUME_STATE`.
- `FSCTL_FILESYSTEM_GET_STATISTICS`.
- `FSCTL_GET_RETRIEVAL_POINTERS`.

## Reparse Points

`FspFsvolFileSystemControlReparsePoint` validates volume support, file-object validity, buffers, access rights, and reparse payloads. For set/delete it validates the input reparse data, enforces write-related access, optionally checks symlink privilege when requested by volume parameters, and computes `TargetOnFileSystem` for absolute symlink targets that point back into the same filesystem. It then posts `FspFsctlTransactFileSystemControlKind` with the file name and input buffer.

For get, it validates output buffer presence and posts a read request under shared full locking. Completion validates the returned reparse buffer, ensures it fits, copies it to the caller buffer, and sets `IoStatus.Information`. Write completion invalidates file info and marks per-handle reparse/metadata flags.

## Oplocks

`FspFsvolFileSystemControlOplock` validates the file node and FSCTL buffers, acquires the file node exclusive for requests or shared for acknowledgements, computes the FSRTL oplock count source, blocks batch/filter/handle oplocks on delete-pending files, hooks the IRP completion, clears top-level IRP, and delegates to `FspFileNodeOplockFsctl`. FSRTL owns completion after this point, so the code returns with `FSP_STATUS_IGNORE_BIT`.

The completion hook queues a delayed work item that dereferences the volume device and frees the completion context. This compensates for the normal WinFsp completion path being bypassed by FSRTL-owned oplock IRPs.

## Other FSCTLs

`FspFsvolFileSystemControlQueryPersistentVolumeState` reports short-name creation disabled when the input request version and mask match expectations.

`FspFsvolFileSystemControlGetStatistics` copies volume statistics into the output buffer.

`FspFsvolFileSystemControlGetRetrievalPointers` provides a synthetic non-resident mapping: one extent with `Lcn = -1`, `NextVcn = AllocationSize / AllocationUnit`. It probes user buffers manually for the method-neither FSCTL and returns `STATUS_END_OF_FILE` when the starting VCN is beyond EOF.

## Completion And Finalization

`FspFsvolFileSystemControlComplete` ignores work FSCTLs with no `FileObject`, maps successful reparse completions to read/write helpers, then releases owner-held file-node locks. `FspFsvolFileSystemControlRequestFini` handles cancellation cleanup.

## Integration Points

This file connects user-mode transactions, `file.c` file-node locking/cache invalidation, `volume.c` control operations, FSRTL oplock APIs, MUP/provider checks for symlink target classification, and statistics helpers.

## Edge Cases And Risks

- Reparse-point symlink target classification has several MUP and volume-prefix branches and tolerates failures by leaving `TargetOnFileSystem` zero.
- Oplock IRPs intentionally bypass normal completion and require the hook/work-item cleanup path.
- Retrieval-pointers support is compatibility-oriented, not real allocation mapping.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/fsctl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/fsext.c -->
# File Research: sources/windows/winfsp/src/sys/fsext.c

## Role

Implements the WinFsp filesystem extension-provider registry and transaction helper. It allows external kernel providers to register custom FSCTL transaction handlers and lets the main driver lazily load providers based on registry configuration.

## Provider Registry

The provider registry is intentionally small and simple:

- Maximum providers: `FSP_FSEXT_PROVIDER_COUNTMAX` = 16.
- Storage: parallel arrays of control codes and provider pointers.
- Synchronization: `FsextSpinLock`.
- Lookup: linear scan by `DeviceTransactCode`.

`FspFsextProviderRegister` finds an empty slot, writes the provider’s device-extension offset to `FSP_FSVOL_DEVICE_EXTENSION.FsextData`, stores the provider control code and pointer, and returns `STATUS_TOO_LATE` if all slots are full.

## Lazy Loading

`FspFsextProvider` first checks the in-memory registry. If no provider is found and the caller supplied `PLoadResult`, it looks under `FSP_REGKEY\Fsext` for a registry value named as the 8-digit hex control code. The value must be `REG_SZ` naming a service. The function builds the service registry path under `CurrentControlSet\Services`, calls `ZwLoadDriver`, tolerates `STATUS_IMAGE_ALREADY_LOADED`, then checks the in-memory registry again. It returns `STATUS_OBJECT_NAME_NOT_FOUND` if the driver loaded but did not register the expected provider.

## Transactions

`FspFsextProviderTransact` builds a synchronous internal transaction IRP to WinFsp using `IoBuildDeviceIoControlRequest(FSP_FSCTL_TRANSACT_INTERNAL)`. Because that helper builds an IOCTL IRP without a file object, this function patches the next stack location to be `IRP_MJ_FILE_SYSTEM_CONTROL`, minor `IRP_MN_USER_FS_REQUEST`, and sets `FileObject`. It also marks the IRP as `IRP_SYNCHRONOUS_API` so `CancelSynchronousIo` can cancel it.

The function asserts that special kernel APCs are enabled, matching the documented `IoBuildDeviceIoControlRequest` caveat.

## Integration Points

This file is used by the private FSCTL dispatch path in `fsctl.c` for extension control codes. It includes public extension definitions from `<winfsp/fsext.h>` and relies on registry helpers plus normal Windows driver loading.

## Edge Cases And Risks

- Registration has no duplicate-control-code check; a later provider with a duplicate code could occupy another slot, but lookup returns the first match.
- The fixed 16-provider limit is deliberate because lookup is linear.
- Transaction IRPs are patched from device-control shape into filesystem-control shape, so correctness depends on stack-location fields being set consistently.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/fsext.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/iop.c -->
# File Research: sources/windows/winfsp/src/sys/iop.c

## Role

Central IRP/request plumbing for WinFsp. This file allocates and frees `FSP_FSCTL_TRANSACT_REQ` objects, attaches them to IRPs, posts kernel work requests back through the filesystem-control path, completes IRPs, supports cancellation, stores retry responses, and dispatches major-function prepare/complete callbacks.

## Request Allocation

`FspIopCreateRequestFunnel` allocates a request header plus aligned transaction request and optional extra filename buffer. Requests and headers must be 16-byte aligned because low pointer bits are used for flags elsewhere. If required alignment exceeds pool alignment, the original allocation pointer is saved immediately before the aligned header.

Flags control:

- Must-succeed vs normal allocation.
- Paged vs nonpaged pool.
- Optional nonpaged work-item allocation.

The function zeroes header/request memory, stores the request finalizer and work item, fills request size and hint with the originating IRP pointer, copies an optional file name into `Request->Buffer`, sets `Request->FileName.Size`, asserts alignment, and attaches the request to the IRP.

`FspIopCreateRequestWorkItem` lazily adds a nonpaged work-item structure to an existing request.

`FspIopDeleteRequest` invokes the request finalizer with its context, frees saved retry response, frees work item, restores the original allocation pointer if over-aligned, and frees the allocation.

`FspIopResetRequest` runs the old finalizer, clears request context, and installs a new finalizer while preserving the request object.

## Posting Work Requests

`FspIopPostWorkRequestFunnel` creates a kernel IRP targeting a device object and sends it as `IRP_MJ_FILE_SYSTEM_CONTROL` with `FSP_FSCTL_WORK` or `FSP_FSCTL_WORK_BEST_EFFORT`. It passes the request through method-neither input, installs a completion routine that frees the IRP, and deletes the request itself if `IoCallDriver` does not return pending.

This path is used for internal work requests not directly attached to an existing user IRP.

## Completion And Cancellation

`FspIopCompleteIrpEx` deletes any attached request, extracts the device object before completion, updates create statistics when appropriate, zeroes `IoStatus.Information` for most non-success statuses, sets final status, completes the IRP, and optionally dereferences the device object.

`FspIopCompleteCanceledIrp` logs cancellation, enters filesystem context, sets the top-level IRP to the canceled IRP, completes it with `STATUS_CANCELLED`, restores the old top-level IRP, and exits filesystem context. This protects request finalizers that release ERESOURCE locks.

## Retry Support

`FspIopRetryPrepareIrp` reposts an IRP to the IOQ best-effort path when preparation must be retried.

`FspIopRetryCompleteIrp` saves a copy of the user-mode response in the request header via `FspIopSetIrpResponse`, then asks the IOQ to retry completion later.

`FspIopIrpResponse` retrieves the saved copied response.

This is used by files such as `fileinfo.c`, `dirctl.c`, and `security.c` when they cannot reacquire locks during completion.

## Dispatch Tables

`FspIopDispatchPrepare` and `FspIopDispatchComplete` call major-function-specific function pointers from `FspIopPrepareFunction` and `FspIopCompleteFunction`. Completion rejects pending/private/ignore statuses in user responses by rewriting them to `STATUS_INTERNAL_ERROR` before dispatching.

The file defines the global prepare and complete function arrays sized to `IRP_MJ_MAXIMUM_FUNCTION + 1`.

## Integration Points

This module is the common substrate for all user-mode WinFsp transactions. Other dispatch files create requests with finalizers, store lock/resource/token state in the request context, post to IOQ, and rely on this file to clean up on success, failure, cancellation, or retry.

## Edge Cases And Risks

- Correctness depends on request finalizers being idempotent with context fields cleared by completion helpers before normal release.
- Over-alignment stores the original allocation pointer in the slot before the aligned header; any layout change must preserve this convention.
- `FspIopPostWorkRequestFunnel` deletes the request when the lower driver does not pend, because ownership only transfers on pending.
- Cancellation completion explicitly wraps filesystem enter/exit because cancels can arrive with APCs enabled.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/iop.c -->