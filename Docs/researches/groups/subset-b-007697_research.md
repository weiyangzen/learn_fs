# subset-b-007697 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/internal.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/internal.cpp

## Purpose
`internal.cpp` provides shared process-local support for the Win32 `afsclass` library: a lazy global critical section, time and restart-time conversions, recurring schedule parsing/formatting, path splitting, address conversion, refresh-domain state, worker initialization, and Kerberos-style user name construction.

## Important APIs, types, and functions
The synchronization surface is `AfsClass_InitCriticalSection`, `AfsClass_GetCriticalSection`, `AfsClass_Enter`, `AfsClass_Leave`, and `AfsClass_GetEnterCount`. With `LOCAL_CRITSEC_COUNT` enabled it tracks recursion count and owning thread separately in `cs_EnterCount` and `cs_ThreadID`.

Time helpers include `AfsClass_UnixTimeToSystemTime`, `AfsClass_SystemTimeToUnixTime`, `AfsClass_ElapsedTimeToSeconds`, `AfsClass_FileTimeToDouble`, `AfsClass_ParseRecurringTime`, `AfsClass_FormatRecurringTime`, `AfsClass_SystemTimeToRestartTime`, and `AfsClass_RestartTimeToSystemTime`.

Utility APIs include `AfsClass_SplitFilename`, `AfsClass_IntToAddress`, `AfsClass_AddressToInt`, `AfsClass_SpecifyRefreshDomain`, `AfsClass_Initialize`, `AfsClass_RequestLongServerNames`, and `AfsClass_GenFullUserName`.

## Control flow
Initialization is lazy. Any caller entering or retrieving the class lock calls `AfsClass_InitCriticalSection`, which allocates and initializes `pcs` once. `AfsClass_Enter` increments the local recursion counter after entering the Win32 critical section; `AfsClass_Leave` validates the local owner/count with `ASSERT` before leaving.

Unix time conversion builds a Windows `FILETIME`-compatible 100 ns interval count by multiplying seconds and adding the 1601-to-1970 epoch offset, then converts to `SYSTEMTIME`. The reverse path calls `SystemTimeToFileTime`, subtracts the same offset, divides by 10,000,000, and returns a 32-bit `ULONG`.

Recurring-time parsing recognizes `never`, optional leading `at`, optional three-letter weekday, first numeric hour, second numeric minute, and an `a`/`p` marker anywhere later in the string. Formatting emits either `never`, `H:MM am/pm`, or `day H:MM am/pm`. BOS restart conversions map these `SYSTEMTIME` fields to `bos_RestartTime_t` masks.

## State and persistence behavior
All state is process-local and in-memory. `pcs`, `cs_EnterCount`, `cs_ThreadID`, `cRefreshAllReq`, `fLongServerNames`, and `dwWant` are globals used by the wider `afsclass` code. No file or registry state is persisted here. Restart-time and recurring-time helpers transform caller-provided structures but do not store schedules themselves.

## Dependencies and integration points
The file depends on WinSock/Win32 types, `afsclass.h`, `internal.h`, BOS restart types, and `worker.h` through `internal.h`. `AfsClass_Initialize` delegates runtime admin-library setup to `Worker_Initialize`. Address helpers translate between AFS integer server addresses and `SOCKADDR_IN`. Restart helpers integrate UI schedule text with BOS admin restart APIs.

## Risks and edge cases
The global critical section is never deleted and lazy initialization is not protected against two racing first callers. The local recursion tracker only stores one owning thread ID, so it is diagnostic rather than a general ownership model. Several string operations (`lstrcpy`, `wsprintf`, copying parsed components into fixed buffers) assume sufficiently sized caller buffers and trusted input. `AfsClass_SystemTimeToUnixTime` returns a 32-bit value and treats year 1970 as zero, which conflates the epoch with failure or "unset" semantics. `AfsClass_ParseRecurringTime` is permissive and can parse malformed strings into zero hour/minute values.

