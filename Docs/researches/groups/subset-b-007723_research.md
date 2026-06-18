# subset-b-007723 research

Grouped research for OpenAFS Windows redirector library sources. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSInit.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSInit.cpp

## Purpose

`AFSInit.cpp` contains the Windows kernel driver's library entry and unload paths. `DriverEntry` establishes global driver state, creates the library control device, initializes library-specific resources, and installs dispatch handlers for the Windows I/O major-function table. `AFSUnload` reverses the library lifetime: it invalidates the global root volume, tears down worker pools and library devices, releases global memory, and closes library state.

## Important APIs, types, and functions

- `DriverEntry(PDRIVER_OBJECT, PUNICODE_STRING)` is the driver load entry point called by the I/O manager.
- `AFSUnload(PDRIVER_OBJECT)` is registered as `DriverObject->DriverUnload`.
- `AFSDeviceExt` is the per-device extension used after `IoCreateDevice`, including `Specific.Library.WorkerCount` and `IOWorkerCount`.
- Global state touched here includes `AFSLibraryDriverObject`, `AFSRegistryPath`, `AFSRtlSysVersion`, `AFSRtlSetGroupSecurityDescriptor`, `AFSLibraryDeviceObject`, `AFSSysProcess`, `AFSGlobalRoot`, and `AFSDefaultSD`.
- Initialization dependencies include `AFSCreateDefaultSecurityDescriptor`, `AFSInitializeLibraryDevice`, `AFSRemoveLibraryDevice`, and `AFSCloseLibrary`.
- The dispatch table is populated with `AFSDefaultDispatch` for all major functions, then replaced for create, close, read, write, query/set information, EA, flush, volume information, directory control, FS control, device control, internal device control, shutdown, lock control, cleanup, security, and WMI/system control.

## Control flow

`DriverEntry` starts inside an exception filter guarded block. It prints the build date/time, keeps a disabled `bExit` backdoor, stores the driver object globally, and copies the registry path into paged pool with `AFSLibExAllocatePoolWithTag`. It captures the OS version via `RtlGetVersion`, dynamically resolves `RtlSetGroupSecurityDescriptor` through `MmGetSystemRoutineAddress`, and attempts to build a default security descriptor. A security-descriptor failure is logged but deliberately downgraded to success, so driver load continues.

The driver creates `AFS_LIBRARY_CONTROL_DEVICE_NAME` with `IoCreateDevice` as a network file-system device. After device creation, it initializes the library device with `AFSInitializeLibraryDevice`, zeros worker-count fields, fills the dispatch table, registers unload, and records the system process id. The `try_return`/`try_exit` pattern centralizes failure cleanup: on failed load it frees `AFSRegistryPath.Buffer`, removes and deletes the library device if present, logs the failure, and returns the failing status.

`AFSUnload` invalidates and shuts down `AFSGlobalRoot` if present, removes the worker pool if the library device exists, frees the copied registry path and default security descriptor, closes the library, removes the library device, and deletes the device object.

## State and persistence behavior

This file owns process-lifetime kernel state, not durable on-disk state. The registry path is copied into global memory for later library use. `AFSRtlSysVersion` and the optional `AFSRtlSetGroupSecurityDescriptor` function pointer are process-wide compatibility state. The control device object and dispatch table are persistent for the loaded driver lifetime. Worker counts are initialized to zero here and later mutated by worker-pool code. On unload, global root volume state is invalidated and worker/library resources are released.

## Dependencies and integration points

The code integrates directly with the Windows I/O manager through `IoCreateDevice`, `IoDeleteDevice`, the major-function table, and `DriverUnload`. It relies on OpenAFS library support from `AFSCommon.h`, including allocation wrappers, exception handling, trace dumping, security descriptor setup, volume invalidation, worker-pool teardown, and library-device lifecycle helpers. It also registers `AFSInternalDevControl` and `AFSLockControl`, which are researched in this group.

## Risks and edge cases

