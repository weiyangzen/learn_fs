# Group Research: group_1850_windows_driver_samples_sources_windows_windows_driver_samples_files_c8ee6e1e2de2

Scope: `Docs/research_subset_a.md`, source tree `sources/windows/windows-driver-samples`. This grouped report covers Windows filesystem minifilter samples for user-mode AV scanning, cancel-safe callback data queues, control device objects, and transaction-aware dirty tracking.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/userscan.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/userscan.c

## Purpose

Implements the user-mode scanner side of the `avscan` minifilter sample. The scanner connects to kernel filter communication ports, runs a fixed pool of scan worker threads, maps sections created by the filter for file data, scans memory for an encoded test signature, sends scan results back to the filter, and listens for abort/unload notifications.

## Public And Internal APIs

- Exported by `userscan.h`: `UserScanInit()` and `UserScanFinalize()`.
- Thread procedures: `UserScanWorker()` handles scan messages from the scan port; `UserScanListenAbortProc()` handles abort and unload notifications from the abort port.
- Scan helpers: `UserScanMemoryStream()` decodes and searches the sample malware pattern; `UserScanHandleStartScanMsg()` drives the create-section, map, scan, unmap, close-section protocol.
- Cleanup helpers: `UserScanSynchronizedCancel()`, `UserScanClosePorts()`, `UserScanCleanup()`, `WaitForAll()`.
- Lookup helper: `UserScanGetThreadContextById()` maps a scan thread ID to its `SCANNER_THREAD_CONTEXT`.

## Control Flow

- `UserScanInit()` creates one suspended abort-listener thread and six suspended scan-worker threads, initializes per-worker critical sections, connects to `AV_SCAN_PORT_NAME` with `AvConnectForScan`, attaches the scan port to an IO completion port, stores handles in the caller-provided `USER_SCAN_CONTEXT`, resumes threads, then posts one overlapped `FilterGetMessage()` per worker.
- Scan messages use `SCANNER_MESSAGE`, which embeds `FILTER_MESSAGE_HEADER`, `AV_SCANNER_NOTIFICATION`, and an `OVERLAPPED` so `GetQueuedCompletionStatus()` can recover the owning message via `CONTAINING_RECORD`.
- `UserScanWorker()` waits on the IO completion port, replies to `AvMsgStartScanning` with the worker thread ID, records `ScanId`, calls `UserScanHandleStartScanMsg()`, then reposts the same message with `FilterGetMessage()`.
- `UserScanHandleStartScanMsg()` sends `AvCmdCreateSectionForDataScan`, maps the returned section read-only, queries the mapped region size, calls `UserScanMemoryStream()`, optionally uses `MEM_UNMAP_WITH_TRANSIENT_BOOST` for open-triggered scans, unmaps, closes the section handle, and sends `AvCmdCloseSectionForDataScan` with the scan result.
- `UserScanListenAbortProc()` connects separately to `AV_ABORT_PORT_NAME` with `AvConnectForAbort`; `AvMsgAbortScanning` finds the target worker and sets its abort flag only if the `ScanId` still matches; `AvMsgFilterUnloading` cancels workers, replies to the filter, closes ports, closes the abort port, and terminates the process.
- `UserScanFinalize()` sets `Context->Finalized`, marks every worker aborted, calls `CancelIoEx()` on the scan connection port, waits for all scan workers, then closes ports/thread handles and frees worker contexts.

## State And Data Structures

- `USER_SCAN_THREAD_COUNT` is fixed at six.
- `SCANNER_MESSAGE_SIZE` deliberately excludes the embedded `OVERLAPPED`; it is used for synchronous abort-port messages and overlapped scan-port receive lengths.
- `SCANNER_REPLY_MESSAGE` replies with the worker thread ID so the kernel filter can associate a scan request with the user-mode thread servicing it.
- Per-worker state comes from `SCANNER_THREAD_CONTEXT`: thread handle, thread ID, current `ScanId`, abort flag, and a critical section.
- Shared state comes from `USER_SCAN_CONTEXT`: worker array, abort thread handle, finalize flag, filter connection port, and IO completion port.

## Dependencies

- User-mode Windows APIs: `CreateThread`, `ResumeThread`, `CreateIoCompletionPort`, `GetQueuedCompletionStatus`, `HeapAlloc`, `HeapFree`, `MapViewOfFile`, `VirtualQuery`, `UnmapViewOfFileEx`, `CloseHandle`, `CancelIoEx`, `WaitForMultipleObjects`, `ExitProcess`.
- Filter manager user APIs: `FilterConnectCommunicationPort`, `FilterGetMessage`, `FilterReplyMessage`, `FilterSendMessage`.
- Shared protocol from `avlib.h`: port names, connection types, command IDs, notification fields, scan reasons, scan IDs, and `AVSCAN_RESULT`.

## Risks And Invariants

