# subset-b-007692 research

This grouped report covers the requested OpenAFS Windows admin-server and application-library files. Each source file has its own section with deterministic reconciliation markers so the sections can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientNotify.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientNotify.cpp

Purpose: implements client-side notification registration for the AFS admin server client library. It tracks windows interested in object property changes and action lifecycle changes, then posts Windows messages when server-side cache updates or action state changes are observed.

Important APIs/types/functions: `LISTENER` binds `idCell`, `idObject`, and `HWND`. `AddObjectNotification()` lazily creates a `HASHLIST` and an object-id key, then stores a listener. `ClearObjectNotifications()` removes all registrations for a window. `TestForNotifications()` builds an `ASIDLIST` for watched objects and calls `RefreshCachedProperties()`. `NotifyObjectListeners()` posts `WM_ASC_NOTIFY_OBJECT`. `SetActionNotification()` manages a growable `HWND` array, and `NotifyActionListeners()` posts copied `ASACTION` records through `WM_ASC_NOTIFY_ACTION`.

Control flow: object notification starts with UI registration, then periodic or explicit refresh checks call `TestForNotifications()`. Cache refresh side effects eventually call `NotifyObjectListeners()`, which filters by object and cell before posting to live windows. Action notifications are more direct: server action callbacks are copied into heap `ASACTION` objects and posted to every valid listener slot.

State and persistence: all state is process-local static memory under `asc_Enter()`/`asc_Leave()`: a listener hash list, an object-id hash key, and a sparse action-listener array. Nothing persists across process lifetime.

Dependencies/integration: depends on `TaAfsAdmSvrClientInternal.h`, AfsAppLib allocation/`REALLOC`, `HASHLIST`, RPC/admin-client cache functions, `ASIDLIST`, and Windows `PostMessage`/`IsWindow`.

Risks and test signals: `ClearObjectNotifications()` removes while enumerating the hash list, so iterator validity is important. `TestForNotifications()` creates an `ASIDLIST` without visibly freeing it in this file, relying on client-library ownership conventions. Action posts transfer heap-allocated `ASACTION` ownership to recipients; tests should verify recipients free it. Useful tests register multiple windows per object, destroy a listener window before notification, clear registrations, and verify action start/finish messages carry independent copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientNotify.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientNotify.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientNotify.h

Purpose: declares the client-library notification helpers implemented by `TaAfsAdmSvrClientNotify.cpp`.

Important APIs/types/functions: exposes `AddObjectNotification()`, `ClearObjectNotifications()`, `TestForNotifications()`, `NotifyObjectListeners()`, `SetActionNotification()`, and `NotifyActionListeners()`. `TestForNotifications()` has a default `idObject = 0`, allowing a caller to refresh all registered objects in a cell.

Control flow: callers include this header to register UI `HWND`s, clear registrations during window teardown, trigger cache-refresh checks, and dispatch action callbacks. The header deliberately keeps storage details private.

State and persistence: no state is declared here. State is private to the implementation file and protected by the client critical section.

Dependencies/integration: requires the surrounding admin client types (`ASID`, `LPASACTION`) and Windows `HWND`; it is normally included through the client internal header graph.

Risks and test signals: because the API exposes raw `HWND` handles and posted message ownership, tests should cover listener teardown and posted action memory lifetime. Header-level compile tests should verify default parameters remain compatible with C++ callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientNotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientPing.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientPing.cpp

Purpose: maintains the client-side keepalive and callback-host threads for admin-server RPC clients. The ping path prevents the server from considering a client stale; the callback-host path keeps an RPC call open so the server has a context for callbacks.

Important APIs/types/functions: static state stores `hPingThread`, sparse `adwClients`, `cdwClients`, `hCallbackThread`, and callback reference count `cReqCallback`. `StartPingThread()` appends a client id and creates `ClientPingThread()` on first use. `StopPingThread()` clears a client slot. `ClientPingThread()` sleeps `csecAFSADMSVR_CLIENT_PING`, calls `AfsAdmSvr_Ping()`, and drops clients reporting `ERROR_INVALID_HANDLE`. `StartCallbackThread()`/`StopCallbackThread()` reference-count the callback host. `ClientCallbackThread()` runs `AfsAdmSvr_CallbackHost()`.

Control flow: the ping thread loops forever, temporarily leaving the client lock while making each RPC so other client operations can progress. Callback hosting starts when the first requester asks for callbacks and is force-terminated when the count reaches zero.

State and persistence: process-local static thread handles, client-id array, and callback refcount. There is no durable state; stale client entries are only zeroed.

Dependencies/integration: uses admin-client RPC stubs, `RpcTryExcept`, AfsAppLib `REALLOC`, Windows `CreateThread`, `Sleep`, and `TerminateThread`, all synchronized by `asc_Enter()`/`asc_Leave()`.

