# Group Research: group_1856_winfsp_sources_windows_winfsp_src_dll_path_c_sources_windows_winfsp_76f2dcef57ff

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/path.c -->
# File Research: sources/windows/winfsp/src/dll/path.c

Tiny in-place wide-string path helper module for WinFsp DLL code.

Key functions:
- `FspPathPrefix(Path, PPrefix, PRemain, Root)`: splits `Path` at the first backslash, replaces that separator with `NUL`, skips repeated separators, and returns prefix/remainder pointers. If the prefix is the leading root separator and `Root` is supplied, the prefix pointer is replaced with `Root`.
- `FspPathSuffix(Path, PRemain, PSuffix, Root)`: splits at the final path separator, replacing it with `NUL`; handles root specially via `Root`; returns suffix as the final component or the string end if no separator exists.
- `FspPathCombine(Prefix, Suffix)`: restores previously split path separators by converting embedded `NUL` characters between `Prefix` and `Suffix` back to backslashes.

Important behavior:
- All helpers mutate the input path buffer.
- Repeated backslashes after a split separator are skipped.
- Used by security and utility code to temporarily isolate parent/name components without extra allocation.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/path.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/security.c -->
# File Research: sources/windows/winfsp/src/dll/security.c

Implements user-mode WinFsp access-check and security descriptor helpers around Windows security APIs.

Key globals/APIs:
- `FspFileGenericMapping`: maps generic file rights to `FILE_GENERIC_*` and `FILE_ALL_ACCESS`.
- `FspGetFileGenericMapping()`: exposes that mapping.

Core flow:
- `FspGetSecurityByName()` calls the file-system `GetSecurityByName` callback, reallocating the descriptor buffer on `STATUS_BUFFER_OVERFLOW`.
- `FspAccessCheckEx()` validates create requests and performs access checks for:
  - full target file access,
  - parent directory access,
  - main file access for named streams,
  - traverse access through each path component when the caller lacks traverse privilege.
- Reparse points are detected from returned attributes and converted to `STATUS_REPARSE` with the suffix index encoded in granted access.
- Parent checks can grant effective `DELETE` or `FILE_READ_ATTRIBUTES` through `FILE_DELETE_CHILD` or `FILE_LIST_DIRECTORY`, matching Windows semantics.
- Readonly files deny write/add/delete-child access and readonly delete-on-close yields `STATUS_CANNOT_DELETE`.

Descriptor lifecycle:
- `FspCreateSecurityDescriptor()` wraps `CreatePrivateObjectSecurity`, skips named-stream descriptors, and builds a child descriptor from an optional parent and create SD.
- `FspSetSecurityDescriptor()` works around `SetPrivateObjectSecurity` ownership expectations by copying the input SD onto the process heap before calling it.
- `FspDeleteSecurityDescriptor()` frees descriptors according to the creator path: `MemFree` for descriptors returned by access/Posix helpers, `DestroyPrivateObjectSecurity` for private-object APIs.

Important dependencies:
- File-system callback table: `FileSystem->Interface->GetSecurityByName`.
- Path helpers: `FspPathSuffix`, `FspPathCombine`, `FspPathSuffixIndex`.
- Windows APIs: `AccessCheck`, `CreatePrivateObjectSecurity`, `SetPrivateObjectSecurity`.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/security.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/service.c -->
# File Research: sources/windows/winfsp/src/dll/service.c

Implements WinFsp service hosting, including SCM mode, console fallback mode, stop/control dispatch, service-context validation, and logging.

Main lifecycle:
- `FspServiceRunEx()` creates a service object, enables console mode, runs the loop, returns the service exit code, and deletes the object.
- `FspServiceCreate()` allocates `FSP_SERVICE`, stores callbacks, initializes status/stop critical sections, and sets accepted controls.
- `FspServiceLoop()` serializes dispatcher use with `FspServiceLoopLock`, installs a temporary service table, and calls `StartServiceCtrlDispatcherW`.
- If SCM connection fails with `ERROR_FAILED_SERVICE_CONTROLLER_CONNECT` and console mode is allowed, it creates a console event, installs `FspServiceConsoleCtrlHandler`, starts a thread that invokes `FspServiceMain`, then waits for console stop signal.

