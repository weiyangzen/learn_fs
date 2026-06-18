# Group Research: group_1859_winfsp_sources_windows_winfsp_src_sys_ioq_c_sources_windows_winfsp__8494a493201d

Scope confirmed against `Docs/research_subset_a.md`. All 16 listed WinFsp source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/ioq.c -->
# File Research: sources/windows/winfsp/src/sys/ioq.c

## Purpose

`ioq.c` implements WinFsp's core IRP queue abstraction, `FSP_IOQ`. It is the bridge between kernel IRP dispatch and the user-mode filesystem transaction loop: IRPs are posted as pending work, moved to processing while user mode handles them, and optionally placed on a retried-completion queue when completion must be retried later.

## Main Contents

- A long design comment documents the pending/processing flow and why an event-backed queue is used instead of a semaphore or manual-reset event.
- `FSP_IOQ_USE_QEVENT` selects WinFsp queued events; the fallback synchronization-event path is deliberately disabled with a compile-time `#error`.
- Optional `FSP_IOQ_PROCESS_NO_CANCEL` provides custom cancel-safe queue helpers that avoid setting a cancellation routine after an IRP enters processing.
- `FSP_IOQ_PEEK_CONTEXT` carries either an IRP boundary/hint or an expiration timestamp for queue scans.
- Three cancel-safe queues are implemented over one `FSP_IOQ` spin lock:
  - `PendingIoCsq`: newly posted IRPs waiting for user-mode pickup.
  - `ProcessIoCsq`: IRPs currently in user-mode processing, also indexed by a hash table for hint lookup.
  - `RetriedIoCsq`: IRPs whose completion needs retry.
- Each queue has callback functions for insert, remove, peek, lock acquire/release, and canceled-IRP completion.
- Public lifecycle and query functions:
  - `FspIoqCreate`
  - `FspIoqDelete`
  - `FspIoqStop`
  - `FspIoqStopped`
  - `FspIoqRemoveExpired`
  - `FspIoqPostIrpEx`
  - `FspIoqNextPendingIrp`
  - `FspIoqPendingIrpCount`
  - `FspIoqPendingAboveWatermark`
  - `FspIoqStartProcessingIrp`
  - `FspIoqEndProcessingIrp`
  - `FspIoqProcessIrpCount`
  - `FspIoqRetryCompleteIrp`
  - `FspIoqNextCompleteIrp`
  - `FspIoqRetriedIrpCount`

## Control Flow

A normal IRP flow is:

1. Dispatch code calls `FspIoqPostIrpEx`.
2. The IRP receives a timestamp unless posted as best effort.
3. It is inserted into the pending cancel-safe queue.
4. User-mode transact code calls `FspIoqNextPendingIrp`, which waits on `PendingIrpEvent` if a timeout was supplied, then removes a pending IRP.
5. The IRP enters processing via `FspIoqStartProcessingIrp`, where it is inserted into `ProcessIoCsq`.
6. Later, completion finds/removes it with `FspIoqEndProcessingIrp`.
7. If completion must be deferred, `FspIoqRetryCompleteIrp` inserts it into the retried queue and wakes transact waiters.
8. `FspIoqNextCompleteIrp` drains retried completions.

## Synchronization

- All queue state is protected by `Ioq->SpinLock`.
- Pending-queue availability is represented by `PendingIrpEvent`.
- `FspIoqPendingResetSynch` resynchronizes the event state with actual pending count or stop state.
- Processing IRPs are also stored in hash buckets keyed by mixed IRP pointer to support direct lookup by hint.

## Integration

This file is used by the WinFsp I/O processor and filesystem volume device extension to move IRPs between kernel dispatch and user-mode `FSP_FSCTL_TRANSACT` handling. The caller supplies `CompleteCanceledIrp`, so this queue layer does not decide how canceled IRPs are completed.

## Notable Details

- `FspIoqStop` marks the queue stopped, wakes waiters permanently, and optionally drains pending, processing, and retried queues through the cancellation callback.
- Expiration uses interrupt time converted to whole seconds, with timeout rounded up at queue creation.
- Best-effort IRPs are assigned `FspIrpTimestampInfinity` and are not expired by timestamp scans.
- `FspIoqPendingAboveWatermark` assumes `PendingIrpCapacity` is nonzero.

## Risks and Edge Cases

- In `FspIoqRemoveExpired`, the retried queue removal references `Ioq->RetryIoCsq`, while the rest of the file and `driver.h` use `RetriedIoCsq`. If this code path is compiled, that looks like a stale-name defect.
- Event correctness depends on every remove or failed dequeue resynchronizing pending state under the queue lock.
- The optional no-cancel processing mode changes cancellation semantics after an operation has been started, which is intentional but important for behavioral compatibility.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/ioq.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/lockctl.c -->
# File Research: sources/windows/winfsp/src/sys/lockctl.c

## Purpose

`lockctl.c` handles `IRP_MJ_LOCK_CONTROL` for WinFsp filesystem volume devices. It validates the target file, performs oplock checks, and delegates byte-range lock processing to the FsRtl file-lock package through WinFsp file-node helpers.

## Main Contents

- `FspFsvolLockControlRetry` is the main retryable lock path.
- `FspFsvolLockControl` validates the request and starts the retry path.
- `FspFsvolLockControlComplete` is an I/O completion logging stub using WinFsp's completion macros.
- `FspLockControl` dispatches by device extension kind.

## Control Flow

1. `FspLockControl` accepts only `FspFsvolDeviceExtensionKind`.
2. `FspFsvolLockControl` rejects invalid file nodes and directories.
3. `FspFsvolLockControlRetry` tries to acquire the file node main resource shared.
4. If acquisition fails, it reposts the IRP as a work item.
5. It performs `FspFileNodeOplockCheckAsync`.
6. If the oplock check succeeds, it clears the top-level IRP and calls `FspFileNodeProcessLockIrp`.
7. It releases the file node based on saved IRP flags and returns the result with `FSP_STATUS_IGNORE_BIT`.

