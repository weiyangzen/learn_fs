# Group Research: group_1851_windows_driver_samples_sources_windows_windows_driver_samples_files_3ff2f7aa531e

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/CtxInit.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/CtxInit.c

## Purpose
Main initialization and lifecycle module for the `ctx` minifilter sample. It registers the filter, declares operation/context registration tables, handles instance attach/teardown, initializes debug tracing in checked builds, and centralizes cleanup for all context types used by the sample.

## Key Contents
- Defines global `CTX_GLOBAL_DATA Globals`.
- Registers operation callbacks for:
  - `IRP_MJ_CREATE` -> `CtxPreCreate` / `CtxPostCreate`
  - `IRP_MJ_CLEANUP` -> `CtxPreCleanup`
  - `IRP_MJ_CLOSE` -> `CtxPreClose`
  - `IRP_MJ_SET_INFORMATION` -> `CtxPreSetInfo` / `CtxPostSetInfo`
- Registers context types:
  - `FLT_INSTANCE_CONTEXT`
  - `FLT_FILE_CONTEXT`
  - `FLT_STREAM_CONTEXT`
  - `FLT_STREAMHANDLE_CONTEXT`
- Defines `FilterRegistration` with unload and instance lifecycle callbacks.

## Important Functions
- `DriverEntry`
  - Opts into `NonPagedPoolNx` via `ExInitializeDriverRuntime`.
  - Clears `Globals`.
  - Initializes checked-build debug level from registry.
  - Calls `FltRegisterFilter`, then `FltStartFiltering`.
  - Unregisters on start failure.

- `CtxUnload`
  - Unregisters the filter and clears `Globals.Filter`.

- `CtxContextCleanup`
  - Dispatches cleanup by `FLT_CONTEXT_TYPE`.
  - Frees instance volume names, file names, stream names, stream-handle names.
  - Deletes and frees `ERESOURCE` objects in stream and stream-handle contexts.
  - Does not free the context object itself; Filter Manager owns that.

- `CtxInstanceSetup`
  - Allocates an instance context.
  - Queries volume name length with `FltGetVolumeName`.
  - Allocates and fills `VolumeName`.
  - Saves `Instance` and `Volume`.
  - Sets the instance context with `FLT_SET_CONTEXT_KEEP_IF_EXISTS`.
  - Always releases the local allocation reference after attempting to set.

- `CtxInstanceQueryTeardown`
  - Always permits manual detach.

- `CtxInstanceTeardownStart`
  - Trace-only start teardown hook.

- `CtxInstanceTeardownComplete`
  - Retrieves and logs the instance context, then releases it.

## Checked-Build Debug Support
Under `#if DBG`:
- Dynamically resolves `IoOpenDriverRegistryKey` with `MmGetSystemRoutineAddress`.
- Falls back to opening the service registry path and `Parameters` subkey with `ZwOpenKey`.
- Reads `DebugLevel` from registry using `ZwQueryValueKey`.
- Defaults `Globals.DebugLevel` to `DEBUG_TRACE_ERROR`.

## Dependencies
- Uses shared definitions from `pch.h`, `CtxStruc.h`, and `CtxProc.h`.
- Relies on:
  - `CtxAllocateUnicodeString` / `CtxFreeUnicodeString`
  - `CtxFreeResource`
  - operation callbacks implemented in `operations.c`
  - context helper callbacks implemented in `context.c`

## Research Notes
This file demonstrates the Filter Manager reference-count pattern for contexts clearly: after `FltAllocateContext`, the local reference must be released regardless of whether `FltSet*Context` succeeds. Cleanup functions only release subordinate allocations, never the context allocation itself.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/CtxInit.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/CtxProc.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/CtxProc.h

## Purpose
Shared prototype and inline helper header for the `ctx` minifilter sample. It declares callbacks and context helper routines implemented across `operations.c`, `context.c`, and `support.c`, and defines inline resource allocation/acquire/release helpers.