## Test signals
Useful tests include lock enter/leave recursion on one thread and failed leave from a non-owner in debug builds; Unix/SYSTEMTIME round trips for zero, current time, and post-2038 boundaries; recurring-time parse/format cases for `never`, daily, weekly, AM/PM noon/midnight, and malformed text; BOS restart mask conversions for disabled, daily, and weekly schedules; path splitting for no separator, slash, backslash, and root-like paths; and address int/socket round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/internal.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/internal.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/internal.h

## Purpose
`internal.h` is the private header tying `afsclass` implementation files to the worker dispatch layer and common internal utilities. It exposes allocation growth constants, shared globals, and helper prototypes used by class objects that manage servers, services, aggregates, filesets, and BOS restart schedules.

## Important APIs, types, and functions
The header defines growth increments `cREALLOC_SERVERS`, `cREALLOC_SERVICES`, `cREALLOC_AGGREGATES`, and `cREALLOC_FILESETS`. It declares the globals `cRefreshAllReq`, `fLongServerNames`, and `dwWant`. It exposes `AfsClass_GetCriticalSection`, time helpers, recurring-time helpers, `AfsClass_FileTimeToDouble`, `AfsClass_SplitFilename`, BOS restart conversion helpers, and `AfsClass_GenFullUserName`.

## Control flow
There is no executable control flow in the header. It enforces include ordering by including `worker.h`, making the private helper layer aware of all worker task and packet definitions. Implementation files include this header to reach the shared lock and helper conversions before calling admin DLL wrappers.

## State and persistence behavior
The header declares process-global state that is defined in `internal.cpp`. These globals are not persisted directly; they coordinate in-memory refresh behavior, display/name preferences, and refresh-domain selection for the `afsclass` process.

## Dependencies and integration points
`internal.h` depends on `worker.h`, which pulls in the AFS admin client, vos, bos, kas, pts, and utility admin headers. That makes this header an integration point between higher-level C++ class code and C-style AFS admin APIs. The BOS restart prototypes require `bos_RestartTime_t` and related masks from the admin headers.

## Risks and edge cases
Any file including `internal.h` inherits the large `worker.h` dependency surface and its Windows/AFS type requirements, increasing rebuild coupling. The fixed reallocation constants encode growth policy globally and may be inefficient for unusually large cells. Since globals are externally mutable, refresh and display behavior can change from any implementation file that includes this header.

## Test signals
Build tests should compile all `afsclass` users with this header under the supported Windows toolchain. Integration tests should verify that server/service/aggregate/fileset collections grow correctly at the declared increments and that callers see consistent `dwWant`, `fLongServerNames`, and `cRefreshAllReq` behavior across translation units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/worker.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/worker.cpp

## Purpose
`worker.cpp` implements the `afsclass` worker dispatch bridge. It dynamically loads the OpenAFS Windows admin DLLs, resolves their exported C APIs, initializes the client admin library, and exposes a single typed dispatcher, `Worker_DoTask`, that converts `WORKERTASK`/`WORKERPACKET` requests into vos, bos, kas, pts, client, and util admin calls.

## Important APIs, types, and functions
The public entry points are `Worker_Initialize` and `Worker_DoTask`. Internal functions are `Worker_LoadLibraries`, `Worker_FreeLibraries`, and `Worker_PerformTask`. Static DLL handles track `AfsVosAdmin.dll`, `AfsBosAdmin.dll`, `AfsKasAdmin.dll`, `AfsPtsAdmin.dll`, `AfsAdminUtil.dll`, and `AfsClientAdmin.dll`.

The file defines many function-pointer typedefs and static function pointers for vos volume/VLDB/server operations, bos server/process/key/log/salvage operations, kas principal/key operations, pts user/group operations, afsclient cell/server/token operations, and util database-server enumeration.