Risks and test signals: the ping thread has no normal exit and never closes thread handles. `StopCallbackThread()` uses `TerminateThread()`, which can leak RPC/runtime resources if the target is inside RPC. Tests should simulate invalid handles, multiple clients, repeated start/stop callback reference counts, and server shutdown causing `AfsAdmSvr_CallbackHost()` to return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientPing.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientPing.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientPing.h

Purpose: declares the ping and callback-thread lifecycle helpers for the admin-server client library.

Important APIs/types/functions: `StartPingThread(UINT_PTR idClient)`, `StopPingThread(UINT_PTR idClient)`, `StartCallbackThread()`, and `StopCallbackThread()` are the only exported helpers.

Control flow: admin-server open logic starts pinging once it receives a client id, and close/error handling stops pinging. Callback consumers start and stop the callback host around listener registration.

State and persistence: no state is exposed; implementation uses private static arrays and handles.

Dependencies/integration: depends on Windows threading and RPC behavior through the implementation; callers only need the admin-client type set and `UINT_PTR`.

Risks and test signals: the API does not report failures to create threads, so integration tests need to observe behavior indirectly through pings and callbacks rather than return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientPing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientUser.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientUser.cpp

Purpose: implements client-side `asc_User*` wrappers for user mutation RPCs. Each wrapper calls the corresponding server RPC and refreshes or invalidates the local client cache afterward so UI callers see updated properties.

Important APIs/types/functions: `asc_UserChange()`, `asc_UserPasswordSet()`, `asc_UserUnlock()`, `asc_UserCreate()`, and `asc_UserDelete()` wrap `AfsAdmSvr_ChangeUser()`, `AfsAdmSvr_SetUserPassword()`, `AfsAdmSvr_UnlockUser()`, `AfsAdmSvr_CreateUser()`, and `AfsAdmSvr_DeleteUser()`. Password setting accepts either a clear string or `ENCRYPTIONKEYLENGTH` bytes. Successful create/change/unlock/password operations call `asc_ObjectPropertiesGet(GET_ALL_DATA, ...)`.

Control flow: every function enters an `RpcTryExcept` block, performs the mutation, refreshes cache state on success, catches RPC exceptions as `RPC_S_CALL_FAILED_DNE`, and only writes `*pStatus` on failure.

State and persistence: the file stores no private state. Its observable state effect is client cache refresh through `asc_ObjectPropertiesGet()`. Delete deliberately calls a cache-refresh path expected to fail so the cache can remove stale data.

Dependencies/integration: depends on generated admin-server RPC stubs, `TaAfsAdmSvrClientInternal.h`, cache/property helpers, Windows string routines, and the `AFSADMSVR_*USER_PARAMS` structures.

Risks and test signals: success paths do not set `*pStatus`, matching older API style but requiring callers to check the Boolean return. `lstrcpy()` into fixed `STRING` buffers assumes bounded RPC inputs. Tests should cover RPC exception mapping, cache refresh after each successful mutation, delete cache cleanup, password string-vs-key selection, and status propagation only on failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientUser.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCommon.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCommon.cpp

Purpose: provides shared allocation and manipulation routines for RPC-friendly growable list structures: `ASIDLIST`, `ASOBJPROPLIST`, and `ASACTIONLIST`.

Important APIs/types/functions: `AfsAdmSvr_ReallocFunction()` reallocates structures with a fixed header and trailing flexible array, using header offset, count offset, element size, required count, increment, and fill byte. `AfsAdmSvr_Create*List()`, `Copy*List()`, `AddTo*List()`, `RemoveFrom*List()`, `IsIn*List()`, and `Free*List()` cover object ids, object properties, and actions. Removal compacts by copying the last entry over the removed slot.

Control flow: callers create an empty list, append entries as they enumerate or search, optionally copy/test/remove, and free with the matching free routine. Reallocation only grows; counts track used entries separately from allocated entries.

State and persistence: no global state. All data is heap memory allocated through OpenAFS `Allocate`/`Free`, suitable for RPC marshaling because the element array is contiguous after the structure header.

Dependencies/integration: depends on `WINNT/TaAfsAdmSvr.h` list structures, OpenAFS memory helpers, and RPC IDL conventions (`size_is`/`length_is` style arrays).

Risks and test signals: copy routines copy `cEntriesAllocated` entries, not just `cEntries`, so zero-fill correctness matters. Several add functions return `NULL` in Boolean contexts on allocation failure. Removal changes ordering, which must not matter to callers. Tests should exercise empty-list creation, growth granularity, duplicate IDs, order-insensitive removal, copy counts, and freeing null/non-null lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCommon.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCommon.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCommon.h

Purpose: declares common list-management APIs used by server RPC handlers and client-side support code.

Important APIs/types/functions: declarations cover `ASIDLIST`, `ASOBJPROPLIST`, and `ASACTIONLIST` create/copy/add/remove/test/free functions. Default arguments allow optional `LPARAM`, `LPASOBJPROP`, and `LPASACTION` outputs.

Control flow: included by code that needs to build RPC-returnable lists or inspect list contents. It exposes semantic operations while hiding the flexible-array reallocator.

State and persistence: no state. The implementation allocates heap-backed contiguous structures that callers must free explicitly.