Status and stop handling:
- `FspServiceSetStatus()` updates selected `SERVICE_STATUS` fields under lock and reports to SCM or signals the console event on stop.
- `FspServiceRequestTime()` increments checkpoint and wait hint.
- `FspServiceStop()` guards against concurrent stop, transitions to `STOP_PENDING`, calls `OnStop`, then either reports stopped or reverts status on failure.
- `FspServiceStopLoop()` can stop the currently registered service from a helper thread.

Control handling:
- `FspServiceCtrlHandler()` handles stop/shutdown, pause/continue unsupported, interrogate success, and delegates unknown controls to `OnControl`.
- `FspServiceConsoleCtrlHandler()` maps Ctrl-C/break/close/shutdown to the console stop event; close/shutdown may sleep to allow cleanup; logoff is ignored.

Context and logging:
- `FspServiceIsInteractive()` detects visible process window station.
- `FspServiceContextCheck()` verifies a token is session 0 and either LocalSystem or a member of Service SID; can duplicate current process token if none is supplied.
- `FspServiceLogV()` writes UTF-8 text to stderr when interactive, otherwise logs through `FspEventLogV`.

Concurrency details:
- Uses SRW locks for global service loop/table protection.
- Uses critical sections for per-service status and stop serialization.
- Finalization intentionally only closes the console event on explicit unload.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/service.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/sxs.c -->
# File Research: sources/windows/winfsp/src/dll/sxs.c

Computes the side-by-side identity/suffix for WinFsp DLL deployments.

Initialization:
- `FspSxsIdentInitialize()` runs once via `InitOnceExecuteOnce`.
- First tries `FspSxsIdentInitializeFromFile()`:
  - gets current DLL path from `DllInstance`,
  - changes `.dll` or `-arch.dll` naming into `.sxs`,
  - reads first UTF-8 line,
  - stores separator plus identifier in `FspSxsIdentBuf`.