## Control flow
`Worker_DoTask` first calls `Worker_Initialize`, then wraps `Worker_PerformTask` in a catch-all C++ exception handler and reports `ERROR_UNEXP_NET_ERR` on unexpected exceptions. `Worker_Initialize` is a one-time gate around `Worker_LoadLibraries`.

`Worker_LoadLibraries` loads all required admin DLLs, resolves each required symbol with `GetProcAddress`, validates that no required pointer is null, and calls `afsclient_Init`. Loading is all-or-fail, but partial load failures return immediately without invoking `Worker_FreeLibraries`.

`Worker_PerformTask` is a large switch. Most cases map one `WORKERTASK` to one admin function call. The wrapper also converts `TCHAR` strings to ANSI and back, maps sentinel values such as `NO_PARTITION` and `NO_VOLUME` to null optional pointers, translates service/process/auth/salvage enum values, converts Unix time to/from `SYSTEMTIME`, copies encryption keys, transforms socket addresses, grows BOS log buffers until large enough, and normalizes success to status zero.

## State and persistence behavior
Worker state is process-local: DLL `HINSTANCE` handles, resolved function pointers, and the static `fInitialized` flag. The worker itself does not persist configuration. The admin calls it invokes can mutate AFS cell/server state, including volumes, VLDB entries, BOS process definitions, keys, users, groups, server host lists, executable files, authentication requirements, and salvage state.

## Dependencies and integration points
This file is the central dynamic-binding point for OpenAFS Windows admin libraries. It depends on Win32 dynamic loading, `afsclass.h`, `internal.h`, `vlserver.h`, and the admin C APIs represented in `worker.h`. It integrates UI/class-level `TCHAR` data with ANSI admin APIs and returns AFS or Win32 status codes to higher-level callers through `pStatus`.

## Risks and edge cases
The switch has a very large manual mapping surface; adding or changing a worker task requires synchronized edits in the enum, packet union, typedefs, static pointers, symbol resolution, null validation, and dispatch case. Many output buffers are caller-owned with implicit size assumptions. Some fixed temporary buffers are small for modern names or command parameters. Partial DLL-load failures leave previously loaded DLLs resident. `fInitialized` is not synchronized, so concurrent first use can race. Catch-all exception handling prevents crashes but can hide the failing task and cleanup context. Security-sensitive operations expose key, principal, BOS command, and salvage actions through a generic dispatcher, so packet correctness and caller authorization are critical.

## Test signals
Tests should cover DLL-missing and symbol-missing initialization failures, successful symbol resolution, `afsclient_Init` failure propagation, task dispatch status propagation, ANSI/TCHAR round trips, `NO_PARTITION`/`NO_VOLUME` optional pointer behavior, BOS service state/type conversions, restart-time conversions, BOS log dynamic buffer growth, address conversions, and representative vos/bos/kas/pts/client enumeration begin/next/done lifecycles. Fault-injection tests around admin call failure should assert output handles are nulled where the code promises that behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/worker.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/worker.h -->
# sources/distributed-fs/openafs/src/WINNT/afsclass/worker.h

## Purpose
`worker.h` defines the typed request contract for the `afsclass` worker dispatcher. It enumerates every supported admin operation as a `WORKERTASK`, describes the corresponding input/output packet shape in `WORKERPACKET`, and declares the worker initialization and execution APIs.

## Important APIs, types, and functions
The key constants are `NO_PARTITION` and `NO_VOLUME`, used as sentinels for optional partition/volume parameters. `WORKERTASK` enumerates vos backup, partition, server, VLDB, volume, and quota tasks; bos server, process, admin, key, cell, host, executable, log, auth, command, and salvage tasks; kas server/principal/key tasks; pts group/user/membership tasks; client token/cell/server tasks; and util database-server enumeration tasks.

`WORKERPACKET` is a large union whose member structs are named after tasks and annotate `[in]`, `[out]`, or `[in out]` fields. Public functions are `Worker_Initialize` and `Worker_DoTask`.