## Integration

The file depends on `FSP_FILE_NODE` locking, oplock helpers, work-queue reposting, and FsRtl file-lock support wrapped by `FspFileNodeProcessLockIrp`.

## Notable Details

- Lock control is accepted only for regular files.
- Asynchronous oplock checks may return `STATUS_PENDING`.
- `FSP_STATUS_IGNORE_BIT` indicates the IRP has been handled in a way that normal dispatch completion should ignore.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/lockctl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/meta.c -->
# File Research: sources/windows/winfsp/src/sys/meta.c

## Purpose

`meta.c` implements a small nonpaged metadata cache used by WinFsp for cached per-file metadata such as security descriptors, directory info, stream info, and EA data. Items are indexed by generated integer IDs and expire by timeout or capacity pressure.

## Main Contents

- `FSP_META_CACHE_ITEM` stores list linkage, hash linkage, backing buffer pointer, item index, expiration time, and refcount.
- `FSP_META_CACHE_ITEM_BUFFER` prefixes returned item buffers with a backpointer and size.
- A static assert verifies that the public metadata item header size matches the actual buffer layout.
- Internal helpers:
  - `FspMetaCacheDereferenceItem`
  - `FspMetaCacheLookupIndexedItemAtDpcLevel`
  - `FspMetaCacheAddItemAtDpcLevel`
  - `FspMetaCacheRemoveIndexedItemAtDpcLevel`
  - `FspMetaCacheRemoveExpiredItemAtDpcLevel`
- Public API:
  - `FspMetaCacheCreate`
  - `FspMetaCacheDelete`
  - `FspMetaCacheInvalidateExpired`
  - `FspMetaCacheReferenceItemBuffer`
  - `FspMetaCacheDereferenceItemBuffer`
  - `FspMetaCacheAddItem`
  - `FspMetaCacheInvalidateItem`

## Data Structure

The cache is one page:

- Header fields live in `FSP_META_CACHE`.
- Hash buckets fill the rest of the page.
- `ItemList` tracks insertion/expiration order.
- `ItemBuckets` provide lookup by item index.
- Items and item buffers are separately allocated.

## Control Flow

- `FspMetaCacheCreate` returns success with a null cache if capacity, max item size, or timeout is zero.
- `FspMetaCacheAddItem`:
  - rejects oversize items,
  - allocates an item and buffer,
  - copies caller data under exception handling,
  - removes one expired/oldest item if capacity is exceeded,
  - assigns a monotonically increasing nonzero item index,
  - inserts into the list and hash table.
- `FspMetaCacheReferenceItemBuffer` looks up an item, increments its refcount under the spin lock, and returns the user-visible buffer pointer plus optional size.
- `FspMetaCacheDereferenceItemBuffer` recovers the hidden header from the buffer pointer and drops the item reference.
- Invalidations remove an item from index/list ownership, then dereference outside the spin lock.

## Synchronization

- Hash/list/cache counters are protected by `MetaCache->SpinLock`.
- Refcounts use interlocked operations.
- Memory is freed only when the final reference drops.

## Notable Details

- Item index zero is reserved as invalid; wrap from `UINT64_MAX` returns to `1`.
- Expiration is checked only against the head of `ItemList`, so the list is expected to be ordered by insertion and expiration time.
- `FspMetaCacheDelete` invalidates all items by passing `(UINT64)-1LL` as expiration time, then frees the cache page.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/meta.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/mountdev.c -->
# File Research: sources/windows/winfsp/src/sys/mountdev.c

## Purpose

`mountdev.c` implements Mount Manager support for WinFsp virtual volume devices. It lets an fsvrt device answer mountdev IOCTLs, provide a device name and unique ID, become persistent or nonpersistent, and purge nonpersistent mount manager points during teardown.

## Main Contents

- `FspMountdevQueryDeviceName`
- `FspMountdevQueryUniqueId`
- `FspMountdevDeviceControl`
- `FspMountdevMake`
- `FspMountdevFini`

## Control Flow

- `FspMountdevDeviceControl` handles mountdev IOCTLs only if the fsvrt extension has `IsMountdev` set.
- Supported IOCTLs:
  - `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME`
  - `IOCTL_MOUNTDEV_QUERY_UNIQUE_ID`
- `FspMountdevMake`:
  - requires external concurrency protection, usually the mount mutex,
  - rejects repeated conversion unless persistence matches,
  - stores persistence mode,
  - creates a stable UUID v5 for persistent volumes from filesystem name, serial number, and creation time,
  - creates a random GUID for nonpersistent volumes,
  - copies the GUID to `UniqueId`,
  - marks the fsvrt device as mountdev-capable.
- `FspMountdevFini`:
  - returns immediately if the device was not a mountdev,
  - keeps Mount Manager state for persistent devices,
  - for nonpersistent devices, sends `IOCTL_MOUNTMGR_DELETE_POINTS` keyed by the mountdev unique ID.

## Buffer Handling

Both query routines first require the fixed header size, then set `IoStatus.Information` to the full required size. If the caller buffer cannot hold the variable-length payload, they return `STATUS_BUFFER_OVERFLOW` after reporting the fixed header size.

## Integration

This file relies on fsvrt and fsvol device extensions, `FspUuid5Make`, `FspCreateGuid`, and `FspSendMountmgrDeviceControlIrp` from utility code.

## Notable Details

- The query unique ID payload is the binary GUID stored in the fsvrt device extension.
- Persistent and nonpersistent mountdev conversion cannot be mixed after the device is marked.
- `FspMountdevFini` intentionally does not clear `IsMountdev`; it only cleans external Mount Manager state.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/mountdev.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/mup.c -->
# File Research: sources/windows/winfsp/src/sys/mup.c