## Key Contents
- Operation callback prototypes:
  - `CtxPreCreate`, `CtxPostCreate`
  - `CtxPreCleanup`
  - `CtxPreClose`
  - `CtxPreSetInfo`, `CtxPostSetInfo`

- Context helper prototypes:
  - File context:
    - `CtxFindOrCreateFileContext`
    - `CtxCreateFileContext`
  - Stream context:
    - `CtxFindOrCreateStreamContext`
    - `CtxCreateStreamContext`
    - `CtxUpdateNameInStreamContext`
  - Stream-handle context:
    - `CtxCreateOrReplaceStreamHandleContext`
    - `CtxCreateStreamHandleContext`
    - `CtxUpdateNameInStreamHandleContext`

- Unicode string support:
  - `CtxAllocateUnicodeString`
  - `CtxFreeUnicodeString`

## Inline Resource Helpers
- `CtxAllocateResource`
  - Allocates an `ERESOURCE` from `NonPagedPool` using `CTX_RESOURCE_TAG`.

- `CtxFreeResource`
  - Frees an `ERESOURCE` allocation using `CTX_RESOURCE_TAG`.

- `CtxAcquireResourceExclusive`
  - Asserts `IRQL <= APC_LEVEL`.
  - Enters a critical region.
  - Acquires the resource exclusively.

- `CtxAcquireResourceShared`
  - Asserts `IRQL <= APC_LEVEL`.
  - Enters a critical region.
  - Acquires the resource shared.

- `CtxReleaseResource`
  - Asserts `IRQL <= APC_LEVEL`.
  - Releases the resource.
  - Leaves the critical region.

## Research Notes
The resource wrappers encode the expected ERESOURCE discipline for the sample: calls must run at or below APC level, and acquisition is paired with critical-region entry so normal kernel APCs cannot interrupt while holding the resource.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/CtxProc.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/CtxStruc.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/CtxStruc.h

## Purpose
Defines all shared data structures, pool tags, global state, context layouts, and debug-tracing macros for the `ctx` minifilter sample.

## Pool Tags
- `CTX_STRING_TAG`
- `CTX_RESOURCE_TAG`
- `CTX_INSTANCE_CONTEXT_TAG`
- `CTX_FILE_CONTEXT_TAG`
- `CTX_STREAM_CONTEXT_TAG`
- `CTX_STREAMHANDLE_CONTEXT_TAG`

## Main Structures
- `CTX_GLOBAL_DATA`
  - Holds the registered `PFLT_FILTER`.
  - In checked builds, stores `DebugLevel`.

- `CTX_INSTANCE_CONTEXT`
  - Stores `PFLT_INSTANCE`.
  - Stores `PFLT_VOLUME`.
  - Stores `UNICODE_STRING VolumeName`.

- `CTX_FILE_CONTEXT`
  - Stores immutable `UNICODE_STRING FileName`.
  - No lock is included because the file name is set at creation and not modified.

- `CTX_STREAM_CONTEXT`
  - Stores `UNICODE_STRING FileName`.
  - Counts observed create, cleanup, and close events:
    - `CreateCount`
    - `CleanupCount`
    - `CloseCount`
  - Uses `PERESOURCE Resource` to protect mutable fields.

- `CTX_STREAMHANDLE_CONTEXT`
  - Stores `UNICODE_STRING FileName`.
  - Uses `PERESOURCE Resource` to protect mutable fields.

## Debug Support
Checked builds define trace flags for:
- errors
- load/unload
- instance lifecycle
- instance/file/stream/stream-handle context operations
- all tracked I/O

`DebugTrace(Level, Data)` maps to `DbgPrint` when the requested level intersects `Globals.DebugLevel`; in free builds it expands to no work.

## Research Notes
The file distinguishes three useful Filter Manager scopes:
- file context: immutable per file object/name snapshot
- stream context: mutable stream-level counters and name
- stream-handle context: mutable handle-level name state

This separation is the core teaching point of the `ctx` sample.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/CtxStruc.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/context.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/context.c