Dependencies/integration: depends on admin-server public types (`ASID`, `LPASIDLIST`, `LPASOBJPROP`, `LPASACTIONLIST`) from `TaAfsAdmSvr.h`.

Risks and test signals: the prototype for `AfsAdmSvr_AddToActionList` names `pLispt`, a harmless typo but a signal that compile coverage should include this header. ABI tests should ensure C++ default arguments do not leak into C-facing RPC code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrDebug.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrDebug.cpp

Purpose: implements simple synchronized console logging for the Windows admin server.

Important APIs/types/functions: static `PrintDetailLevel` initializes to `dlDEFAULT`. `vPrint()` lazily creates a `CRITICAL_SECTION`, filters by level, formats with `wvsprintf()`, writes an `AdmSvr:` prefix, optional alert marker, and indentation spaces. Two `Print()` overloads dispatch to `vPrint()`. `GetPrintDetailLevel()` and `SetPrintDetailLevel()` expose the filter mask.

Control flow: callers use `Print(level, format, ...)` or `Print(format, ...)`. Messages with a zero level always print; otherwise the configured bitmask controls output.

State and persistence: only process-local static logging level and lazily allocated critical section. No log file or registry persistence.

Dependencies/integration: included through `TaAfsAdmSvrInternal.h`; uses Windows critical sections, C varargs, `wvsprintf`, and stdout `printf`.

Risks and test signals: lazy critical-section creation is not itself synchronized, so two threads could race during first log. `wvsprintf()` and a fixed 1024-character buffer risk truncation/overflow on long formatted output. Tests should cover level masks, indentation bits, concurrent logging, and debug/non-debug default masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrDebug.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrDebug.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrDebug.h

Purpose: defines admin-server logging levels and declares logging helpers.

Important APIs/types/functions: level bits include `dlSTANDARD`, `dlWARNING`, `dlERROR`, `dlCONNECTION`, `dlOPERATION`, `dlDETAIL`, `dlDETAIL2`, `dlALL`, and indentation bits `dlINDENT1` through `dlINDENT3`. `dlDEFAULT` is broader under `DEBUG`. Declares `Print()` overloads and detail-level getters/setters.

Control flow: server code annotates log calls with detail bits; runtime code can alter the active mask via `SetPrintDetailLevel()`.

State and persistence: no state in the header; implementation stores a process-local mask.

Dependencies/integration: includes `WINNT/TaAfsAdmSvr.h` for base admin types and is pulled into the internal server header.

Risks and test signals: `GetPrintDetailLevel` is declared with a `DWORD dwLevel` parameter but implemented with no parameter, so strict prototype checking would flag a mismatch. Compile tests should cover callers and the declaration/definition consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrDebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGeneral.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGeneral.cpp

Purpose: centralizes admin-server process state: synchronization, client lifetime, operation/action tracking, startup/shutdown, auto-shutdown, name resolution, auto-open, and minimum refresh scope.

Important APIs/types/functions: `CLIENTINFO` stores client name, resolved address, and last ping. `OPERATION` stores active action metadata and start tick. `AfsAdmSvr_Enter()`/`Leave()` guard shared state. `AfsAdmSvr_AttachClient()`, `DetachClient()`, `PingClient()`, and `fIsValidClient()` manage client handles. `AfsAdmSvr_BeginOperation()`/`EndOperation()` track actions and post callbacks. `AfsAdmSvr_GetOperation()`/`GetOperations()` return action snapshots. `AfsAdmSvr_Startup()` initializes AfsClass and notification callback; `AfsAdmSvr_AutoShutdownThread()` stops RPC listening when idle. `AfsAdmSvr_AutoOpen_ThreadProc()` opens and refreshes the default cell.

Control flow: startup registers the AfsClass notification callback and starts the idle-shutdown monitor. RPC handlers validate client ids, begin an operation when needed, call AfsClass work, and end operations through helper wrappers. The shutdown thread periodically detaches stale clients, checks active operations/clients/idle time, and stops RPC listening if auto-shutdown is enabled.

State and persistence: static process state includes operational flag, critical section, client array, callback object, auto-shutdown state, operation array, action counter, and minimum refresh scope. There is no durable persistence; AfsClass cache contents live in memory.

Dependencies/integration: integrates with Windows sockets/RPC, `AfsClass_Initialize`, `CELL::OpenCell`, admin callback posting, `TaAfsAdmSvrProperties` refresh hooks, list helpers, and logging.

Risks and test signals: client ids are raw `CLIENTINFO*` pointers, so stale pointers are rejected only by list membership and ping age. `AfsAdmSvr_AutoShutdownThread()` calls `AfsAdmSvr_DetachClient()` while already holding the same non-recursive critical section, which is a deadlock risk unless the platform behavior or call path avoids it. First-use critical-section initialization is unsynchronized. Tests should cover stale client detachment, operation callback start/finish, auto-shutdown idle timing, command-line auto-open scope, and invalid client rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGeneral.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGeneral.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGeneral.h

