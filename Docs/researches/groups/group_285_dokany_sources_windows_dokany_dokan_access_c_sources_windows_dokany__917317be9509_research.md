# Group Research: group_285_dokany_sources_windows_dokany_dokan_access_c_sources_windows_dokany__917317be9509

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/windows/dokany`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/access.c -->
# File Research: sources/windows/dokany/dokan/access.c

User-mode helper for retrieving the Windows access token of the process/thread that issued a Dokan create request.

Key responsibilities:
- Implements `DokanOpenRequestorToken(PDOKAN_FILE_INFO)`.
- Validates that `DOKAN_FILE_INFO.DokanContext` points to a valid `DOKAN_IO_EVENT` with an event context and instance.
- Restricts token retrieval to `IRP_MJ_CREATE` callbacks.
- Builds a small `EVENT_INFORMATION` request carrying the event serial number.
- Sends `FSCTL_GET_ACCESS_TOKEN` to the per-mount raw device name and returns the driver-provided token handle.

Important behavior:
- Returns `INVALID_HANDLE_VALUE` and sets `ERROR_INVALID_PARAMETER` for invalid context or non-create events.
- Returns `INVALID_HANDLE_VALUE` and sets `ERROR_OUTOFMEMORY` if the temporary event buffer cannot be allocated.
- The returned handle is owned by the caller, matching the public API contract in `dokan.h`.

Dependencies:
- Depends on `DOKAN_IO_EVENT`, `EVENT_INFORMATION`, and mount device naming from `dokani.h`.
- Uses `GetRawDeviceName()` and `SendToDevice()` from the core Dokan library.
- Uses driver FSCTL `FSCTL_GET_ACCESS_TOKEN`.

Notable risks:
- Assumes `FileInfo` and `FileInfo->DokanContext` are valid; only the decoded `ioEvent` fields are checked.
- The function shares one `EVENT_INFORMATION` buffer as both input and output, so the driver IOCTL contract must preserve this layout.
- A successful result may still return an invalid handle if the driver does so; no additional handle validation is performed.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/access.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/cleanup.c -->
# File Research: sources/windows/dokany/dokan/cleanup.c

Dispatcher for `IRP_MJ_CLEANUP`, bridging kernel cleanup notifications to the user filesystem callback.

Key responsibilities:
- Normalizes the cleanup file name with `CheckFileName()`.
- Allocates a default `EVENT_INFORMATION` reply through `CreateDispatchCommon()`.
- Forces the reply status to `STATUS_SUCCESS`, regardless of user callback behavior.
- Transfers `DOKAN_DELETE_ON_CLOSE` into `DOKAN_FILE_INFO.DeletePending`.
- Invokes `DOKAN_OPERATIONS.Cleanup` when implemented.
- Completes the event through `EventCompletion()`.

Important behavior:
- Cleanup is treated as non-failing: user callback return value is ignored because the callback returns `void`.
- Delete-on-close is exposed to user mode before the cleanup callback so the filesystem can delete the object at cleanup time.
- Open-info lifetime is released through the common completion path.

Dependencies:
- Uses `DOKAN_IO_EVENT`, `EVENT_CONTEXT.Operation.Cleanup`, and `DOKAN_FILE_INFO`.
- Depends on core helpers declared in `dokani.h`: `CheckFileName`, `CreateDispatchCommon`, and `EventCompletion`.

Notable risks:
- Cleanup correctness depends on the user filesystem honoring `DeletePending`; the library cannot recover from a failed delete in this callback.
- The event result allocation is assumed to succeed; this function does not explicitly handle `CreateDispatchCommon()` allocation failure.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/cleanup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/close.c -->
# File Research: sources/windows/dokany/dokan/close.c

Dispatcher for `IRP_MJ_CLOSE`, handling final open-context release without sending a reply to the driver.

Key responsibilities:
- Normalizes the close file name with `CheckFileName()`.
- Emits debug information about the close and associated open event.
- Calls `ReleaseDokanOpenInfo()` to decrement open tracking and run delayed `CloseFile` callback when safe.

Important behavior:
- Does not allocate or send `EVENT_INFORMATION`; the driver has already completed close and expects no reply.
- Actual user `CloseFile` invocation may be delayed until all in-flight operations on the same `DOKAN_OPEN_INFO` have released their references.

Dependencies:
- Uses `DOKAN_OPEN_INFO` lifetime logic from `dokan.c`.
- Includes `dokan_pool.h` for pooled open-info cleanup functions used indirectly.

Notable risks:
- Correctness relies on `ReleaseDokanOpenInfo()` balancing the extra close decrement against prior per-event increments.
- Because no result is returned to the driver, failures inside user `CloseFile` cannot be reported.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/close.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/create.c -->
# File Research: sources/windows/dokany/dokan/create.c

Create/open dispatcher for `IRP_MJ_CREATE`, including security-context translation, open-context allocation, create-disposition mapping, target-directory handling, and delete access fallback.

Key responsibilities:
- `SetIOSecurityContext()` converts serialized driver security context fields into user-mode `DOKAN_IO_SECURITY_CONTEXT` pointers and `UNICODE_STRING` views.
- `CreateSuccesStatusCheck()` treats normal success plus selected `STATUS_OBJECT_NAME_COLLISION` cases as successful opens for `FILE_OPEN_IF`, `FILE_SUPERSEDE`, and `FILE_OVERWRITE_IF`.
- `DispatchCreate()` allocates and initializes a `DOKAN_OPEN_INFO`, stores it in `EVENT_INFORMATION.Context`, and calls `DOKAN_OPERATIONS.ZwCreateFile`.
- Splits `CreateOptions` into high-byte disposition and low 24-bit create options.
- Detects directory opens through `FILE_DIRECTORY_FILE` and `SL_OPEN_TARGET_DIRECTORY`.
- Handles `SL_OPEN_TARGET_DIRECTORY` by temporarily opening the original child, then opening its parent directory.
- Maps user callback status into `FILE_OPENED`, `FILE_CREATED`, `FILE_OVERWRITTEN`, `FILE_SUPERSEDED`, `FILE_EXISTS`, or `FILE_DOES_NOT_EXIST`.
- On delete access denial, attempts a parent-directory open with `FILE_DELETE_CHILD` and/or `FILE_LIST_DIRECTORY`.

Important behavior:
- `DOKAN_OPEN_INFO` starts with `OpenCount = 1`; subsequent operations increment/decrement it in `dokan.c`.
- On create failure, the open info is returned to the pool and the result context is cleared.
- On success, `DOKAN_OPEN_INFO` captures `IsDirectory` and user `DOKAN_FILE_INFO.Context`.
- Conflicting `FILE_NON_DIRECTORY_FILE` and `FILE_DIRECTORY_FILE` options return `STATUS_INVALID_PARAMETER`.
- `SL_OPEN_TARGET_DIRECTORY` mutates the request file name in place to parent path form and keeps `origFileName` for child checks.

Dependencies:
- Depends on driver `EVENT_CONTEXT.Operation.Create` layout, including embedded offsets for names and security descriptors.
- Uses pooled open info from `dokan_pool.c`.
- Calls user callbacks `ZwCreateFile`, optionally `Cleanup`, and optionally `CloseFile`.
- Uses Windows create disposition, access mask, and NTSTATUS constants.

Notable risks:
- `SetIOSecurityContext()` trusts driver-provided offsets into the serialized access state.
- `origFileName = _wcsdup(fileName)` is not checked before use in the `SL_OPEN_TARGET_DIRECTORY` child-open path.
- The delete-access fallback mutates `fileName` to the parent path and does not restore it, which is acceptable for reply processing but fragile for later diagnostics.
- A failed `PopFileOpenInfo()` would be dereferenced; allocation failure is not handled locally.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/create.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/directory.c -->
# File Research: sources/windows/dokany/dokan/directory.c

Directory enumeration implementation, converting user `WIN32_FIND_DATAW` entries into the Windows directory information classes requested by the kernel.

Key responsibilities:
- Defines `DOKAN_FIND_DATA`, the internal wrapper for `WIN32_FIND_DATAW` entries.
- Provides fill helpers for:
  - `FileDirectoryInformation`
  - `FileFullDirectoryInformation`
  - `FileIdFullDirectoryInformation`
  - `FileNamesInformation`
  - `FileBothDirectoryInformation`
  - `FileIdBothDirectoryInformation`
  - `FileIdExtdDirectoryInformation`
  - `FileIdExtdBothDirectoryInformation`
- Aligns directory entries to 8-byte boundaries with `QuadAlign`.
- Implements `DokanFillFileData()` callback to append user-provided `WIN32_FIND_DATAW` entries to a `DOKAN_VECTOR`.
- Implements `MatchFiles()` to filter cached entries by search pattern, file index, single-entry requests, and buffer capacity.
- Adds missing `.` and `..` entries for non-root wildcard directory scans.
- Caches enumeration results and search pattern per `DOKAN_OPEN_INFO`.
- Dispatches `FindFilesWithPattern` first, falls back to `FindFiles`, and filters internally when pattern-aware enumeration is unavailable.
- Implements `DokanIsNameInExpression()` for Windows-style wildcard matching, including DOS wildcard characters `<`, `>`, and `"`.

