# Research: subset-b-007741

This grouped report covers the requested OpenAFS Windows OSI, eventlog, installer, loopback, WiX custom action, and KClient compatibility files. Each section is bounded by the required reconciliation markers and titled with the original source path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osibasel.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osibasel.h

Purpose: Declares the base Windows OSI mutex and read/write lock ABI used by the client-side OSI layer. It is the public contract for lock objects, lock-order validation references, core lock operations, sleep-while-unlocking helpers, initialization, finalization, conversion, and assertion macros.

Important APIs, types, and functions: `osi_mutex_t` represents either a built-in exclusive mutex (`type == 0`) or a dynamically dispatched mutex using `d.privateDatap`; its state includes `flags`, owner `tid`, waiter count, hierarchy `level`, and a turnstile. `osi_rwlock_t` tracks exclusive flag, reader count, waiter count, writer/read owner thread ids, hierarchy level, and either private data or turnstile. `osi_lock_ref_t` records per-thread lock-order references and uses `OSI_LOCK_MUTEX` / `OSI_LOCK_RW`. The header exports `lock_ObtainRead`, `lock_ObtainWrite`, `lock_ReleaseRead`, `lock_ReleaseWrite`, `lock_ObtainMutex`, `lock_ReleaseMutex`, try-lock calls, `osi_SleepR/W/M`, generic `osi_Sleep` / `osi_Wakeup`, lock finalizers, `lock_InitializeMutex`, `lock_InitializeRWLock`, conversion calls, state query calls, `osi_BaseInit`, and `osi_SetLockOrderValidation`.

Control flow and state: Callers initialize OSI once, initialize each lock with a name and hierarchy level, then use obtain/release operations. For type-zero locks the implementation uses critical sections, turnstiles, flags, waiter counts, and reader counts; for nonzero lock types the implementation dispatches through `osi_lockOps`. The assertion macros query state and owner thread id to validate expected lock ownership.

Persistence and dependencies: No persistent storage is declared here. The state is in caller-owned lock structs and in global arrays such as `osi_baseAtomicCS`. Dependencies are `windows.h`-style `DWORD`, `CRITICAL_SECTION`, `LONG_PTR`, `osi_turnstile_t`, `osi_queue_t`, `thrd_Current`, and `osi_assertx`, so this header is tightly coupled to `osisleep.h`, `osiqueue.h`, `osiltype.h`, and the aggregate `osi.h`.

Integration points: This is the central lock API consumed by OSI tests (`perf.c`, `trylock.c`), the sleep package, the stats lock type (`osistatl.c`), and higher client code using `osi.h`. Dynamic lock types such as `stat` must preserve the field layout assumptions documented here.

Risks: The lock structs expose internal fields, so consumers can corrupt invariants if they mutate them directly. `OSI_RWLOCK_THREADS` is a fixed-size thread-id history and can be incomplete for many readers. The assertion macros depend on accurate owner tracking, which is debug-oriented and may be partial. Cross-header type ordering must remain correct because the header names types declared elsewhere.

Test signals: Useful tests include basic lock obtain/release, reader/writer exclusion, try-lock behavior, sleep-while-unlocked behavior, dynamic lock type dispatch, owner assertion failures, and lock-order validation under nested mutex/rwlock use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osibasel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidb.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osidb.c

Purpose: Implements the server side of the OSI remote debugging RPC interface. It exposes ping, format lookup, logical fd open/read/close, and server initialization for local OSI diagnostic collections.

Important APIs, types, and functions: `osi_maxCalls` defaults to `OSI_MAXRPCCALLS`. `debugType` is the RPC object type UUID. `dbrpc_Ping` is a no-op health check. `dbrpc_GetFormat` looks up an `osi_fdType_t` and an `osi_fdTypeFormat_t` by name, region, and index. `dbrpc_Open` allocates a debug fd by type name and returns it in an `osi_remHyper_t`. `dbrpc_GetInfo` resolves the fd and calls its `GetInfo` op. `dbrpc_Close` closes and frees the fd. `osi_InitDebug` initializes OSI, fd support, RPC protocol sequences, interface registration, object UUID typing, endpoint registration, and optionally starts listening under `OSISTARTRPCSERVER`.

Control flow and state: RPC calls are thin dispatchers over the fd registry in `osifd.c`. Open creates a process-local 32-bit fd id and projects it into a 64-bit wire field. GetInfo initializes counts to zero before dispatching so failure paths do not leak stale data. Initialization is guarded by `osi_Once`; only the first successful caller performs RPC registration.

Persistence and dependencies: No disk persistence is used. Runtime state lives in the Microsoft RPC endpoint mapper, registered bindings, fd registries, and the exported object UUID. Dependencies include `windows.h`, `rpc.h`, generated `dbrpc.h`, OSI initialization, fd APIs, and `osi_uid_t` UUID values.

Integration points: Remote UI code in `osidebug.c` calls the generated `dbrpc_*` methods. Debuggable subsystems register fd types such as `type`, `sleep`, `lock`, and `log:<name>` with format descriptors. AFS service startup can call `osi_InitDebug` with an instance UUID so external tools can bind to a specific process.

Risks: `dbrpc_GetFormat` uses `strncpy` without explicit null termination if the source exactly fills the target. The fd number is only locally unique and stored in the low 32 bits. RPC registration errors abort initialization but there is no cleanup of earlier registration steps. The server exposes process diagnostics through RPC; endpoint exposure and ACL behavior are not visible in this file.

Test signals: Exercise `osi_InitDebug` idempotence, endpoint registration failure paths, opening unknown types (`OSI_DBRPC_NOFD` / `NOENTRY`), iterating known fd types, format EOF behavior, GetInfo count initialization, and Close on invalid fds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidb.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osidb.h

Purpose: Defines remote-debug data layouts for lock and sleep diagnostics plus the initialization entry point and RPC call count defaults.

Important APIs, types, and functions: `osi_remLockInfo_t` describes a remotely exported lock with type, address, reader/writer/waiter/owner state, and aggregate read/write lock and blocked timing counts. `osi_remSleepInfo_t` describes a blocked thread id and sleep value. `OSI_MAXRPCCALLS` reserves two RPC server calls. `osi_InitDebug` initializes the debug server. `osi_maxCalls` and `osi_maxCallsp` expose configuration hooks inside and outside OSI.

Control flow and state: This header is schema, not behavior. Implementations populate the structures from `osistatl.c` and `osisleep.c` fd iterators. Clients interpret integer arrays and string arrays defined in the generated RPC types alongside these named structures.

Persistence and dependencies: No persistence. It depends on OSI scalar types such as `LONG_PTR`, `thread_t`, and `osi_uid_t`, and on the generated debug RPC transport contract.

Integration points: Included by OSI remote-debug server/client code and any external diagnostic tool that wants to interpret lock and sleep records.

Risks: The structure comments and the fd iterator fields must stay consistent; otherwise remote tools can mislabel statistics. Timing is stored in `long` milliseconds and may overflow on long-lived processes. `owner` is explicitly incomplete for multiple readers.

Test signals: Validate ABI sizes across 32/64-bit builds, ensure `OSI_MAXRPCCALLS` can be overridden where expected, and compare generated RPC data against these structures for lock and sleep reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidebug.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osidebug.c

Purpose: Implements a Win32 GUI application for browsing OSI remote-debug collections exposed by the `dbrpc` RPC server. It connects to a host/object id, lists available collection types, retrieves entries, formats them with server-provided labels, and optionally saves displayed results to a file.

Important APIs, types, and functions: `WinMain`, `InitApplication`, and `InitInstance` set up the window class and child controls. `main_Layout` computes button, name, type list, result list, and status rectangles. `main_GetBinding` composes an `ncacn_ip_tcp` RPC binding, sets a short communication timeout, and attaches an object UUID. `main_GetFormatCache` caches positive and negative format descriptors from `dbrpc_GetFormat`. `main_RetrieveType` opens a remote fd, repeatedly calls `dbrpc_GetInfo`, formats string and integer data by region/index metadata, and closes the fd. `MainWndProc` handles command buttons, list selection, resize, paint, save-to-file, and quit. `FileProc` and `About` are modal dialog procedures; `main_SetStatus` updates the status control.

Control flow and state: The user enters a value like `host:instance`, clicks "Debug Server", and the code parses the suffix as a long converted to a UUID with `osi_LongToUID`. It obtains a remote binding, fetches the `"type"` collection into the types list, and later fetches a selected collection into the results list. Format metadata is cached globally in `main_allFormatsp`, so repeated fields avoid extra RPC calls. Save-to-file enumerates listbox strings and writes newline-terminated records with `WriteFile`.

Persistence and dependencies: Persistent writes are limited to a user-selected output file. Runtime state is mostly global HWNDs, rectangles, format cache entries, a binding handle, and `main_fileName`. Dependencies include Win32 GUI APIs, Microsoft RPC APIs, generated `dbrpc` client stubs, `osiutils.c` UUID conversion, `osidebug.h` resource IDs, and remote server format contracts.

Integration points: This is the manual diagnostic client for `osidb.c`, `osifd.c`, `osilog.c`, `osisleep.c`, and `osistatl.c`. It expects fd type names and format descriptors registered by those packages.

Risks: Several functions use implicit `int` return style and old Win32 casts. String handling uses fixed buffers, `strcpy`, `strcat`, and `wsprintf`, so long host names, file names, or server-returned values can overflow. `main_RetrieveType` treats `code == 1` as negative-cache format absence, coupling to numeric RPC constants. The condition `if (index != LB_ERR || main_remoteHandle == NULL)` appears inverted for null-handle protection and could call RPC with no binding. The GUI assumes ANSI APIs and old help/dialog resources.