- `AFSCreateDefaultSecurityDescriptor` failure is ignored after logging. This is intentional-looking compatibility behavior, but it may result in later security behavior depending on a missing or defaulted descriptor.
- `AFSRegistryPath.MaximumLength` is copied from the source string, but allocation uses `Length`, not `MaximumLength`. That is acceptable for a copied immutable path but unsafe if later code assumes spare terminator space.
- `AFSUnload` does not null global pointers after freeing/deleting. The lifetime is driver unload, so reuse should not occur, but crash-dump or double-unload paths would be sensitive.
- The exception handler in `DriverEntry` logs and dumps traces but does not explicitly convert the exception to a failing status. If an exception occurs before `ntStatus` is set to failure, the return value can remain `STATUS_SUCCESS`.
- Dispatch registration makes this file a blast-radius center: wrong handler wiring affects every IRP type.

## Test signals

Useful validation signals include successful driver load/unload on supported Windows versions, existence and deletion of the library control device, correct dispatch-table entries for all implemented IRP major functions, failure-injection of registry-path and device allocation, and load behavior when `RtlSetGroupSecurityDescriptor` is unavailable. Runtime logs should show build initialization, device initialization failures when injected, and clean unload without leaked worker threads or volume references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSInit.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSInternalDevControl.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSInternalDevControl.cpp

## Purpose

`AFSInternalDevControl.cpp` implements the `IRP_MJ_INTERNAL_DEVICE_CONTROL` dispatch hook for the library device. In the current code it is a deliberate stub: every internal device-control IRP is completed with `STATUS_NOT_IMPLEMENTED`.

## Important APIs, types, and functions

- `AFSInternalDevControl(PDEVICE_OBJECT, PIRP)` is installed by `DriverEntry`.
- `IoGetCurrentIrpStackLocation` obtains the `IO_STACK_LOCATION`, though the returned stack pointer is not used after assignment.
- `AFSCompleteRequest` completes the IRP with the selected status.
- `AFSExceptionFilter`, `AFSDbgTrace`, and `AFSDumpTraceFilesFnc` provide exception tracing.

## Control flow

The dispatch function ignores `LibDeviceObject`, initializes `ntStatus` to `STATUS_NOT_IMPLEMENTED`, obtains the current IRP stack location, enters an exception-guarded block, completes the IRP with `STATUS_NOT_IMPLEMENTED`, and returns the same status. If an exception occurs during completion, the handler logs and dumps trace files, then falls through returning the initialized status.

## State and persistence behavior

The function has no persistent state and does not mutate driver structures. Its only side effect is IRP completion. Because the IRP stack location is not inspected, all IOCTL codes, buffer methods, and caller identities receive identical treatment.

## Dependencies and integration points

This function is wired by `AFSInit.cpp` into `DriverObject->MajorFunction[IRP_MJ_INTERNAL_DEVICE_CONTROL]`. It depends on the common OpenAFS request-completion and exception-tracing helpers. It does not call into cache manager, file-system runtime, service request, or redirector state.

## Risks and edge cases

- Since all internal device-control requests are rejected, any filter, file-system stack participant, or future feature expecting private internal IOCTL behavior will fail.
- The unused `pIrpSp` assignment may hide missing validation or planned switch logic.
- The function completes the IRP inside the try block; if completion itself faults, the exception path does not attempt a second completion, which is appropriate but leaves fault handling to tracing.

## Test signals

Tests should assert that an internal device-control IRP completes exactly once with `STATUS_NOT_IMPLEMENTED` and no information payload. Driver verifier or IRP instrumentation can confirm no pending IRP is leaked. A regression signal for future work would be a new internal IOCTL requiring a non-stub switch on `Parameters.DeviceIoControl.IoControlCode`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSInternalDevControl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSIoSupport.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSIoSupport.cpp

## Purpose

`AFSIoSupport.cpp` contains helper logic for non-cached and paging I/O over OpenAFS cache-file extents. It maps a caller's file offset and length onto one or more cached extents, collapses contiguous cache extents into I/O runs, allocates and launches child IRPs, aggregates asynchronous completions, and provides a direct memory-copy path for processing extent runs against `AFSLibCacheBaseAddress`.

## Important APIs, types, and functions