- Scan message buffers are heap-allocated in `UserScanInit()` and owned by workers after completion-port delivery; each worker frees its current message on exit.
- `ScanId` and `Aborted` updates are protected when reset/set, but `UserScanMemoryStream()` polls `Aborted` directly through a pointer while scanning. This is acceptable for a sample but not a strongly synchronized cancellation primitive.
- `Context->Finalized` is also read by workers without synchronization.
- On filter unload, the abort listener calls `ExitProcess(0)`, so normal caller-controlled cleanup may be bypassed.
- The code assumes kernel/user protocol ordering: a scan worker must reply with its thread ID before asking the filter to create a section, and must always send `AvCmdCloseSectionForDataScan` after creating a section so the filter can release waiting I/O and update file state.
- `hEvent` in `UserScanInit()` is initialized and cleaned up but never assigned or used.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/userscan.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/userscan.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/userscan.h

## Purpose

Defines the user scanner’s exported API and shared scanner context types for the `avscan` sample’s user-mode component.

## API Surface

- Includes `<windows.h>`, `<fltUser.h>`, and shared `avlib.h`.
- Provides a fallback `MAKE_HRESULT()` macro if the platform headers did not define it.
- Declares `UserScanInit(PUSER_SCAN_CONTEXT Context)` and `UserScanFinalize(PUSER_SCAN_CONTEXT Context)`.

## Data Structures

- `SCANNER_THREAD_CONTEXT` stores one worker’s thread handle, thread ID, current scan ID, abort flag, and critical section used to synchronize `ScanId`/`Aborted` transitions.
- `USER_SCAN_CONTEXT` stores the scanner’s worker context array, abort listener thread handle, finalize flag, scan connection port, and IO completion port.

## Dependencies And Usage

- `userscan.c` owns allocation and lifetime of the worker context array and thread handles.
- Callers must provide a writable `USER_SCAN_CONTEXT`, call `UserScanInit()` after the minifilter is loaded, and call `UserScanFinalize()` before normal scanner exit.
- The header is user-mode only; it depends on Filter Manager user-mode communication APIs through `fltUser.h`.

## Risks And Invariants

- `USER_SCAN_CONTEXT` has no constructor or zeroing helper; callers are expected to initialize or provide clean storage before `UserScanInit()`.
- `Finalized` is a plain `BOOLEAN`; `userscan.c` treats it as cross-thread state without interlocked access.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/userscan.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/utility.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/utility.c

## Purpose

Provides a user-mode diagnostic helper for translating Win32/HRESULT-style error codes into printable messages for the `avscan` user scanner.

## API Surface

- Implements `DisplayError(DWORD Code)` declared in `utility.h`.

## Control Flow

- Calls `FormatMessage(FORMAT_MESSAGE_FROM_SYSTEM)` first.
- If the system table does not contain the message, obtains the system directory, appends `\fltlib.dll`, loads it as a data file, and retries `FormatMessage(FORMAT_MESSAGE_FROM_HMODULE)`.
- Frees the message module if loaded and prints either the translated wide string or a fallback `Could not translate error` message.

## Dependencies

- Windows APIs: `FormatMessage`, `GetSystemDirectory`, `LoadLibraryExW`, `FreeLibrary`.
- String helper: `StringCchCat` from `<Strsafe.h>`.
- C runtime output: `printf`.

## Risks And Invariants

- Uses a `MAX_PATH` stack buffer and checks the system directory length before appending.
- The input parameter is named `Code` and typed as `DWORD`, but callers often pass `HRESULT` values; this matches the sample’s diagnostic needs because Filter Manager HRESULTs may be backed by `fltlib.dll` messages.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/utility.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/utility.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/utility.h

## Purpose

Declares the common user-mode error reporting helper used by the `avscan` scanner program.

## API Surface

- Includes `<windows.h>`.
- Declares `VOID DisplayError(_In_ DWORD Code);`.

## Dependencies And Usage

- Implemented by `utility.c`.
- Used by `userscan.c` on Filter Manager and Win32 error paths to print human-readable diagnostics.

## Risks And Invariants

- Header is minimal and user-mode specific.
- It exposes only diagnostics; it does not affect scanner protocol or lifecycle state.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/utility.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/cancelSafe/cancelSafe.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/cancelSafe/cancelSafe.c

## Purpose

Implements a kernel-mode minifilter sample demonstrating Filter Manager cancel-safe callback data queues (`FltCbdq*`). It delays matching read IRPs for a configurable period, supports cancellation and instance teardown, and completes queued reads safely from a worker item.

## Public And Internal APIs

- Driver lifecycle: `DriverEntry()`, `Unload()`, `FreeGlobals()`.
- Registry configuration: `GetIoOpenDriverRegistryKey()`, `OpenServiceParametersKey()`, `SetConfiguration()`.
- Instance lifecycle: `InstanceSetup()`, `InstanceQueryTeardown()`, `InstanceTeardownStart()`, `InstanceTeardownComplete()`.
- Context cleanup: `ContextCleanup()`.
- Callback data queue hooks: `CsqAcquire()`, `CsqRelease()`, `CsqInsertIo()`, `CsqRemoveIo()`, `CsqPeekNextIo()`, `CsqCompleteCanceledIo()`.
- Read path: `PreRead()`, `PreReadWorkItemRoutine()`, `PreReadPendIo()`, `PreReadProcessIo()`, `PreReadEmptyQueueAndComplete()`.