## Control flow
The header encodes a synchronous request/response pattern: caller fills the union member matching the selected `WORKERTASK`, calls `Worker_DoTask`, then reads status and any output fields. Enumeration tasks follow explicit begin/next/done token lifecycles. Open/close tasks expose server, cell, and credentials handles as opaque `PVOID` tokens.

## State and persistence behavior
The header does not allocate state itself. It defines packet fields that can carry handles to long-lived admin objects and fields for persistent AFS mutations: volume creation/deletion/move/release, VLDB lock/site changes, BOS process/key/cell/host/executable/auth changes, kas principal changes, and pts user/group changes.

## Dependencies and integration points
The header includes AFS admin headers for vos, bos, kas, pts, client, util, protection errors, and Kerberos admin error constants. It bridges Windows C++ callers using `LPTSTR`, `SOCKADDR_IN`, `SYSTEMTIME`, `BOOL`, and OpenAFS admin structures such as `vos_partitionEntry_t`, `vos_vldbEntry_t`, `bos_RestartTime_t`, `kas_principalEntry_t`, `pts_GroupEntry_t`, and `afs_serverEntry_t`.

## Risks and edge cases
The union contract is not type-safe at runtime: passing a task with the wrong active packet member will reinterpret memory. Many string output fields are raw `LPTSTR` buffers with sizes implied by the caller rather than encoded in the type. Opaque `PVOID` handles require strict open/close/enumeration discipline. The enum and union must remain in exact sync with `worker.cpp`; the `ADD HERE` comments show the intended extension points but do not enforce completeness.

## Test signals
Compile-time tests should catch ABI drift with the admin headers. Runtime tests should exercise one task from each family, verify begin/next/done cleanup, assert sentinel handling for optional values, and validate that output buffers are populated or cleared consistently. Static analysis should flag switch coverage in `worker.cpp` whenever a `WORKERTASK` value is added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsclass/worker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afscpcc.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afscpcc.c

## Purpose
`afscpcc.c` is a small Windows command-line helper that copies an AFS file credential cache into the default Kerberos credential cache using the KFW integration library.

## Important APIs, types, and functions
The only function is `main`. It calls `KFW_initialize` and then `KFW_AFS_copy_file_cache_to_default_cache(argv[1])`. It includes `windows.h` and `afskfw.h` in addition to OpenAFS configuration headers.

## Control flow
The program expects exactly one argument. If `argc != 2`, it exits with status `1`. Otherwise it initializes the Kerberos for Windows layer and returns the result of copying the named file cache to the default cache.

## State and persistence behavior
The helper does not maintain its own state. It reads a credential cache path from the command line and mutates the user's default Kerberos cache through KFW. The persistence behavior is delegated entirely to `KFW_AFS_copy_file_cache_to_default_cache`.

## Dependencies and integration points
This utility integrates OpenAFS credential handling with Kerberos for Windows. It relies on KFW being installed and configured and on the caller passing a valid cache file path.

## Risks and edge cases
Argument validation is minimal. There is no diagnostic output for wrong usage, KFW initialization failure, invalid cache path, permission failure, or copy failure. The return code comes directly from KFW copy behavior, so callers must know that convention.

## Test signals
Tests should run the helper with zero, one, and multiple arguments; with a valid temporary cache file; with a missing or unreadable cache file; and in an environment where KFW initialization fails. Expected signals are process exit codes and changes to the default credential cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afscpcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsd.c

## Purpose
`afsd.c` is the Win32 GUI-style entry point and minimal window host for the OpenAFS Windows cache manager process. It sets panic handling, initializes the hidden AFSD window class/instance, starts core AFS client subsystems, and runs the Windows message loop.

## Important APIs, types, and functions
Important globals include `main_inst`, `main_wnd`, `main_statusText`, `main_rect`, `afsd_logp`, `hAFSDWorkerThread`, `DoTerminate`, and `WaitToTerminate`. Functions are `afsd_notifier`, `WinMain`, `InitClass`, `InitInstance`, and `MainWndProc`.