- `AFSGetExtents(AFSFcb *, PLARGE_INTEGER, ULONG, AFSExtent *, ULONG *, ULONG *)` counts the number of file extents and discontiguous cache runs covering a request span.
- `AFSSetupIoRun(PDEVICE_OBJECT, PIRP, PVOID, AFSIoRun *, PLARGE_INTEGER, ULONG, AFSExtent *, ULONG *)` builds child IRPs and cache offsets for each contiguous run.
- `AFSStartIos(PFILE_OBJECT, UCHAR, ULONG, AFSIoRun *, ULONG, AFSGatherIo *)` fills child IRP stack locations and submits them to the cache device.
- `CompletionFunction` is the child IRP completion routine; it forwards status to `AFSCompleteIo`, unlocks/free MDLs if present, frees the child IRP, and returns `STATUS_MORE_PROCESSING_REQUIRED`.
- `AFSCompleteIo(AFSGatherIo *, NTSTATUS)` aggregates completion status and either completes the master IRP, signals a synchronous waiter, or frees the gather object.
- `AFSProcessExtentRun(PVOID, PLARGE_INTEGER, ULONG, AFSExtent *, BOOLEAN)` copies bytes between a system buffer and the mapped cache base over one or more extent runs.
- Key structures are `AFSExtent`, `AFSIoRun`, and `AFSGatherIo`; key list helper/macros include `AFSExtentContains` and `NextExtent(..., AFS_EXTENTS_LIST)`.

## Control flow

`AFSGetExtents` assumes `From` contains the start offset, then walks `NextExtent` until the requested span is covered. It increments `ExtentCount` for every extent and `RunCount` whenever the next extent is not contiguous in cache-file offset.

`AFSSetupIoRun` repeats the same span walk while building runnable cache I/O segments. For each run it computes the cache offset by adding the delta between requested file offset and extent file offset, advances across adjacent extents whose cache offsets are contiguous, trims the final run to the requested length, computes the caller-buffer offset, fills `AFSIoRun.CacheOffset` and `ByteCount`, and allocates a child IRP with `IoAllocateIrp(CacheDevice->StackSize + 1, FALSE)`. The child IRP is initialized with a user-buffer pointer into the supplied system buffer, current thread, kernel requestor mode, and no MDL. On allocation failure it frees all child IRPs in the caller-provided run array and returns `STATUS_INSUFFICIENT_RESOURCES`; on success it updates `*RunCount` to the actual run count.

`AFSStartIos` obtains the related cache device object from the cache file object, iterates prepared runs, writes the next stack location for read/write style parameters, increments `Gather->Count` before calling the driver, installs `CompletionFunction`, and submits with `IoCallDriver`. It stops and returns on the first synchronous failure from `IoCallDriver`.

`CompletionFunction` calls `AFSCompleteIo` with the child IRP status, unlocks and frees any MDL, frees the IRP, and claims ownership from the I/O manager by returning `STATUS_MORE_PROCESSING_REQUIRED`.

`AFSCompleteIo` records the first failing status into `Gather->Status`, decrements the outstanding count, and when the count reaches zero updates the master IRP failure fields, optionally completes the master IRP, signals the event for synchronous gathers, or frees the gather allocation for asynchronous gathers.

`AFSProcessExtentRun` mirrors the run-collapsing logic without child IRPs. It copies between `SystemBuffer` and `AFSLibCacheBaseAddress + CacheOffset` for writes or reads, with an `AMD64` path using the 64-bit offset and a 32-bit path asserting `HighPart == 0`.

## State and persistence behavior

This file does not own durable state. It mutates transient IRPs, I/O run arrays, and `AFSGatherIo` counters/status. The extent list is treated as stable during the call; callers must hold any required FCB or extent-list synchronization. `AFSCompleteIo` owns the lifetime transition for `AFSGatherIo` depending on synchronous/asynchronous mode, and `CompletionFunction` owns child IRP and MDL cleanup. `AFSProcessExtentRun` directly mutates either the caller's system buffer or the cache memory mapping.

## Dependencies and integration points

The code sits between higher-level read/write paths and the Windows cache file/device. It depends on `AFSFcb` extent metadata, `AFSExtent` list ordering, OpenAFS allocation/free tags, `AFSCompleteRequest`, Windows IRP allocation/submission APIs, `IoGetRelatedDeviceObject`, interlocked counters, kernel events, and the global cache mapping `AFSLibCacheBaseAddress`. It is expected to be called by paging or non-cached read/write paths after an extent lookup has selected the starting extent.

## Risks and edge cases