## Purpose

`mup.c` implements WinFsp's filesystem MUP redirector device support. It registers volume prefixes, answers network redirector prefix-resolution IOCTLs, and forwards IRPs arriving at the fsmup device to the appropriate fsvol device.

## Main Contents

- `FSP_MUP_PREFIX_CLASS` is enabled, so WinFsp claims class prefixes like `\ClassName` instead of only full prefixes like `\ClassName\InstanceName`.
- `FSP_MUP_CLASS` tracks class-prefix refcounts and prefix-table entries.
- Functions:
  - `FspMupGetClassName`
  - `FspMupRegister`
  - `FspMupUnregister`
  - `FspMupGetFsvolDeviceObject`
  - `FspMupHandleIrp`
  - `FspMupRedirQueryPathEx`

## Prefix Registration

`FspMupRegister`:

- Extracts the class prefix from the fsvol `VolumePrefix`.
- Allocates a class record.
- Inserts the full volume prefix into `PrefixTable`.
- References the fsvol device object while registered.
- Inserts or refcounts the class entry in `ClassTable`.

`FspMupUnregister` reverses this:

- Removes the full prefix.
- Dereferences the fsvol device.
- Decrements and possibly removes/frees the class record.

Both operations are protected by the fsmup prefix-table lock.

## IRP Handling

`FspMupHandleIrp`:

- Enters filesystem context.
- Special-cases `IRP_MJ_CREATE` with empty name as an open of the fsmup device itself and completes it with `STATUS_SUCCESS`.
- For other creates, follows related file objects to the root and resolves the filename against the prefix table.
- Special-cases `IRP_MJ_DEVICE_CONTROL` with `IOCTL_REDIR_QUERY_PATH_EX` and handles it locally.
- For all other requests, tries to recover the fsvol device from `FileObject->FsContext` or `FsContext2`.
- If an fsvol target is found, skips the current stack location and calls the fsvol driver.
- If no target is found, completes locally with status chosen by major function.

## Prefix Resolution

`FspMupRedirQueryPathEx`:

- Accepts only kernel-mode callers.
- Validates input and output buffers.
- With class-prefix mode enabled, extracts the class from the query path and succeeds if that class is registered.
- Sets `QUERY_PATH_RESPONSE.LengthAccepted` to the class prefix length.

## Notable Details

- For unresolved creates, the code returns `STATUS_BAD_NETWORK_PATH`, specifically to satisfy DFS/MUP behavior around `\ClassName\IPC$` probes.
- Cleanup and close without a target return success because their status is ignored except for pending.
- Query/set information without a target return `STATUS_INVALID_PARAMETER`; other unhandled IRPs return `STATUS_INVALID_DEVICE_REQUEST`.
- Class-prefix claiming improves resolution speed for known classes but prevents another redirector from owning shares under the same class prefix.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/mup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/name.c -->
# File Research: sources/windows/winfsp/src/sys/name.c

## Purpose

`name.c` validates and manipulates WinFsp file names, stream names, wildcard patterns, EA names, and name-expression matches.

## Main Contents

- `FspFileNameIsValid`
- `FspFileNameIsValidPattern`
- `FspEaNameIsValid`
- `FspFileNameSuffix`
- `FspFileNameInExpression`

## File Name Validation

`FspFileNameIsValid` checks:

- Nonempty even-byte UTF-16 length.
- Component length does not exceed `MaxComponentLength`.
- No doubled backslashes inside the path.
- Stream names only appear in the final path component.
- Colon use is rejected unless stream parsing outputs were requested.
- ASCII characters are checked with `FsRtlTestAnsiCharacter`.
- Stream type, if present, must be `$DATA` case-insensitively.
- A stream name without a stream type must be nonempty.

If a stream is accepted, `StreamPart` points into the original path buffer and `StreamType` is set to none or data.

## Pattern Validation

`FspFileNameIsValidPattern` permits wildcard characters but rejects:

- Backslashes.
- Colons.
- Invalid ASCII characters under NTFS legal-name rules.
- Components longer than the maximum.

## EA Name Validation

`FspEaNameIsValid` follows FastFAT-like rules:

- Length must be 1 through 254 bytes.
- DBCS lead bytes are skipped as a pair.
- Other bytes must be legal FAT ANSI characters.

## Path Splitting

`FspFileNameSuffix` splits a path into:

- `Remain`: everything before the final component.
- `Suffix`: the final component after the last run of backslashes.

