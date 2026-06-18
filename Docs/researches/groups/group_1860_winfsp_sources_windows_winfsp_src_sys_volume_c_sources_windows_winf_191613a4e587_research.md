# Group Research: WinFsp Kernel Volume, Work Queue, and Write Paths

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/volume.c -->
# File Research: sources/windows/winfsp/src/sys/volume.c

This file implements WinFsp kernel volume lifecycle and the kernel/user-mode transaction bridge for file-system requests.

Key responsibilities:
- Creates volume devices from encoded `FSP_FSCTL_VOLUME_PARAMS`, normalizing defaults for sector size, allocation unit size, component length, timeouts, IRP capacity, cache timeout fields, network prefixes, and release-build buffering policy.
- Creates the fsvol device and, for disk file systems, the paired fsvrt disk device with secure device naming and sector-size setup.
- Registers network file systems with the WinFsp MUP path and creates symbolic links for named volumes.
- Handles teardown: stops the IOQ, finalizes mountdev state, unregisters MUP/symbolic links, swaps or delays VPB destruction, forces active file sections closed, releases notify/rename ownership, and dereferences device objects.
- Mounts virtual disk volumes by matching the fsvrt device to a live fsvol device, patching the VPB, setting the serial number, and compensating for the extra reference passed in the mount IRP.
- Supports mountdev and mount-manager integration, including persistent mountdev setup, drive-letter/directory mount creation, registry-gated mount-manager use from the FSD, and cleanup of mount points.
- Returns single volume names and volume lists, appending network volume prefixes where applicable.
- Implements the main transact loop used by user-mode file systems: consumes responses, completes processing IRPs, handles retried/reposted IRPs, waits for pending IRPs, prepares requests, copies them to user buffers or internal buffers, and moves IRPs into the processing queue.
- Dispatches extension-provider control codes through `Provider->DeviceTransact`.
- Implements two-phase stopping via `FSP_FSCTL_STOP0` and `FSP_FSCTL_STOP`, avoiding premature cancellation of IRPs still visible to user-mode dispatcher threads.
- Handles asynchronous volume notifications by copying user buffers into nonpaged work items, taking rename/delete coordination locks, validating notify file names, invalidating file-node caches, and issuing change notifications.
- Posts kernel-owned work requests via `FspVolumeWork`.

Important dependencies:
- `FspDeviceCreate`, `FspDeviceInitialize`, `FspDeviceReference`, and global device-list helpers.
- `FspIoq*` queue primitives for pending, processing, retried, stopped, timeout, and cancellation state.
- `FspIopDispatchPrepare` / `FspIopDispatchComplete` for request/response handoff.
- Mount helpers such as `FspMountdevMake`, `FspMountdevFini`, `FspMountmgrCreateDrive`, and `FspMountmgrNotifyCreateDirectory`.
- Name/cache helpers such as `FspFileNameIsValid` and `FspFileNodeInvalidateCachesAndNotifyChangeByName`.
- Silo globals and MUP registration for network file systems.

Filesystem relevance:
- This is the control-plane core for a WinFsp file system instance.
- It defines how a user-mode file-system process creates a kernel volume, how Windows mounts it, how user-mode receives kernel IRP requests, and how user-mode responses complete those IRPs.
- The transaction path is especially central: most ordinary file operations prepared elsewhere eventually flow through this file to cross the kernel/user boundary.

Notable watchpoints:
- Volume creation decodes binary volume parameters through specially encoded `WCHAR` values in the create path; validation failures return `STATUS_INVALID_PARAMETER`.
- Release builds force `AlwaysUseDoubleBuffering` to avoid unsafe read behavior.
- `RejectIrpPriorToTransact0` is hardcoded on, so early IRP acceptance depends on transaction readiness.
- VPB lifetime is delicate: teardown may free immediately, release a mount reference, or schedule delayed cleanup depending on reference count.
- `FspVolumeFastTransact` must preserve forward progress while handling reposted/retried IRPs, bogus hints, stopped queues, internal transactions, and buffer-size limits.
- `FspVolumeNotify` intentionally defers work to avoid deadlocks with locks already held by file-system request handlers.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/wq.c -->
# File Research: sources/windows/winfsp/src/sys/wq.c

This file provides WinFsp’s helper path for deferring IRP processing to a system work queue.

Key responsibilities:
- Prepares IRPs before worker execution by locking user buffers for reads, writes, and directory queries when the IRP is not using the MDL minor path.
- Creates or augments an `FSP_FSCTL_TRANSACT_REQ` with an embedded work item.
- Stores the target `FSP_IOP_REQUEST_WORK` routine and initializes the `WORK_QUEUE_ITEM`.
- Optionally posts the work item immediately and returns `STATUS_PENDING`.
- Marks IRPs pending and queues work to `CriticalWorkQueue`.
- Runs the saved work routine with `CanWait=TRUE` from `FspWqWorkRoutine`.
- Completes the IRP directly when the routine returns an ordinary status.
- Posts the IRP to the fsvol IOQ when the work routine returns WinFsp private queue-post statuses.