## Purpose
Implements creation, lookup, attachment, replacement, and name-update logic for the `ctx` sample’s file, stream, and stream-handle contexts.

## Key Functions
- `CtxFindOrCreateFileContext`
  - Attempts `FltGetFileContext`.
  - If missing and creation is requested, allocates a file context and attaches it with `FltSetFileContext`.
  - Handles `STATUS_FLT_CONTEXT_ALREADY_DEFINED` races by releasing the new context and returning the existing one from `oldFileContext`.

- `CtxCreateFileContext`
  - Allocates `FLT_FILE_CONTEXT` from `PagedPool`.
  - Copies the supplied file name into `fileContext->FileName`.

- `CtxFindOrCreateStreamContext`
  - Attempts `FltGetStreamContext`.
  - If missing and requested, allocates and attaches a stream context.
  - Handles concurrent attach races by using `oldStreamContext`.

- `CtxCreateStreamContext`
  - Allocates and zeroes a stream context.
  - Allocates an `ERESOURCE` with `CtxAllocateResource`.
  - Initializes it with `ExInitializeResourceLite`.

- `CtxUpdateNameInStreamContext`
  - Frees any existing stream-context file name.
  - Allocates and copies the supplied name.
  - Caller is responsible for synchronization.

- `CtxCreateOrReplaceStreamHandleContext`
  - Always allocates a new stream-handle context.
  - Attaches it with either `FLT_SET_CONTEXT_REPLACE_IF_EXISTS` or `FLT_SET_CONTEXT_KEEP_IF_EXISTS`.
  - Releases replaced contexts when needed.
  - Handles already-defined races when replacement is not requested.

- `CtxCreateStreamHandleContext`
  - Allocates and zeroes a stream-handle context.
  - Allocates and initializes its `ERESOURCE`.

- `CtxUpdateNameInStreamHandleContext`
  - Frees any existing handle-context name.
  - Allocates and copies the supplied name.
  - Caller is responsible for synchronization.

## Concurrency and Lifetime Pattern
The file consistently follows Filter Manager context rules:
- `FltAllocateContext` returns a referenced context.
- Successful `FltSet*Context` creates an object-held reference.
- The caller retains and later releases its own returned reference.
- If a set loses a race to another thread, the new context is released and the existing context is returned.

## Notable Detail
`CtxCreateFileContext` assigns `*FileContext = fileContext` and returns `STATUS_SUCCESS` even if `CtxAllocateUnicodeString` fails. That means a file context may be returned without a populated `FileName` buffer if allocation fails. Stream and stream-handle context creation paths return allocation failures more directly for their resource allocations.

## Dependencies
- Uses global `Globals.Filter`.
- Uses tags and structures from `CtxStruc.h`.
- Uses resource and string helpers from `CtxProc.h` / `support.c`.

## Research Notes
This is the central context mechanics file for the sample. It is useful as a compact reference for correct `FltGet*Context` / `FltSet*Context` race handling.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/context.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/operations.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/operations.c

## Purpose
Implements the I/O operation callbacks for the `ctx` minifilter sample. It demonstrates how file, stream, and stream-handle contexts are created, updated, counted, and queried across create, cleanup, close, and rename operations.

## Operation Flow
- `CtxPreCreate`
  - Trace-only pre-create callback.
  - Always returns `FLT_PREOP_SUCCESS_WITH_CALLBACK` so `CtxPostCreate` can attach contexts after successful open.

- `CtxPostCreate`
  - Ignores failed creates.
  - Queries normalized file name with `FltGetFileNameInformation`.
  - Finds or creates a stream context, increments `CreateCount`, and updates the stream name under exclusive resource protection.
  - Creates or replaces a stream-handle context and updates its name under exclusive protection.
  - Builds a file name excluding the stream-name suffix and finds or creates a file context.
  - Releases all acquired contexts and name information before return.
  - Does not modify the underlying create status if its own context work fails.

- `CtxPreCleanup`
  - Retrieves existing stream context only.
  - Increments `CleanupCount` under exclusive resource protection.
  - Ignores errors and returns `FLT_PREOP_SUCCESS_NO_CALLBACK`.