`afsd_notifier` is registered with `osi_InitPanic`. `WinMain` installs the unhandled exception filter, enables debug allocation behavior in debug builds, registers/creates the window, and dispatches messages. `InitInstance` calls `afsi_start`, `afsd_InitCM`, `afsd_InitDaemons`, and `afsd_InitSMB`.

## Control flow
Startup enters `WinMain`, configures debug behavior when `_DEBUG` is defined, registers the `AFSDWinClass` window class, creates the main window, computes text metrics for a status rectangle, installs `afsd_notifier`, starts lower-level subsystems, initializes the cache manager, daemon threads, and SMB interface, then shows the window minimized without activation. The main loop runs until `PostQuitMessage`.

The window procedure blocks attempts to open the window via `WM_QUERYOPEN`, delegates commands to the default window procedure, clears paint invalidation on `WM_PAINT`, and on `WM_DESTROY` stops RPC server listening and posts quit.

## State and persistence behavior
This file initializes process-global runtime state but does not directly write persistent configuration. Downstream initialization functions read configuration and initialize cache, daemon, SMB, and RPC state. Panic handling forces AFSD and buffer traces before process exit, making diagnostic state visible through the tracing subsystem.

## Dependencies and integration points
The file depends on Win32 windowing, RPC management, the OSI layer, AFSD initialization headers, SMB initialization, tracing (`afsd_ForceTrace`, `buf_ForceTrace`), and many globals declared in `afsd.h`. It is the UI-subsystem entry point for the Windows cache manager and coordinates with service-oriented pieces in adjacent files.

## Risks and edge cases
Panic handling displays a modal message box and exits the process, which is useful interactively but risky in service or unattended contexts. `sprintf` into fixed buffers assumes short file paths in panic text. Initialization failures call `osi_panic`, so partial subsystem startup cleanup depends on panic/exit behavior. The window is hidden/minimized and refuses open, so diagnostics through UI are intentionally minimal. Inline `_asm int 3h` is architecture/compiler-specific debug behavior.

## Test signals
Tests should verify startup success and failure paths for `afsd_InitCM`, `afsd_InitDaemons`, and `afsd_InitSMB`; message handling for `WM_QUERYOPEN`, `WM_PAINT`, and `WM_DESTROY`; panic notifier trace forcing; and debug command-line allocation break parsing in debug builds. Integration smoke tests should assert that cache manager, daemon, SMB/RDR, and RPC state are initialized as expected after `InitInstance`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsd.h

## Purpose
`afsd.h` is the central private include for the Windows AFSD cache manager executable. It collects subsystem headers, declares the GUI entry-point functions, exposes major AFSD globals, defines service names and hook symbols, and sets compile-time feature flags used by AFSD implementation files.

## Important APIs, types, and functions
The header declares `InitClass`, `InitInstance`, `MainWndProc`, `About`, `afs_exit`, and `afsi_log`. It defines service/event names `AFS_DAEMON_SERVICE_NAME` and `AFS_DAEMON_EVENT_NAME`, worker thread count `WORKER_THREADS`, hook DLL/function-name constants for `afsdhook.dll`, and `SERVICE_CONTROL_CUSTOM_DUMP`.

It exports many cache-manager globals: root volume/cell/fid/scache, mount-root strings, cache path, gateway/session flags, freelance root state, DNS/read-only/short-name/direct-IO settings, RX MTU, redirector/SMB state, virtual cache, and data verification settings.

## Control flow
The header does not execute code. It shapes compile-time behavior by defining flags such as `USE_BPLUS`, `DFS_SUPPORT`, `LOG_PACKET`, `LOCK_TESTING`, and by undefining `NOTSERVICE`. Its broad include list makes AFSD implementation files see cache manager, SMB, redirector, volume, directory, buffer, daemon, ioctl, performance, rawops, initialization, and event-log interfaces.