Important dependencies:
- `FspLockUserBuffer` for safe user-buffer access after deferral.
- `FspIopCreateRequestAndWorkItem`, `FspIopCreateRequestWorkItem`, and `FspIopRequestWorkItem`.
- `FspIoqPostIrpEx` for handing a deferred IRP back to the user-mode transaction queue.
- `FspIopCompleteIrp` for final completion.
- Top-level IRP management via `IoSetTopLevelIrp`.

Filesystem relevance:
- This is a small but important scheduling shim for operations that cannot complete immediately, often because they need a waitable context.
- It is used by paths such as cached/non-cached I/O retry handling to move work out of the original dispatch context without losing the IRP/request association.

Notable watchpoints:
- The helper asserts that the request finalizer matches the request header, so callers must preserve finalizer consistency when reusing requests.
- Debug assertions restrict queued major functions to create, read, write, directory control, and lock control.
- Private status handling assumes only `FSP_STATUS_IOQ_POST` and `FSP_STATUS_IOQ_POST_BEST_EFFORT` are valid queue-post outcomes.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/wq.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/write.c -->
# File Research: sources/windows/winfsp/src/sys/write.c

This file implements WinFsp write handling for fast I/O, cached IRP writes, non-cached/paging writes, request preparation, completion, cleanup, and dispatch.

Key responsibilities:
- `FspFastIoWrite` handles non-extending cached writes when the file is valid, regular, cache-supported, not write-through, lock/oplock state allows fast I/O, and cache manager write checks pass.
- `FspFsvolWrite` validates the file object, handles MDL write completion, rejects directory writes, ignores zero-length writes, and chooses cached versus non-cached handling.
- `FspFsvolWriteCached`:
  - Acquires the file node main resource.
  - Performs async oplock checks and byte-range lock checks.
  - Computes write-to-EOF and extension state.
  - Initializes the cache map when needed.
  - Defers through `CcDeferWrite` and WinFsp work items when cache manager throttling requires it.
  - Extends the file by issuing a set-information IRP before writing past EOF.
  - Performs copy writes or MDL writes through WinFsp cache-manager wrappers.
  - Updates synchronous current offset and marks the file modified.
- `FspFsvolWriteNonCached`:
  - Rejects MDL writes and invalid paging write-to-EOF cases.
  - Locks the user buffer for read access.
  - Acquires the file node full resource.
  - Performs oplock and file-lock checks for non-paging writes.
  - Flushes and purges cache when non-cached writes target a cached file.
  - Creates or resets a transact write request and fills user contexts, offset, length, key, and constrained-I/O state.
  - Sets request ownership on the file node and returns `FSP_STATUS_IOQ_POST`.
- `FspFsvolWritePrepare` maps write data for user-mode consumption, choosing either a copied process buffer or a safe MDL mapped into user mode.
- `FspFsvolWriteComplete` validates response length, updates file info, sends size-change notifications, updates synchronous offsets, marks modified state, resets the request, and reports bytes written.
- `FspFsvolWriteNonCachedRequestFini` releases process buffers or unmaps user-mode MDL mappings, dereferences captured process objects, deletes safe MDLs, and releases file-node ownership.
- `FspWrite` dispatches write IRPs only for fsvol devices.

Important dependencies:
- Cache-manager wrappers: `FspCcCopyWrite`, `FspCcPrepareMdlWrite`, `FspCcMdlWriteComplete`, `FspCcInitializeCacheMap`.
- File-node locking, oplock, cache flush/purge, owner, file-info, and notification helpers.
- `FspWqRepostIrpWorkItem` / `FspWqCreateIrpWorkItem` for retrying in waitable contexts.
- `FspIopCreateRequestEx`, `FspIopResetRequest`, and request context slots for non-cached transaction state.
- Safe-MDL and process-buffer helpers for exposing write data safely to user mode.
- WinFsp statistics counters for paging and non-cached write accounting.

Filesystem relevance:
- This is the write data path from Windows IRPs into a user-mode WinFsp filesystem.
- Cached writes may complete in-kernel through the cache manager when possible.
- Non-cached and paging writes are converted into `FspFsctlTransactWriteKind` requests for user-mode servicing.
- The file carefully separates normal writes, paging I/O, cache-extension behavior, MDL write paths, file-lock enforcement, and file-size/file-info updates.

Notable watchpoints:
- Fast I/O is deliberately denied for extending writes and write-to-EOF writes.
- Cached extension requires `CanWait`; otherwise the IRP is reposted to a work item.
- Non-cached writes on cached files force flush/purge before handing data to user mode.
- Paging writes are marked as constrained I/O and bypass normal oplock/file-lock checks.
- `FspFsvolWritePrepare` has two ownership modes encoded in the same context slot: copied process buffer with a tagged cookie, or safe-MDL mapping.
- Completion treats user-mode `Information` larger than requested length as `STATUS_INTERNAL_ERROR`.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/write.c -->