Important behavior:
- Reuses cached directory lists unless the search pattern changes or `SL_RESTART_SCAN` requires a rescan.
- `SL_INDEX_SPECIFIED` overrides restart behavior to match FastFat semantics.
- Returns `STATUS_NO_SUCH_FILE` for no match at index 0, `STATUS_NO_MORE_FILES` after prior entries, and `STATUS_BUFFER_OVERFLOW` when the output buffer is too small.
- Directory entries set `NextEntryOffset` except for the last returned entry.
- Case sensitivity follows `DOKAN_OPTION_CASE_SENSITIVE`.

Dependencies:
- Uses `DOKAN_VECTOR` for directory-list storage.
- Uses pooled directory lists and temporary open info from `dokan_pool.c`.
- Uses user callbacks `FindFilesWithPattern` and `FindFiles`.
- Uses `ALIGN_ALLOCATION_SIZE()` from `dokan.c` to report allocation size consistently with volume options.

Notable risks:
- `DokanFillFileData()` does not check `DokanVector_PushBack()` failure, so out-of-memory during enumeration is not propagated.
- `MatchFiles()` writes `NextEntryOffset` through `PFILE_BOTH_DIR_INFORMATION` even when the actual information class differs; this relies on compatible leading layout.
- The temporary open-info path for events without open context can cache during the dispatch but is immediately returned to the pool after completion.
- The wildcard matcher is recursive for `*` and DOS star matching, so pathological patterns/names can be expensive.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/directory.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/dokan.c -->
# File Research: sources/windows/dokany/dokan/dokan.c