Test signals: Manual or UI automation should verify binding success/failure messages, type listing, selecting each built-in fd type, formatting hex/signed/unsigned fields, EOF handling, repeated retrieval with format cache, save-to-file content, and behavior for unreachable hosts or malformed `host:id` strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidebug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidebug.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osidebug.h

Purpose: Declares resource IDs, window procedure prototypes, remote-debug client format cache shape, and small compatibility macros for the OSI remote-debug GUI.

Important APIs, types, and functions: Button/control IDs include `IDM_CMD1` through `IDM_CMD4`, `IDM_NAME`, `IDM_TYPES`, `IDM_RESULTS`, and `IDM_STATUS`; dialog/menu IDs include `IDM_ABOUT`, `IDM_HELP`, `IDM_FILEBOX`, and `IDM_FILENAME`. `dbrpc_v1_0_c_ifspecp` accounts for exported RPC interface indirection. `main_formatCache_t` stores cached type/region/index label and format data. The header declares `InitApplication`, `InitInstance`, `MainWndProc`, `About`, `FileProc`, `main_SetStatus`, and the global `main_screenText`.

Control flow and state: The format cache supports `osidebug.c` by memoizing format lookups, including negative entries where `labelp == NULL`. UI resource IDs drive `WM_COMMAND` routing and dialog callbacks.

Persistence and dependencies: No persistence. Depends on Win32 `HWND`, `HANDLE`, `RPC_IF_HANDLE`, and the generated RPC client symbol. The `GET_WM_HSCROLL_*` macros preserve compatibility between Win32 and older Windows message packing.

Integration points: Tied directly to `osidebug.c`, resource scripts, and generated `dbrpc` client stubs.

Risks: The header exposes globals and old-style prototypes. Resource ID collisions would break message routing. The manual declaration of `dbrpc_v1_0_c_ifspecp` is linker-specific and brittle.

Test signals: Build/link the GUI against generated RPC stubs, verify resource IDs match `.rc` resources, and exercise dialog callbacks on both WIN32 macro paths where relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osifd.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osifd.c

Purpose: Implements an in-process file-descriptor abstraction used by OSI remote debugging. It lets subsystems register named diagnostic collections, open logical cursors, iterate records, close them, and advertise formatting metadata.

Important APIs, types, and functions: Globals include `osi_fdCS`, `osi_allFDs`, `osi_allFDTypes`, and monotonic `osi_nextFD`. `osi_TypeFDOps` implements the built-in `"type"` collection. `osi_FindFDType`, `osi_RegisterFDType`, and `osi_UnregisterFDType` manage type registrations. `osi_AddFDFormatInfo` attaches labels and formatting flags to type fields. `osi_InitFD` initializes the fd registry and registers `"type"`. `osi_AllocFD` creates an fd via a type's `Create` op and adds it to `osi_allFDs`. `osi_FindFD` resolves fd ids. `osi_CloseFD` unthreads and closes a descriptor. `osi_FDTypeCreate`, `osi_FDTypeGetInfo`, and `osi_FDTypeClose` implement iteration over registered type names.

Control flow and state: The registry is protected by a critical section for list and id mutations. Registering a type duplicates the name, stores the ops and owner rock, and pushes it on the type list. Opening an fd looks up the type by name, calls its create function, assigns a new id, and adds it to the live fd list. RPC callers then iterate records through the ops vector and close the fd.

Persistence and dependencies: No disk persistence. Runtime lists are process-global and allocated with `malloc`. Dependencies include `osiqueue` list operations, `dbrpc` data shapes, OSI thread critical-section wrappers, and the caller's fd op implementations.

Integration points: `osidb.c` exposes this registry over RPC. `osisleep.c`, `osistatl.c`, and `osilog.c` register `"sleep"`, `"lock"`, and `"log:<name>"` fd types. `osidebug.c` first opens `"type"` to discover available collections.

Risks: `osi_UnregisterFDType` returns without leaving `osi_fdCS` when the type is not found, which can deadlock future fd operations. `osi_FindFD` returns a live pointer after releasing the registry lock, so concurrent close could invalidate it if RPC calls race. Type iteration snapshots `osi_allFDTypes` without consistently holding the lock while reading the current pointer. Several functions lack explicit return types in K&R style. Duplicate type registration asserts instead of returning an error.

Test signals: Test duplicate registration, unregister missing type lock handling, fd open/close lifecycle, concurrent GetInfo/Close races, `"type"` iteration across registered dynamic types, and format metadata lookup including EOF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osifd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osifd.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osifd.h

Purpose: Declares the OSI diagnostic fd abstraction and the registration/iteration APIs used by remote-debug collections.

Important APIs, types, and functions: `osi_fdOps_t` contains `Create`, `GetInfo`, and `Close` callbacks. `osi_fd_t` is the common descriptor header with queue linkage, ops pointer, and numeric fd. `osi_typeFD_t` is the cursor for the built-in type iterator. `osi_fdTypeFormat_t` describes a field label, region, index, and formatting flags. `osi_fdType_t` stores a registered collection name, owner rock, operations, and format list. Public functions cover type lookup/registration/unregistration, adding format info, fd initialization, allocation, lookup, close, and built-in type fd ops.

Control flow and state: Collection owners register a type once, then fd clients open by name. The fd header must be the first member of concrete fd structs so generic code can cast.

Persistence and dependencies: No persistence. Depends on generated `dbrpc.h` for `osi_remGetInfoParms_t` and constants, and on `osiqueue.h` for intrusive list fields.

Integration points: This header is included by sleep, stat, log, and debug RPC modules. It is the common bridge between in-process diagnostics and RPC exposure.

Risks: Intrusive layout requirements are convention-based. Returned pointers are not ref-counted by the API. Format metadata ownership belongs to the registry and is freed only on unregister.