- The span walkers assume valid, sufficient extents. If the extent list ends early or `NextExtent` returns an invalid node, the code has no explicit bounds check beyond asserts.
- `Length` and run byte counts are `ULONG`; very large requests must be split by callers or can truncate run lengths.
- `AFSStartIos` increments `Gather->Count` before each `IoCallDriver`, but if `IoCallDriver` returns a failure for an IRP that will not complete asynchronously, the count may remain elevated unless lower-layer semantics still invoke completion.
- `AFSSetupIoRun` cleanup loops over the original `*RunCount`, so callers must zero-initialize `IoRuns` or stale child pointers could be freed on an early allocation failure.
- Direct memory copies in `AFSProcessExtentRun` trust `AFSLibCacheBaseAddress` and extent offsets; corrupt extent metadata can become kernel memory corruption.
- The completion routine frees MDLs if present, although setup initializes child MDL to null. If a lower layer attaches an MDL with different ownership expectations, this ownership convention matters.

## Test signals

Focused tests should cover single-extent reads/writes, multi-extent cache-contiguous coalescing into one run, discontiguous extents producing multiple runs, trimmed first and final extents, child IRP allocation failure cleanup, completion aggregation where one child fails, synchronous gather event signaling, asynchronous gather free behavior, and 32-bit high-offset assertion behavior. Integration signals include correct non-cached/paging I/O data across sparse/discontiguous cache extents and no IRP/MDL leaks under driver verifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSIoSupport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSLockControl.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSLockControl.cpp

## Purpose

`AFSLockControl.cpp` implements the `IRP_MJ_LOCK_CONTROL` dispatch path for byte-range locks. It validates the target FCB, coordinates with the OpenAFS service to establish or release file-server byte-range locks, flushes cached data before unlock operations, and then hands the IRP to the Windows file-lock runtime through `FsRtlProcessFileLock`.

## Important APIs, types, and functions

- `AFSLockControl(PDEVICE_OBJECT, PIRP)` is the dispatch function installed by `DriverEntry`.
- It uses `AFSFcb` from `FileObject->FsContext` and `AFSCcb` from `FsContext2`.
- Lock protocol structures include `AFSByteRangeLockRequestCB`, `AFSByteRangeLockResultCB`, `AFSByteRangeUnlockRequestCB`, and `AFSByteRangeUnlockResultCB`.
- `AFSProcessRequest` sends synchronous service requests for `AFS_REQUEST_TYPE_BYTE_RANGE_LOCK`, `AFS_REQUEST_TYPE_BYTE_RANGE_UNLOCK_ALL`, and `AFS_REQUEST_TYPE_BYTE_RANGE_UNLOCK`.
- `FsRtlProcessFileLock` performs local Windows lock-package processing against `pFcb->Specific.File.FileLock`.
- `CcFlushCache` flushes section object data before unlocks.
- Synchronization uses `AFSAcquireShared` and `AFSReleaseResource` on `pFcb->NPFcb->Resource` and `SectionObjectResource`.

## Control flow

The function obtains the current IRP stack, extracts FCB and CCB, validates that the FCB exists, and acquires the main FCB resource shared. It rejects IOCTL, special-share, and invalid FCB node types with `STATUS_INVALID_DEVICE_REQUEST`.

For `IRP_MN_LOCK`, it builds a one-entry exclusive byte-range lock request with the current process id, requested byte offset, and length. It sends the request synchronously to the service with the caller's auth group, directory file name, object file id, and volume cell identity. If the service rejects the lock, the IRP is completed immediately with that status.

For `IRP_MN_UNLOCK_ALL` and `IRP_MN_UNLOCK_ALL_BY_KEY`, it acquires the section-object resource shared, flushes the entire file with `CcFlushCache`, logs failures, releases the section-object resource, zeroes and fills an unlock-all request with the current process id, and sends it to the service. A comment states that even service failure should still notify the RTL lock package.

For `IRP_MN_UNLOCK_SINGLE`, it flushes the specific byte range, logs any flush failure, fills a one-entry exclusive unlock request, and sends it to the service.

After the service-side work, the code sets `bCompleteRequest = FALSE` and calls `FsRtlProcessFileLock`. From that point the Windows lock package owns IRP completion. On earlier validation/service failures, `bCompleteRequest` remains true and `AFSCompleteRequest` completes the IRP in `try_exit`. The exception handler traces, dumps, sets `STATUS_UNSUCCESSFUL`, and completes the IRP.