- `CtxPreClose`
  - Retrieves existing stream context only.
  - Increments `CloseCount` under exclusive resource protection.
  - Ignores errors and returns `FLT_PREOP_SUCCESS_NO_CALLBACK`.

- `CtxPreSetInfo`
  - Only requests a post-operation callback for `FileRenameInformation` and `FileRenameInformationEx`.
  - Uses `FLT_PREOP_SYNCHRONIZE` so the post-operation callback can run in the initiating thread at a pageable IRQL.

- `CtxPostSetInfo`
  - Ignores failed set-information operations.
  - Retrieves instance context for logging.
  - Queries the normalized post-rename name.
  - Retrieves existing stream context and updates its name under exclusive protection.
  - Creates or replaces stream-handle context and updates its name.
  - Retrieves, but does not modify, existing file context. This matches the sample’s design where file context name is immutable after creation.

## Synchronization
Mutable context fields are protected with the resource helpers from `CtxProc.h`:
- stream `FileName` and counters
- stream-handle `FileName`

File context does not have a lock because its name is intended to be immutable.

## Error Handling
Failures in context bookkeeping are traced but generally do not fail already-successful file-system operations. This is intentional sample behavior: context logging should not alter the successful result from the underlying file system.

## Research Notes
The file demonstrates the semantic difference between stream, stream-handle, and file contexts:
- Stream context follows the file stream across opens and records aggregate counters.
- Stream-handle context is replaced for each successful open or rename update.
- File context captures a stable file-level name without stream suffix and is not renamed in place.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/operations.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/pch.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/pch.h

## Purpose
Precompiled header for the `ctx` minifilter sample. It centralizes common system and project includes and enables strict compiler warnings.

## Key Contents
- Include guard: `__CTX_PCH_H__`
- Warning pragmas promoted to errors:
  - `4100` unreferenced formal parameter
  - `4101` unreferenced local variable
  - `4061` missing enum case in switch
  - `4505` unreferenced local function
- Includes:
  - `<fltKernel.h>`
  - `<dontuse.h>`
  - `<suppress.h>`
  - `"CtxStruc.h"`
  - `"CtxProc.h"`

## Notable Detail
The closing directive is written as `#endif __CTX_PCH_H__`, which places extra tokens after `#endif`. This is accepted by some C preprocessors with a warning, but the conventional form would be `#endif // __CTX_PCH_H__`.

## Research Notes
This file intentionally makes unused parameters and locals build-breaking unless explicitly marked with `UNREFERENCED_PARAMETER`, which explains the frequent annotations in the implementation files.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/pch.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/support.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/support.c

## Purpose
Implements small support routines for the `ctx` minifilter sample, specifically allocation and freeing of `UNICODE_STRING` buffers.

## Functions
- `CtxAllocateUnicodeString`
  - Expects `String->MaximumLength` to already contain the requested allocation size.
  - Allocates a zeroed `PagedPool` buffer with `CTX_STRING_TAG`.
  - Sets `String->Length` to zero on success.
  - Returns `STATUS_INSUFFICIENT_RESOURCES` if allocation fails.

- `CtxFreeUnicodeString`
  - Frees `String->Buffer` with `CTX_STRING_TAG`.
  - Resets `Length`, `MaximumLength`, and `Buffer`.

## Implementation Details
- Both routines are pageable.
- The functions use SAL annotations to describe postconditions for `Length`, `MaximumLength`, and `Buffer`.
- Debug tracing reports failed allocation size.

## Dependencies
- Includes `pch.h`.
- Uses `CTX_STRING_TAG` from `CtxStruc.h`.

## Research Notes
These helpers rely on callers setting `MaximumLength` correctly before allocation. They are used throughout the context sample to store volume names and file names in instance, file, stream, and stream-handle contexts.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/support.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/delete/delete.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/delete/delete.c