Core Dokan user-mode runtime: initialization, mount lifecycle, driver communication, event pulling/dispatch, completion, open-context lifetime, mount queries, create-flag mapping, and notification APIs.

Key responsibilities:
- Maintains global debug settings, initialization refcount, mounted-instance list, and instance critical section.
- Allocates and destroys `DOKAN_INSTANCE` objects, including device handles, thread-pool cleanup groups, wait handles, keepalive handles, and notify handles.
- Validates drive-letter mount availability and allocation/sector sizes.
- Starts a Dokan mount via `FSCTL_EVENT_START` and maps user options into driver `EVENT_START` flags.
- Opens the per-volume raw device and launches main event-pull workers.
- Dispatches driver events by major function to create, cleanup, close, directory, read, write, information, volume, lock, set-info, flush, and security dispatchers.
- Supports driver log forwarding through `DOKAN_IRP_LOG_MESSAGE`.
- Sends event replies and pulls new batches with `FSCTL_EVENT_PROCESS_N_PULL`.
- Implements both batched event dispatch and dedicated single-event pull loops.
- Allocates event result buffers through default, 16K, 32K, 64K, 128K, or direct allocation paths.
- Tracks `DOKAN_OPEN_INFO.OpenCount`, user context, delayed close filenames, directory cache cleanup, and final `CloseFile` callback.
- Provides public APIs for `DokanInit`, `DokanShutdown`, `DokanMain`, `DokanCreateFileSystem`, `DokanCloseHandle`, wait registration, mount point list retrieval, unmount release FSCTLs, debug mode, mount cleanup, notifications, and create-flag mapping.

Important behavior:
- `DokanCreateFileSystem()` requires prior `DokanInit()` and raises `DOKAN_EXCEPTION_NOT_INITIALIZED` otherwise.
- Main pull-thread count is derived from process affinity, clamped between 2 and 16 unless single-thread mode is enabled.
- Very high CPU counts enable IPC batching automatically.
- `EventCompletion()` currently only releases open info; the dispatch loop later sends `IoEvent->EventResult` back while pulling more work.
- `CloseFile` is invoked only when the open count reaches zero, allowing close to wait for in-flight operations.
- `CheckFileName()` normalizes double-leading backslashes and removes trailing backslash for non-root paths.
- Notifications strip the drive-letter prefix from absolute paths before sending `FSCTL_NOTIFY_PATH`.
- `DokanMapKernelToUserCreateFileFlags()` maps kernel create options/dispositions/access masks back toward Win32 `CreateFile` parameters.