Test signals: Compile-time tests should ensure concrete fd structs start with `osi_fd_t`; runtime tests should register a mock type and verify create/get/close and format discovery through `osidb.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osifd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osilog.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osilog.c

Purpose: Implements OSI circular in-memory logging, debug-output mirroring, remote fd iteration of log records, Windows Event Log forwarding, trace option discovery, and helper string preservation for log parameters.

Important APIs, types, and functions: `osi_logSize` sets default entry count. `osi_LogCreate` initializes high-resolution timing, allocates an `osi_log_t`, registers a `log:<name>` fd type, and adds field format metadata. `osi_LogPanic` logs panic text to all enabled logs and disables them. `osi_LogReset`, `osi_LogFree`, `osi_LogEnable`, and `osi_LogDisable` manage logs. `osi_IntLogAdd` is the core append path; wrappers are `osi_LogAdd` and `osi_DebugAdd`. `osi_LogPrint` writes formatted records to a file handle. `osi_LogSaveString` and `osi_LogSaveStringW` store transient strings in a rotating string pool. `osi_LogFDCreate`, `osi_LogFDGetInfo`, and `osi_LogFDClose` implement remote iteration. `osi_InitTraceOption` reads `TraceOption` from the AFS client service registry key. `osi_LogEvent0` and `osi_LogEvent` emit information events when trace-to-event-log is enabled. `osi_HexifyString` returns a dotted lowercase hex representation of a byte string.

Control flow and state: Creation links the log into `osi_allLogsp`, allocates an entry ring and string ring, initializes a critical section, and registers the log as an fd type. Appending takes the log critical section, advances `nused` and `first` as a circular buffer, records thread id, timestamp, format pointer, and up to five parameters, then optionally writes to the debugger. Remote fd creation snapshots `first` and `nused`; GetInfo formats each captured record into string fields and exposes thread id as an integer.

Persistence and dependencies: The primary log is in memory only. `osi_LogPrint` persists to a caller-supplied handle, and event functions write to Windows Event Log source `TransarcAFSDaemon`. Trace configuration is read from `HKLM` via `AFSREG_CLT_SVC_PARAM_SUBKEY`. Dependencies include `strsafe.h`, `WINNT/afsreg.h`, high-resolution counter APIs, the fd registry, and thread wrappers.

Integration points: Lock stats can log blocking events through `osi_SetStatLog`. `osi_panic` calls `osi_LogPanic`. Remote debug clients retrieve `log:<name>` collections. Windows service configuration controls event/debug-log tracing.

Risks: `osi_LogFree` frees `namep` and `datap` but not `stringsp`, leaking the string pool. Registered `log:<name>` fd types are not unregistered on free. `osi_InitTraceOption` does not check `RegOpenKeyEx` before querying/closing and does not close the key. Format strings are stored by pointer, so callers must pass stable strings. `osi_HexifyString` allocates `len * 3` bytes, which is just enough for nonempty strings but allocates zero bytes for empty strings and leaves ownership to callers. High-resolution timestamp uses only `LowPart`, losing high bits.

Test signals: Test ring wraparound, disabled/enabled behavior, debug output path, string saving/truncation for ANSI and wide strings, fd snapshot iteration, panic disabling, registry trace option reads, Event Log emission, and memory-leak checks around create/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osilog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osilog.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osilog.h

Purpose: Declares the OSI logging data structures, fd cursor, logging functions, event helpers, debug macros, and convenience macros for 0-to-5 parameter log entries.

Important APIs, types, and functions: `osi_logEntry_t` stores thread id, microsecond timestamp, format pointer, and five `size_t` parameters. `osi_log_t` is a named circular log with queue linkage, counters, critical section, entry storage, rotating string storage, and enabled flag. `osi_logFD_t` snapshots a log for remote iteration. Exports include create/free/add/debug/reset/print/enable/disable, fd operations, panic logging, string saving, trace option init, event logging, and `osi_HexifyString`. `osi_Log0` through `osi_Log5` guard on enabled logs; `osi_Debug0` through `osi_Debug5` always call the debug path.

Control flow and state: Callers create a log, enable it, and use macros to append. String parameters that might not outlive the log call can be stored in the log string pool first. Remote debugging opens the log fd type registered by `osi_LogCreate`.

Persistence and dependencies: In-memory ring by default; printing and Event Log calls are implemented in `osilog.c`. The header depends on aggregate OSI headers for sleep, base locks, stats, fd, queue, and thread handle types.

Integration points: Used throughout Windows client code for debug traces and by stats/panic code for instrumentation. The `DEBUG_EVENT*` macros provide compile-time optional Event Log traces under `DEBUG_VERBOSE`.

Risks: The macro API casts all parameters to `size_t`, so pointer/integer formatting must match the format string and platform width. Debug macros do not check for null logs in the macro itself but the implementation does. `DEBUG_EVENT*` macros use fixed local buffers and `sprintf` under `DEBUG_VERBOSE`.

Test signals: Compile 32/64-bit format cases, verify macro parameter ordering, confirm disabled logs skip `osi_LogAdd`, and test `DEBUG_VERBOSE` builds for Event Log path correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osilog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiltype.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osiltype.c

Purpose: Implements the registry of dynamic OSI lock operation types, allowing alternate lock implementations such as statistics-gathering locks to be selected by name.

Important APIs, types, and functions: Globals are `osi_lockOps[OSI_NLOCKTYPES]`, `osi_lockOpNames[OSI_NLOCKTYPES]`, `osi_lockTypeIndex`, and `osi_lockTypeDefault`. `osi_LockTypeFind` returns a registered index by name. `osi_LockTypeAdd` installs an ops vector/name pair and returns the assigned index through `indexp`. `osi_LockTypeSetDefault` selects a named type or resets the default to base type 0.

Control flow and state: Types are appended from index 1 upward; index 0 is reserved for the built-in fast implementation. Lock initialization code can use `osi_lockTypeDefault` to decide whether to create a base lock or dispatching lock. There is no unregister path.

Persistence and dependencies: No persistence. State is process-global and initialized by static zeroing. It depends on `osi_lockOps_t` from `osiltype.h`, aggregate `osi.h`, and string comparison.

Integration points: `osistatl.c` registers the `"stat"` lock type through `osi_LockTypeAdd`, and base lock functions dispatch through `osi_lockOps` for nonzero lock types.

Risks: No synchronization protects the registry, so types should be registered during single-threaded initialization. Overflow silently returns without setting `indexp`. `osi_LockTypeSetDefault` has implicit return type in old C and silently ignores unknown names. Names are stored by pointer, not copied.

Test signals: Register mock ops, verify lookup and default selection, test overflow behavior at `OSI_NLOCKTYPES`, and ensure initialization order sets `"stat"` before selecting it as default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiltype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiltype.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osiltype.h

Purpose: Defines the dynamic lock operation vector ABI and state-bit constants returned by lock state query functions.

Important APIs, types, and functions: `OSI_NLOCKTYPES` limits dynamic lock types to 32. `osi_lockOps_t` includes operations for rwlock read/write obtain/release, mutex obtain/release, try operations, sleep with lock release, initialization/finalization, read/write conversions, and state queries. The header exports `osi_lockOps`, `osi_lockTypeDefault`, `osi_LockTypeAdd`, and `osi_LockTypeSetDefault`. State bits are `OSI_MUTEX_HELD`, `OSI_RWLOCK_READHELD`, and `OSI_RWLOCK_WRITEHELD`.

Control flow and state: Nonzero lock objects store a type index and private data pointer; lock API functions dispatch through the matching `osi_lockOps_t`.

Persistence and dependencies: No persistence. Depends on forward-declared `osi_rwlock` and `osi_mutex` shapes, `LONG_PTR`, and OSI lock structs from `osibasel.h`.

Integration points: Used by `osibasel.c` and `osistatl.c` to plug in instrumented lock behavior without changing callers.

Risks: Every ops vector must be complete and semantically compatible with the base lock API. The ABI assumes function signatures match exactly; missing or reordered fields would break dispatch.

Test signals: Compile-time coverage for all vector fields, runtime dispatch of each operation through a nonzero type, and state query compatibility with assertion macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiltype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiqueue.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osiqueue.c

Purpose: Implements a simple non-circular intrusive doubly linked queue and a pooled `osi_queueData_t` allocator.

Important APIs, types, and functions: `osi_QAdd` pushes to head with only a head pointer. `osi_QAddH` pushes to head and maintains a tail pointer. `osi_QAddT` appends to tail with head/tail maintenance. `osi_QRemove` removes from a head-only list. `osi_QRemoveHT` removes from a list with head and tail pointers. `osi_InitQueue` initializes allocator locking. `osi_QDAlloc` allocates one `osi_queueData_t`, bulk-allocating `OSI_NQDALLOC` entries when needed. `osi_QDFree` returns an entry to the free list.

Control flow and state: Queue operations manipulate caller-owned intrusive `nextp`/`prevp` fields and do not perform locking. The queue-data allocator is protected by `osi_qdcrit`; it bulk-allocates blocks and threads all but the returned entry onto `osi_QDFreeListp`.

Persistence and dependencies: No persistence. Allocated blocks are never globally freed, forming a process-lifetime pool. Dependencies include `malloc`, thread critical-section wrappers, and `osi_assertx`.

Integration points: Used heavily by fd registries, sleep hash buckets and turnstiles, stats lock lists, active-info lists, and lock-order references.

Risks: Queue operations assume the element is currently in the list on remove and not in another list on add. `osi_InitQueue` uses a plain static int without interlocked protection, so concurrent first calls could race. The allocator's pooled blocks are intentionally retained and not individually freed to the OS.

Test signals: Add/remove head, tail, single-element, middle-element cases; allocator/free-list reuse; assertion on stale `datap`; and concurrent allocator stress after explicit initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiqueue.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osiqueue.h

Purpose: Declares the intrusive queue node, one-pointer queue-data wrapper, queue APIs, allocator APIs, and small accessor macros.

Important APIs, types, and functions: `osi_queue_t` has `nextp` and `prevp`. `osi_queueData_t` embeds `osi_queue_t` plus `datap`. `OSI_NQDALLOC` sets bulk allocation size to 64. Exports cover add-head, add-tail, add-head-with-tail, remove, remove-with-tail, initialization, allocate, and free. Macros read/write data, next/prev pointers, and queue emptiness.

Control flow and state: Structures embedding `osi_queue_t` can be cast to queue nodes. The queue is null-terminated, not circular, making end checks simple.

Persistence and dependencies: No persistence and no external dependencies beyond C types. Implementations require OSI thread wrappers.

Integration points: Shared infrastructure across most OSI diagnostic and locking packages.

Risks: Intrusive queues require careful ownership; an element cannot safely belong to two lists using the same embedded node. Macros do no null checking.

Test signals: Unit-test list invariants after each operation and verify embedding/casting in representative OSI structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osisleep.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osisleep.c

Purpose: Implements OSI initialization, once-only initialization, sleep/wakeup primitives, lock turnstiles, sleep remote-debug fd iteration, panic hooks, time helpers, and prime/hash utilities for the Windows OSI layer.

Important APIs, types, and functions: `osi_Init` initializes boot time, TLS, fd registry, sleep hash critical sections, sleep-info allocation, sleep fd type, base locks, stat locks, and queues. `osi_AllocSleepInfo`, `osi_FreeSleepInfo`, and `osi_ReleaseSleepInfo` manage TLS-backed semaphore wait records with refcounts. `osi_Once`, `osi_TestOnce`, and `osi_EndOnce` implement spin-based one-time initialization. `osi_TWait`, `osi_TWaitExt`, `osi_TSignal`, `osi_TBroadcast`, and `osi_TSignalForMLs` implement turnstile waits and wakeups for locks. `osi_SleepSpin`, `osi_WakeupSpin`, `osi_Sleep`, and `osi_Wakeup` implement address-based sleeping. `osi_SleepFDCreate`, `osi_SleepFDGetInfo`, `osi_AdvanceSleepFD`, and `osi_SleepFDClose` expose sleepers to remote debugging. `osi_IsPrime`, `osi_PrimeLessThan`, `osi_GetBootTime`, `osi_InitPanic`, `osi_panic`, `osi_Time`, and `osi_GetTime` provide utility behavior.

Control flow and state: Each sleeping thread reuses a TLS `osi_sleepInfo_t` containing a semaphore. Address-based sleep hashes by sleep value, adds the record to a bucket under `osi_critSec[idx]`, releases the caller's critical section atomically with entering the wait, waits on the semaphore, then frees or marks the record. Wakeup scans the bucket and releases matching semaphores. Turnstiles maintain explicit FIFO/LIFO lists for lock waiters and can patch lock flags/read counts before releasing waiters. Sleep fd iteration holds refs on sleep records so remote-debug reads can safely traverse while sleepers exit.

Persistence and dependencies: No disk persistence. Runtime state includes TLS slot, sleep hash buckets, per-bucket critical sections, free list, boot time, and fd type registrations. Dependencies include Windows semaphores/TLS/critical sections, `osifd`, `osiqueue`, base locks, stats initialization, large integer helpers, and aggregate `osi_internal.h`.

Integration points: Base and stat lock implementations call turnstile and sleep helpers. `osidb.c` exposes the `"sleep"` fd type over RPC. `osi_panic` informs an optional callback and calls `osi_LogPanic`.

Risks: `osi_Once` sets `done = 1` before the initializer has finished and relies on `atomic` to block other callers until `osi_EndOnce`; initializers must always call `osi_EndOnce` or future callers spin forever. TLS values for deleted sleep infos are cleared only in some paths. Turnstile code patches lock state using raw `void *` casts and assumes caller lock layout. `osi_SleepFDGetInfo` assigns `LONG_PTR` sleep values into integer RPC slots that may be narrower depending on generated definitions. `DLLMain` is a stub. Time logic subtracts a magic high-date offset.

Test signals: Stress sleep/wakeup lost-wakeup prevention, wake-all semantics, turnstile writer/reader ordering, one-time initialization races, remote sleep iteration while sleepers exit, panic callback/log call, and `osi_Time`/`osi_GetTime` monotonic sanity on 32/64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osisleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osisleep.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osisleep.h

Purpose: Declares sleep-info state, turnstile structures, once-control structure, hash constants, sleep/wakeup APIs, sleep fd APIs, panic/time utilities, and assertion macros for the OSI layer.

Important APIs, types, and functions: `osi_sleepInfo_t` stores queue linkage, sleep value, thread id, semaphore, states, bucket index, wait reason, and fd refcount. `osi_turnstile_t` stores first/last sleeper pointers. `osi_sleepFD_t` is the remote-debug cursor. `osi_once_t` has `atomic` and `done`. State bits include signalled, in-hash, deleted, wait-for-read, and wait-for-write. Hash constants are `OSI_MUTEXHASHSIZE`, `OSI_SLEEPHASHSIZE`, `osi_MUTEXHASH`, and `osi_SLEEPHASH`. Public functions include sleep/wakeup, init, sleep info free, once helpers, sleep cookie declarations, fd ops, prime helpers, boot time, panic, time, turnstile waits/signals, and `osi_TInit` / `osi_TEmpty`.

Control flow and state: Callers initialize OSI, then sleep on integer/pointer values or use turnstiles from lock code. Assertions call `osi_panic` with file and line.

Persistence and dependencies: No persistence. Depends on fd and queue headers and OSI thread/event types supplied by the aggregate include path.

Integration points: Used by base locks, stats locks, logging, fd registry, and panic handling.

Risks: Some declared sleep cookie functions are not implemented in the read file; callers may rely instead on fd functions. Hash macros assume pointer/integer values can be shifted and moduloed safely. Assertion macros evaluate expressions once but terminate through panic side effects rather than returning errors.

Test signals: Header/API tests should cover compile visibility, hash behavior for representative pointers, assertion/panic wiring, and matching declarations to implementation exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osisleep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osistatl.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osistatl.c

Purpose: Implements the `"stat"` dynamic lock type, which wraps mutex/rwlock operations with timing, blocking, owner/waiter tracking, optional logging, long-held-lock watch callbacks, and remote fd reporting.

Important APIs, types, and functions: Globals include watch callback fields, `osi_statType`, `osi_statLogp`, `osi_allRWLocks`, `osi_allMutexes`, active-info free list, per-hash atomic critical sections, and `osi_statFDCS`. `lock_ObtainWriteStat`, `lock_ObtainReadStat`, release/convert/try/state functions, and `osi_SleepRStat/WStat/MStat` implement instrumented lock semantics. `lock_InitializeRWLockStat` and `lock_InitializeMutexStat` allocate auxiliary stat records and put them on global lists. Active-info helpers allocate, queue, find, remove, and free per-thread timing records. `osi_StatFDCreate`, `osi_StatFDGetInfo`, and `osi_StatFDClose` expose mutex/rwlock summaries. `osi_StatInit` registers the `"stat"` lock type and `"lock"` fd type with field formats. `osi_SetStatLog` and `osi_SetWatchProc` configure optional logging and watch callbacks.

Control flow and state: Stat locks store `lockp->type = osi_statType` and `lockp->d.privateDatap` pointing to an `osi_mutexStat_t` or `osi_rwlockStat_t`. Obtain paths either take the lock immediately and queue an owner active-info record or queue a waiter active-info record, wait on a turnstile, then merge blocked-time statistics. Release paths find the current thread's active-info, merge held-time counts, clear flags/readers, and signal eligible waiters. Remote fd iteration walks all mutex stat records first, then rwlocks, incrementing per-record refs while the cursor points at a record.

Persistence and dependencies: No disk persistence. Runtime statistics live in process memory until lock finalization. Dependencies include base lock struct fields, turnstile helpers, queue helpers, fd registry, large integer math, `GetCurrentTime`, optional `osi_log_t`, and thread ids.

Integration points: Registered by `osi_Init`; selected when `osi_lockTypeDefault` is set to `"stat"` or a lock is explicitly initialized as stat. Remote debug clients retrieve the `"lock"` collection. Watch callbacks let higher code detect locks held beyond a configured threshold.

Risks: Some sleep paths appear to add read-held time into write counters and write-held time into read counters, which deserves scrutiny. `lock_ConvertRToWStat` asserts `OSI_LOCKFLAG_EXCL` before upgrading from read, which looks inconsistent with expected read-to-write conversion. Ref-counted fd iteration protects stat auxiliary records but not all back-pointers from concurrent mutation. Active-info matching by current thread can fail if ownership tracking is inconsistent. Time uses `GetCurrentTime` low-resolution millisecond counts. Header declares active-info helpers as extern, but implementation defines them `static`, creating declaration/definition mismatch in strict compilers.

Test signals: Run lock API conformance tests under stat type, verify counters for read/write acquire/release/try/sleep/conversion, test blocked-time logging, watch callback threshold triggering, remote `"lock"` fd iteration during lock finalization, and compare stat behavior with base locks under contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osistatl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osistatl.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osistatl.h

Purpose: Declares data structures and entry points for the OSI statistics-gathering lock type and remote lock-stat fd.

Important APIs, types, and functions: `osi_activeInfo_t` records a thread's active owner/waiter timing state. `osi_statFD_t` stores fd scan cursor and whether it is scanning mutexes or rwlocks. `osi_qiStat_t` stores active list, lock name, and back pointer. `osi_mutexStat_t` and `osi_rwlockStat_t` contain queue linkage, turnstile, refcount, delete state, owner tid fields, timing/count aggregates, and shared queue info. `osi_watchProc_t` is a callback for long-held locks. The header declares stat lock initializers, active-info helpers, `osi_StatInit`, `osi_SetStatLog`, and `osi_SetWatchProc`.

Control flow and state: Stat locks use auxiliary records to retain instrumentation while the public lock structs keep the normal fields needed by callers and lock assertions.

Persistence and dependencies: No persistence. Depends on `osibasel.h`, `largeint.h` for older MSVC, and `osiqueue.h`.

Integration points: Included by `osilog.h` and stat implementation, and indirectly by code that selects dynamic lock type `"stat"`.

Risks: Public declarations for helpers implemented as `static` in `osistatl.c` can cause linkage inconsistency if referenced externally. The header documents layout assumptions for fd code; changing field order in stat structs can break iteration/finalization.

Test signals: Compile with strict warnings, verify struct layout assumptions, and test long-held-lock watch callback ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osistatl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osithrdnt.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osithrdnt.h

Purpose: Provides the Windows NT thread, event, critical-section, and handle abstraction macros used by OSI code.

Important APIs, types, and functions: Maps `thread_t` to `HANDLE`, `ThreadFunc` to `LPTHREAD_START_ROUTINE`, `SecurityAttrib` to `PSECURITY_ATTRIBUTES`, and wrappers such as `thrd_Create`, `thrd_CloseHandle`, event create/set/reset/wait functions, interlocked increment/decrement, `thrd_Sleep`, critical-section init/enter/leave/delete, `thrd_Current`, `EVENT_HANDLE`, and `FILE_HANDLE`.

Control flow and state: This is a macro layer; callers write OSI-neutral names but compile directly to Win32 APIs.

Persistence and dependencies: No persistence. Depends on Windows headers already being available.

Integration points: Used throughout client OSI lock, queue, fd, sleep, stats, log, and tests.

Risks: Macros expose raw Win32 semantics and do not normalize error handling. `thrd_Create` ignores the `name` argument. Event and wait macro names do not distinguish manual-reset/autoreset creation options.

Test signals: Build tests should confirm the macro layer compiles under supported Windows SDKs and that callers include required Windows types before this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osithrdnt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiutils.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osiutils.c

Purpose: Implements utility functions for deterministic UUID construction/comparison, RPC stub allocation hooks, and compatibility `LARGE_INTEGER` arithmetic functions for newer MSVC builds.

Important APIs, types, and functions: `osi_LongToUID` writes a generic Cazamar UUID template with `Data1` replaced by a long value. `osi_UIDCmp` lexicographically compares UUID fields. `MIDL_user_allocate` and `MIDL_user_free` route RPC allocations to `malloc`/`free`. For `_MSC_VER >= 1300`, the file defines `LargeIntegerAdd`, `LargeIntegerSubtract`, `ExtendedLargeIntegerDivide`, `LargeIntegerDivide`, and `ConvertLongToLargeInteger`.

Control flow and state: UUID conversion is stateless. Comparisons check `Data1`, `Data2`, `Data3`, and then eight `Data4` bytes in order. Division helpers convert `LARGE_INTEGER` values to `ULONGLONG`, compute quotient/remainder, and rebuild `LARGE_INTEGER`.

Persistence and dependencies: No persistence. Dependencies include Windows/RPC UUID types, C runtime allocation, and `osiutils.h`.

Integration points: `osidebug.c` uses `osi_LongToUID` for instance ids; RPC stubs require MIDL allocation hooks; sleep/log/stat code relies on large-integer helpers when platform headers do not provide them.

Risks: `osi_UIDCmp` treats `Data4` bytes through `char *`, so signed-char platforms could affect ordering. Large integer division collapses to unsigned 64-bit arithmetic and has limited handling for divide-by-zero. `ExtendedLargeIntegerDivide` contains a placeholder overflow comment but no action.

Test signals: UUID roundtrip/ordering tests, RPC allocation/free smoke tests, large integer arithmetic compared with native operations, and divide-by-zero behavior tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiutils.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osiutils.h

Purpose: Declares UUID utility functions for OSI remote-debug identity handling.

Important APIs, types, and functions: `osi_UIDCmp(UUID *uid1, UUID *uid2)` compares UUIDs. `osi_LongToUID(long inval, UUID *outuidp)` creates a deterministic UUID from a long instance id.

Control flow and state: Stateless declarations only.

Persistence and dependencies: No persistence. Requires Windows/RPC `UUID` type in the including context.

Integration points: Used by debug client/server code to map simple numeric instance ids to RPC object UUIDs.

Risks: The header does not include the UUID-defining header itself, so include order matters.

Test signals: Build include-order checks and UUID utility unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiutils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/perf.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/perf.c

Purpose: Provides a Win32 test workload for OSI mutex sleep/wakeup performance and correctness by ping-ponging two threads through a shared flag.

Important APIs, types, and functions: `main_perfMutex` protects `flags`, `count`, and `done`. `main_Perf1` waits for `STARTA`, hands off to `STARTB`, increments count, sleeps on `flags`, and exits after `main_NITERS`. `main_Perf2` mirrors that for `STARTB` to `STARTA`. `main_PerfTest` initializes OSI, display, mutex, two threads, waits for `done == 2` with `osi_SleepM`, finalizes the mutex, closes handles, and returns status.

Control flow and state: The test starts with `STARTA`. Each worker obtains the mutex, waits if its flag is not set, toggles flags, wakes sleepers on `flags`, increments count, and then sleeps atomically with releasing the mutex. Completion wakes the main test waiting on `done`.

Persistence and dependencies: No persistence. Depends on Win32 threads, `main.h` display helpers, `perf.h`, and OSI lock/sleep APIs.

Integration points: Invoked from the client OSI test GUI/menu to stress synchronization.

Risks: Uses old implicit `int` declarations (`static done`, `main_PerfTest`). If `CreateThread` for the second thread fails, the first thread handle is not closed and the first thread may continue. The loop breaks while still holding the mutex, then increments `done` and releases, which is intentional but easy to misread.

Test signals: Confirm no deadlocks, count reaches expected threshold, both threads finish, display remains responsive, and repeated runs do not leak handles or leave stale mutex state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/perf.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/perf.h

Purpose: Declares the OSI performance test entry point.

Important APIs, types, and functions: `main_PerfTest(HANDLE)` runs the two-thread mutex ping-pong test.

Control flow and state: The caller supplies a window handle for display updates.

Persistence and dependencies: No persistence. Requires Windows `HANDLE`.

Integration points: Included by the OSI test GUI.

Risks: The declaration says `extern int` while the implementation uses old-style implicit return; strict builds should align prototypes.

Test signals: Build warning checks and GUI invocation smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/perf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/trylock.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/trylock.c

Purpose: Implements an OSI try-lock stress test with two threads acquiring a three-lock hierarchy in opposite directions to validate nonblocking acquisition, fallback waits, and deadlock avoidance.

Important APIs, types, and functions: Global locks are `trylock_first` rwlock, `trylock_second` mutex, and `trylock_third` rwlock. `main_Neon` acquires read/mutex/write in hierarchy order and releases them. `main_Salmon` attempts to acquire read/mutex/write in reverse order using `lock_TryRead`, `lock_TryMutex`, and `lock_TryWrite`; on failure it releases held locks, waits for the contended lock, increments `interestingEvents`, and retries. `main_TryLockTest` initializes OSI and locks, starts both threads, periodically updates `main_screenText`, waits for `done == 2`, finalizes locks, and closes handles.

Control flow and state: `main_Neon` represents normal lock ordering. `main_Salmon` deliberately goes against hierarchy but uses try-lock/fallback to avoid deadlock. `done` is incremented under the mutex, while progress counters are unsynchronized and only used for display.

Persistence and dependencies: No persistence. Depends on Win32 threads/sleep, test UI globals, `trylock.h`, and OSI lock APIs.

Integration points: Invoked by the OSI test GUI/menu to exercise lock behavior and lock-order validation scenarios.

Risks: Progress counters are read without synchronization. If thread creation fails after the first thread starts, cleanup is incomplete. The test depends on scheduler timing (`Sleep(0)`, `Sleep(1000)`) and may be nondeterministic. The thematic function names do not explain lock roles, so maintainers must inspect code.

Test signals: The key signal is completing both threads without deadlock while showing nonzero or plausible `interestingEvents`. Run under base and stat lock types and with lock-order validation enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/trylock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/trylock.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/trylock.h

Purpose: Declares the try-lock stress test entry point.

Important APIs, types, and functions: `main_TryLockTest(HANDLE)` runs the two-thread hierarchy/try-lock test.

Control flow and state: The caller supplies the UI handle used for display updates.

Persistence and dependencies: No persistence. Requires Windows `HANDLE`.

Integration points: Included by the OSI test GUI.

Risks: Implementation uses old-style return declarations; strict compile checks should ensure prototype consistency.

Test signals: Build and GUI invocation smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/trylock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/eventlog/logevent.c -->
## sources/distributed-fs/openafs/src/WINNT/eventlog/logevent.c

Purpose: Provides alternate AFS Windows Event Log helper functions for error, warning, and informational events with variable insertion strings and optional raw status data.

Important APIs, types, and functions: `ReportEventAlt` is the internal helper that opens the event source `AFSREG_SVR_APPLOG_SUBKEY`, calls `ReportEvent`, deregisters, and returns 0/-1. `ReportErrorEventAlt` and `ReportWarningEventAlt` collect up to `AFSEVT_MAXARGS` insertion strings and pass the status as raw event data when nonzero. `ReportInformationEventAlt` collects insertion strings and reports information events with no status data.

Control flow and state: Public functions parse a NULL-terminated varargs string list into a fixed array. If the caller supplies more than `AFSEVT_MAXARGS`, the function returns `-1` without logging. Each log call independently registers and deregisters the event source.

Persistence and dependencies: Events are persisted by Windows Event Log. Dependencies include Win32 Event Log APIs, `WINNT/afsreg.h`, and the event source registry being configured.

Integration points: Used by server-side tools or services that need to write AFS event messages. The test program `elogtest.c` exercises these APIs with event IDs from `WINNT/afsevent.h`.

Risks: The insertion string array is `char **` and uses ANSI strings. Passing non-NULL-terminated varargs can read past the intended list. `ReportEventAlt` passes `&status` even when raw data size is zero; Windows should ignore it, but it is still a notable convention.

Test signals: Registry-present and registry-missing tests, zero/two insertion strings, max-argument boundary, status raw data presence, and Event Viewer message rendering for configured message DLLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/eventlog/logevent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/eventlog/logevent.h -->
## sources/distributed-fs/openafs/src/WINNT/eventlog/logevent.h

Purpose: Declares alternate Windows Event Log helper APIs and the insertion-string limit.

Important APIs, types, and functions: `AFSEVT_MAXARGS` is 16. Exports are `ReportErrorEventAlt`, `ReportWarningEventAlt`, and `ReportInformationEventAlt`.

Control flow and state: Callers pass event id, status where applicable, and a NULL-terminated sequence of insertion strings.

Persistence and dependencies: Persistence is through Windows Event Log in the implementation. The header itself has no external include guard dependencies beyond C types.

Integration points: Included by eventlog implementation and consumers/tests such as `elogtest.c`.

Risks: Varargs API is easy to misuse if the terminating `0` is omitted or if the event id does not match message table definitions.

Test signals: Compile callers with prototypes visible and test max argument enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/eventlog/logevent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/eventlog/test/elogtest.c -->
## sources/distributed-fs/openafs/src/WINNT/eventlog/test/elogtest.c

Purpose: Command-line smoke test for AFS Windows Event Log configuration and the alternate event logging functions.

Important APIs, types, and functions: `main` opens the application log registry key, checks the AFS server event source key, then calls `ReportInformationEventAlt`, `ReportWarningEventAlt`, and `ReportErrorEventAlt` with no insertion strings and with two insertion strings.

Control flow and state: If the expected event source registry keys are missing, the test prints a skip message and exits success. Otherwise it logs six test events and exits with status 1 on the first logging failure.

Persistence and dependencies: Writes test events to Windows Event Log. Depends on `WINNT/afsreg.h`, `WINNT/afsevent.h`, registry helpers such as `RegOpenKeyAlt`, and the logging implementation.

Integration points: Validates installation-time event source registration and message IDs for server test events.

Risks: Success when registry keys are absent means CI can miss broken registration if it does not assert the skip text. The test uses fixed server event IDs and ANSI insertion strings.

Test signals: Expected console lines, six Event Log entries with correct severity and insertion text, nonzero exit on logging failure, and explicit handling of missing registry keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/eventlog/test/elogtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/AFSCell.ini -->
## sources/distributed-fs/openafs/src/WINNT/install/NSIS/AFSCell.ini

Purpose: Defines an NSIS InstallOptions page for OpenAFS client cell and behavior defaults.

Important fields: The page has 11 fields. It prompts for the AFS cell name with default `openafs.org`, enables crypt security by default, enables Freelance client by default, enables DNS lookup for cell servers by default, disables integrated logon by default, and shows explanatory label text.

Control flow and state: NSIS reads the `[Settings]` and `[Field N]` sections to render controls and later consume `State` values. The field numbering is not strictly visual order; fields 9/10 appear before 7/8.

Persistence and dependencies: The INI does not persist by itself; installer scripts use selected states to write registry/service configuration. It depends on NSIS InstallOptions semantics.

Integration points: Feeds client configuration properties such as cell name, security level, freelance mode, DNS cell server lookup, and integrated logon in the NSIS installer.

Risks: Defaulting to `openafs.org` may be inappropriate for local deployments if the installer does not override it. Text/control coordinates are fixed and may not localize well. Field order mismatches can break scripts that assume sequential visual layout.

Test signals: Run the NSIS page, verify default states, ensure installer script reads the intended field IDs, and test persisted registry values after install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/AFSCell.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/AFSCreds.ini -->
## sources/distributed-fs/openafs/src/WINNT/install/NSIS/AFSCreds.ini

Purpose: Defines an NSIS InstallOptions page for AFS Credentials startup and command-line options.

Important fields: The page has 14 fields. It defaults to starting AFS Credentials at system login and enabling auto-initialize (`-a`), renew drive maps (`-m`), IP address change detection (`-n`), and quiet (`-q`). It defaults to not showing the credentials window on startup (`-s` absent). Labels group startup parameters and command-line options.

Control flow and state: NSIS renders checkboxes and labels from fixed coordinates. Installer scripts consume checkbox `State` values to construct shortcut parameters or registry settings.

Persistence and dependencies: Persistence occurs later through installer registry/shortcut writes. Depends on NSIS InstallOptions.

Integration points: Related WiX custom action code reads/writes `StartAfscredsOnStartup` and `AfscredsShortcutParams`; this NSIS page represents the older installer path.

Risks: Mixed-case `Type`/`type` keys depend on parser tolerance. Defaults may silently enable behaviors users did not expect. Fixed coordinates are localization-sensitive.

Test signals: Verify checkbox defaults, generated shortcut parameters, persisted registry values, and upgrade migration consistency with WiX `DetectSavedConfiguration`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/AFSCreds.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/AdminGroup.cpp -->
## sources/distributed-fs/openafs/src/WINNT/install/NSIS/AdminGroup.cpp

Purpose: Command-line utility for NSIS installers to create or remove the local `AFS Client Admins` group and initially populate it with members of the built-in Administrators group.

Important APIs, types, and functions: `LookupAliasFromRid` resolves a localized built-in alias name from a RID. `createAfsAdminGroup` calls `NetLocalGroupAdd`. `initializeAfsAdminGroup` resolves Administrators, enumerates members with `NetLocalGroupGetMembers`, and adds them to `AFS Client Admins` with `NetLocalGroupAddMembers`. `removeAfsAdminGroup` deletes the group. `main` parses `-create` and `-remove`.

Control flow and state: On `-create`, the utility creates the group, treats `ERROR_ALIAS_EXISTS` as success, and only populates members after a new group is created. On `-remove`, it ignores deletion status and exits success.

Persistence and dependencies: Persists local SAM group and membership changes. Depends on `netapi32`, `advapi32`, well-known SID APIs, and administrative privileges.

Integration points: NSIS installation/uninstallation uses this tool; WiX `afscustom.cpp` contains similar embedded logic.

Risks: Existing group membership is not reconciled or updated when the group already exists. Error logging has malformed `fprintf` format arguments in some paths. Removing ignores failures. The fallback English `Administrators` name can fail on localized systems if SID lookup fails.

Test signals: Run on localized and English systems, create existing/nonexisting group cases, verify copied members, remove group, and test non-admin failure codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/AdminGroup.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/CellServPage.ini -->
## sources/distributed-fs/openafs/src/WINNT/install/NSIS/CellServPage.ini

Purpose: Defines an NSIS InstallOptions page that asks where the installer should obtain `CellServDB`.

Important fields: The page offers radio buttons for using an existing `CellServDB`, using the packaged file, downloading from `http://grand.central.org/dl/cellservdb/CellServDB`, or selecting a local file. Field 7 is a `FileRequest` with `FILE_MUST_EXIST`.