## Registration And Configuration

- Registers only `IRP_MJ_READ` with `FLTFL_OPERATION_REGISTRATION_SKIP_PAGING_IO`.
- Registers an instance context containing a `FLT_CALLBACK_DATA_QUEUE`, list head, fast mutex, worker flag, and teardown event.
- Initializes a nonpaged lookaside list for per-I/O `QUEUE_CONTEXT` allocations.
- Reads optional service parameters:
  - `DebugLevel` controls `DbgPrint` categories.
  - `OperatingDelay` sets the relative wait delay before completing a pended read.
  - `OperatingPath` selects the parent-directory prefix to delay, defaulting to `\`.
- Uses `IoOpenDriverRegistryKey` when available, with a `ZwOpenKey` fallback for older systems.

## Control Flow

- `DriverEntry()` opts into `NonPagedPoolNx`, initializes defaults and lookaside storage, applies registry configuration, registers the minifilter, and starts filtering.
- `InstanceSetup()` allocates and initializes an `INSTANCE_CONTEXT`, initializes the CBDQ with this file’s queue callbacks, initializes `QueueHead`, `Lock`, `WorkerThreadFlag`, and `TeardownEvent`, then attaches the context to the instance.
- `PreRead()` skips paging I/O, synchronous paging I/O, and non-null `TopLevelIrp`; it obtains normalized file name information, parses it, checks whether `Globals.MappingPath` prefixes the parent directory, disallows fast I/O for matched files, allocates a queue context, gets the instance context, stores queue context pointers in `Data->QueueContext`, and inserts the operation with `FltCbdqInsertIo()`.
- `CsqInsertIo()` inserts callback data at the tail of the internal list. If the queue was empty and no worker is active, it allocates and queues a generic work item. If work-item creation fails, it decrements the worker flag and removes the just-inserted operation.
- `PreReadWorkItemRoutine()` gets the instance context, repeatedly waits `Globals.TimeDelay` or until teardown, removes the next queued I/O, calls `PreReadProcessIo()`, locks user buffers when required, completes the pended pre-operation, frees the queue context, and exits only when the queue is empty and the worker flag race resolves to zero.
- `InstanceTeardownStart()` disables further CBDQ insertion, drains queued I/O through `PreReadEmptyQueueAndComplete()`, and signals the teardown event to wake a waiting worker.
- `CsqCompleteCanceledIo()` completes canceled pended operations with `STATUS_CANCELLED` and frees the per-I/O queue context.

## State And Data Structures

- `CSQ_GLOBAL_DATA` contains debug level, filter handle, queue-context lookaside list, configured mapping path buffer/string, and delay interval.
- `INSTANCE_CONTEXT` contains the Filter Manager instance pointer, the CBDQ object, private list head, fast mutex, worker-thread presence flag, and teardown event.
- `QUEUE_CONTEXT` wraps `FLT_CALLBACK_DATA_QUEUE_IO_CONTEXT`, which Filter Manager uses for cancel-safe tracking.
- The private list uses `FLT_CALLBACK_DATA.QueueLinks`.

## Dependencies

- Filter Manager kernel APIs: `FltRegisterFilter`, `FltStartFiltering`, `FltAllocateContext`, `FltSetInstanceContext`, `FltGetInstanceContext`, `FltCbdqInitialize`, `FltCbdqInsertIo`, `FltCbdqRemoveNextIo`, `FltCbdqDisable`, `FltCompletePendedPreOperation`, `FltAllocateGenericWorkItem`, `FltQueueGenericWorkItem`, `FltFreeGenericWorkItem`, `FltGetFileNameInformation`, `FltParseFileNameInformation`, `FltLockUserBuffer`.
- Kernel synchronization/allocation: fast mutexes, events, interlocked operations, nonpaged lookaside lists, registry Zw APIs.
- Name filtering depends on normalized file names and `RtlPrefixUnicodeString()` against the parent directory.

## Risks And Invariants

- Queue lock callbacks use a fast mutex, so they run at APC-level constraints and store a dummy IRQL value.
- The worker flag is the central race-control invariant. `CsqInsertIo()` increments it when adding work to an empty queue; the worker reduces it to one before removing I/O and decrements on empty to decide whether to exit or continue after racing inserts.
- Fast I/O cannot be queued; matched Fast I/O reads are rejected with `FLT_PREOP_DISALLOW_FASTIO` to force the request down the IRP path for demonstration.
- User buffers must be locked before completing a pended operation in a different process context unless the data is already system-buffered or has an MDL.
- Teardown must disable the CBDQ before draining; otherwise new inserts could race with queue drain.
- `PreReadProcessIo()` is intentionally a stub returning success; this sample demonstrates queueing/cancellation rather than data inspection.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/cancelSafe/cancelSafe.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoInit.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoInit.c

## Purpose

Initializes the control device object minifilter sample. It registers a minifilter for lifetime management, creates a named control device object, initializes global synchronization, optionally reads debug settings, and deliberately refuses volume attachment.

## Public And Internal APIs

- Driver lifecycle: `DriverEntry()`, `CdoUnload()`.
- Instance callback: `CdoInstanceSetup()`.
- Debug-only registry helpers: `CdoGetIoOpenDriverRegistryKey()`, `CdoOpenServiceParametersKey()`, `CdoInitializeDebugLevel()`.

## Control Flow

- `DriverEntry()` zeroes `Globals`, initializes debug level in DBG builds, initializes `Globals.Resource`, records the driver object, registers a minimal `FLT_REGISTRATION`, creates the control device object through `CdoCreateControlDeviceObject()`, and starts filtering.
- Failure after each stage unwinds the prior stage: unregisters the filter, deletes the resource, and/or deletes the CDO.
- `CdoUnload()` refuses optional unload when the CDO still has an open reference, unregisters the minifilter, deletes the CDO, releases the resource, and deletes the resource object.
- `CdoInstanceSetup()` returns `STATUS_FLT_DO_NOT_ATTACH`, so the minifilter does not attach to any volume; this sample focuses on the CDO surface rather than file I/O filtering.

## Registration

- `FLT_REGISTRATION` has no contexts and no operation callbacks.
- It supplies unload and instance setup callbacks only.
- KTM/name-provider callbacks are unused.

## State And Data Structures

- Uses the global `CDO_GLOBAL_DATA Globals` declared in `CdoStruct.h`.
- `Globals.Resource` serializes CDO open/close/unload state.
- `Globals.FilterDriverObject`, `Globals.Filter`, and `Globals.FilterControlDeviceObject` are initialized across driver entry and CDO creation.

## Dependencies

- Filter Manager lifecycle APIs: `FltRegisterFilter`, `FltStartFiltering`, `FltUnregisterFilter`.
- Kernel resource APIs: `ExInitializeResourceLite`, `ExDeleteResourceLite`.
- Debug-only registry reads use `IoOpenDriverRegistryKey` when available, otherwise `ZwOpenKey` on the service `Parameters` subkey, then `ZwQueryValueKey("DebugLevel")`.

## Risks And Invariants

- Optional unload is blocked while `GLOBAL_DATA_F_CDO_OPEN_REF` is set; mandatory unload proceeds.
- The resource must remain valid until CDO state is no longer inspected.
- The sample’s filter instance callbacks exist mainly to make a loadable minifilter package while demonstrating a separately named device object.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoInit.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoOperations.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoOperations.c

## Purpose

Implements creation, deletion, IRP dispatch, open/cleanup/close state management, FS-control handling, and Fast I/O dispatch behavior for the CDO sample’s named control device object.

## Public And Internal APIs

- CDO lifecycle: `CdoCreateControlDeviceObject()`, `CdoDeleteControlDeviceObject()`.
- IRP dispatch: `CdoMajorFunction()`.
- Supported private operations: `CdoHandlePrivateOpen()`, `CdoHandlePrivateCleanup()`, `CdoHandlePrivateClose()`, `CdoHandlePrivateFsControl()`.
- Fast I/O dispatch table: `CdoFastIoDispatch`.
- Fast I/O callbacks cover check/read/write/query info/locks/device control/network open/MDL/compressed/query-open operations.

## Control Flow

- `CdoCreateControlDeviceObject()` creates `\FileSystem\Filters\CdoSample` with `FILE_DEVICE_DISK_FILE_SYSTEM` and `FILE_DEVICE_SECURE_OPEN`, installs `CdoMajorFunction` for every IRP major code, and installs `CdoFastIoDispatch`.
- `CdoDeleteControlDeviceObject()` calls `IoDeleteDevice()` on `Globals.FilterControlDeviceObject`.
- `CdoMajorFunction()` asserts the device object is the sample CDO, then supports:
  - `IRP_MJ_CREATE`: calls `CdoHandlePrivateOpen()`, completes with `FILE_OPENED` on success.
  - `IRP_MJ_CLOSE`: calls `CdoHandlePrivateClose()` and always completes success.
  - `IRP_MJ_FILE_SYSTEM_CONTROL`: forwards system buffer and lengths to `CdoHandlePrivateFsControl()`.
  - `IRP_MJ_CLEANUP`: calls `CdoHandlePrivateCleanup()` and always completes success.
  - All other major codes complete with `STATUS_INVALID_DEVICE_REQUEST`.
- `CdoHandlePrivateOpen()` takes the global resource exclusive and permits only one outstanding open at a time. It sets both `GLOBAL_DATA_F_CDO_OPEN_REF` and `GLOBAL_DATA_F_CDO_OPEN_HANDLE` on success.
- `CdoHandlePrivateCleanup()` clears `GLOBAL_DATA_F_CDO_OPEN_HANDLE`; `CdoHandlePrivateClose()` later clears `GLOBAL_DATA_F_CDO_OPEN_REF`.
- `CdoHandlePrivateFsControl()` takes the resource shared, asserts an open reference exists, fails if cleanup already closed the handle, then demonstrates two phases: work requiring the handle still be open while the resource is held, and work that can continue after the handle may close while the IRP’s device reference remains.

## Fast I/O Behavior

- Almost every Fast I/O callback asserts the CDO and returns a terminal failure for the CDO, usually by setting `IoStatus->Status = STATUS_INVALID_DEVICE_REQUEST`, `Information = 0`, and returning `TRUE`.
- MDL completion routines return `FALSE` because there is no operation to complete.
- `CdoFastIoDeviceControl()` is the main exception: it routes the Fast I/O device-control request into `CdoHandlePrivateFsControl()` and returns `TRUE`.
- `CdoFastIoQueryOpen()` writes failure status into the create IRP’s `IoStatus` and returns `TRUE`.

## State And Data Structures

- Global open state is represented by `Globals.Flags`:
  - `GLOBAL_DATA_F_CDO_OPEN_REF` means the CDO still has an object reference and close has not run.
  - `GLOBAL_DATA_F_CDO_OPEN_HANDLE` means a user handle remains open and cleanup has not run.
- `Globals.Resource` protects flag transitions and unload checks.
- Driver dispatch table and Fast I/O table are installed on the shared driver object during CDO creation.

## Dependencies

- Kernel APIs: `IoCreateDevice`, `IoDeleteDevice`, `IoGetCurrentIrpStackLocation`, `IoCompleteRequest`.
- Synchronization wrappers from `CdoProc.h`: `CdoAcquireResourceExclusive`, `CdoAcquireResourceShared`, `CdoReleaseResource`.
- Debug and identity macros from `CdoStruct.h`: `DebugTrace`, `IS_MY_CONTROL_DEVICE_OBJECT`.

## Risks And Invariants

- The sample enforces one open handle to the CDO. Create fails with `STATUS_DEVICE_ALREADY_ATTACHED` if either open flag is already set.
- Cleanup and close ordering matters: cleanup clears the handle flag, close clears the reference flag. Assertions encode the expected IRP sequence.
- FS-control must check `GLOBAL_DATA_F_CDO_OPEN_HANDLE` while holding the resource if the requested operation requires the user handle still to be open.
- After releasing the resource in FS-control, cleanup may run; only operations independent of the live handle are safe in that phase.
- The Fast I/O table is intentionally broad so unexpected fast paths are handled explicitly rather than falling through to undefined behavior.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoOperations.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoProc.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoProc.h

## Purpose

Declares the CDO sample’s internal functions and inline resource helpers.

## API Surface

- Declares CDO lifecycle functions: `CdoCreateControlDeviceObject()` and `CdoDeleteControlDeviceObject()`.
- Declares `CdoMajorFunction()` and private IRP handlers for open, cleanup, close, and FS-control.
- Declares all Fast I/O callback functions installed in `CdoFastIoDispatch`.
- Provides inline wrappers:
  - `CdoAcquireResourceExclusive()`
  - `CdoAcquireResourceShared()`
  - `CdoReleaseResource()`

## Resource Semantics

- Acquisition wrappers assert `KeGetCurrentIrql() <= APC_LEVEL`.
- They enter a critical region before acquiring the `ERESOURCE`, preventing normal kernel APC delivery while the resource is held.
- Release asserts the resource is held, releases it, and leaves the critical region.

## Dependencies

- Uses kernel driver annotations, `PERESOURCE`, `PDEVICE_OBJECT`, `PIRP`, Fast I/O types, and file information structures from the WDK headers included through `pch.h`.
- Function declarations match implementations in `CdoOperations.c`.

## Risks And Invariants

- Inline resource helpers must be paired exactly. Holding the resource also means the current thread is in a critical region.
- The annotations describe expected lock ownership for static analysis and should remain aligned with the implementation.
- The header is internal to the sample and assumes `CdoStruct.h`/WDK types are already available through `pch.h`.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoProc.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoStruct.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoStruct.h

## Purpose

Defines global state, flag values, CDO identity helpers, and debug tracing macros for the CDO minifilter sample.

## Data Structures

- `CDO_GLOBAL_DATA` stores:
  - Filter Manager handle.
  - Driver object pointer.
  - Control device object pointer.
  - CDO open-state flags.
  - `ERESOURCE` protecting flag access.
  - Debug level in DBG builds.
- Declares `extern CDO_GLOBAL_DATA Globals`.

## Constants And Macros

- `GLOBAL_DATA_F_CDO_OPEN_REF` tracks an outstanding object reference to the CDO.
- `GLOBAL_DATA_F_CDO_OPEN_HANDLE` tracks an outstanding user handle to the CDO.
- `CONTROL_DEVICE_OBJECT_NAME` is `\FileSystem\Filters\CdoSample`.
- `IS_MY_CONTROL_DEVICE_OBJECT()` verifies the device object matches `Globals.FilterControlDeviceObject` and asserts driver object/device extension invariants.
- DBG-only trace flags distinguish errors, load/unload, CDO create/delete, supported operations, Fast I/O operations, all operations, and all flags.

## Dependencies

- Requires WDK types from `fltKernel.h` via `pch.h`.
- Used by both `CdoInit.c` and `CdoOperations.c`.

## Risks And Invariants

- Open reference and open handle are intentionally separate because cleanup and close are separate IRP phases.
- `IS_MY_CONTROL_DEVICE_OBJECT()` assumes `Globals.FilterControlDeviceObject` is initialized before dispatch paths use it.
- In free builds `DebugTrace` compiles to no-op.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoStruct.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/pch.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/pch.h

## Purpose

Precompiled header for the CDO kernel-mode sample.

## Contents

- Enables warnings as errors for unreferenced parameters, unreferenced locals, missing enum cases in switch statements, and dead functions.
- Includes WDK headers: `<fltKernel.h>`, `<dontuse.h>`, and `<suppress.h>`.
- Includes sample headers: `CdoStruct.h` and `CdoProc.h`.
- Disables the PREfast encoded member function pointer warning as not valid for kernel-mode drivers.

## Dependencies And Usage

- Included by `CdoInit.c` and `CdoOperations.c`.
- Centralizes strict warning policy and internal declarations.

## Risks And Invariants

- The final `#endif __CDO_PCH_H__` includes trailing tokens after `#endif`, which is tolerated by many preprocessors but is stylistically noisy.
- Because warning 4100 is an error, implementations must explicitly mark unused parameters with `UNREFERENCED_PARAMETER`.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/pch.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/change/change.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/change/change.c