Dependencies:
- Uses Windows threadpool APIs, critical sections, events, handles, `DeviceIoControl`, and mount manager style drive checks.
- Depends on driver public protocol types and FSCTLs from included Dokan public headers.
- Depends on object pools from `dokan_pool.c` and vectors from `dokan_vector.c`.
- Calls dispatchers declared in `dokani.h` and implemented across the Dokan library.

Notable risks:
- `DokanShutdown()` enters `g_InstanceCriticalSection` and then calls `DokanCloseHandle()`, which also enters the same critical section around deletion; this relies on Windows critical sections being recursive for the same thread and on careful list mutation.
- `QueueIoEvent()` does not close the `PTP_WORK` handle after submission in this file; lifetime is presumably tied to cleanup-group closure, but it is not explicit here.
- `SendAndPullEventInformation()` frees event result buffers after IOCTL completion; any later use would be unsafe, so dispatchers must not retain them.
- `DokanGetMountPointList(uncOnly=TRUE)` copies matching entries into original indexes while reporting the unfiltered count, which can leave zeroed gaps in the returned array.
- `CreateDispatchCommon()` can return with `EventResult == NULL`; several dispatchers assume allocation succeeded.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/dokan.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/dokan.h -->
# File Research: sources/windows/dokany/dokan/dokan.h

Primary public Dokan user-mode API header defining mount options, file operation callback contracts, lifecycle APIs, notifications, and helper functions.

Key responsibilities:
- Defines DLL import/export calling convention macros `DOKANAPI` and `DOKAN_CALLBACK`.
- Defines version constants, driver/network provider names, mount result codes, and exception codes.
- Defines `DOKAN_OPTIONS`, including version, threading mode, feature flags, global context, mount point, UNC name, timeout, sector/allocation sizing, and optional volume security descriptor.
- Defines `DOKAN_FILE_INFO`, the per-operation context passed to user callbacks.
- Defines callback typedefs `PFillFindData` and `PFillFindStreamData`.
- Defines `DOKAN_OPERATIONS`, the complete callback table for user filesystem implementations.
- Declares lifecycle APIs: `DokanInit`, `DokanShutdown`, `DokanMain`, `DokanCreateFileSystem`, wait APIs, close/unmount APIs.
- Declares mount point list APIs, wildcard matching, version queries, timeout reset, requestor token retrieval, create-flag mapping, Win32-to-NTSTATUS conversion, and change notification APIs.

Important behavior specified by the header:
- `ZwCreateFile` is central and must set `DOKAN_FILE_INFO.IsDirectory` for directories.
- User `Context` stored in `DOKAN_FILE_INFO.Context` is carried between related operations and must be cleaned by user code.
- `Cleanup` is where delete-on-close deletion must occur when `DeletePending` is true.
- `CloseFile` is final context cleanup and cannot report failure.
- Read/write callbacks may occur after cleanup for memory-mapped I/O.
- `FindFilesWithPattern` is preferred; `FindFiles` is fallback.
- Delete callbacks should validate whether deletion is allowed, not delete immediately.
- Volume information and disk free-space callbacks may occur without a preceding create.
- Alternate stream enumeration is only used with `DOKAN_OPTION_ALT_STREAM`.
- Notifications must be called independently of normal filesystem operation callbacks and require absolute mounted paths.

Dependencies:
- Includes Windows headers, `ntstatus.h`, `fileinfo.h`, and `public.h`.
- Public contracts rely on Windows file information classes, security descriptors, access masks, file attributes, and NTSTATUS values.

Notable risks:
- This is ABI/API surface: structure layout, callback order, and calling convention changes would break consumers.
- Many callback contracts require user filesystems to implement Windows semantics precisely, especially cleanup/delete, sharing, paging I/O, and directory state.
- `DOKAN_FILE_INFO` contains reserved fields that consumers must not modify, but the header cannot enforce that.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/dokan.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/dokan_pool.c -->
# File Research: sources/windows/dokany/dokan/dokan_pool.c