## Purpose
Self-contained delete-detection minifilter sample. It tracks streams that become deletion candidates through `FILE_DELETE_ON_CLOSE` or delete disposition changes, verifies deletion after cleanup, distinguishes file deletes from alternate data stream deletes, supports NTFS/ReFS differences, and defers transaction-related delete notifications until commit or rollback.

## Global Configuration
- `gFilterHandle`: registered filter handle.
- `gTraceFlags`: debug trace mask, defaulting to errors.
- Attaches only to writable NTFS or ReFS volumes.
- Registers callbacks for:
  - `IRP_MJ_CREATE`
  - `IRP_MJ_SET_INFORMATION`
  - `IRP_MJ_CLEANUP`
- Registers contexts:
  - `FLT_INSTANCE_CONTEXT`
  - `FLT_STREAM_CONTEXT`
  - `FLT_TRANSACTION_CONTEXT`

## Core Types
- `DF_FILE_REFERENCE`
  - Holds either a 64-bit NTFS file ID or 128-bit ReFS file ID.
  - `DfSizeofFileId` chooses the size based on whether upper 64 bits are zero.

- `DF_INSTANCE_CONTEXT`
  - Caches a volume GUID name.

- `DF_STREAM_CONTEXT`
  - Stores last opened-name information.
  - Stores file ID.
  - Tracks in-flight delete-disposition operations with `NumOps`.
  - Tracks notification state with `IsNotified`.
  - Tracks candidate state:
    - `SetDisp`
    - `DeleteOnClose`
    - `FileIdSet`

- `DF_TRANSACTION_CONTEXT`
  - Holds a list of pending delete notifications.
  - Uses a NonPagedPool `ERESOURCE` to protect the list.

- `DF_DELETE_NOTIFY`
  - List node for a pending delete notification inside a transaction.
  - References the stream context and records whether it was a file delete or stream delete.

## Initialization and Instance Handling
- `DriverEntry`
  - Opts into `NonPagedPoolNx`.
  - Registers and starts the minifilter.

- `DfUnload`
  - Unregisters the filter.

- `DfInstanceSetup`
  - Rejects read-only volumes.
  - Accepts writable `FLT_FSTYPE_NTFS` and `FLT_FSTYPE_REFS`.
  - Rejects other file systems.

- Teardown callbacks are trace-only and allow detach.

## Context Helpers
- `DfAllocateContext`
  - Allocates and initializes stream, transaction, or instance contexts.
  - Transaction contexts initialize `DeleteNotifyList` and allocate an `ERESOURCE`.

- `DfSetContext` / `DfGetContext`
  - Type-switching wrappers over Filter Manager context APIs.

- `DfGetOrSetContext`
  - Generic get-or-create-and-attach helper.
  - Handles already-attached context races.
  - Enlists in a transaction after setting a transaction context.

- Cleanup callbacks:
  - Stream cleanup releases `NameInfo`.
  - Transaction cleanup drains pending notifications, releases stream contexts, frees notify nodes, and deletes the resource.
  - Instance cleanup frees cached volume GUID name.

## Name and ID Helpers
- `DfGetFileNameInformation`
  - Gets opened file name, parses it, and atomically swaps it into stream context.

- `DfGetFileId`
  - Queries `FileInternalInformation`.
  - For ReFS-style invalid 64-bit ID, queries `FileIdInformation` to obtain 128-bit ID.
  - Uses `KeMemoryBarrier` before setting `FileIdSet`.

- `DfGetVolumeGuidName`
  - Gets or creates an instance context.
  - Lazily caches the volume GUID name with trailing backslash.
  - Uses `InterlockedCompareExchangePointer` to resolve concurrent cache population.

- `DfBuildFileIdString`
  - Builds a volume-GUID-plus-file-ID string for open-by-ID checks.

- `DfDetectDeleteByFileId`
  - Attempts `FltCreateFileEx2` with `FILE_OPEN_BY_FILE_ID`.
  - Uses transaction parameters when available.
  - Converts open-by-ID outcomes into deletion detection signals elsewhere.