## Purpose

Implements a transaction-aware minifilter sample that tracks whether file contents have become dirty. It distinguishes normal dirty state from transaction-local dirty state and propagates transaction changes only on KTM commit.

## Public And Internal APIs

- Driver/instance lifecycle: `DriverEntry()`, `CgUnload()`, `CgInstanceSetup()`, `CgInstanceQueryTeardown()`, `CgInstanceTeardownStart()`, `CgInstanceTeardownComplete()`.
- Operation callbacks: `CgPreCreate()`, `CgPostCreate()`, `CgPreClose()`, `CgPreOperationCallback()`, `CgPreFsControl()`.
- KTM callback: `CgKtmNotificationCallback()`.
- Dirty/transaction helpers: `CgOperationsNeedDirty()`, `CgQueryTransactionOutcome()`, `CgProcessPreviousTransaction()`, `CgProcessTransactionOutcome()`, inline `CgPropagateDirty()`.

## Registration

- Registers callbacks for:
  - `IRP_MJ_CREATE`: pre and post.
  - `IRP_MJ_CLOSE`: pre.
  - `IRP_MJ_WRITE`: pre dirty tracking.
  - `IRP_MJ_SET_INFORMATION`: pre dirty tracking.
  - `IRP_MJ_FILE_SYSTEM_CONTROL`: pre savepoint handling and dirty tracking.