It preserves root-style remain length for a path beginning with `\`.

## Expression Matching

`FspFileNameInExpression` wraps `FsRtlIsNameInExpression` in exception handling and asserts that custom upcase tables are not supported.

## Notable Details

- The stream parsing routine mutates only output `UNICODE_STRING` descriptors; it does not copy path text.
- Non-ASCII file-name characters bypass the ASCII `FsRtlTestAnsiCharacter` check.
- `FspFileNameSuffix` tolerates multiple backslashes while suffix extraction does; strict validity checking separately rejects doubled backslashes.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/name.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/psbuffer.c -->
# File Research: sources/windows/winfsp/src/sys/psbuffer.c

## Purpose

`psbuffer.c` implements reusable per-process user-mode virtual buffers for WinFsp operations. It avoids repeated virtual memory allocation for small transfer buffers by caching a bounded number of buffers per process and cleaning them up when the process exits.

## Main Contents

- `FSP_PROCESS_BUFFER_ITEM` tracks one process ID, buffer count, and reusable buffer entries.
- `FSP_PROCESS_BUFFER_LIST_ENTRY` stores one virtual buffer pointer.
- A global spin lock protects a fixed hash table of process items.
- Functions:
  - `FspProcessBufferInitialize`
  - `FspProcessBufferFinalize`
  - `FspProcessBufferCollect`
  - `FspProcessBufferAcquire`
  - `FspProcessBufferRelease`
- `FspProcessBufferNotifyRoutine` hooks process creation/deletion notifications.

## Buffer Limits

- Maximum reusable buffer size is `FspProcessBufferSizeMax`, defined elsewhere as 64 KiB.
- Per-process reusable buffer count is:
  - 2 on systems with up to 2 processors,
  - up to 8 on larger systems,
  - otherwise equal to processor count.

## Control Flow

`FspProcessBufferAcquire`:

1. If requested size is within the reusable limit, looks up the current process ID.
2. Pops an available buffer entry if one exists.
3. If none exists and the process has capacity, allocates a new list entry and possibly a process item.
4. If capacity is exhausted, falls back to non-reusable direct virtual allocation.
5. Lazily allocates the actual virtual buffer to `FspProcessBufferSizeMax` with `ZwAllocateVirtualMemory`.
6. Returns a cookie when the buffer is reusable; returns a null cookie for direct allocations.

`FspProcessBufferRelease`:

- If a cookie exists, returns the buffer entry to the current process cache.
- If no cookie exists, releases the virtual memory directly.

`FspProcessBufferCollect`:

- Removes the process item from the hash table on process exit.
- Frees list-entry metadata.
- Does not free virtual memory in that path because the process address space is going away.

## Synchronization

- The process table and per-process buffer lists are protected by `ProcessBufferLock`.
- Allocation is intentionally done outside the spin lock when possible.
- If an entry cannot be returned because the process item disappeared, its virtual memory and metadata are freed.

## Integration

This is used by noncached read preparation paths when mapping/copying through a process-local buffer is preferable to exposing the original MDL mapping.

## Notable Details

- `SafeGetCurrentProcessId` uses `PsGetProcessId(PsGetCurrentProcess())`, avoiding deprecated direct current-process ID access.
- `Finalize` unregisters the process callback and frees remaining item/list metadata.
- Reusable virtual buffers are process-address-space allocations, so release must happen in the owning process context.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/psbuffer.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/read.c -->
# File Research: sources/windows/winfsp/src/sys/read.c

## Purpose

`read.c` implements WinFsp read handling for fast I/O, cached IRP reads, noncached IRP reads, read request preparation for user mode, and read completion.

## Main Contents

- `FspFastIoRead`
- `FspFsvolRead`
- `FspFsvolReadCached`
- `FspFsvolReadNonCached`
- `FspFsvolReadPrepare`
- `FspFsvolReadComplete`
- `FspFsvolReadNonCachedRequestFini`
- `FspRead`

## Fast I/O Path

`FspFastIoRead`:

- Validates the file node.
- Rejects directories.
- Succeeds immediately on zero-length reads.
- Requires `FO_CACHE_SUPPORTED` and an existing private cache map.
- Acquires the file node main resource shared.
- Rejects fast I/O if oplocks or byte-range locks block it.
- Trims reads to file size because cache manager reads cannot extend beyond EOF.
- Calls `FspCcCopyRead`.
- Sets `FO_FILE_FAST_IO_READ`.
- Updates current byte offset for successful synchronous-style fast reads.

## Dispatch Path

`FspFsvolRead`:

- Handles `IRP_MN_COMPLETE` for MDL read completion through `FspCcMdlReadComplete`.
- Rejects invalid file nodes and directories.
- Succeeds immediately on zero-length reads.
- Chooses cached I/O when caching is supported and the IRP is neither paging nor no-cache.
- Otherwise uses noncached handling.

## Cached Reads

`FspFsvolReadCached`:

- Requires top-level IRP.
- Acquires file-node main shared, with work-queue repost if it cannot wait.
- Performs asynchronous oplock checks.
- Checks file locks.
- Trims the read to file size.
- Initializes the cache map if needed using current file information.
- Uses either `FspCcCopyRead` or `FspCcMdlRead`.
- Reposts on cache-manager `STATUS_PENDING`.
- Updates current file offset for synchronous I/O.

## Noncached Reads

`FspFsvolReadNonCached`:

- Rejects MDL minor requests.
- Locks the user buffer for write access.
- Acquires file-node full shared.
- Performs oplock and file-lock checks for non-paging reads.
- If reading noncached from a cached file, flushes and purges relevant cached data under exclusive full acquisition.
- During create-section activity, trims reads to file size to avoid bugchecks if the user-mode filesystem reports inconsistent sizes.
- Creates or resets a `FSP_FSCTL_TRANSACT_REQ`.
- Fills `FspFsctlTransactReadKind` with user contexts, offset, length, and key.
- Sets file-node ownership to the request and posts to the IOQ.
- Updates filesystem statistics, distinguishing paging/user-file reads from noncached reads.

## User-Mode Preparation

`FspFsvolReadPrepare` chooses how user mode receives the target buffer:

- If `FspReadIrpShouldUseProcessBuffer` returns true:
  - Verifies the IRP MDL has a system address.
  - Acquires a reusable process buffer.
  - References the current process.
  - Stores the user-mode address in the request.
  - Stores cookie, address, and process in request context.
- Otherwise:
  - Creates a safe MDL for unaligned edge pages if needed.
  - Maps locked pages into user mode.
  - References the current process.
  - Stores safe MDL, address, and process in request context.

## Completion and Cleanup

`FspFsvolReadComplete`:

- Propagates user-mode failure status.
- Validates that returned byte count does not exceed requested length.
- If a process buffer was used, copies returned bytes back into the IRP MDL system address.
- If a safe MDL was used, copies edge pages back.
- Updates current byte offset for synchronous non-paging top-level reads.
- Resets the request and sets `IoStatus.Information`.

`FspFsvolReadNonCachedRequestFini`:

- Releases process buffers or unmaps user-mode MDL mappings in the original process context.
- Dereferences the process object.
- Deletes safe MDLs.
- Releases file-node request ownership.

## Notable Details

- Cached reads rely on `FileInfoTimeout` being infinite, asserted before using cached file information.
- Process-buffer context encodes the reusable-buffer flag in the low bit of `RequestCookie`.
- The noncached path is also used for paging I/O, but skips oplock and byte-range lock checks for paging reads.
- Completion treats oversized user-mode read responses as `STATUS_INTERNAL_ERROR`.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/read.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/security.c -->
# File Research: sources/windows/winfsp/src/sys/security.c

## Purpose

`security.c` implements `IRP_MJ_QUERY_SECURITY` and `IRP_MJ_SET_SECURITY` for WinFsp filesystem volume devices. It combines file-node security descriptor caching with fallback user-mode filesystem requests.

## Main Contents

- Query path:
  - `FspFsvolQuerySecurity`
  - `FspFsvolQuerySecurityComplete`
  - `FspFsvolQuerySecurityRequestFini`
- Set path:
  - `FspFsvolSetSecurity`
  - `FspFsvolSetSecurityComplete`
  - `FspFsvolSetSecurityRequestFini`
- Dispatch entries:
  - `FspQuerySecurity`
  - `FspSetSecurity`

## Query Flow

`FspFsvolQuerySecurity`:

1. Validates the file node and file descriptor.
2. Acquires the file node main resource shared.
3. If a cached security descriptor exists, releases the node and answers directly with `FspQuerySecurityDescriptorInfo`.
4. Otherwise acquires the paging I/O/full lock path.
5. Buffers the caller output buffer for write access.
6. Creates a `FspFsctlTransactQuerySecurityKind` request.
7. Stores file-node ownership in request context and posts to IOQ.

`FspFsvolQuerySecurityComplete`:

- Propagates user-mode failure status.
- Validates the returned relative security descriptor bounds and format.
- Releases file-node ownership after capturing the security change number.
- Tries to reacquire the file-node main resource exclusively.
- If reacquisition fails, retries completion through `FspIopRetryCompleteIrp`.
- Attempts to cache the descriptor if the file-node security change number still matches.
- Answers the original query from cached security if possible, otherwise from the response buffer.
- Sets `IoStatus.Information` to the resulting descriptor length.

## Set Flow

`FspFsvolSetSecurity`:

- Validates file node and descriptor relationship.
- Determines whether the input security descriptor is self-relative.
- Computes the self-relative size.
- Acquires the file node full resource exclusively.
- Creates a `FspFsctlTransactSetSecurityKind` request with extra buffer space.
- Copies or converts the descriptor into the request buffer.
- Sets file-node ownership and posts to IOQ.

`FspFsvolSetSecurityComplete`:

- Propagates user-mode failure status.
- If user mode returns a valid relative security descriptor, updates the cached descriptor.
- Otherwise invalidates the cached security descriptor.
- Marks the file descriptor as having set security and metadata.
- Emits a security change notification.
- Releases request ownership.
- Completes with zero information.

## Integration

The file depends on:

- file-node security cache helpers,
- `FspQuerySecurityDescriptorInfo` from `util.c`,
- `FspIopCreateRequestEx`,
- request-finalizer ownership cleanup,
- IOQ retry completion for lock contention during completion.

## Notable Details

- The query path can complete entirely from cached metadata without contacting user mode.
- Returned security descriptors are required to be relative and valid before caching.
- The set path assumes the kernel has captured a valid security descriptor; disabled code documents the validation point.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/security.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/shutdown.c -->
# File Research: sources/windows/winfsp/src/sys/shutdown.c

## Purpose

`shutdown.c` defines the WinFsp shutdown dispatch routine.

## Main Contents

- `FspShutdown` is registered as an `FSP_DRIVER_DISPATCH`.

## Behavior

`FspShutdown`:

- Enters the major-function dispatch macro.
- Explicitly marks `IrpSp` as unused.
- Always returns `STATUS_INVALID_DEVICE_REQUEST`.
- Emits an empty leave trace through the WinFsp dispatch macro.

## Integration

This is a minimal dispatch stub. It does not perform filesystem flush, volume teardown, or shutdown-specific cleanup.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/shutdown.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/silo.c -->
# File Research: sources/windows/winfsp/src/sys/silo.c

## Purpose

`silo.c` adds Windows Server silo/container awareness to WinFsp. It dynamically loads silo monitor APIs on supported Windows versions, creates per-silo global state, and runs WinFsp initialization/finalization callbacks inside each server silo context.

## Main Contents

- Local typedefs for silo-related Windows kernel APIs.
- Dynamically loaded function pointers for `PsRegisterSiloMonitor`, `PsGetSiloContext`, `PsAttachSiloToCurrentThread`, and related APIs.
- Global monitor state:
  - `FspSiloMonitor`
  - init/fini callbacks
  - `FspSiloInitDone`
  - `FspSiloListMutex`
  - `FspSiloList`
  - host fallback globals
- Public API:
  - `FspSiloIsHost`
  - `FspSiloGetGlobals`
  - `FspSiloDereferenceGlobals`
  - `FspSiloGetContainerId`
  - `FspSiloInitialize`
  - `FspSiloPostInitialize`
  - `FspSiloFinalize`
  - `FspSiloEnumerate`

## Initialization

`FspSiloInitialize`:

- Initializes the silo list mutex and list.
- Checks for Windows 10 RS5 or newer.
- Dynamically resolves all required silo APIs with `MmGetSystemRoutineAddress`.
- Registers a silo monitor with create and terminate callbacks.
- Stores WinFsp init/fini callbacks and marks silo support initialized.
- If the OS or APIs are unavailable, it leaves silo support disabled but returns success.

`FspSiloPostInitialize` starts the registered monitor after primary initialization.

## Silo Creation

`FspSiloMonitorCreateCallback`:

- Gets the monitor context slot.
- Creates a `FSP_SILO_GLOBALS` silo context.
- Inserts it into the silo.
- Enters filesystem context and locks the silo list.
- Attaches the current thread to the new silo and invokes the WinFsp init callback.
- On success, inserts the globals into the global silo list.
- On failure, removes inserted context and dereferences globals.
- Always returns `STATUS_SUCCESS` to avoid blocking container creation or triggering known Windows crashes.

## Silo Termination

`FspSiloMonitorTerminateCallback`:

- Retrieves silo globals.
- Removes them from the global list.
- Attaches to the terminating silo and invokes the WinFsp fini callback.
- Removes the silo context, dropping the monitor's reference.

## Global Lookup

- `FspSiloIsHost` reports host mode before initialization or when no current server silo exists.
- `FspSiloGetGlobals` returns host globals outside a silo, otherwise returns the current silo context and leaves it referenced.
- `FspSiloDereferenceGlobals` dereferences only real silo contexts, not host globals.
- `FspSiloGetContainerId` returns the current silo container GUID or a zero GUID for host/no-silo.

## Enumeration

`FspSiloEnumerate`:

- Locks the list.
- Attaches to `PsInitialSystemProcess`.
- Iterates silo globals.
- Attaches the thread to each silo and calls the supplied enumeration callback.

## Notable Details

- The code monitors existing silos as well as future silos.
- Host globals are always available even when silo support is not active.
- Debug finalization asserts that the silo list is empty after unregistering the monitor.
- Silo callbacks deliberately use `FsRtlEnterFileSystem` and `ExAcquireFastMutexUnsafe` around shared list state.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/silo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/statistics.c -->
# File Research: sources/windows/winfsp/src/sys/statistics.c

## Purpose

`statistics.c` manages per-processor filesystem statistics buffers exposed through filesystem statistics queries.

## Main Contents

- `FspStatisticsCreate`
- `FspStatisticsDelete`
- `FspStatisticsCopy`

## Behavior

`FspStatisticsCreate`:

- Allocates an array of `FSP_STATISTICS`, one entry per processor.
- Zeroes the array.
- Initializes each entry's `FILESYSTEM_STATISTICS` base header.
- Reports filesystem type as `FILESYSTEM_STATISTICS_TYPE_FAT`.

`FspStatisticsDelete` frees the array.

`FspStatisticsCopy`:

- Rejects null output buffers.
- Requires at least `sizeof(FILESYSTEM_STATISTICS)` bytes.
- Computes the full statistics length as `sizeof(FSP_STATISTICS) * FspProcessorCount`.
- If the caller buffer is large enough, returns the full length and success.
- Otherwise returns `STATUS_BUFFER_OVERFLOW` and copies only the caller-provided length.
- Copies statistics into the caller buffer.

## Notable Details

- The implementation "pretends" to be FAT for statistics compatibility.
- Partial copies are allowed once the buffer can hold the common filesystem statistics header.
- Statistics storage is nonpaged.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/statistics.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/sxs.c -->
# File Research: sources/windows/winfsp/src/sys/sxs.c

## Purpose

`sxs.c` extracts and exposes a side-by-side identity/suffix from the loaded driver name. This lets WinFsp derive variant-specific naming when the driver binary name contains the configured side-by-side separator.

## Main Contents

- Static buffer `FspSxsIdentBuf`.
- Static strings:
  - `FspSxsIdentStr`
  - `FspSxsSuffixStr`
- Public functions:
  - `FspSxsIdentInitialize`
  - `FspSxsIdent`
  - `FspSxsSuffix`

## Behavior

`FspSxsIdentInitialize`:

- Scans backward through `DriverName`.
- Stops at a path separator or at `FSP_SXS_SEPARATOR_CHAR`.
- If no side-by-side separator is found in the final path component, leaves identity empty.
- Copies from the separator through the end into `FspSxsIdentBuf`, capped to the static buffer size.
- Sets:
  - ident string to skip the first copied character,
  - suffix string to include the separator.

`FspSxsIdent` returns the identity string.

`FspSxsSuffix` returns the suffix string.

## Notable Details

- The static `UNICODE_STRING` buffers are initialized so `Ident` starts at `FspSxsIdentBuf + 1`, while `Suffix` starts at the separator.
- Initialization is marked `INIT`, so it is intended only during driver initialization.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/sxs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/trace.c -->
# File Research: sources/windows/winfsp/src/sys/trace.c

## Purpose

`trace.c` provides optional debug tracing support when `FSP_TRACE_ENABLED` is enabled. It prints compact function/file/line traces and enriches insufficient-resource traces with low-memory event state.

## Main Contents

Compiled only under `#if FSP_TRACE_ENABLED`:

- `FspTrace`
- `FspTraceNtStatus`
- `FspOpenEvent`
- `FspCloseEvent`
- `FspTraceInitialize`
- `FspTraceFinalize`

## Behavior

`FspTrace`:

- Strips directory components from the source file path.
- Asserts IRQL is no higher than dispatch level.
- Prints `DRIVER_NAME`, function, file, and line through `DbgPrintEx`.

`FspTraceNtStatus`:

- Also strips source path.
- For `STATUS_INSUFFICIENT_RESOURCES`, checks kernel low-memory condition events and prints a three-character memory state:
  - memory,
  - nonpaged pool,
  - paged pool.
- For other statuses, prints the hex status.

`FspTraceInitialize` opens and references:

- `\KernelObjects\LowMemoryCondition`
- `\KernelObjects\LowNonPagedPoolCondition`
- `\KernelObjects\LowPagedPoolCondition`

`FspTraceFinalize` dereferences and closes any opened events.

## Integration

This file supports tracing macros such as `FSP_TRACE()` and status-tracing sites elsewhere in the driver. It uses object-manager event handles and `ObReferenceObjectByHandle`.

## Notable Details

- It locally redefines `STATUS_INSUFFICIENT_RESOURCES` after undefining it, likely to avoid macro/header inconsistencies in trace builds.
- If low-memory events cannot be opened, tracing still works but omits those event states.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/util.c -->
# File Research: sources/windows/winfsp/src/sys/util.c