## State and persistence behavior
The extern globals declared here represent long-lived AFSD process state. Some mirror persistent configuration loaded elsewhere, such as cache path, mount root, DNS settings, redirector policy, and SMB/RDR enablement. The header itself stores nothing but centralizes access to mutable global runtime state.

## Dependencies and integration points
`afsd.h` is a high-coupling integration header. It includes Windows NetBIOS headers, OSI, VLDB/AFS protocol headers, protection server headers, and most AFSD cache-manager modules. It is included by event logging and flush-volume code to access service names and interface state.

## Risks and edge cases
Because this header includes many subsystems and declares many globals, changes can cause widespread rebuilds and hidden coupling. Compile-time flags in a common header can silently change behavior across unrelated modules. Global mutable state makes initialization order important and complicates tests. Hook function typedefs expose extension points that can affect startup, daemon, SMB, stopping, and stopped phases.

## Test signals
Build tests should compile representative AFSD modules after any header change. Integration tests should validate service/event names, hook loading expectations, worker thread count assumptions, and consistent visibility of SMB/RDR/cache-manager globals across modules. Static analysis should watch for unwanted dependency growth from adding includes here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_eventlog.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsd_eventlog.c

## Purpose
`afsd_eventlog.c` implements AFSD Windows Event Log registration and message reporting. It ensures the OpenAFS client event source exists in the registry, formats substitution strings for known message IDs, rate-limits duplicate events, and calls `ReportEvent`.

## Important APIs, types, and functions
Internal helpers are `GetServicePath` and `AddEventSource`; `GetServicePath` reads the service `ImagePath` but is not used by the active logging path. Public functions are `LogEventMessage` and `LogEvent`. `LogEventMessage` formats a system message for a Win32 error code and delegates to `LogEvent`.

`LogEvent` accepts an event type, message ID, and varargs whose expected shape depends on the message ID. It handles startup/running messages, flush-volume messages, SMB diagnostics, RX/server status messages, service stop/error messages, crypt status, and dirty-buffer shutdown messages.

## Control flow
Before each log attempt, `LogEvent` calls `AddEventSource`. That function lazily opens or creates the Application EventLog registry key and the AFSD source subkey, writes `EventMessageFile` as `afsd_service.exe`, and writes supported event types. It caches success/failure with static `bOnce` and `bRet`.

`LogEvent` registers the event source, builds up to eight substitution strings based on a switch over `dwEventID`, then uses a named mutex to compare the event with the last logged event. Consecutive duplicates with matching type, ID, argument count, and argument strings are suppressed for five seconds. Non-suppressed events are sent to `ReportEvent` and the source handle is deregistered.

## State and persistence behavior
Persistent state is written to `HKLM` under the Windows EventLog Application tree for the AFSD event source. Runtime state includes static cached event-source setup status and last-message fields used for duplicate suppression. The named mutex `AFSD Event Log Mutex` coordinates duplicate suppression across threads in the process and potentially across processes using the same name.

## Dependencies and integration points
The file depends on Windows registry and event-log APIs, `strsafe.h`, OpenAFS registry constants, AFSD service names from `afsd.h`, message IDs from `afsd_eventmessages.h`, and version/interface globals such as `AFSVersion`, `smb_Enabled`, and `RDR_Initialized`. It is used by AFSD service, flush-volume, SMB, RX, and shutdown paths that need Event Log diagnostics.

## Risks and edge cases
Creating or updating the event source requires registry permissions; failure causes logging to silently return. `EventMessageFile` is hard-coded to `afsd_service.exe` instead of using `GetServicePath`, so unusual install layouts may not resolve message text. Varargs are message-ID-dependent and unchecked by the compiler, so mismatched callers can corrupt formatting. Fixed 128-byte temporary strings may truncate large values. Duplicate suppression state is protected only around the comparison/update block; callers still pay setup/register cost. The update loop for `lpLastStrings` appears to use `i` as the loop variable while initializing `j`, so changed-argument copying should be reviewed carefully.