- Uses context registration from `context.c`.
- Supplies `CgKtmNotificationCallback` as the transaction notification callback.

## Dirty Tracking Semantics

- `CgOperationsNeedDirty()` returns true for content-affecting operations:
  - All writes.
  - FSCTLs `FSCTL_OFFLOAD_WRITE`, `FSCTL_WRITE_RAW_ENCRYPTED`, `FSCTL_SET_ZERO_DATA`.
  - Set-information classes `FileEndOfFileInformation` and `FileValidDataLengthInformation`.
- `CgPreOperationCallback()` obtains the file context; if the file has an active transaction context, it sets `TxDirty`, otherwise it sets `Dirty`.
- `CgPropagateDirty()` ORs `TxDirty` into `Dirty` only if the transaction committed, then clears `TxDirty` regardless of outcome.

## Transaction Flow

- `CgPostCreate()` ignores failed/reparse creates, finds or creates the file context, and if desired access includes write/delete/security-changing rights, calls `CgProcessPreviousTransaction()`.
- `CgProcessPreviousTransaction()` finds or creates a transaction context when `FltObjects->Transaction` is non-null, enlists it for `TRANSACTION_NOTIFY_COMMIT_FINALIZE | TRANSACTION_NOTIFY_ROLLBACK`, then atomically swaps `FileContext->TxContext`.
- When moving a file context between transactions, it queries the old transaction outcome, removes the file from the old transaction list, propagates dirty state if appropriate, updates references, and inserts into the new transaction list if still active.
- `CgProcessTransactionOutcome()` drains the transaction context’s file-context list under its mutex, atomically clears matching `TxContext` pointers, propagates dirty state for commit, releases transaction/file references, marks the list drained, and prints dirty file IDs in debug output.
- `CgKtmNotificationCallback()` maps commit-finalize to `TransactionOutcomeCommitted`; rollback maps to `TransactionOutcomeAborted`.