Purpose: declares the core internal admin-server lifecycle, synchronization, client, action, and utility APIs.

Important APIs/types/functions: exposes lock helpers, startup/shutdown, auto-shutdown, operation begin/end/query helpers, client attach/detach/ping helpers, common Boolean/null return wrappers, `GetAsidType()`, `AfsAdmSvr_ResolveName()`, auto-open/min-scope functions, callback manager declaration, and `AfsAdmSvr_GetCurrentTime()`.

Control flow: server RPC implementation files include this header to validate clients, bracket operations, update action callbacks, and share common error-return idioms.

State and persistence: no state is exposed. State is implementation-private static memory in `TaAfsAdmSvrGeneral.cpp`.

Dependencies/integration: includes `WINNT/TaAfsAdmSvr.h` and is part of `TaAfsAdmSvrInternal.h`.

Risks and test signals: the helper wrappers combine status propagation with operation completion, so misuse can double-end or leak an operation. Tests should verify each RPC handler path pairs begin/end exactly once and that default `iOp = (size_t)-2` leaves operations untouched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGeneral.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGroup.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGroup.cpp

Purpose: implements server-side RPC handlers for PTS group mutation and relationship queries.

Important APIs/types/functions: mutation handlers include `AfsAdmSvr_ChangeGroup()`, `AddGroupMember()`, `RemoveGroupMember()`, `RenameGroup()`, `CreateGroup()`, and `DeleteGroup()`. Query handlers include `GetGroupMembers()`, `GetGroupMembership()`, and `GetGroupOwnership()`. The code builds `ASACTION` records for mutating operations and uses `AfsClass_*` group APIs. Relationship queries return `ASIDLIST` structures translated from PTS string lists.

Control flow: each handler begins an operation, logs, validates the client, opens the relevant `LPIDENT` object, performs AfsClass work, maps failures through `FALSE_()`, and ends the operation on success. `ChangeGroup()` compares incoming requested values with cached current properties to build a `GROUPPROPERTIES.dwMask` before calling `AfsClass_SetGroupProperties()`.

State and persistence: no file-local state. Persistent effects occur in AFS PTS/KAS databases through AfsClass calls. Creating a group may alter max group id, so the cell properties cache is re-tested.

Dependencies/integration: depends on `AfsClass_SetGroupProperties`, PTS group/user open methods, `IDENT::FindGroup`, `IDENT::FindUser`, `USER::SplitUserName`, list helpers, action tracking, property cache, and admin-server logging.

Risks and test signals: `GetGroupMembers()` first tries `IDENT::FindGroup()` for member names, then falls back to user lookup, which can mask ambiguous names. Several early returns after object open rely on wrapper cleanup. Ordering is not preserved in returned lists beyond enumeration order. Tests should cover valid/invalid client ids, no-op change masks, owner lookup by user or group, membership translation, create/delete property-cache updates, and failures from AfsClass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGroup.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrInternal.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrInternal.h

Purpose: umbrella internal header for the Windows AFS admin server implementation.

Important APIs/types/functions: includes RPC headers, AfsClass, public `TaAfsAdmSvr.h`, and internal modules for debug, search, properties, general server helpers, and callbacks. It also includes C admin-library headers for KAS, PTS, VOS, BOS, client, and utility admin APIs.

Control flow: implementation files include this header to get the full internal server surface and backend admin-library dependencies.

State and persistence: no state. It organizes dependencies and compile visibility only.

Dependencies/integration: bridges C++ AfsClass/Windows code with C OpenAFS admin APIs inside an `extern "C"` block.

Risks and test signals: as an umbrella header it can hide excess coupling and slow or complicate builds. Compile tests should ensure C/C++ linkage remains correct and include ordering does not break Windows/RPC definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrInternal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrMain.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrMain.cpp

Purpose: contains the admin-server executable entry point, RPC server registration/listening lifecycle, debug memory window hook, and MIDL allocation callbacks.

Important APIs/types/functions: `main()` initializes Winsock, parses keywords for timed auto-shutdown, manual startup, user/volume scope, and debug mode. It registers `ITaAfsAdminSvr_v1_0_s_ifspec`, attempts endpoint `AFSADMSVR_ENDPOINT_DEFAULT`, registers bindings with the endpoint mapper, starts `AfsAdmSvr_Startup()`, optionally launches `AfsAdmSvr_AutoOpen_ThreadProc()`, then calls `RpcServerListen()`. `MIDL_user_allocate()` and `MIDL_user_free()` route RPC memory through OpenAFS allocation helpers.

Control flow: the process prepares RPC, starts server internals, listens until stopped, then shuts down internals and unregisters RPC interfaces/endpoints. Debug builds can create a thread running memory-manager UI messages.

State and persistence: no private persistent state beyond process RPC registration. Runtime effects are endpoint mapper registration and in-memory AfsClass cache startup.

Dependencies/integration: depends on Windows RPC, Winsock, admin-server internal modules, generated MIDL interface symbol `ITaAfsAdminSvr_v1_0_s_ifspec`, OpenAFS allocation, and command keywords from public headers.