## State and persistence behavior

Local lock state lives in `pFcb->Specific.File.FileLock` and is updated by `FsRtlProcessFileLock`. Remote/server lock state is mediated by synchronous `AFSProcessRequest` calls using the current process id and object identity. Unlock paths flush cached data before informing the server and local lock runtime. No durable state is written directly in this file, but lock state affects ongoing file access semantics and server-side coordination.

## Dependencies and integration points

This file bridges Windows lock IRPs, cache-manager flushing, OpenAFS FCB/CCB structures, service RPC/control-block protocol, and the FsRtl lock package. It depends on object identity from `pFcb->ObjectInformation`, auth and file-name context from `pCcb`, volume cell metadata, and initialized file-lock state on the FCB. It is registered in `AFSInit.cpp` for `IRP_MJ_LOCK_CONTROL`.

## Risks and edge cases

- Shared FCB locking protects metadata lookup but lock state is ultimately delegated to FsRtl; callers must ensure the FCB and CCB lifetimes remain stable through synchronous service calls.
- Unlock-all-by-key is treated the same as unlock-all for the service request, and the key is not propagated to the server request.
- The service lock request always uses `AFS_BYTE_RANGE_LOCK_TYPE_EXCL`; shared lock intent is not distinguished in this function.
- `Length->LowPart` is passed to `CcFlushCache` for single unlock range flushing, so ranges larger than 4 GiB are not fully represented in the flush length.
- Flush failures are logged and assigned to `ntStatus`, but the code can still proceed to service unlock and then `FsRtlProcessFileLock`, potentially masking or replacing the earlier status.
- If `pCcb` or nested fields such as `DirectoryCB` are null, the code would fault; only `pFcb` is explicitly checked.

## Test signals

Validation should include successful exclusive lock, service-denied lock, unlock-single with range flush, unlock-all with full flush, invalid FCB node types, null FCB, and exception handling around `CcFlushCache`. Test doubles for `AFSProcessRequest` should verify request type, process id, byte offset, length, file id, auth group, file name, and cell metadata. Integration tests should confirm local Windows byte-range behavior matches server-side lock grant/release and that cached dirty data is flushed before unlock release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSLockControl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSMD5Support.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSMD5Support.cpp

## Purpose

`AFSMD5Support.cpp` embeds an independent MD5 implementation derived from L. Peter Deutsch's Aladdin Enterprises source and exposes an OpenAFS wrapper, `AFSGenerateMD5`, for hashing a buffer into a 16-byte digest. It is a local digest utility for kernel code that needs deterministic MD5 without depending on a separate crypto provider.

## Important APIs, types, and functions

- `md5_byte_t`, `md5_word_t`, and `md5_state_t` define the MD5 byte, word, and state layout.
- `md5_init(md5_state_t *)` initializes count and the four MD5 state words.
- `md5_append(md5_state_t *, const md5_byte_t *, int)` updates the message length, processes full 64-byte blocks, and stores trailing partial bytes.
- `md5_finish(md5_state_t *, md5_byte_t digest[16])` pads the message, appends the bit length, and emits the digest in little-endian byte order.
- `md5_process(md5_state_t *, const md5_byte_t *)` is the internal 64-byte compression routine implementing all four MD5 rounds.
- `AFSGenerateMD5(char *DataBuffer, ULONG Length, UCHAR *MD5Digest)` is the OpenAFS-facing wrapper.

## Control flow

`AFSGenerateMD5` creates a stack `md5_state_t`, initializes it, appends the caller buffer of the supplied length, and finishes into the caller-provided digest buffer.

The MD5 implementation maintains a 64-bit bit count in two 32-bit words. `md5_append` updates that count, fills any existing partial block, processes full 64-byte blocks via `md5_process`, and copies a final partial block into state. `md5_finish` snapshots the original bit length, appends the standard `0x80` then zero padding to reach 56 bytes modulo 64, appends the saved bit length, and serializes the four state words into 16 digest bytes.

`md5_process` reads the block as 16 little-endian words. On little-endian aligned data it aliases the input directly; otherwise it copies the block into an aligned local buffer with `RtlCopyMemory`. It then applies the standard MD5 F, G, H, and I rounds using predefined constants and rotate counts, finally adding the working registers back into the state.