Control flow and state: NSIS displays mutually exclusive options and a text/file input. Installer script logic must interpret which radio button is selected and then copy/download/use the chosen source.

Persistence and dependencies: The INI itself persists nothing. It depends on installer script handling and network/file availability for selected sources.

Integration points: Affects client cell-server database installation, which later determines how the client locates AFS cell servers when DNS is not used.

Risks: The default radio `State` is only explicit for the download option and is `0`; if scripts do not initialize defaults, behavior can be ambiguous. The URL is plain HTTP and external. Mixed `Type` key casing depends on parser tolerance.

Test signals: Verify radio defaults, packaged/existing/download/file paths, file-exists enforcement, and installer behavior when the download URL is unreachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/CellServPage.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/Service.cpp -->
## sources/distributed-fs/openafs/src/WINNT/install/NSIS/Service.cpp

Purpose: Small NSIS helper executable to create or delete a Windows service for OpenAFS components.

Important APIs, types, and functions: `main` opens the Service Control Manager, creates a service with `CreateService` unless the first argument starts with `u`/`U`, and deletes a service with `OpenService` plus `DeleteService` for uninstall mode. It treats paths ending in `sys` as `SERVICE_FILE_SYSTEM_DRIVER` with demand start; otherwise it creates an auto-start own-process service.