## Purpose

`util.c` is a collection of kernel utility wrappers and support mechanisms used throughout the WinFsp driver. It covers version detection, synchronous internal IRPs, user-buffer handling, cache-manager wrappers, security and EA validation, notification and oplock wrappers, work-item helpers, safe MDLs, IRP completion hooks, and optimized Unicode comparison.

## Main Contents

Major groups:

- Must-succeed allocation helpers:
  - `FspAllocatePoolMustSucceed`
  - `FspAllocateIrpMustSucceed`
- System/version/object utilities:
  - `FspIsNtDdiVersionAvailable`
  - `FspCreateGuid`
  - `FspGetDeviceObjectPointer`
  - `FspRegistryGetValue`
- Synchronous IRP senders:
  - `FspSendSetInformationIrp`
  - `FspSendQuerySecurityIrp`
  - `FspSendQueryEaIrp`
  - `FspSendMountmgrDeviceControlIrp`
  - `FspSendIrpCompletion`
- Buffer and MDL helpers:
  - `FspBufferUserBuffer`
  - `FspLockUserBuffer`
  - `FspMapLockedPagesInUserMode`
  - `FspSafeMdlCheck`
  - `FspSafeMdlCreate`
  - `FspSafeMdlCopyBack`
  - `FspSafeMdlDelete`