Risks and test signals: `RpcServerUseProtseq()` is called before `RpcServerUseProtseqEp()`, and the endpoint fallback/error handling is unusual because `fExportedBinding` remains false. Tests should cover command-line scope combinations, endpoint already in use, endpoint mapper registration/unregistration, startup failure that still reports errors to clients, and MIDL allocation/free pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrMain.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrProperties.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrProperties.cpp

Purpose: manages cached `ASOBJPROP` data for cells, servers, services, partitions, volumes, users, and groups, and runs optional per-cell auto-refresh threads.

Important APIs/types/functions: `REFRESHTHREAD` tracks cell id, last refresh time, refresh rate, and handle. `AfsAdmSvr_SetCellRefreshRate()`, `StopCellRefreshThread()`, and `MarkRefreshThread()` manage refresh entries. `AfsAdmSvr_ObtainRudimentaryProperties()` maps an `IDENT` to common type/name/parent fields. `AfsAdmSvr_ObtainFullProperties()` opens the typed AfsClass object and fills status-specific union fields. `AfsAdmSvr_TestProperties()` refreshes cached properties and bumps `verProperties` on changes. `AfsAdmSvr_NotifyCallback()` reacts to AfsClass create/destroy/refresh events. `GetCurrentProperties()` and `InvalidateObjectProperties()` are typed access helpers.

Control flow: AfsClass notify create initializes an `ASOBJPROP` and stores it in `IDENT::SetUserParam()`. Refresh-end and mutation paths call `AfsAdmSvr_TestProperties()` to detect changes. Auto-refresh threads wake every minute, invalidate a cell, and run `RefreshAll()` when the configured interval has elapsed.

State and persistence: file-local static refresh-thread array and critical section. Object properties are stored as heap pointers in each `IDENT` user parameter. No durable persistence; the cache is rebuilt from AfsClass/admin calls.

Dependencies/integration: heavily integrated with AfsClass `CELL`, `SERVER`, `SERVICE`, `AGGREGATE`, `FILESET`, `USER`, and `PTSGROUP` objects, admin property structs, action refresh tracking, logging, and `GetAsidType()`.

Risks and test signals: refresh-thread entries are stopped by zeroing `idCell`; thread handles are not joined or closed. Full property collection copies sensitive user key material into `ASOBJPROP`. `AfsAdmSvr_GetCurrentProperties()` assumes `GetUserParam()` already exists after opening an object. Tests should cover each object type, missing objects setting `verPROP_NO_OBJECT`, version increment on property change, destroy of cell stopping refresh, and auto-refresh interval behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrProperties.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrProperties.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrProperties.h

Purpose: declares property-cache, AfsClass notification, and cell auto-refresh helpers for the admin server.

Important APIs/types/functions: declarations include `AfsAdmSvr_NotifyCallback()`, rudimentary/full property collection, current-property lookup, property invalidation, change testing, refresh-rate setup, refresh-thread stop, and refresh-thread timestamp marking.

Control flow: AfsClass initialization registers the callback; RPC handlers and search code call property helpers to obtain or refresh `ASOBJPROP` data.

State and persistence: no state is exposed. Implementation stores refresh-thread state privately and attaches property state to `IDENT` objects.

Dependencies/integration: includes public `WINNT/TaAfsAdmSvr.h` for `ASOBJPROP`, `ASID`, and related types.

Risks and test signals: callers receive raw `LPASOBJPROP` pointers into cache state, so tests should ensure callers do not free or retain stale pointers across object destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrProperties.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrSearch.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrSearch.cpp

Purpose: implements object search helpers for admin-server RPC handlers, including regex-style name filtering, optional refresh before search, scoped enumeration, exact lookup, and advanced user-expiration filtering.

Important APIs/types/functions: `AfsAdmSvr_Search_Compare()` caches the last `REGEXP` and supports leading `!` negation. `AfsAdmSvr_SearchRefresh()` refreshes a cell or server depending on requested object type. `AfsAdmSvr_Search_*InCell`, `*InServer`, and `VolumesInPartition` build `ASIDLIST` results. `AfsAdmSvr_Search_*InCell/Server/Partition` exact functions resolve one object id. `AfsAdmSvr_Search_OneUser()` and `OneGroup()` search cell-scoped principals. `AfsAdmSvr_Search_Advanced()` filters a list by account-expiration or password-expiration thresholds.

Control flow: search handlers optionally refresh the scope, enumerate AfsClass objects or global `IDENT` registry, apply name matching, append ASIDs, and then advanced filtering may remove list entries in place. Exact searches open typed children directly where possible, or scan cached identifiers when no direct open helper exists.

State and persistence: the regex compare function keeps static last-pattern state and compiled expression. Search results are heap `ASIDLIST`s; object/property data comes from the in-memory AfsClass cache.

Dependencies/integration: depends on `REGEXP`, AfsClass enumeration APIs, `IDENT::FindFirst/Next`, list helpers, property helpers, Windows time conversion, and `ASOBJPROP` user/group metadata.