## Other Control Flow

- `CgPreCreate()` returns `FLT_PREOP_SYNCHRONIZE` so `CgPostCreate()` runs at a safe IRQL for context/resource work.
- `CgPreFsControl()` explicitly fails `FSCTL_TXFS_SAVEPOINT_INFORMATION` with `STATUS_NOT_SUPPORTED`, because the sample does not support savepoints.
- `CgPreClose()` reports non-transacted dirty files on close.
- Instance setup/query teardown always succeeds; teardown callbacks only log.

## Dependencies

- Filter Manager: `FltRegisterFilter`, `FltStartFiltering`, `FltUnregisterFilter`, file and transaction contexts, transaction enlistment.
- KTM/transaction APIs: `FltEnlistInTransaction`, `ZwQueryInformationTransaction`, `ObOpenObjectByPointer`, `TmTransactionObjectType`.
- Context helpers from `context.c`: `CgFindOrCreateFileContext()`, `CgFindOrCreateTransactionContext()`.
- List and mutex helpers from `utility.h`.

## Risks And Invariants

- Transaction context replacement uses `InterlockedExchangePointer()` and `InterlockedCompareExchangePointer()` to coordinate with asynchronous KTM notifications.
- File contexts linked into transaction lists hold an extra file-context reference; the reference is released when the list entry is removed.
- Transaction contexts referenced by file contexts hold a separate context reference; it must be released when `TxContext` is cleared/replaced.
- KTM notifications can arrive out of order; committed dirty propagation uses OR assignment to avoid clearing existing dirty state.
- Savepoints are not modeled; the sample rejects them rather than attempting partial rollback tracking.
- The code assumes TxF semantics that only one transacted writer exists for a file at a time.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/change/change.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/change/change.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/change/change.h