## State and persistence behavior

All hash state is stack/local to the call chain. There is no global mutable state and no persistence. The digest output is entirely determined by `DataBuffer` and `Length`. The implementation assumes little-endian CPU behavior for direct aligned block interpretation, which matches Windows targets for this driver era.

## Dependencies and integration points

The only OpenAFS/NT dependency inside the algorithm is `RtlCopyMemory` and the surrounding `__Enter` macro in `AFSGenerateMD5`. The wrapper likely serves cache naming, identity, validation, or protocol code elsewhere in the redirector/library. The file includes `AFSCommon.h` for kernel types and macros.

## Risks and edge cases

- MD5 is cryptographically broken for collision resistance. It is acceptable only for non-adversarial checksums, legacy identifiers, or compatibility protocols, not for security decisions requiring collision resistance.
- `md5_append` accepts `int nbytes`; `AFSGenerateMD5` passes a `ULONG Length`, so values above `INT_MAX` can wrap or become negative depending on ABI conversion.
- The direct aligned read path assumes little-endian interpretation and sufficient alignment; the comments describe endian handling historically, but this version does not include a byte-swap path for big-endian targets.
- The implementation does not validate null `DataBuffer` or `MD5Digest`; callers must pass valid buffers for the requested length.

## Test signals

Known RFC 1321 MD5 vectors should pass, including empty string, `"a"`, `"abc"`, long multi-block inputs, and lengths around 55, 56, 63, 64, and 65 bytes. Kernel wrapper tests should verify digest output for aligned and unaligned buffers, zero-length input, and a large input below the `int` limit. Security review should flag any caller using this digest as an authenticity or collision-resistant trust boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSMD5Support.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSNameArray.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSNameArray.cpp

## Purpose

`AFSNameArray.cpp` manages `AFSNameArrayHdr` path-tracking arrays used by the Windows redirector to represent a sequence of directory control blocks from a volume/share root through path components. The helpers allocate, populate, clone, extend, backtrack, reset, dump, and free these arrays while maintaining `AFSDirectoryCB::NameArrayReferenceCount` references.

## Important APIs, types, and functions

- `AFSInitNameArray(AFSDirectoryCB *, ULONG)` allocates a name array and optionally seeds it with one directory entry.
- `AFSPopulateNameArray(AFSNameArrayHdr *, UNICODE_STRING *, AFSDirectoryCB *)` initializes an existing array with the volume root entry for a directory's volume.
- `AFSPopulateNameArrayFromRelatedArray(AFSNameArrayHdr *, AFSNameArrayHdr *, AFSDirectoryCB *)` copies entries from a related array up to a requested directory or the related array end.
- `AFSFreeNameArray(AFSNameArrayHdr *)` decrements all held directory references and frees the array.
- `AFSInsertNextElement(AFSNameArrayHdr *, AFSDirectoryCB *)` appends a directory entry while rejecting recursive FID reuse.
- `AFSBackupEntry(AFSNameArrayHdr *)` removes the current entry, returns the new current directory, and recursively removes an associated mount point when backing out of a volume root.
- `AFSGetParentEntry(AFSNameArrayHdr *)` returns the previous entry without mutating the array.
- `AFSResetNameArray(AFSNameArrayHdr *, AFSDirectoryCB *)` releases current contents, zeroes the allocation, and optionally seeds a new first entry.
- `AFSDumpNameArray(AFSNameArrayHdr *)` prints all populated entries.
- Core data includes `AFSNameArrayHdr`, `AFSNameArrayCB`, `AFSDirectoryCB`, `AFSFileID`, `Count`, `MaxElementCount`, `CurrentEntry`, `LinkCount`, `Component`, `FileId`, and `AFS_NAME_ARRAY_FLAG_ROOT_ELEMENT`.

## Control flow

`AFSInitNameArray` chooses the initial capacity from the caller or `AFSRDRDeviceObject->DeviceExtension->Specific.RDR.NameArrayLength`, allocates a header plus element array from paged pool, zeroes it, stores `MaxElementCount`, and if a directory is supplied, seeds element zero with that directory's file name and file id, marks vnode 1 as a root element, increments the directory's name-array reference count, sets `CurrentEntry`, `Count`, and `LinkCount`, and traces the entry.