- Falls back to `FspSxsIdentInitializeFromDirectory()`:
  - opens the DLL and gets final path,
  - scans for `\SXS\SXS.<ident>\`,
  - extracts `<ident>` into the same buffer.

Exported/internal helpers:
- `FspSxsIdent()`: returns identity without separator.
- `FspSxsSuffix()`: returns separator-prefixed suffix.
- `FspSxsAppendSuffix(Buffer, Size, Ident)`: appends current suffix to a supplied identifier, returning `L"<INVALID>"` if the caller buffer is too small.

Important behavior:
- Identifier buffer is small and bounded: 32 plus separator/NUL storage.
- Fallback directory parsing supports SxS layouts even without a companion `.sxs` file.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/sxs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/util.c -->
# File Research: sources/windows/winfsp/src/dll/util.c

DLL utility module for diagnostics, directory creation through `NtCreateFile`, secure named-pipe calls, module version lookup, and adaptive locking.

Diagnostic identity:
- `FspDiagIdent()` lazily derives a short identifier from the process module basename without extension, defaulting to `UNKNOWN`.

Directory creation:
- `FspCreateDirectoryFileW()` dynamically resolves `NtCreateFile` from `ntdll.dll`.
- Builds a parent-relative `OBJECT_ATTRIBUTES` using a parent directory handle.
- Forces directory create semantics via `FILE_DIRECTORY_FILE` and maps selected Win32 file flags to NT create options.
- Returns Win32-style errors through `SetLastError`.

Named-pipe security:
- `FspCallNamedPipeSecurely()` delegates to `FspCallNamedPipeSecurelyEx()`.
- Opens the pipe with identification or optional impersonation SQOS.
- Retries once after `ERROR_PIPE_BUSY` using `WaitNamedPipeW`.
- Optionally verifies pipe owner SID; small numeric `Sid` values are treated as `WELL_KNOWN_SID_TYPE`.
- Switches to message read mode and calls `TransactNamedPipe`.

Version helpers:
- `FspVersion()` caches the DLL file version MS word from version resources.
- `FspGetModuleVersion()` does the same for an arbitrary module path without global cache.
- `FspGetModuleFileName()` resolves module path, optionally combining with a relative path.

Adaptive lock:
- `FspAdaptiveLockAcquire()` always takes an SRW lock and optionally attempts a one-byte overlapped file lock at a specified offset.
- `FspAdaptiveLockRelease()` unlocks/closes the file handle if acquired and releases the SRW lock.

Notable concerns:
- `FspVersion()` is intentionally not fully thread-safe, relying on same-value resource reads and atomic 32-bit store.
- `FspCreateDirectoryFileW()` assumes non-null `SecurityAttributes` when using inherit/security fields.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/util.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/wksid.c -->
# File Research: sources/windows/winfsp/src/dll/wksid.c

Caches commonly used Windows well-known SIDs for DLL code.

Initialization:
- `FspWksidInitialize()` lazily allocates:
  - `WinWorldSid`,
  - `WinAuthenticatedUserSid`,
  - `WinLocalSystemSid`,
  - `WinServiceSid`.

APIs:
- `FspWksidNew(WellKnownSidType, PResult)` allocates `SECURITY_MAX_SID_SIZE`, calls `CreateWellKnownSid`, and returns the SID or sets an NTSTATUS error.
- `FspWksidGet(WellKnownSidType)` initializes once and returns the cached SID pointer for supported types.
- `FspWksidFinalize(Dynamic)` frees cached SIDs only during explicit dynamic unload.

Important behavior:
- Unsupported well-known SID types return `0`.
- Cached SIDs are process-wide static objects; callers should not free pointers returned by `FspWksidGet`.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/wksid.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/callbacks.c -->
# File Research: sources/windows/winfsp/src/sys/callbacks.c

Kernel driver Fast I/O and cache-manager resource callback implementation.

Fast I/O:
- `FspFastIoCheckIfPossible()` currently asserts and returns `FALSE`, disabling this fast path.

Section/cache callbacks:
- `FspAcquireFileForNtCreateSection()` acquires the file node full lock exclusively and marks TLS `CreateSection`.
- `FspReleaseFileForNtCreateSection()` clears the flag and releases.
- `FspAcquireForModWrite()` tries full exclusive acquisition for mapped page writer and returns paging resource to release; returns `STATUS_CANT_WAIT` if it cannot acquire without waiting.
- `FspReleaseForModWrite()` temporarily restores top-level IRP to `FSRTL_MOD_WRITE_TOP_LEVEL_IRP` before release to tolerate observed external corruption.
- `FspAcquireForCcFlush()` handles both synthetic top-level values and real IRP top levels, preserving/restoring top flags around full acquisition.
- `FspReleaseForCcFlush()` reverses that state.

Lazy writer and read-ahead:
- `FspAcquireForLazyWrite()` exclusive-acquires full lock, records lazy-write thread, and sets top-level IRP to cache top-level.
- `FspReleaseFromLazyWrite()` validates thread/top-level state, clears it, releases.
- `FspAcquireForReadAhead()` shared-acquires full lock and sets cache top-level.
- `FspReleaseFromReadAhead()` clears top-level and releases.

Top-level propagation:
- `FspPropagateTopFlags()` propagates acquisition/top flags from top-level IRP context into nested IRPs when recursion is detected on the same file node.

Primary role:
- Coordinates WinFsp file-node resource ownership with Windows cache manager, memory manager, oplock, and recursive I/O expectations.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/callbacks.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/cleanup.c -->
# File Research: sources/windows/winfsp/src/sys/cleanup.c

Handles `IRP_MJ_CLEANUP` for control, virtual, and volume devices.

Device variants:
- `FspFsctlCleanup()` deletes a volume when the control file object has `FsContext2`.
- `FspFsvrtCleanup()` is a no-op success path.
- `FspFsvolCleanup()` performs real per-open cleanup for volume file objects.

Volume cleanup flow:
- Ignores invalid/uninitialized file objects.
- Acquires file-node main lock exclusively.
- Calls `FspFileNodeCleanup()` and decodes cleanup flags:
  - delete pending,
  - allocation-size reset,
  - file modified.
- Sends directory delete-pending/cleanup notifications through notify support.
- Removes byte-range locks for the file object/process.
- Creates a must-succeed user-mode `Cleanup` request.
- Populates cleanup metadata update flags for archive bit and times based on file object and descriptor state.
- Acquires paging I/O lock, assigns request ownership, stores IRP in request context, and flushes cleanup state.
- Posts best-effort if needed; otherwise completes locally and lets request finalizer do the mandatory teardown.

Completion/finalization:
- `FspFsvolCleanupComplete()` sends remove/modify notifications and invalidates parent directory or stream info caches as needed.
- `FspFsvolCleanupRequestFini()` always runs cleanup post-processing, even if user-mode disappears:
  - releases paging owner,
  - completes file-node cleanup,
  - checks oplocks,
  - sets `FO_CLEANUP_COMPLETE`,
  - detaches main file handle,
  - releases main owner,
  - closes main file handle.

Important semantic point:
- Cleanup cannot fail from the I/O manager perspective, so the code uses must-succeed request allocation and best-effort posting.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/cleanup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/close.c -->
# File Research: sources/windows/winfsp/src/sys/close.c

Handles `IRP_MJ_CLOSE` for WinFsp devices.

Device variants:
- `FspFsctlClose()` dereferences a device stored in `FsContext2`.
- `FspFsvrtClose()` is a no-op success path.
- `FspFsvolClose()` handles volume file object close.

Volume close flow:
- Ignores invalid file objects.
- If cleanup did not complete, performs oplock check.
- Creates a must-succeed user-mode `Close` request populated with `UserContext` and `UserContext2`.
- Calls `FspFileNodeClose()`.
- Deletes the file descriptor and dereferences the file node.
- If a rename is active or IOQ pending count is above watermark, attaches request to the IRP and posts best-effort synchronously.
- Otherwise posts a best-effort work request and completes the close IRP immediately.

Completion:
- `FspFsvolCloseComplete()` only traces; actual state is already torn down.

Important behavior:
- Close cannot fail, and user-mode close notification is best-effort because the file-system may already be going away.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/close.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/create.c -->
# File Research: sources/windows/winfsp/src/sys/create.c

Large `IRP_MJ_CREATE` implementation for WinFsp control, virtual, and volume devices. This is the core namespace/open path.

Top-level dispatch:
- `FspFsctlCreate()` recognizes volume-control opens by prefix and calls `FspVolumeCreate`; otherwise succeeds as `FILE_OPENED`.
- `FspFsvrtCreate()` succeeds as `FILE_OPENED`.
- `FspFsvolCreate()` handles volume file opens and wraps the main flow with the file-rename resource unless the open is a recursive main-file open.

ECP handling:
- Detects WinFsp main-file-open ECP to avoid deadlocking on rename resource.
- Optionally fixes reparse-point case damage from an undocumented reparse ECP.
- For WSL features, detects atomic-create ECP and accepts reparse-buffer creation data.

Create validation/building:
- Rejects unsupported file-id opens, paging-file opens, conflicting directory/non-directory options, invalid temp directory creates, invalid EA usage, invalid atomic-create inputs, and root operations that cannot be created/overwritten/superseded/deleted.
- Aligns allocation size to volume allocation unit.
- Normalizes doubled leading backslashes.
- Builds absolute path from related file object plus relative file name or validates absolute path.
- Validates stream syntax and optionally opens the main file for named streams.
- Strips volume prefix when mounted below a prefix.
- Tracks trailing backslash and stream type.
- Allocates `FSP_FILE_NODE`, `FSP_FILE_DESC`, and user-mode create request.
- Copies optional security descriptor and EA/reparse extra buffer into request.
- Populates create request with options, attributes, allocation size, desired/granted/share access, privilege flags, case sensitivity, named-stream offset, and security-descriptor acceptance flag.

Prepare phase:
- For create requests, duplicates the subject token into a user-mode impersonation-token handle, stores process for later close, and passes token handle plus originating process id in request.
- For overwrite requests, acquires full file-node lock, performs oplock processing, checks `MmCanFileBeTruncated`, purges cache, and marks request ownership.

Completion phase:
- Handles user-mode failures and `STATUS_REPARSE`.
- Reparse handling supports:
  - `IO_REMOUNT`,
  - device-absolute paths,
  - symbolic-link reparse buffers, including device-relative symlinks that are prefixed with volume name/prefix,
  - generic reparse buffers copied to IRP auxiliary buffer.
- Populates file node and descriptor from create response.
- Handles normalized names for case-insensitive file systems, requiring response normalized name to differ only by case.
- Calls `FspFileNodeOpen()` with additional access for overwrite/supersede share checks.
- On sharing violation, may break oplocks and retry.
- Sets access state, file object contexts, section object pointer, VPB, temporary flag, and cache support.
- For normal opens, calls `FspFsvolCreateTryOpen()` to acquire main lock, process oplocks, update metadata/security if safe, flush image sections for write/delete opens, and send create notifications.
- For overwrite/supersede, converts the request into an `Overwrite` transaction, validates hidden/system attribute rules, and posts best-effort.

Cleanup/finalizers:
- `FspFsvolCreatePostClose()` posts a best-effort close to user mode after failed local open completion.
- `FspFsvolCreateRequestFini()` releases extra file nodes, descriptors, token handles, process refs, and rename ownership.
- Try-open and overwrite finalizers back out oplocks, post close if needed, close file nodes, dereference, and release rename ownership.

Oplock logic:
- `FspFsvolCreateSharingViolationOplock()` mimics FastFat behavior for sharing violations, reposting to worker context when waiting may be needed.
- Handles main-file and stream sharing violations across alternate data streams.
- `FspFsvolCreateOpenOrOverwriteOplock()` checks oplock keys, async breaks when multiple handles exist, and supports `FILE_OPEN_REQUIRING_OPLOCK`.
- Async prepare/complete helpers bridge oplock completion back into create retry paths.

Key role in architecture:
- Bridges Windows create/open semantics to WinFsp’s user-mode transaction model while preserving kernel object lifetime, share access, reparse behavior, named streams, WSL atomic create, oplocks, cache coherency, and security token propagation.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/create.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/debug.c -->
# File Research: sources/windows/winfsp/src/sys/debug.c

Debug-only symbolization and IRP logging helpers, compiled under `#if DBG`.