Control flow and state: Arguments are interpreted as install mode `ServiceName ServicePath DisplayName` or uninstall mode using `argv[2]` as service name. The created service uses `SERVICE_ERROR_IGNORE` and no dependencies/account/password.

Persistence and dependencies: Persists SCM service entries. Depends on administrative privileges and Win32 service APIs.

Integration points: Used by NSIS scripts to install `TransarcAFSDaemon`, drivers, or related services.

Risks: The argument count check says fewer than three args but usage text names four tokens; install mode dereferences `argv[3]`. It calls `CloseServiceHandle(hService)` twice and may call it on an uninitialized/null handle. `stricmp(argv[2] + strlen(argv[2]) - 3, "sys")` underflows for short paths. Error reporting is minimal and install failures may still return 0.

Test signals: Create/delete service in a disposable VM, short path argument handling, driver-vs-service classification, insufficient arguments, and handle-checking under Application Verifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/Service.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/killer.cpp -->
## sources/distributed-fs/openafs/src/WINNT/install/NSIS/killer.cpp

Purpose: NSIS helper that enumerates running processes by executable name and terminates matching processes, including support for old NT4 and 16-bit WOW task enumeration.

Important APIs, types, and functions: `EnumProcs` abstracts process enumeration using PSAPI on NT4 and Toolhelp32 on Win9x/newer NT. It dynamically loads `PSAPI.DLL`, `VDMDBG.DLL`, or `Kernel32.DLL` functions. `Enum16` bridges NTVDM task enumeration. `MyProcessEnumerator` compares process names to global `strProcessName`, opens matching processes with `PROCESS_ALL_ACCESS`, and calls `TerminateProcess`. `main` copies the requested process name and starts enumeration.