## Delete Detection
- `DfPreCreateCallback`
  - If create has `FILE_DELETE_ON_CLOSE`, allocates a stream context and requests synchronized post-create callback.

- `DfPostCreateCallback`
  - On successful create, attaches or retrieves stream context.
  - Sets `DeleteOnClose` based on create options.

- `DfPreSetInfoCallback`
  - Handles `FileDispositionInformation` and `FileDispositionInformationEx`.
  - Gets or sets stream context.
  - Increments `NumOps` to detect racing delete-disposition changes.
  - If a race is detected, it deliberately does not request postop, leaving `NumOps` positive so cleanup will conservatively verify deletion.

- `DfPostSetInfoCallback`
  - Updates `SetDisp` or `DeleteOnClose` based on successful disposition operation.
  - Handles `FILE_DISPOSITION_INFORMATION_EX` distinction between `FILE_DISPOSITION_ON_CLOSE` and regular set-disposition behavior.
  - Decrements `NumOps`.

- `DfPreCleanupCallback`
  - Retrieves stream context if one exists.
  - Captures name information before cleanup completes.
  - Requests synchronized post-cleanup.

- `DfPostCleanupCallback`
  - Core deletion check.
  - If candidate state indicates possible deletion and no notification was sent, queries `FileStandardInformation`.
  - On `STATUS_FILE_DELETED`, calls `DfProcessDelete`.

- `DfIsFileDeleted`
  - Determines whether the whole file was deleted after a stream deletion.
  - Uses open-by-file-ID for transactions and ReFS.
  - Uses `FSCTL_GET_OBJECT_ID` as a cheaper NTFS non-transaction check.

- `DfProcessDelete`
  - Creates or gets transaction context if operation is transacted.
  - Calls `DfIsFileDeleted`.
  - Calls `DfNotifyDelete`.

## Transaction Notifications
- `DfNotifyDelete`
  - Prints immediate non-transaction delete messages.
  - For transaction deletes, adds a pending notification to the transaction context.

- `DfAddTransDeleteNotify`
  - Allocates a pending notification node.
  - References stream context.
  - Inserts it under transaction-context resource protection.

- `DfTransactionNotificationCallback`
  - Handles commit-finalize and rollback notifications.
  - Drains pending notifications.
  - On rollback, decrements `IsNotified`.
  - Logs final deleted or saved outcome.
  - Releases stream contexts and frees notification nodes.

## Research Notes
This sample is intentionally conservative. When delete-disposition operations race and final state cannot be known, it preserves candidate state and verifies deletion at cleanup. It also shows the extra complexity needed for:
- alternate data stream deletion versus whole-file deletion
- transactional NTFS-style delete semantics
- ReFS 128-bit file IDs
- safe context lifetime across transaction-deferred notifications
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/delete/delete.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/RegistrationData.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/RegistrationData.c

## Purpose
Contains MiniSpy’s static Filter Manager registration data in a separate file so it can be placed in the `INIT` segment.

## Operation Registration
Registers MiniSpy’s generic pre/post callbacks for broad coverage across IRP and fast-I/O style operations, including:
- create, create named pipe, create mailslot
- close, cleanup
- read, write
- query/set file information
- query/set EA
- flush buffers
- query/set volume information
- directory control
- filesystem/device/internal-device control
- lock control
- security and quota operations
- PNP
- section synchronization and cache-manager callbacks
- fast I/O check
- network query open
- MDL read/write operations
- volume mount/dismount

`IRP_MJ_SHUTDOWN` has only a pre-operation callback because post-operation callbacks are not supported for shutdown.

## Context Registration
- If `MINISPY_VISTA` is true, registers `FLT_TRANSACTION_CONTEXT` with:
  - cleanup callback `SpyDeleteTxfContext`
  - size `sizeof(MINISPY_TRANSACTION_CONTEXT)`
  - tag `'ypsM'`
- Ends with `FLT_CONTEXT_END`.