Risks and test signals: the static regex cache is not synchronized, so concurrent searches with different patterns can race. Several exact-search loops return `FALSE` immediately on a zero-refcount object without closing enumeration, which risks iterator cleanup. Advanced password expiration uses 100ns arithmetic and must handle invalid times. Tests should cover empty and negated patterns, all object scopes, refresh modes, exact lookup misses, advanced expiration filters, and concurrent pattern searches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrSearch.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrSearch.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrSearch.h

Purpose: declares the admin-server search helper surface used by object-find RPC handlers.

Important APIs/types/functions: prototypes cover refresh, multi-result searches by cell/server/partition and object type, exact lookup by scope/name, principal-only lookup, and advanced list filtering.

Control flow: object RPC code can compose these helpers to implement `ObjectFind` and `ObjectFindMultiple` without exposing enumeration internals.

State and persistence: no header state. Implementation maintains only the regex cache and returns heap `ASIDLIST`s.

Dependencies/integration: includes `WINNT/TaAfsAdmSvr.h` for `ASID`, `ASOBJTYPE`, `AFSADMSVR_SEARCH_REFRESH`, and `AFSADMSVR_SEARCH_PARAMS`.

Risks and test signals: many functions accept output pointers and optional status pointers; integration tests should check null/missing outputs and error code propagation from failed AfsClass opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrSearch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrUser.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrUser.cpp

Purpose: implements server-side RPC handlers for AFS user account mutation.

Important APIs/types/functions: `AfsAdmSvr_ChangeUser()` compares requested KAS/PTS fields with cached `ASOBJPROP` and builds `USERPROPERTIES.dwMask`. `AfsAdmSvr_SetUserPassword()` chooses clear-string or encryption-key overload of `AfsClass_SetUserPassword()`. `AfsAdmSvr_UnlockUser()`, `CreateUser()`, and `DeleteUser()` call the corresponding AfsClass functions and track actions.

Control flow: mutating calls build an `ASACTION`, begin operation tracking, log the request, validate the client, perform AfsClass work, and end the operation. Create and delete operate on KAS and/or PTS according to supplied flags. Successful create re-tests cell properties because max user id can change.

State and persistence: no file-local state. Persistent effects are KAS/PTS account changes through AfsClass. Cache state is updated indirectly by property-test calls and AfsClass notifications.

Dependencies/integration: depends on current-property cache, action tracking, AfsClass user APIs, Windows `SYSTEMTIME` comparison, `ENCRYPTIONKEYLENGTH`, and admin-server logging.

Risks and test signals: `ChangeUser()` assumes both KAS and PTS property substructures are populated when comparing fields. Fixed string copies require bounded names/passwords. Tests should cover no-op mask generation, each mutable flag, account-expiration time comparisons, key-string vs raw-key password setting, unlock failures, create/delete combinations, and invalid client ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrUser.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/resource.h

Purpose: defines resource identifiers for the admin-server Windows executable.

Important APIs/types/functions: `IDI_MAIN` is resource id 102. The `APSTUDIO_INVOKED` block sets default resource editor values such as `_APS_NEXT_RESOURCE_VALUE`, command, control, and symbol ids.

Control flow: no runtime logic. The resource compiler and Visual Studio resource editor consume these constants.

State and persistence: no runtime state or persistence.

Dependencies/integration: integrated with the admin-server `.rc` resource file and Windows executable icon loading.

Risks and test signals: low runtime risk. Build tests should ensure `IDI_MAIN` matches the resource script and that new resources do not collide with the reserved default range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/afsapplib.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/afsapplib.cpp

Purpose: implements top-level AfsAppLib application identity and main-window hook behavior.

Important APIs/types/functions: static `g_hMain` and `g_szAppName` hold the current main window and display name. `AfsAppLib_SetAppName()`/`GetAppName()` copy the app name. `AfsAppLib_SetMainWindow()` subclasses the chosen window with `AfsAppLib_MainHook()` and removes the old hook. `AfsAppLib_MainHook()` dispatches library-private messages for cover windows, expired credentials, and modeless error dialogs, and clears the main window on `WM_DESTROY`.

Control flow: applications set the main window once during UI startup. Background threads can post library messages to that window so UI work runs on the UI thread. The hook forwards unhandled messages to the next subclass hook or default window procedure.

State and persistence: process-local app name and window handle only. No registry or file persistence.

Dependencies/integration: depends on `subclass.h` hook chaining, cover-window, credentials, and error-dialog implementations, plus Windows message dispatch.

Risks and test signals: global state means only one main window is supported. Destroy handling removes the hook by calling `AfsAppLib_SetMainWindow(NULL)` from inside the hook. Tests should cover hook install/remove, message dispatch to cover/credential/error handlers, chained subclass forwarding, and main-window destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/afsapplib.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/afsapplib.h -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/afsapplib.h

Purpose: public header for the Windows AFS Application Library. It aggregates common UI, dialog, tasking, credential, remote-admin, image, help, and utility APIs for OpenAFS Windows tools.