Control flow and state: The utility sets a global target process name from `argv[1]`. Enumeration invokes the callback for every process and optional 16-bit tasks. Matching is case-insensitive exact executable-name comparison.

Persistence and dependencies: No persistent storage, but it forcibly changes system runtime state by terminating processes. Depends on process enumeration APIs, dynamic libraries, and sufficient privileges.

Integration points: NSIS uninstall/install scripts can use it to stop AFS tools before replacing files.

Risks: Uses `TerminateProcess` rather than graceful shutdown, risking data loss. `PROCESS_ALL_ACCESS` can fail under modern privilege/UAC settings. It closes `hProcess` even when `OpenProcess` returns null. Library-free logic can double-free `hInstLib` on some paths. Old OS branches are obsolete and lightly guarded. Process-name matching may kill unrelated programs with the same executable name.

Test signals: Enumerate on supported Windows versions, target a harmless process, verify no crash on access-denied processes, validate no double-free with instrumentation, and confirm installer scripts avoid broad names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/killer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/instloop.c -->
## sources/distributed-fs/openafs/src/WINNT/install/loopback/instloop.c

Purpose: Command-line installer/uninstaller for the Microsoft Loopback Adapter configured for OpenAFS.

Important APIs, types, and functions: `ShowUsage` prints CLI syntax. `DisplayStartup` and `DisplayResult` print install/uninstall status. `_tmain` parses `-i [name [ip mask]]` and `-u`, applies defaults from `loopbackutils.h`, calls `IsLoopbackInstalled`, `InstallLoopBack`, or `UnInstallLoopBack`, and returns the resulting code.

Control flow and state: Install mode defaults to connection name `AFS`, IP `10.254.254.253`, and mask `255.255.255.252`. If a loopback adapter is already detected, it returns success without installing another. Optional compile-time output redirection appends to `instlog.txt`.

Persistence and dependencies: Persists network adapter installation, connection rename, IP/mask, binding changes, and hosts/lmhosts updates through `loopbackutils.cpp` and `wmi.cpp`. Depends on administrative privileges and SetupAPI/WMI support.

Integration points: Standalone wrapper around the loopback DLL/helper functions also used by MSI/rundll entry points.

Risks: Argument parsing requires both IP and mask if either is specified. Installation can take a long time and depends on hardware/driver enumeration. Existing adapter detection does not validate current name/IP/bindings.