## Filter Registration
- Uses `FLT_REGISTRATION_VERSION`.
- On Windows 8 and later, uses `FLTFL_REGISTRATION_SUPPORT_NPFS_MSFS`.
- Supplies:
  - `Contexts`
  - `Callbacks`
  - `SpyFilterUnload`
  - `SpyQueryTeardown`
- No instance setup or teardown start/complete callbacks.
- No name provider callbacks.
- If Vista transaction support is compiled, supplies `SpyKtmNotificationCallback`.

## Section Placement
When `ALLOC_DATA_PRAGMA` is defined:
- data and const data are placed in `INIT`
- section settings are restored at the end

## Research Notes
This file is declarative. MiniSpy’s behavior is centralized in generic callbacks; this registration table makes MiniSpy observe nearly every meaningful file-system operation rather than implementing operation-specific callbacks.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/RegistrationData.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/minispy.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/minispy.c

## Purpose
Main kernel module for the MiniSpy minifilter. It initializes global state, registers the filter, creates the user-mode communication port, logs pre/post operation activity, handles user commands, and manages optional transaction enlistment/logging.

## Global State
- `MINISPY_DATA MiniSpyData`
  - Holds driver/filter handles, communication ports, output buffer list, lookaside list, record throttling counters, logging sequence number, name query method, debug flags, and optional transaction API pointers.

- `NTSTATUS StatusToBreakOn`
  - Debug-only support for breaking on a selected name-query status.

## Initialization and Unload
- `DriverEntry`
  - Initializes logging counters and defaults.
  - Initializes output buffer list and spin lock.
  - Initializes nonpaged lookaside list for records.
  - Dynamically imports transaction APIs on Vista+ builds.
  - Reads registry parameters with `SpyReadDriverParameters`.
  - Registers the filter with `FltRegisterFilter`.
  - Builds a default security descriptor.
  - Creates a communication port named by `MINISPY_PORT_NAME`.
  - Starts filtering.
  - Cleans up partially initialized resources on failure.

- `SpyFilterUnload`
  - Closes the server communication port.
  - Unregisters filter.
  - Empties queued output records.
  - Deletes lookaside list.

- `SpyQueryTeardown`
  - Allows manual detach from a volume.

## User-Mode Communication
- `SpyConnect`
  - Accepts a single client connection.
  - Stores `ClientPort`.

- `SpyDisconnect`
  - Closes the client port.

- `SpyMessage`
  - Handles raw user-mode input/output buffers.
  - Uses try/except for user buffer access.
  - Supports:
    - `GetMiniSpyLog`: validates output buffer, alignment, and returns log records via `SpyGetLog`.
    - `GetMiniSpyVersion`: writes `MINISPY_MAJ_VERSION` and `MINISPY_MIN_VERSION`.
  - Performs explicit alignment checks because Filter Manager probing does not guarantee alignment.

## Operation Logging
- `SpyPreOperationCallback`
  - Allocates a log record with `SpyNewRecord`.
  - Attempts normalized name lookup using `MiniSpyData.NameQueryMethod`.
  - Falls back to opened name or textual no-name markers if normalized lookup fails.
  - Optionally parses names when `SPY_DEBUG_PARSE_NAMES` is set.
  - On Vista+ builds, parses ECPs for create operations.
  - Stores name/ECP data in the log record.
  - Fills operation data with `SpyLogPreOperationData`.
  - For `IRP_MJ_SHUTDOWN`, invokes post logging inline because shutdown has no post callback.
  - Otherwise passes the record as completion context and requests post callback.

- `SpyPostOperationCallback`
  - Frees the record immediately if post operation is draining.
  - Completes operation logging via `SpyLogPostOperationData`.
  - If reparse tag data is present, emits a second record containing file tag data.
  - Queues records with `SpyLog`.
  - For successful transacted creates, calls `SpyEnlistInTransaction`.