- Cache-manager wrappers:
  - `FspCcInitializeCacheMap`
  - `FspCcSetFileSizes`
  - `FspCcCopyRead`
  - `FspCcCopyWrite`
  - `FspCcMdlRead`
  - `FspCcMdlReadComplete`
  - `FspCcPrepareMdlWrite`
  - `FspCcMdlWriteComplete`
  - `FspCcFlushCache`
- Security/EA helpers:
  - `FspQuerySecurityDescriptorInfo`
  - `FspEaBufferFromOriginatingProcessValidate`
  - `FspEaBufferFromFileSystemValidate`
- Notification/oplock wrappers:
  - `FspNotifyInitializeSync`
  - `FspNotifyFullChangeDirectory`
  - `FspNotifyFullReportChange`
  - `FspOplockBreakH`
  - `FspCheckOplock`
  - `FspCheckOplockEx`
  - `FspOplockFsctrl`
- Work-item helpers:
  - `FspInitializeSynchronousWorkItem`
  - `FspExecuteSynchronousWorkItem`
  - `FspExecuteSynchronousWorkItemRoutine`
  - `FspInitializeDelayedWorkItem`
  - `FspQueueDelayedWorkItem`
  - `FspQueueDelayedWorkItemDPC`
- IRP hook helpers:
  - `FspIrpHook`
  - `FspIrpHookReset`
  - `FspIrpHookContext`
  - `FspIrpHookNext`
- Unicode compare helpers:
  - `FspUpcaseAscii`
  - `FspCompareUnicodeString`

## Version and Object Utilities

`FspIsNtDdiVersionAvailable`:

- Caches the computed OS version.
- Uses `RtlGetVersion`.
- Builds an NTDDI-style value.
- Maps Windows 10 build numbers to subversions with binary search.
- Uses `InterlockedExchange` for benign thread-safe caching.

`FspGetDeviceObjectPointer` progressively extends a partial object name component by component, trying `IoGetDeviceObjectPointer` and validating intermediate directory or symbolic-link objects.

`FspRegistryGetValue` opens a registry key and queries one value, treating `STATUS_BUFFER_OVERFLOW` from `ZwQueryValueKey` as success.

## Internal IRP Sending

The send helpers allocate their own IRPs, fill one stack location, set a completion routine, call the target driver, wait if pending, and return the captured `IO_STATUS_BLOCK`.

They are used for:

- setting allocation/EOF information,
- querying security,
- querying EAs,
- sending Mount Manager buffered device-control requests.

The common completion routine copies `Irp->IoStatus`, signals an event, frees the IRP, and returns `STATUS_MORE_PROCESSING_REQUIRED`.

## User Buffer Handling

`FspBufferUserBuffer`:

- Handles zero length and already-buffered IRPs as success.
- Reuses kernel system buffers for kernel-mode system-range buffers.
- Otherwise allocates a nonpaged system buffer.
- Copies input for `IoReadAccess`; zeroes output buffers otherwise.
- Sets buffered I/O flags so I/O manager cleanup/copyback behavior applies.

`FspLockUserBuffer`:

- Allocates an MDL over `Irp->UserBuffer`.
- Probes and locks pages with exception handling.
- Stores the MDL in `Irp->MdlAddress`.

`FspMapLockedPagesInUserMode` wraps `MmMapLockedPagesSpecifyCache` with exception handling.

## Cache Manager Wrappers

The `FspCc*` functions wrap cache-manager calls in structured exception handling and return `NTSTATUS` rather than propagating exceptions. `FspCcCopyRead` and `FspCcCopyWrite` convert a false cache-manager return to `STATUS_PENDING`.

## Security and EA Validation

`FspQuerySecurityDescriptorInfo` wraps `SeQuerySecurityDescriptorInfo`, maps expected user-buffer exceptions to `STATUS_INVALID_USER_BUFFER`, and converts `STATUS_BUFFER_TOO_SMALL` to `STATUS_BUFFER_OVERFLOW`.

`FspEaBufferFromOriginatingProcessValidate`:

- Calls `IoCheckEaBufferValidity`.
- Validates every EA name with `FspEaNameIsValid`.
- Reports invalid EA offset.

`FspEaBufferFromFileSystemValidate`:

- Allows zero-length EA buffers.
- Normalizes the final EA's `NextEntryOffset` to zero before validation because user-mode filesystems may return a final nonzero offset.

## Safe MDL Logic

`FspSafeMdlCheck` returns true only when the MDL begins and ends on page boundaries.

`FspSafeMdlCreate` builds a replacement MDL that is safe to map to user mode:

- Gets a system address for the original MDL.
- Allocates a new MDL with copied PFN array.
- Detects unaligned first and last pages.
- Allocates nonpaged page buffers for edge pages.
- For input/read access, copies original edge-page data and zero-fills unused page portions.
- For output/write access, zeroes edge pages.
- Replaces first/last PFNs with the safe buffer PFNs.

`FspSafeMdlCopyBack` copies modified edge-page data back to the original user MDL for write operations.

`FspSafeMdlDelete` frees edge buffers, the replacement MDL, and the wrapper.

## IRP Completion Hooks

`FspIrpHook` replaces the current stack completion routine while preserving the prior routine/context/control flags in an allocated hook context when needed.

`FspIrpHookReset` restores or clears the completion routine.

`FspIrpHookNext` invokes the preserved completion routine if its original invoke flags match the final IRP state, otherwise propagates pending state. It frees the hook context.

## Unicode Comparison

`FspCompareUnicodeString` performs a fast ASCII path:

- Compares length first.
- For case-insensitive comparison, uses bit-twiddling ASCII upcase.
- Falls back to `RtlCompareUnicodeString` if either character is non-ASCII.
- In debug builds, compares the sign of the optimized result against `RtlCompareUnicodeString`.

## Notable Details

- Must-succeed allocation loops retry forever with increasing short delays.
- Many wrappers are paged, but completion and DPC routines are explicitly marked nonpaged by comments and omitted from alloc pragmas.
- The safe-MDL implementation is central to avoiding exposure of unrelated data in partially covered pages mapped to user mode.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/util.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/volinfo.c -->
# File Research: sources/windows/winfsp/src/sys/volinfo.c

## Purpose

`volinfo.c` implements volume information query and set handling for WinFsp filesystem volume devices. It answers static volume classes directly where possible, asks user mode for dynamic volume information when needed, and supports setting the filesystem label.

## Main Contents

Query helpers:

- `FspFsvolQueryFsAttributeInformation`
- `FspFsvolQueryFsDeviceInformation`
- `FspFsvolQueryFsFullSizeInformation`
- `FspFsvolQueryFsSectorSizeInformation`
- `FspFsvolQueryFsSizeInformation`
- `FspFsvolQueryFsVolumeInformation`
- `FspFsvolQueryVolumeInformation`
- `FspFsvolQueryVolumeInformationComplete`

Set helpers:

- `FspFsvolSetFsLabelInformation`
- `FspFsvolSetVolumeInformation`
- `FspFsvolSetVolumeInformationComplete`

Dispatch entries:

- `FspQueryVolumeInformation`
- `FspSetVolumeInformation`

## Query Behavior

`FspFsvolQueryVolumeInformation` handles these classes:

- `FileFsAttributeInformation`
- `FileFsDeviceInformation`
- `FileFsFullSizeInformation`
- `FileFsSectorSizeInformation`
- `FileFsSizeInformation`
- `FileFsVolumeInformation`

Static classes are answered directly from volume parameters. Dynamic classes use the `GETVOLUMEINFO` macro, which first tries cached volume information and returns `FSP_STATUS_IOQ_POST` when user mode must be queried.

If a user-mode query is required, the code creates a `FspFsctlTransactQueryVolumeInformationKind` request. Completion stores returned volume information in the fsvol device cache and formats the requested filesystem information class.

## Information Classes

`FspFsvolQueryFsAttributeInformation` fills:

- filesystem feature flags from volume parameters,
- maximum component length,
- filesystem name, optionally prefixed with `DRIVER_NAME` when the configured name begins with `-`, `/`, or `\`.

`FspFsvolQueryFsDeviceInformation` reports:

- `FILE_DEVICE_DISK`, intentionally required for `GetFileType` compatibility,
- device characteristics from the fsvol device object.

`FspFsvolQueryFsFullSizeInformation` and `FspFsvolQueryFsSizeInformation` compute allocation units from sector size and sectors per allocation unit.

`FspFsvolQueryFsSectorSizeInformation` reports logical and physical sector sizes equal to configured sector size and marks the device aligned with no seek penalty.

`FspFsvolQueryFsVolumeInformation` reports creation time, serial number, label length/text, and no object-ID support.

## Set Behavior

Only `FileFsLabelInformation` is supported.

`FspFsvolSetFsLabelInformation` has three modes:

- Preflight mode computes the extra request-buffer size from `VolumeLabelLength + sizeof(WCHAR)`.
- Request-fill mode writes the label into the request buffer and null-terminates it.
- Completion mode updates cached fsvol volume information from the response.

`FspFsvolSetVolumeInformation` validates the class, creates a `FspFsctlTransactSetVolumeInformationKind` request, fills it, and posts to IOQ.

`FspFsvolSetVolumeInformationComplete` propagates user-mode failure status or updates cached volume info and completes with zero information.

## Buffer Handling

- Each query helper checks fixed-structure space before writing.
- Variable-length names/labels may return `STATUS_BUFFER_OVERFLOW` after copying what fits.
- `IoStatus.Information` is always set to bytes written from the original system buffer.

## Notable Details

- `FileFsSectorSizeInformation` does not require dynamic user-mode volume info.
- Query/set dispatch accepts only `FspFsvolDeviceExtensionKind`.
- `FspFsvolSetVolumeInformationComplete` reads `Length` from `IrpSp->Parameters.SetFile.Length` even though this is a set-volume completion path; the label completion mode does not currently use that length, but it is a notable field mismatch.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/volinfo.c -->