`AFSPopulateNameArray` resets header cursor state to element zero and seeds that element from the volume root associated with `DirectoryCB`. It increments the volume root directory reference, marks root element when vnode is 1, sets `Count` to one, and returns early if the target directory is the volume root. The `Path` argument is only used in tracing.

`AFSPopulateNameArrayFromRelatedArray` copies entries from another name array. For each copied entry it uses the related element's `DirectoryCB`, copies the current file name and file id from live directory/object information, marks root elements, increments the copied directory reference, increments this array's count, and stops when it reaches the requested `DirectoryCB` or the related count. `CurrentEntry` is set to the last copied element.

`AFSFreeNameArray` walks `Count` entries, decrements each directory's `NameArrayReferenceCount`, asserts non-negative counts, and frees the allocation with `AFS_NAME_ARRAY_TAG`.

`AFSInsertNextElement` first checks capacity, then scans existing entries for the same file id with `AFSIsEqualFID` to reject recursion with `STATUS_ACCESS_DENIED`. It advances or initializes `CurrentEntry`, increments `Count` and the directory reference count, fills component, file id, flags, and traces the inserted element.

`AFSBackupEntry` removes the current element by decrementing its directory reference, nulling its `DirectoryCB`, decrementing array count, moving `CurrentEntry` backward if any entries remain, and returning the new current directory. If the removed element was a volume root and the new current element is not also root, it recursively backs up once more to remove the mount point entry paired with that volume root.

`AFSGetParentEntry` returns element `Count - 2` when at least two entries exist. `AFSResetNameArray` mirrors free-then-seed behavior without freeing the allocation: it decrements references for current entries, zeroes the header and configured array footprint, resets capacity, and optionally seeds a first directory. `AFSDumpNameArray` prints entries until it reaches a null `DirectoryCB`.

## State and persistence behavior

Name arrays are transient in-memory path state. Their most important side effect is reference accounting on each `AFSDirectoryCB` they hold. Every insert/populate copy increments `NameArrayReferenceCount`; free, reset, and backup decrement it. `Count`, `CurrentEntry`, `LinkCount`, and root flags encode traversal state. No on-disk state is persisted, but incorrect reference accounting can keep directory entries alive too long or free them while still represented in a path traversal.

## Dependencies and integration points

This module depends on redirector device configuration (`AFSRDRDeviceObject`, `Specific.RDR.NameArrayLength`), pool allocation wrappers, OpenAFS debug tracing, `AFSDirectoryCB` and object/volume metadata, interlocked reference counters, FID equality via `AFSIsEqualFID`, and root semantics based on vnode `1`. Name arrays are likely used by path parsing, mount-point traversal, related-open handling, and directory lookup code elsewhere in the redirector.

## Risks and edge cases

- `AFSPopulateNameArray` does not actually parse or append `Path`; it only seeds the volume root. Callers must insert subsequent path elements elsewhere.
- Several functions assume non-null `DirectoryCB`, `ObjectInformation`, `VolumeCB`, and `AFSRDRDeviceObject` once called; invalid callers will fault.
- `AFSResetNameArray` zeroes using the current global configured `NameArrayLength`, not `NameArray->MaxElementCount`. If the original allocation used a different `InitialElementCount`, this can under-zero or over-zero relative to the allocation.
- `AFSDumpNameArray` walks until `DirectoryCB == NULL` rather than using `Count`, so a corrupt or non-zeroed array can be overrun.
- `AFSInsertNextElement` protects against recursive FIDs, but `AFSPopulateNameArrayFromRelatedArray` copies related entries without checking capacity against `NameArray->MaxElementCount`.
- The reference-count discipline is manual and spread across populate, insert, backup, reset, and free paths; missed decrement or double decrement would destabilize directory lifetime.

## Test signals

Tests should cover allocation with default and explicit capacities, seeding with null and non-null directory entries, volume-root flagging for vnode 1, populate from a related array stopping at a target directory, capacity exhaustion, recursion detection by equal FID, backup from normal entries, backup from volume-root entries with mount-point removal, parent lookup at counts zero/one/two, reset after non-empty arrays, and free reference-count balance. Instrumentation should assert every increment has a matching decrement across successful and failing path traversal scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSNameArray.cpp -->