Important APIs/types/functions: defines `EXPORTED`, instance macros, `cchNAME`, and debug normalization. Includes TaLocale and many AfsAppLib component headers. Declares app name/main-window APIs, remote admin-server open/close/client-id APIs, cell-list management, browse user/group and fileset dialogs, cover-window APIs, credential dialogs/checks, task queue APIs, error dialogs, modeless dialog pump helpers, window data helpers, image-list helpers, help registration, font/instance helpers, animation, time conversion, error translation, local-cell lookup, and `REALLOC` via `AfsAppLib_ReallocFunction()`.

Control flow: applications include this single header, set instance/main-window/app-name state, then call specialized AfsAppLib functions. If the admin-server client header is already included, this header conditionally includes `al_admsvr.h` to remap `asc_*` calls through AfsAppLib.

State and persistence: the header declares APIs whose implementations maintain UI globals, modeless-dialog lists, task queues, settings, credentials, and admin-server client state. The header itself has no storage.

Dependencies/integration: integrates Windows APIs, TaLocale resources, OpenAFS admin client/server types, and local helper components such as hash lists, resize, subclassing, custom controls, settings, fast lists, wizard/progress, and regex.

Risks and test signals: this is a broad umbrella header with conditional macro remapping, so include order matters. Tests should compile consumers with and without `TAAFSADMSVRCLIENT_H`, DLL export/import modes, and direct `asc_*` use through AfsAppLib. API tests should also cover `REALLOC` growth and ownership conventions for returned lists/strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/afsapplib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_admsvr.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/al_admsvr.cpp

Purpose: bridges AfsAppLib and `TaAfsAdmSvrClient.lib`, letting applications that load AfsAppLib use the same initialized admin-server client context through exported wrapper functions.

Important APIs/types/functions: static state tracks `fUseAdminServer` and `idAdminServerClient`. `AfsAppLib_OpenAdminServer()` closes any previous connection, calls `asc_AdminServerOpen()`, and stores the assigned client id. `AfsAppLib_CloseAdminServer()` calls `asc_AdminServerClose()`. `AfsAppLib_GetAdminServerClientID()` returns the active id or zero. The rest of the file exports `AfsAppLib_asc_*` wrappers for list helpers, admin server open/close, credentials, local cell/error translation, actions/listeners, cell operations, object search/properties/listeners/refresh, random keys, fast property access, critical-section access, user mutations, and group mutations.

Control flow: applications call `AfsAppLib_OpenAdminServer()` once, then direct or macro-remapped `asc_*` calls enter the wrapper functions and reach the library's initialized client implementation.

State and persistence: only process-local admin-server connection state. The remote server and client library maintain the actual RPC/cache state.

Dependencies/integration: includes `TaAfsAdmSvrClient.h` and `AfsAppLib.h`; wrappers mirror the public admin-client API and are declared/remapped by `al_admsvr.h`.

Risks and test signals: wrappers are pass-through, so signature drift between `TaAfsAdmSvrClient` and AfsAppLib can silently break consumers. The open/close state is global and not synchronized. Tests should verify every wrapper delegates correct arguments, open failure reports status, close is idempotent, macro-remapped callers share the same client id, and user/group wrappers update cache through the underlying client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_admsvr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_admsvr.h -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/al_admsvr.h

Purpose: declares AfsAppLib's exported admin-server client wrappers and, for normal consumers, remaps `asc_*` symbols to those wrappers so direct admin-client calls use AfsAppLib's initialized client-library instance.

Important APIs/types/functions: prototypes cover `AfsAppLib_asc_*` list management, admin-server open/close, credentials, local cell, error translation, actions, cells, object search/properties/listen/refresh, random key, fast object access, critical-section access, user operations, and group operations. The `#ifndef EXPORT_AFSAPPLIB` block defines `asc_*` macros to `AfsAppLib_asc_*`.

Control flow: when included by an application, calls written as `asc_ObjectFind()` compile to AfsAppLib wrapper calls. When building AfsAppLib itself, `EXPORT_AFSAPPLIB` suppresses remapping so the implementation can call the real client library.

State and persistence: no state in the header; wrapper implementation stores active admin-server client id.

Dependencies/integration: requires AfsAppLib export macros and admin-client public types. It is conditionally included by `afsapplib.h` when the admin-client header has already been included.

Risks and test signals: macro remapping is include-order-sensitive and can surprise code that expects the original `asc_*` symbol addresses. Tests should compile representative consumers with direct client-library linking, AfsAppLib DLL linking, and `EXPORT_AFSAPPLIB` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_admsvr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_browse.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/al_browse.cpp

Purpose: implements the modal browse dialog for selecting AFS users or groups, with local KAS enumeration or remote admin-server enumeration.