## Purpose

Main internal header for the `change` minifilter sample. It pulls in WDK/context/utility definitions, declares global filter state, and defines debug tracing controls.

## Contents

- Defines `CG_VISTA` as `NTDDI_VERSION >= NTDDI_VISTA`.
- Includes `<fltKernel.h>`, `<suppress.h>`, `context.h`, and `utility.h`.
- Disables the PREfast encoded member function pointer warning for kernel-mode drivers.
- Defines `PFLT_FILTER gFilterInstance`.
- Defines trace categories: routines, operation status, debug, and error.
- Initializes `gTraceFlags` to debug plus error.
- Defines `CG_DBG_PRINT()` wrapper around `DbgPrint`.

## Dependencies And Usage

- Included by both `change.c` and `context.c`.
- `gFilterInstance` is used by context allocation in `context.c` and initialized by `DriverEntry()` in `change.c`.

## Risks And Invariants

- The header defines, rather than declares, `gFilterInstance` and `gTraceFlags`; in stricter modern builds, this can create multiple-definition risk when included by multiple C files. The sample relies on its build environment’s handling.
- Debug output is controlled by a static trace flag initialized at compile time, not by registry configuration.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/change/change.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/change/context.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/change/context.c

## Purpose

Implements file and transaction context allocation, lookup, initialization, cleanup, and file-ID extraction for the transaction-aware `change` minifilter sample.

## Public And Internal APIs

- Context registration: `ContextRegistration[]`.
- File context APIs: `CgFindOrCreateFileContext()`, local `CgCreateFileContext()`, `CgFileContextCleanup()`.
- Transaction context APIs: `CgFindOrCreateTransactionContext()`, `CgTransactionContextCleanup()`.
- File identity helper: `CgGetFileId()`.

## Context Registration

- Registers `FLT_FILE_CONTEXT` with `CgFileContextCleanup()`, size `CG_FILE_CONTEXT_SIZE`, tag `CG_FILE_CONTEXT_TAG`.
- Registers `FLT_TRANSACTION_CONTEXT` with `CgTransactionContextCleanup()`, size `CG_TRANSACTION_CONTEXT_SIZE`, tag `CG_TRANSACTION_CONTEXT_TAG`.

## File Context Flow

- `CgFindOrCreateFileContext()` first attempts `FltGetFileContext()`.
- On `STATUS_NOT_FOUND`, it queries a file ID using `CgGetFileId()`, allocates a file context from paged pool, zeroes it, stores the file ID, and attempts `FltSetFileContext(..., FLT_SET_CONTEXT_KEEP_IF_EXISTS, ...)`.
- If another thread won the race and already set a context, it releases the newly allocated context and returns the existing `oldFileContext`.
- `CgFileContextCleanup()` asserts the file is not still linked to a transaction context and logs file ID plus dirty state.

## Transaction Context Flow