Global object-pool implementation for Dokan runtime buffers, open-info objects, directory vectors, and the shared Windows thread pool.

Key responsibilities:
- Creates the global thread pool with `CreateThreadpool`.
- Initializes critical sections for all pools.
- Allocates vector-backed pools for IO batches, IO events, default event results, 16K/32K/64K/128K event results, open info, and directory lists.
- Cleans up pooled objects, vectors, critical sections, and the thread pool.
- Provides pop/push/free functions for:
  - `DOKAN_IO_BATCH`
  - `DOKAN_IO_EVENT`
  - `EVENT_INFORMATION` result buffers
  - extra-sized event result buffers
  - `DOKAN_OPEN_INFO`
  - directory-list vectors
- Initializes per-open critical sections on first allocation and cleans cached directory lists/search patterns when returning open info to the pool.
- Uses `EventContextBatchCount` as a shared reference count for batched event contexts.

Important behavior:
- Pools are bounded; if a pool is full on push, the object is freed.
- Pop functions zero or reset metadata before returning objects.
- Extra event-result pools zero only the fixed header, leaving variable buffer memory uncleared unless the caller requested direct allocation clearing.
- `PushIoBatchBuffer()` decrements `EventContextBatchCount` and only returns/frees the batch once the count reaches zero.
- `PopDirectoryList()` returns a vector sized for `WIN32_FIND_DATAW` and clears its item count.

Dependencies:
- Uses `DOKAN_VECTOR` as the backing storage for pointer pools.
- Uses Windows critical sections and threadpool APIs.
- Depends on size macros from `dokan_pool.h` and protocol constants from Dokan headers.

Notable risks:
- `InitializePool()` does not unwind partially initialized resources if a vector allocation fails.
- Cleanup assumes all global pool vectors are non-null.
- `PopIoBatchBuffer()` allocates `DOKAN_IO_BATCH_SIZE`, while `FreeIoBatchBuffer()` simply frees; callers that allocate non-pool large batches must set `PoolAllocated` correctly.
- Open-info reuse depends on `CleanupFileOpenInfo()` clearing directory cache and search pattern every time.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/dokan_pool.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/dokan_pool.h -->
# File Research: sources/windows/dokany/dokan/dokan_pool.h

Internal header for Dokan global thread pool and reusable object-buffer pools.

Key responsibilities:
- Defines event pull timeout and main pull thread count bounds.
- Defines batch event context sizing and `DOKAN_IO_BATCH_SIZE`.
- Defines default extra event result sizes for 16K, 32K, 64K, and 128K buffers.
- Declares thread-pool lifecycle functions `GetThreadPool`, `InitializePool`, and `CleanupPool`.
- Declares pop/push/free APIs for IO batch buffers, IO event buffers, event result buffers, open-info objects, and directory-list vectors.

Important behavior:
- `BATCH_EVENT_CONTEXT_SIZE` is four times `EVENT_CONTEXT_MAX_SIZE`, allowing the driver to return multiple event contexts per pull.
- Extra result sizes are expressed as `FIELD_OFFSET(EVENT_INFORMATION, Buffer) + payload_size`, matching variable-sized reply buffers.

Dependencies:
- Includes `dokani.h`, so this internal pool API sees all core Dokan runtime types.

Notable risks:
- The header exposes pool ownership conventions only by function naming; callers must know whether a returned object came from a pool and whether direct freeing is allowed.
- Size constants must remain synchronized with driver protocol maximums and `CreateDispatchCommon()` selection logic.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/dokan_pool.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/dokan_vector.c -->
# File Research: sources/windows/dokany/dokan/dokan_vector.c

Small generic dynamically-sized vector used by Dokan object pools and directory enumeration.

Key responsibilities:
- Allocates vectors with default capacity or explicit capacity.
- Frees vector items and, unless marked stack-allocated, the vector object itself.
- Supports push-front, push-front-array, push-back, push-back-array, pop-back, pop-back-array, clear, indexed lookup, last-item lookup, count, capacity, and item-size queries.
- Grows backing storage by doubling or by at least twice the requested minimum increase.

Important behavior:
- Default capacity is 128 items.
- `AllocWithCapacity(..., 0)` creates a vector with no backing allocation until it grows.
- Push-front shifts existing entries with `memmove_s`; push-back appends with `memcpy_s`.
- Pop and get functions assert their preconditions but include limited runtime fallback behavior.
- `DokanVector_Grow()` handles a zero-capacity vector and otherwise reallocates.