## Test signals
Tests should verify registry source creation with and without permissions, `ReportEvent` calls for each message-ID argument shape, system error formatting through `LogEventMessage`, startup/running substitution strings for SMB/RDR combinations, duplicate suppression within and after five seconds, and vararg formatting for server/RX/SMB/dirty-buffer messages. Installation tests should confirm that Event Viewer resolves messages from the configured message file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_eventlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_eventlog.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsd_eventlog.h

## Purpose
`afsd_eventlog.h` declares the AFSD event logging interface and includes generated event-message definitions used by callers throughout the Windows cache manager.

## Important APIs, types, and functions
The header includes `afsd_eventmessages.h` and declares `LogEventMessage(WORD wEventType, DWORD dwEventID, DWORD dwMessageID)` and `LogEvent(WORD wEventType, DWORD dwEventID, ...)`.

## Control flow
There is no runtime control flow in the header. Callers include it to get message IDs and invoke the varargs logging functions implemented in `afsd_eventlog.c`.

## State and persistence behavior
The header stores no state. It exposes APIs that can write persistent EventLog registry source configuration and runtime event records when called.

## Dependencies and integration points
This header ties AFSD modules to Windows event types and the message table generated in `afsd_eventmessages.h`. Any module logging AFSD startup, service, SMB, RX, flush-volume, or shutdown diagnostics depends on this interface.

## Risks and edge cases
`LogEvent` is varargs, so the header cannot enforce that callers pass the correct substitution arguments for each message ID. Missing or stale `afsd_eventmessages.h` definitions will break either compilation or Event Viewer message resolution.