Test signals: CLI usage, default install, custom name/IP/mask install, already-installed behavior, uninstall behavior, and return codes requiring reboot or failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/instloop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/loopbackutils.cpp -->
## sources/distributed-fs/openafs/src/WINNT/install/loopback/loopbackutils.cpp

Purpose: Implements loopback adapter installation/uninstallation, installed detection, rundll/MSI entry points, argument parsing, and MSI/printf reporting for OpenAFS loopback configuration.

Important APIs, types, and functions: `UnInstallLoopBack` enumerates present network devices, finds hardware id `*msloop`, selects and removes it. `IsLoopbackInstalled` scans present devices for the same hardware id. `InstallLoopBack` creates a net-class device info set, finds the Microsoft loopback class driver, registers/installs the phantom device, reads `NetCfgInstanceId`, renames the connection, sets IP/mask, adjusts bindings, and updates hosts/lmhosts. `process_args` parses rundll/MSI command-line tokens with defaults. `doLoopBackEntryW` and `uninstallLoopBackEntryW` are RunDll32 entry points. `installLoopbackMSI` and `uninstallLoopbackMSI` consume `CustomActionData`, call install/uninstall, and schedule reboot for return code 2. `ReportMessage` and `SetMsiReporter` report through stdout or MSI action data.

Control flow and state: Install creates and registers the adapter first, then configures it. On error after registration, cleanup removes the device. The code sets `registered` and `destroyList` flags to decide cleanup operations. MSI mode sets global `dwReporterType` and `hMsiHandle`; reporting is otherwise printf-based. Argument parsing allocates wide strings and frees them in `Args` destructor.

Persistence and dependencies: Persists device installation, registry/device state, network connection name, static IP configuration, binding order/enabled protocols, and `hosts`/`lmhosts` edits. Dependencies include SetupAPI, COM/WMI helpers from `wmi.cpp`, shell rename helper, MSI APIs, and admin rights.

Integration points: Used by `instloop.c`, RunDll32 custom entries, and WiX/MSI custom actions. Calls exported functions declared in `loopbackutils.h`: `RenameConnection`, `SetIpAddress`, `LoopbackBindings`, and `UpdateHostsFile`.

Risks: Device enumeration and driver detail parsing use fixed buffers and pointer bounds that must match MULTI_SZ layout. `InstallLoopBack` calls `SetupDiDeleteDeviceInfo` even after successful install, relying on behavior of the setup API. MSI property buffer allocation loops must handle `ERROR_MORE_DATA` carefully. Global MSI reporter state is not thread-safe. `process_args` treats any substring containing `help` as help. `ReportMessage` creates MSI records but sets only four fields in a five-field record.

Test signals: Install/uninstall in clean VM, already-installed detection, failure cleanup after driver registration, MSI custom action `CustomActionData` parsing, RunDll32 invocation, scheduled reboot paths, and host/lmhost/binding/IP postconditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/loopbackutils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/loopbackutils.h -->
## sources/distributed-fs/openafs/src/WINNT/install/loopback/loopbackutils.h

Purpose: Declares the C ABI for loopback adapter installation/configuration helpers and shared defaults/reporting constants.

Important APIs, types, and functions: Exports include `InstallLoopBack`, `IsLoopbackInstalled`, `UnInstallLoopBack`, `RenameConnection`, `SetIpAddress`, `LoopbackBindings`, `UpdateHostsFile`, `ReportMessage`, and `SetMsiReporter`. Defaults are `DRIVER_DESC`, `DRIVER`, `DRIVERHWID`, `MANUFACTURE`, `DEFAULT_NAME`, `DEFAULT_IP`, and `DEFAULT_MASK`. Reporting modes are `REPORT_PRINTF`, `REPORT_MSI`, and `REPORT_IGNORE`; globals are `dwReporterType` and `hMsiHandle`.

Control flow and state: Consumers call install/uninstall/detect and lower-level configuration helpers. Reporting behavior is controlled by global mode and handle.

Persistence and dependencies: Implementations persist network and file changes. Header depends on Windows TCHAR/DWORD types and is C/C++ compatible via `extern "C"`.

Integration points: Shared by command-line installer, RunDll32/MSI DLL entry points, WMI helpers, and rename helper.

Risks: Default IP/mask and connection name are hard-coded. Reporter globals are process-wide. The ABI exposes lower-level helpers that can be called out of sequence.

Test signals: ABI export checks, C and C++ include tests, default value verification, and integration tests that call each exported helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/loopbackutils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/renameconnection.cpp -->
## sources/distributed-fs/openafs/src/WINNT/install/loopback/renameconnection.cpp

Purpose: Renames a Windows network connection identified by adapter GUID, using supported shell-folder APIs when available and an older `netshell.dll` fallback otherwise.

Important APIs, types, and functions: `rename_shellfolder` creates the Network Connections shell folder (`CLSID_NetworkConnections`), parses the adapter display name `::{GUID}`, and calls `IShellFolder::SetNameOf`. `RenameConnection` first calls `rename_shellfolder`; if it returns `E_NOTIMPL`, it loads `netshell.dll`, resolves undocumented `HrRenameConnection`, converts the GUID string to a CLSID, and calls the fallback.

Control flow and state: COM is initialized inside `rename_shellfolder` and uninitialized before returning. The fallback is only attempted for `E_NOTIMPL`, not all failures. Return value is `0` on success and `-1` on failure.

Persistence and dependencies: Persists the network connection display name. Depends on COM, shell APIs, Network Connections shell folder, and optionally `netshell.dll`.

Integration points: Called by `InstallLoopBack` after reading `NetCfgInstanceId`.

Risks: `pShellFolder` and `pShellMalloc` release handling is incomplete; COM interfaces are not released in all paths. `CoInitialize` return is ignored. The fallback uses an undocumented API. GUID length validation only checks `MAX_PATH`, not GUID syntax before shell parse.

Test signals: Rename on XP-era and newer platforms, fallback path simulation, invalid GUID/name handling, and COM leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/renameconnection.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/wmi.cpp -->
## sources/distributed-fs/openafs/src/WINNT/install/loopback/wmi.cpp

Purpose: Configures the loopback adapter after installation: finds the adapter's WMI instance by GUID, sets static IP/mask, disables DNS registration, enables NetBIOS, adjusts network bindings/order, updates NetBIOS `MaxLana`, and edits `hosts`/`lmhosts`.

Important APIs, types, and functions: `FindNetworkAdapterConfigurationInstanceByGUID` queries `Win32_NetworkAdapterConfiguration` and matches `SettingID`. `SetupStringAsSafeArray` builds single-element BSTR safe arrays for WMI method parameters. `IsXP` and `FixupXPDNSRegistrations` apply registry fixes for XP pre-SP2 DNS registration behavior. `WMIEnableStatic` connects to `root\\cimv2`, finds an adapter instance, calls `EnableStatic`, `SetDynamicDNSRegistration`, and `SetTcpipNetbios`. `LoopbackBindings` uses `INetCfg` to move binding paths to the end, enable TCP/IP/NetBIOS/NetBT/client bindings, and disable others. `SetIpAddress` wraps WMI setup and XP fixup. `AdjustMaxLana` ensures the NetBIOS `MaxLana` registry value is large enough. `UpdateHostsFile` creates or rewrites a file under `%SystemRoot%\\System32\\drivers\\etc`, removing existing entries for the adapter name and appending the new IP/name line.

Control flow and state: WMI setup initializes COM, sets security/impersonation, connects to CIMV2, gets class and instance, builds method input instances, retries `EnableStatic` up to five times with sleeps, then applies DNS and NetBIOS settings. Binding setup obtains an `INetCfg` write lock, enumerates net adapters, matches the loopback GUID, iterates upper binding paths, moves each path to the end, and toggles enabled state by component id. Hosts update rewrites through a temp file and renames the old file to `.old` or a randomized backup.

Persistence and dependencies: Persists WMI network configuration, NetCfg binding state, TCP/IP and NetBIOS registry values, and `hosts`/`lmhosts` file content. Depends on COM, WMI, NetCfg COM interfaces from DDK headers, SetupAPI GUIDs, Shell folder APIs, C runtime file I/O, registry APIs, and admin rights.

Integration points: Called by `loopbackutils.cpp` during loopback install. Reporting uses `ReportMessage` from the loopback utility layer. The functions are exported with C linkage for use through `loopbackutils.h`.

Risks: `UpdateHostsFile` has fragile path building: `tempPath` appends `szFilename` without inserting a slash after the etc directory copy. The condition `if (!MoveFileA( tempPath, etcPath ) != 0)` is confusing and likely wrong due to double negation. Host entry filtering appears inverted: it may keep lines when the name is found under common delimiter conditions. Several fixed 2048-byte buffers and `strcat`/`strcpy` operations can overflow. `FixupXPDNSRegistrations` does not check registry opens before using handles. `LoopbackBindings` may not call `CoUninitialize` despite initializing COM. `AdjustMaxLana` is declared and defined but not obviously called in this file's main flow. Broad binding changes can disrupt networking if the wrong adapter GUID is matched.

Test signals: WMI instance matching by GUID, EnableStatic retry behavior, DNS/NetBIOS method return codes, binding enable/disable postconditions, hosts/lmhosts rewrite with existing names/comments/long lines, XP registry fix path, and COM/resource leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/wmi.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/afsdesktop.ini -->
## sources/distributed-fs/openafs/src/WINNT/install/wix/afsdesktop.ini

Purpose: Provides shell folder customization metadata for an OpenAFS desktop/start-menu folder icon in the WiX installer tree.