Symbol helpers:
- `NtStatusSym()` maps NTSTATUS values, plus WinFsp IOQ pseudo-statuses, to strings; includes generated `ntstatus.i`.
- `IrpMajorFunctionSym()` maps major IRP codes.
- `IrpMinorFunctionSym()` maps minor IRP codes for read/write, directory control, file-system control, lock control, power, system control, and PNP.
- `IoctlCodeSym()` maps WinFsp IOCTLs and generated IOCTL constants from `ioctl.i`.
- `FileInformationClassSym()` maps many `FILE_INFORMATION_CLASS` values, including explicit numeric cases for `FileStatInformation` and `FileStatLxInformation`.
- `FsInformationClassSym()` maps file-system info classes.
- `DeviceExtensionKindSym()` maps WinFsp extension kinds to short labels.

Other utilities:
- `DebugRandom()` implements a spinlock-protected ucrt-style deterministic PRNG.
- `FspDebugLogIrp()` prints current IRQL, function, IRP pointer, device kind, requestor mode, major/minor operation, NTSTATUS symbol, and IoStatus information.

Important behavior:
- No runtime effect in non-debug builds.
- Includes generated symbol tables to keep logs readable during kernel debugging.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/devctl.c -->
# File Research: sources/windows/winfsp/src/sys/devctl.c