## Transaction Support
- `SpyEnlistInTransaction`
  - Compiled for Vista+.
  - No-ops if dynamic Filter Manager transaction APIs are unavailable.
  - Retrieves or creates a `MINISPY_TRANSACTION_CONTEXT`.
  - Handles races where another thread sets transaction context first.
  - Enlists with `FLT_MAX_TRANSACTION_NOTIFICATIONS`.
  - Marks context with `MINISPY_ENLISTED_IN_TRANSACTION`.
  - Logs a transaction-start-style record.

- `SpyKtmNotificationCallback`
  - Allocates a log record and records KTM transaction notifications.

- `SpyDeleteTxfContext`
  - Transaction context cleanup callback.
  - Asserts correct context type and nonzero count.

## Exception Handling
- `SpyExceptionFilter`
  - Allows expected NTSTATUS exceptions.
  - If not accessing user buffers, unexpected exceptions continue searching.
  - If accessing user buffers, the caller handles the exception.

## Research Notes
MiniSpy is a logging sample rather than a policy filter. Its core architecture is:
1. capture operation metadata in pre-op,
2. enrich it in post-op,
3. queue it to user mode,
4. optionally log transaction notifications.

The file also demonstrates careful user-buffer handling for minifilter communication ports: Filter Manager probes buffers, but MiniSpy still guards access with try/except and performs alignment checks itself.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/minispy.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/mspyKern.h -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/mspyKern.h

## Purpose
Kernel-only MiniSpy header. It defines version/platform feature macros, internal global state, transaction support types, constants, and prototypes for MiniSpy’s kernel modules.

## Includes and Tags
- Includes:
  - `<fltKernel.h>`
  - `<suppress.h>`
  - `"minispy.h"`
- Defines allocation tag:
  - `SPY_TAG 'ypSM'`

## Platform Feature Macros
- `MINISPY_WIN8`
  - Windows 8+ behavior, including NPFS/MSFS registration support.
- `MINISPY_WIN7`
  - Windows 7+ ECP support.
- `MINISPY_VISTA`
  - Vista+ transaction and older ECP support.
- `MINISPY_NOT_W2K`
  - Excludes Windows 2000 behavior paths.

## Vista+ Transaction and ECP Support
When `MINISPY_VISTA` is true:
- Defines dynamic Filter Manager API function pointer types:
  - `PFLT_SET_TRANSACTION_CONTEXT`
  - `PFLT_GET_TRANSACTION_CONTEXT`
  - `PFLT_ENLIST_IN_TRANSACTION`
- Defines known ECP type flags:
  - prefetch
  - oplock key
  - NFS
  - SRV
- Defines `ECP_TYPE` enumeration.
- Defines `ADDRESS_STRING_BUFFER_SIZE`.

## Global Data Structure
`MINISPY_DATA` contains:
- driver object and filter handle
- server and client communication ports
- output buffer list and spin lock
- nonpaged lookaside list for records
- record allocation throttling fields
- static out-of-memory record buffer
- log sequence counter
- configured name query method
- debug flags
- dynamically imported transaction API pointers on Vista+ builds

## Transaction Context
`MINISPY_TRANSACTION_CONTEXT`
- `Flags`
- `Count`

`MINISPY_ENLISTED_IN_TRANSACTION` marks contexts that have successfully enlisted.

## Defaults and Registry Names
- `DEFAULT_MAX_RECORDS_TO_ALLOCATE`
- `MAX_RECORDS_TO_ALLOCATE`
- `DEFAULT_NAME_QUERY_METHOD`
- `NAME_QUERY_METHOD`
- `SPY_DEBUG_PARSE_NAMES`

## Prototypes
Declares:
- operation callbacks
- KTM transaction callback
- unload and teardown callbacks
- registry parameter loading
- exception filter
- buffer allocation/free routines
- log record allocation/free routines
- ECP parsing and record name helpers
- operation and transaction logging routines
- user-mode log retrieval
- output queue draining
- transaction context cleanup

## Research Notes
This header is the internal contract tying together MiniSpy’s registration, logging, communication, and transaction code. It also preserves compatibility across OS versions by compiling feature blocks conditionally and dynamically importing newer Filter Manager transaction APIs.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/mspyKern.h -->