Dependencies:
- Includes `dokani.h` for debug printing and Windows types.
- Uses CRT allocation and secure copy/move functions.

Notable risks:
- Capacity checks use `ItemCount + Count >= MaxItems`, so a full vector grows before using the final slot; this wastes one slot but avoids boundary ambiguity.
- Multiplication for allocation sizes is not checked for overflow.
- `DokanVector_Grow(Vector, 0)` on a nonzero full vector relies on normal doubling; zero-capacity with nonzero minimum skips the first special case and still reaches default capacity.
- `IsStackAllocated` is supported in `Free()` but no initializer for stack-allocated vectors appears in this file.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/dokan_vector.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/dokan_vector.h -->
# File Research: sources/windows/dokany/dokan/dokan_vector.h

Internal generic vector API declaration for Dokan C code.

Key responsibilities:
- Defines `DOKAN_VECTOR` with raw item storage, item count, item size, capacity, and stack-allocation flag.
- Declares allocation, free, push, pop, clear, access, count, capacity, and item-size functions.

Important behavior:
- The API stores items by value in contiguous memory; callers pass pointers to item data for copying.
- The same vector type is used both for pointer pools and concrete `WIN32_FIND_DATAW` directory entries.

Dependencies:
- Relies on Windows-style types (`PVOID`, `BOOL`, `VOID`) already available through includers; the header itself does not include Windows headers.

Notable risks:
- Because this is a raw byte-vector API, type safety depends entirely on consistent `ItemSize` use by callers.
- The public struct fields make it possible for callers to mutate invariants directly.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/dokan_vector.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/dokanc.h -->
# File Research: sources/windows/dokany/dokan/dokanc.h

Internal/public control header for Dokan service, debug logging, driver control, and installation helper APIs.

Key responsibilities:
- Defines global device and driver service names using `DOKAN_MAJOR_API_VERSION`.
- Defines service operation constants for start, stop, and delete.
- Declares global debug flags `g_DebugMode` and `g_UseStdErr`.
- Implements static debug print helpers for narrow and wide strings using stack allocation and secure formatting.
- Defines `DbgPrint` and `DbgPrintW` macros for MSVC and GCC builds.
- Defines local `NT_SUCCESS` macro.
- Declares APIs for stderr/debug mode toggles, service install/delete, network provider install/uninstall, driver debug mode changes, and stale mount point cleanup.

Important behavior:
- Debug output goes either to `stderr` or `OutputDebugString[A/W]`.
- `DOKAN_OPTION_STDERR` can force debug output through stderr at runtime in `dokan.c`.
- Formatting failure falls back to outputting the format string.

Dependencies:
- Includes `dokan.h` and `<malloc.h>`.
- Uses `_vscprintf`, `_vscwprintf`, `_malloca`, `_freea`, `OutputDebugString`, and CRT output functions.

Notable risks:
- The debug helpers call `va_start` once and then use the same `va_list` for both sizing and formatting; portable C normally requires `va_copy` or reinitialization after a sizing pass.
- Debug macros depend on compiler-specific variadic macro handling.
- The local `NT_SUCCESS` macro can conflict with other definitions if include ordering changes.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/dokanc.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/dokani.h -->
# File Research: sources/windows/dokany/dokan/dokani.h

Main internal Dokan runtime header defining mount instances, open contexts, batched IO buffers, per-event state, and dispatcher/helper prototypes.

Key responsibilities:
- Includes Windows, standard IO, public Dokan API, debug/control header, list helpers, and vector API.
- Defines `DOKAN_INSTANCE_THREADINFO` for per-instance threadpool association.
- Defines `DOKAN_INSTANCE`, the mount-level runtime object holding device names, mount point, UNC name, IDs, options, callbacks, device handles, threadpool cleanup state, notify/keepalive handles, stop flag, and unmount callback guard.
- Defines `DOKAN_OPEN_INFO`, the per-open object carrying directory cache, search pattern, user context, event ID, directory flag, open count, delayed close data, and original event context.
- Defines `DOKAN_IO_BATCH`, the shared buffer returned from driver event pulls, including batch byte count, main-pull flag, pool ownership, event-context refcount, and flexible event context storage.
- Defines `DOKAN_IO_EVENT`, the per-dispatched operation state linking mount instance, optional open info, event result buffer, pool ownership, file info, event context, and owning batch.
- Defines `IOEVENT_RESULT_BUFFER_SIZE()`.
- Declares internal lifecycle, mount, device, dispatch, completion, name normalization, open-info release, and unmounted notification helpers.