Important APIs/types/functions: `BROWSEDIALOGPARAMS` stores cell/name selections, browse type, image list, thread state, cell list, and credentials. `AfsAppLib_ShowBrowseDialog()` constructs params and launches `IDD_APPLIB_BROWSE`. `DlgProc_Browse()` handles initialization, list selection, enter key, none checkbox, thread status, and found-name messages. `DlgProc_Browse_StartSearch()` and `StopSearch()` manage the enumeration thread. `DlgProc_Browse_ThreadProc()` chooses remote enumeration when `AfsAppLib_GetAdminServerClientID()` is nonzero, otherwise opens local client/KAS libraries. `EnumeratePrincipalsLocally()` uses KAS principal enumeration; `EnumeratePrincipalsRemotely()` opens a cell and retrieves user properties through `asc_ObjectFindMultiple()` and `asc_ObjectPropertiesGetMultiple()`.

Control flow: dialog startup fills UI text/cell choices, starts a worker thread, and receives `WM_FOUNDNAME` messages containing heap strings to add to the list. Selection updates the edit field. Changing the cell or pressing restart stops the old search and starts a new one.

State and persistence: per-dialog heap state and worker thread state only. No durable persistence. Posted strings are freed after insertion.

Dependencies/integration: depends on AfsAppLib dialog/list helpers, image resources, `al_dynlink` local library loading, KAS/client admin C APIs, remote `asc_*` APIs, credentials handles, and Windows common controls.

Risks and test signals: local enumeration does not visibly filter by `BROWSETYPE`, and remote enumeration always asks for `TYPE_USER`, so group browse behavior may be incomplete. `StopSearch()` may use `TerminateThread()` before enumeration becomes easily stoppable. Tests should cover local vs remote paths, cell changes, none checkbox behavior, cancelled searches, posted string ownership, and user/group browse modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_browse.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_browseset.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/al_browseset.cpp

Purpose: implements the modal fileset browse dialog shell for selecting a volume/fileset name.

Important APIs/types/functions: `AfsAppLib_ShowBrowseFilesetDialog()` launches `IDD_APPLIB_BROWSE_FILESET`. `BrowseSet_DlgProc()` handles dialog initialization, destruction, worker messages, selection, double-click, restart, and enter key. `BrowseSet_OnInitDialog()` configures title/prompt, image list, cell combo, selected fileset, and starts search. `BrowseSet_StartSearch()` clones parameters and creates `BrowseSet_Init_ThreadProc()`. `BrowseSet_OnAddString()` inserts fileset names and stores heap string pointers in list item data. `BrowseSet_EmptyList()` frees those strings.

Control flow: dialog startup populates cell choices and starts a worker. The worker posts start/done notifications; found names would be posted back as `WM_FOUNDNAME` and added to the list. Selecting a list item updates the edit field; OK writes the edit value to `lpp->szFileset`.

State and persistence: per-dialog state is held in the caller's `BROWSESETDLG_PARAMS` and the list item data. The worker receives a heap copy of parameters and deletes it on exit. No durable state.

Dependencies/integration: uses AfsAppLib dialog, listview, image-list, string, and cell-list helpers plus Windows threading/messages.

Risks and test signals: `BrowseSet_Init_ThreadProc()` currently contains no actual fileset enumeration, so the dialog can show an empty list while still enabling manual entry. `CreateThread()` failure is compared with `INVALID_HANDLE_VALUE`, but Windows returns `NULL` on failure. Tests should cover manual entry, empty enumeration, list string cleanup, restart behavior, cell-list disabled mode, and thread failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_browseset.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_cover.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/al_cover.cpp

Purpose: implements AfsAppLib cover windows: lightweight child/sibling dialogs that hide a window or its client area and display descriptive text plus an optional button.

Important APIs/types/functions: `COVERPARAMS` carries client-vs-window mode, target window, description, and button text. `AfsAppLib_CoverClient()` and `AfsAppLib_CoverWindow()` uncover any existing cover, clone parameters, and either call `OnCoverWindow()` directly or post `WM_COVER_WINDOW` to the main UI window. `AfsAppLib_Uncover()` removes covers. `OnCoverWindow()` creates or destroys cover dialogs identified by `dwCOVER_SIGNATURE`. `Cover_DialogProc()` initializes controls, hides covered child windows using `WS_EX_HIDDENBYCOVER`, resizes the cover, restores children on destroy, and forwards optional button clicks to the parent.

Control flow: callers request cover/uncover from any thread. If a main window exists, work is marshaled to that UI thread. Cover creation hides target content and positions the cover over the same rectangle. Uncover searches child dialogs for the signature and destroys the cover.

State and persistence: no global state beyond the resize table. Temporary cloned strings and params are freed after cover creation. Hidden child state is marked in extended window style bits until cover destroy.

Dependencies/integration: depends on AfsAppLib main-window hook, dialog helpers, resize helpers, Windows child/sibling window relationships, and cover resources/control ids.

Risks and test signals: `WS_EX_HIDDENBYCOVER` uses a high extended-style bit that could collide with platform-defined styles. Uncover logic treats invisible target windows as sibling-cover cases. Tests should cover client-area and whole-window cover modes, optional button forwarding, resize behavior, multiple cover/uncover cycles, child visibility restoration, and cross-thread posting through the main window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_cover.cpp -->