## Test signals
Build tests should confirm that all modules include this header with the generated message header available. Static checks should verify that each `LogEvent` call passes the argument count/types expected by `afsd_eventlog.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_eventlog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_flushvol.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsd_flushvol.c

## Purpose
`afsd_flushvol.c` handles flushing AFS volumes in response to Windows power notifications such as hibernate/resume coordination. It runs a helper thread, impersonates the logged-in shell user, enumerates connected network resources, identifies AFS volume UNC paths, issues `VIOC_FLUSHVOLUME` pioctls, logs timing/failure events, and coordinates completion with the service main thread.

## Important APIs, types, and functions
The pioctl wrapper is `afsd_ServicePerformFlushVolumeCmd`. The main flush routine is `afsd_ServicePerformFlushVolumes`. Thread and service integration functions are `PowerNotificationThreadCreate`, `PowerNotificationThreadNotify`, `PowerNotificationThreadExit`, and `afsd_ServiceFlushVolumesThreadProc`.

Security/session helpers are `GetUserToken` and `ImpersonateClient`. Resource helpers are `CheckAndCloseHandle` and `LogTimingEvent`. Static globals `gThreadInfo` and `gThreadHandle` hold event/thread handles.

## Control flow
`PowerNotificationThreadCreate` creates three named events for power notification, main-thread resume, and termination, then starts `afsd_ServiceFlushVolumesThreadProc`. The thread waits on terminate and power events. On terminate, it reverts impersonation, closes event handles, and exits. On power event, it impersonates the logged-in shell user, calls `afsd_ServicePerformFlushVolumes`, resets the power event, and signals the resume event.

`PowerNotificationThreadNotify` signals the power event and waits for resume, bounded by `HardDeadtimeout * 1000`. `PowerNotificationThreadExit` signals terminate and waits for the thread.

The flush routine obtains the AFS share name via `smb_GetSharename`, determines the server prefix, opens a connected-resource enumeration with `WNetOpenEnum`, scans each `NETRESOURCE`, filters resources whose remote name matches the AFS share prefix but is not the root share itself, and calls `pioctl(..., VIOC_FLUSHVOLUME, ...)` for each volume. It logs per-volume timing on success, warning on failure, and total volume count/time at the end.

## State and persistence behavior
State is in-memory thread/event state plus the current impersonation token. The routine does not persist configuration. It can change cache-manager state by flushing cached volume data. EventLog entries are persisted through `LogEvent`. The thread uses named kernel objects, so names can collide with existing objects in the session/global namespace.

## Dependencies and integration points
The file depends on AFSD cache-manager state (`cm_noIPAddr`, `HardDeadtimeout`), SMB share naming (`smb_GetSharename`), Windows network resource enumeration (`WNetOpenEnum`, `WNetEnumResource`, `WNetCloseEnum`), shell/window-station APIs for token discovery, impersonation APIs, `pioctl`/`VIOC_FLUSHVOLUME`, `fs_utils.h`, `lanahelper.h`, and AFSD event logging. It is called from service power-notification paths outside this file.

## Risks and edge cases
`cm_noIPAddr == 0` short-circuits flushing with a comment indicating loopback-only handling; that condition should be verified against the variable's actual semantics. `WNetOpenEnum` failure leaks `lpNetResBuf` because the buffer is allocated before opening enumeration and not freed on that path. `ImpersonateClient` does not close `hUserToken` after `ImpersonateLoggedOnUser`, leaking a token handle on success and failure after token acquisition. The flush thread impersonates once and does not call `RevertToSelf` after each flush cycle, only on termination. `PowerNotificationThreadCreate` logs `eventName` on existing events without initializing the buffer. Named events can collide with stale or maliciously created objects. `CheckAndCloseHandle` nulls only its local copy, leaving globals unchanged. `GetTickCount` elapsed math ignores wraparound for long intervals. The thread closes handles that are also stored globally, creating possible stale-handle use if exit paths race.

## Test signals
Tests should cover share-name null/bad/root-only cases, WNet enumeration success/failure/no-more-items, filtering of AFS root share versus child volume paths, pioctl success/failure, total/per-volume event logs, timeout behavior in `PowerNotificationThreadNotify`, clean thread termination, token acquisition with and without shell desktop access, handle leak detection for token and enumeration error paths, and duplicate named-event collision behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_flushvol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_flushvol.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsd_flushvol.h

## Purpose
`afsd_flushvol.h` declares the AFSD power-notification volume-flush interface and the internal thread, impersonation, pioctl, and logging helpers used by `afsd_flushvol.c`.

## Important APIs, types, and functions
The header defines `FLUSHVOLTHREADINFO`, containing handles for the power-event, main-resume, and terminate events. Public functions are `PowerNotificationThreadCreate`, `PowerNotificationThreadNotify`, and `PowerNotificationThreadExit`.

It also declares file-local helpers as `static`: `afsd_ServicePerformFlushVolumeCmd`, `afsd_ServiceFlushVolumesThreadProc`, `CheckAndCloseHandle`, `GetUserToken`, `ImpersonateClient`, and `LogTimingEvent`.

## Control flow
There is no executable code in the header. It documents the thread lifecycle contract: create the notification thread, notify it when a power event requires flushing, and exit it during service shutdown.

## State and persistence behavior
The declared `FLUSHVOLTHREADINFO` carries kernel object handles that coordinate in-memory service/thread state. The public API can lead to cache flushes and EventLog writes, but the header itself does not persist anything.

## Dependencies and integration points
The header includes `Winnetwk.h` for network-resource enumeration types and `fs_utils.h` for pioctl-related definitions. It integrates AFSD service power handling with the flush implementation and Windows event/thread primitives.

## Risks and edge cases
Declaring implementation helpers as `static` in a header is unusual; each includer would get private declarations and could hide mismatches if definitions change. Public lifecycle functions have no explicit state object, so they rely on globals in `afsd_flushvol.c` and can be misordered by callers. The header exposes no timeout or error-detail reporting beyond Boolean success.

## Test signals
Build tests should ensure only the intended implementation includes the static helper declarations. Integration tests should call create/notify/exit in normal and repeated sequences, verify Boolean return behavior on timeout/failure, and check that handle lifecycle remains valid across service power events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsd_flushvol.h -->