Important behavior:
- `DOKAN_IO_EVENT.EventContext` is owned by its `DOKAN_IO_BATCH`, not by the event itself.
- `DOKAN_OPEN_INFO` owns cached directory enumeration state and must survive across related operations until close.
- Some events, notably close, intentionally have no `EventResult`.
- Batch lifetime is tied to `EventContextBatchCount`.

Dependencies:
- Internal structs depend directly on driver protocol structs such as `EVENT_CONTEXT` and `EVENT_INFORMATION`.
- Exposes dispatcher prototypes implemented in multiple C files in this group and adjacent Dokan files.

Notable risks:
- Raw pointer contexts are exchanged with the kernel via `EVENT_INFORMATION.Context`; this is inherently process-local and requires matching driver/user assumptions.
- Lifetime coupling between `DOKAN_IO_EVENT`, `DOKAN_IO_BATCH`, and `DOKAN_OPEN_INFO` is subtle and must be maintained by every dispatcher.
- The header centralizes many internal APIs, so unrelated modules can easily depend on implementation details.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/dokani.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/fileinfo.c -->
# File Research: sources/windows/dokany/dokan/fileinfo.c

Query-information dispatcher and conversion helpers for file metadata and alternate stream enumeration.

Key responsibilities:
- Converts `BY_HANDLE_FILE_INFORMATION` into NT file information structures:
  - `FILE_BASIC_INFORMATION`
  - `FILE_STANDARD_INFORMATION`
  - `FILE_POSITION_INFORMATION`
  - `FILE_INTERNAL_INFORMATION`
  - `FILE_ALL_INFORMATION`
  - `FILE_NAME_INFORMATION`
  - `FILE_ATTRIBUTE_TAG_INFORMATION`
  - `FILE_NETWORK_OPEN_INFORMATION`
  - `FILE_ID_INFORMATION`
- Aligns allocation size with Dokan volume options.
- Implements `DokanFillFindStreamData()` to append `FILE_STREAM_INFORMATION` entries from user `WIN32_FIND_STREAM_DATA`.
- Implements `DokanEndDispatchGetFileInformation()` to select the requested file information class and complete the event.
- Implements `DokanEndDispatchFindStreams()` to finalize stream entry offsets and validate buffer size.
- Implements `DispatchQueryInformation()` for `IRP_MJ_QUERY_INFORMATION`, including special handling for `FileStreamInformation`.

Important behavior:
- Unsupported classes such as alternate name and compression return `STATUS_NOT_IMPLEMENTED`; unknown classes return `STATUS_INVALID_PARAMETER`.
- `FileEaInformation` is treated as success with an empty EA size.
- `FileNameInformation` and `FileNormalizedNameInformation` copy the name from the driver event context.
- `FileStreamInformation` is dispatched to `FindStreams` instead of `GetFileInformation`.
- Event result `BufferLength` is computed from the requested buffer length minus remaining space.

Dependencies:
- Uses `DOKAN_OPERATIONS.GetFileInformation` and optionally `FindStreams`.
- Uses `CreateDispatchCommon()` and `EventCompletion()` from `dokan.c`.
- Uses `ALIGN_ALLOCATION_SIZE()` and `IOEVENT_RESULT_BUFFER_SIZE()`.
- Depends on Windows NT information structure layouts and stream alignment requirements.

Notable risks:
- If user `GetFileInformation` fails, this code maps the result to `STATUS_INVALID_PARAMETER` instead of preserving the original status.
- `DokanFillFindStreamData()` uses the current buffer tail and `NextEntryOffset` protocol carefully; malformed internal state would corrupt stream enumeration.
- `DokanEndDispatchFindStreams()` assumes there is at least a `FILE_STREAM_INFORMATION` entry in the result buffer when finalizing offsets.
- Buffer overflow handling is present, but several helper calls inside `DokanFillFileAllInfo()` ignore intermediate status because a full `FILE_ALL_INFORMATION` size check is done first.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/fileinfo.c -->