Handles fast and regular `IRP_MJ_DEVICE_CONTROL` paths.

Fast I/O device control:
- `FspFastIoDeviceControl()` only attempts fast path for waitable `FSP_IOCTL_TRANSACT` on fsctl devices.
- Validates input/output sizes, copies user buffers into nonpaged system buffer under exception handling, sets top-level IRP to fast-I/O sentinel, calls `FspVolumeFastTransact()`, copies output back, and frees the buffer.

Control device:
- `FspFsctlDeviceControl()` forwards `FSP_IOCTL_TRANSACT`, batch, and internal transact requests to `FspVolumeTransact()` when a volume context exists.

Virtual disk device:
- `FspFsvrtDeviceControl()` first handles storage query, then mountdev IOCTLs, then returns `STATUS_UNRECOGNIZED_VOLUME` for unknown IOCTLs to avoid blocking WinFsp mount attempts by foreign file systems.
- `FspFsvrtDeviceControlStorageQuery()` implements `IOCTL_STORAGE_QUERY_PROPERTY` for `StorageAccessAlignmentProperty`, returning sector-size alignment data to satisfy clients such as SQL Server.

Volume device forwarding:
- `FspFsvolDeviceControl()` forwards only if the volume advertises `DeviceControl`.
- Rejects kernel-originated IOCTLs.
- Allows only custom device types and `METHOD_BUFFERED`.
- Validates file object and max buffer sizes.
- Creates a user-mode `DeviceControl` request, shared-acquires the file node, copies input buffer, records output length, sets ownership, and posts.
- `FspFsvolDeviceControlComplete()` validates response buffer bounds, copies output to the system buffer, truncating with `STATUS_BUFFER_OVERFLOW` if needed.
- Finalizer releases file-node ownership.

Primary role:
- Supports WinFsp’s control protocol, selected virtual-storage compatibility IOCTLs, and safe user-mode forwarding of custom buffered file IOCTLs.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/devctl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/device.c -->
# File Research: sources/windows/winfsp/src/sys/device.c