- `CgFindOrCreateTransactionContext()` first attempts `FltGetTransactionContext()`.
- On `STATUS_NOT_FOUND`, it allocates a nonpaged fast mutex separately, allocates a paged transaction context, zeroes it, stores and references the KTM transaction object, initializes the file-context list and mutex, then sets the transaction context with `FLT_SET_CONTEXT_KEEP_IF_EXISTS`.
- If a race finds an already-defined transaction context, it releases the new context and returns the old one.
- `CgTransactionContextCleanup()` frees the separately allocated fast mutex and dereferences the KTM transaction object.

## File ID Handling

- `CgGetFileId()` calls `FltGetFileSystemType()`.
- For ReFS, it queries `FileIdInformation` and copies the 128-bit file ID.
- For other file systems, it queries `FileInternalInformation`, stores the 64-bit index number, and zeroes the upper 64 bits.

## Dependencies

- Filter Manager context APIs: `FltAllocateContext`, `FltGetFileContext`, `FltSetFileContext`, `FltGetTransactionContext`, `FltSetTransactionContext`, `FltReleaseContext`, `FltQueryInformationFile`, `FltGetFileSystemType`.
- Kernel object references: `ObReferenceObject`, `ObDereferenceObject`.
- Allocation helpers from `utility.h`: `CgAllocateMutex()`, `CgFreeMutex()`.

## Risks And Invariants

- Transaction-context mutex is allocated from nonpaged pool because fast mutex storage must be resident.
- File context cleanup asserts `TxContext == NULL`; transaction cleanup/list drain must clear all file links before file context teardown.
- Races in context creation are handled through `FLT_SET_CONTEXT_KEEP_IF_EXISTS`; returned existing contexts carry references that callers must release.
- `CgFindOrCreateTransactionContext()` references the KTM transaction object and relies on cleanup to dereference it exactly once.
- File identity is normalized to a 128-bit union so NTFS-style and ReFS-style IDs can be logged through common storage.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/change/context.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/change/context.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/change/context.h

## Purpose

Defines context structures and public context helper prototypes for the `change` minifilter sample.

## Data Structures

- `CG_TRANSACTION_CONTEXT` stores:
  - Referenced `PKTRANSACTION`.
  - `Enlisted` flag.
  - `ListDrained` flag.
  - `ScListHead`, the list of file contexts participating in the transaction.
  - Nonpaged `PFAST_MUTEX` protecting the list.
- `CG_FILE_REFERENCE` is a union supporting both 64-bit file IDs and 128-bit ReFS file IDs.
- `CG_FILE_CONTEXT` stores:
  - File ID.
  - Non-transactional `Dirty` flag.
  - Transaction-local `TxDirty` flag.
  - Current transaction context pointer.
  - Embedded transaction-list entry.

## Constants

- `CG_FILE_CONTEXT_TAG` and `CG_TRANSACTION_CONTEXT_TAG` identify context allocations.
- `CG_TRANSACTION_CONTEXT_SIZE` and `CG_FILE_CONTEXT_SIZE` wrap `sizeof()` for registration/allocation.

## API Surface

- `CgFindOrCreateFileContext(PFLT_CALLBACK_DATA Cbd, PCG_FILE_CONTEXT *FileContext)`.
- `CgFindOrCreateTransactionContext(PCFLT_RELATED_OBJECTS FltObjects, PCG_TRANSACTION_CONTEXT *TransactionContext)`.

## Dependencies And Usage

- Used by `change.c` for dirty tracking and transaction enlistment.
- Implemented by `context.c`.
- Requires WDK Filter Manager and KTM-related types from `fltKernel.h`.

## Risks And Invariants

- `ListInTransaction` is valid only while the file context is linked into one transaction context list.
- `TxContext` and list membership must be updated together with the transaction-context mutex and interlocked pointer operations used by `change.c`.
- `ListDrained` prevents new file contexts from being inserted into a transaction context after KTM outcome processing has drained it.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/change/context.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/change/utility.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/change/utility.h

## Purpose

Provides small kernel-mode utility helpers for the `change` minifilter sample, mainly fast-mutex allocation and safe list iteration.

## API Surface

- Defines `CG_MUTEX_TAG`.
- `CgAllocateMutex()` allocates a zeroed `FAST_MUTEX` from `NonPagedPoolNx`.
- `CgFreeMutex()` frees a mutex with `CG_MUTEX_TAG`.
- `LIST_FOR_EACH_SAFE(curr, n, head)` iterates a doubly linked list while allowing removal of the current element.

## Dependencies And Usage

- `context.c` uses the mutex helpers for transaction context mutex allocation and cleanup.
- `change.c` uses `LIST_FOR_EACH_SAFE()` while draining transaction file-context lists.

## Risks And Invariants

- Fast mutex storage must remain in nonpaged pool; the helper encodes that requirement.
- `CgFreeMutex()` assumes the input pointer is valid and was allocated with `CG_MUTEX_TAG`.
- The safe-list macro assumes a standard initialized `LIST_ENTRY` head and valid `Flink` pointers.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/change/utility.h -->