Important fields: `[.ShellClassInfo]` sets `IconFile=client\\program\\afsd_service.exe` and `IconIndex=0`.

Control flow and state: Windows Explorer reads this INI when the folder is marked appropriately by installer attributes.

Persistence and dependencies: Persisted as an installed INI file. Depends on the referenced executable path existing relative to the folder context and on shell folder customization behavior.

Integration points: WiX installer packaging for OpenAFS client desktop resources.

Risks: If `afsd_service.exe` is moved or not installed, the icon breaks. The file has no localized resource indirection.

Test signals: Install package and verify folder icon display, uninstall cleanup, and path validity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/afsdesktop.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/custom/afscustom.cpp -->
## sources/distributed-fs/openafs/src/WINNT/install/wix/custom/afscustom.cpp

Purpose: Implements OpenAFS WiX/MSI custom actions for abort messaging, service failure-action configuration, network provider order management, NSIS-uninstall migration, local admin group creation/removal, registry backup/restore, and detection of saved client configuration.

Important APIs, types, and functions: `ShowMsiError` emits MSI error records. `AbortMsiImmediate` formats `ABORTREASON` and returns failure. `ConfigureClientService` and `ConfigureServerService` call `ConfigService`, which sets service restart failure actions. `InstallNetProvider`, `UninstallNetProvider`, `InstallRedirNetProvider`, and `UninstallRedirNetProvider` call `InstNetProvider` to edit `ProviderOrder`; `npi_CheckAndAddRemove` adds/removes provider tokens, optionally before `LanmanWorkstation`. `UninstallNsisInstallation` runs a prior NSIS uninstaller inside a job object and waits for all child processes to exit. `CreateAFSClientAdminGroup`, `RemoveAFSClientAdminGroup`, `createAfsAdminGroup`, `initializeAfsAdminGroup`, and `removeAfsAdminGroup` manage the local AFS admin group. Registry backup tables define source keys, selected values, and backup keys. `ShowMsiActionData`, `do_reg_copy_value`, `do_reg_copy`, `BackupAFSClientRegistryKeys`, `RestoreAFSClientRegistryKeys`, `SetMsiPropertyFromRegValue`, `SetAfscredsOptionsFromRegValue`, and `DetectSavedConfiguration` preserve and surface existing client settings.

Control flow and state: Provider install opens `HKLM\\...\\NetworkProvider\\Order`, reads `ProviderOrder`, modifies the comma-separated provider string, and writes it back. Service config opens SCM, locks the service database, opens the target service, and sets three failure actions. NSIS migration gets `NSISUNINSTALL`, starts `Uninstall /S` suspended, assigns it to a job with completion port, resumes, and waits for `ACTIVE_PROCESS_ZERO`. Registry backup copies selected values/subkeys to `SOFTWARE\\OpenAFS\\BackupSettings`; restore copies back and deletes backup keys. Detection first backs up current keys, then maps saved registry values to MSI properties such as `AFSCELLNAME`, `FREELANCEMODE`, `USEDNS`, `SECURITYLEVEL`, credential startup/options, and `LOGONOPTIONS`.

Persistence and dependencies: Persists SCM failure actions, network provider order registry, local SAM group/membership, OpenAFS backup registry keys, MSI properties, and side effects of NSIS uninstaller execution. Depends on MSI APIs, registry APIs, SCM APIs, NetAPI, job objects, string-safe APIs, and administrative privileges.

Integration points: Called from WiX custom action tables during install, uninstall, upgrade, and migration. Complements older NSIS utilities and loopback custom actions.

Risks: `InstNetProvider` allocates based on registry byte size and service name length but comma insertion before another token must fit exactly; edge cases can overflow if provider order is malformed. `npi_CheckAndAddRemove` treats provider order as comma-separated string and can mishandle case or substring issues. `ConfigureServerService` returns success even if `ConfigService` fails after showing an error. `AbortMsiImmediate` returns bitwise-not of success rather than a standard MSI error constant. `UninstallNsisInstallation` passes a constant command line `"Uninstall /S"` rather than quoting the executable path in the command line; behavior depends on `lpApplicationName`. Registry recursive copy/delete uses `RegDeleteKey`, which only deletes empty keys on older Windows. Some exported actions (`BackupAFSClientRegistryKeys`, `RestoreAFSClientRegistryKeys`, `DetectSavedConfiguration`) are implemented but not declared in the provided header.

Test signals: MSI custom-action unit tests for provider order add/remove/before behavior, service failure-action verification, admin group create/existing/remove on localized systems, NSIS uninstaller job completion, registry backup/restore of values and subkeys, saved configuration property detection, and rollback/uninstall scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/custom/afscustom.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/custom/afscustom.h -->
## sources/distributed-fs/openafs/src/WINNT/install/wix/custom/afscustom.h

Purpose: Declares OpenAFS WiX/MSI custom action exports, helper functions, registry/service constants, and MSI error codes.

Important APIs, types, and functions: `MSIDLLEXPORT` expands to `UINT __stdcall`. Helper macros `CHECK`, `CHECKX`, and `CHECK2` jump to `_cleanup`. Constants define provider-order registry path/value, service names (`TransarcAFSDaemon`, `AFSRedirector`, `LanmanWorkstation`), provider-order result codes, and MSI error codes. Helper prototypes include `npi_CheckAndAddRemove`, `InstNetProvider`, `ShowMsiError`, `ConfigService`, and admin group functions. Export prototypes include network provider install/uninstall, redirector provider install/uninstall, client/server service configuration, abort, NSIS uninstall, and admin group create/remove.

Control flow and state: The header establishes the MSI custom action ABI consumed by WiX tables and implemented in `afscustom.cpp`.

Persistence and dependencies: Implementations persist registry/service/group state. Header depends on Windows, SetupAPI, MSI query, stdio/string, and NetAPI headers.

Integration points: Included by `afscustom.cpp` and used to export functions from the custom action DLL.

Risks: Export declarations omit explicit return type before macro names in old C/C++ style (`MSIDLLEXPORT InstallNetProvider`), relying on compiler tolerance. Several implemented exports for registry backup/detection are not declared here. Cleanup macros require local labels and `msiErr` variables in callers that use them.

Test signals: Build with modern compiler warnings, verify DLL exports match WiX custom action names, and check header coverage for all implemented custom actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/custom/afscustom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/uninstall/uninstall.c -->
## sources/distributed-fs/openafs/src/WINNT/install/wix/uninstall/uninstall.c

Purpose: Standalone helper that uninstalls all MSI products related to the OpenAFS for Windows upgrade code.

Important APIs, types, and functions: `main` sets MSI UI to progress-only, loops over `MsiEnumRelatedProducts` for upgrade code `{6823EEDD-84FC-4204-ABB3-A80D25779833}`, and calls `MsiConfigureProduct(..., INSTALLSTATE_ABSENT)` for each product code found.

Control flow and state: The loop increments `iProduct` after each successful configure call and stops when `MsiEnumRelatedProducts` returns something other than success. It returns 0 only when the terminal code is `ERROR_NO_MORE_ITEMS`.

Persistence and dependencies: Persists uninstallation of matching MSI products. Depends on Windows Installer APIs and installed product metadata.

Integration points: Used by installer/uninstaller flows to remove related OpenAFS products by upgrade code.

Risks: Incrementing `iProduct` while uninstalling products can skip entries if enumeration order compacts after removal; a safer pattern often keeps index 0 until no products remain. It ignores `MsiConfigureProduct` return code, so configure failures do not directly stop/report. Product code buffer is 39 chars, matching GUID length plus NUL.

Test signals: Multiple related products installed, configure failure simulation, return code on no products, and UI level behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/uninstall/uninstall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/kclient/kclient.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/kclient/kclient.h

Purpose: Declares the legacy KClient Kerberos API used by Windows OpenAFS/KfW integration code, with calling convention differences for Win32 and non-Win32 builds.

Important APIs, types, and functions: `KC_CALLTYPE` is `__stdcall` on Win32 and `WINAPI` otherwise; `KC_EXPORT` is empty on Win32 and `_export` otherwise. Ticket/session functions include `GetTicketForService`, `GetTicketGrantingTicket`, `DeleteAllSessions`, `SetUserName`, `KCGetUserName` or `GetUserName`, `ListTickets`, `SetTicketLifeTime`, `SetKrbdllMode`, `TgtExist`, optional `ChangePassword`, `KClientErrno`, `KClientKerberosErrno`, `SendTicketForService`, and `_KCGetNumInUse` on Win32.

Control flow and state: This is a header-only API contract; implementations manage Kerberos tickets, sessions, usernames, ticket lifetimes, and error state elsewhere. The Win32 export note says a `.def` file is used because the compiler could not combine `__stdcall` and `__declspec(dllexport)` as desired.

Persistence and dependencies: Ticket/session persistence is implementation-dependent, not in this header. Depends on `kcmacerr.h`, Windows `BOOL`, `LPSTR`, `LPDWORD`, `HWND`, `DWORD`, and `OSErr`.

Integration points: Used by OpenAFS Windows Kerberos compatibility and credential acquisition code.

Risks: This is a legacy ANSI API with global process/session state and non-thread-obvious error retrieval functions. `GetUserName` name conflicts with Win32 API, so Win32 uses `KCGetUserName`. Conditional `KLITE` changes exported surface. Calling convention/export mismatches can break binary compatibility.

Test signals: ABI/export tests against the DLL `.def`, calling-convention smoke tests from C/C++ clients, ticket acquisition/list/delete integration tests, and error-code propagation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/kclient/kclient.h -->