Device object creation, initialization, lifetime, volume caches, context tables, and volume-info cache implementation.

Device creation/lifetime:
- `FspDeviceCreateSecure()` chooses extension size by device kind and calls `IoCreateDeviceSecure` or `IoCreateDevice`, initializes spinlock/refcount/kind.
- `FspDeviceCreate()` is the insecure unnamed wrapper.
- `FspDeviceInitialize()` dispatches kind-specific init and clears `DO_DEVICE_INITIALIZING` on success.
- `FspDeviceDelete()` dispatches kind-specific finalization then deletes the device.
- `FspDeviceDoIoDeleteDevice()` ensures `IoDeleteDevice` runs once.
- `FspDeviceReference()` / `FspDeviceDereference()` manage refcount under spinlock; dereference deletes at zero.
- DPC-level reference helpers are used by timer code and assert no deletion from DPC dereference.

Volume device init/fini:
- Initializes optional fsext provider.
- References virtual disk object and allocates swap VPB if mounted on virtual disk.
- Creates IO queue with timeout.
- Creates metadata caches for security, directory info, stream info, and EA.
- Initializes notify systems, statistics, delete/rename resources, context list, context-by-name AVL table, expiration timer/work item, and volume-info spinlock.
- Finalization stops timer first, then tears down statistics, notify, caches, IOQ, resources, virtual disk reference/VPB, and provider.

Expiration:
- `FspFsvolDeviceTimerRoutine()` runs at DPC, references the device, prevents duplicate expiration work item queuing, and queues passive-level work.
- `FspFsvolDeviceExpirationRoutine()` invalidates expired metadata caches, runs provider expiration, removes expired IOQ items, clears in-progress flag, and dereferences the device.

Context management:
- `FspFsvolDeviceCopyContextList()` snapshots active file-node contexts from a list.
- `FspFsvolDeviceCopyContextByNameList()` snapshots AVL table contexts.
- Enumerate/lookup/insert/delete helpers wrap the context-by-name AVL table.
- Compare uses `FspFileNameCompare` with case sensitivity derived from volume params.
- Allocation callback returns caller-provided element storage; free callback is no-op.

Volume information:
- `FspFsvolDeviceGetVolumeInfo()` copies cached info under spinlock.
- `FspFsvolDeviceTryGetVolumeInfo()` returns cached info only if expiration time is valid.
- `FspFsvolDeviceSetVolumeInfo()` updates info and sets expiration from volume params.
- `FspFsvolDeviceInvalidateVolumeInfo()` clears expiration.

Other device kinds:
- Fsvrt init/fini initializes mount mutex and frees mount-point buffer.
- Fsmup init/fini initializes prefix/class prefix tables and asserts emptiness on fini.
- `FspDeviceCopyList()` wraps `IoEnumerateDeviceObjectList`.
- `FspDeviceDeleteList()` dereferences enumerated device objects and frees the list.
- Defines global `FspDeviceGlobalMutex`.

Primary role:
- Centralizes WinFsp kernel device object lifecycle and per-volume shared infrastructure.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/device.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/sys/devtimer.c -->
# File Research: sources/windows/winfsp/src/sys/devtimer.c

Imulates Windows `IoInitializeTimer` / `IoStartTimer` / `IoStopTimer` support for platforms where those APIs are unavailable, notably Windows on ARM64.

Global timer:
- `FspDeviceInitializeAllTimers()` initializes a global list, spinlock, DPC, synchronization timer, and starts a 1-second periodic timer.
- `FspDeviceFinalizeAllTimers()` cancels timer, flushes queued DPCs, and in debug asserts the device timer list is empty.

DPC routine:
- `FspDeviceTimerRoutine()` acquires the global timer spinlock and walks all registered `FSP_DEVICE_TIMER` entries, invoking each timer routine with its device object and context.

Per-device timer API:
- `FspDeviceInitializeTimer()` stores callback, device object, and context in the device extension.
- `FspDeviceStartTimer()` inserts the device timer entry into the global list under lock.
- `FspDeviceStopTimer()` removes it under lock.

Important behavior:
- Uses a single global periodic timer for all registered devices.
- Timer callbacks run while the global list spinlock is held, so callbacks must be DPC-safe and avoid operations that could deadlock on the same lock.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/sys/devtimer.c -->