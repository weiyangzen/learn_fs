<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGeneral.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGeneral.cpp

Purpose: centralizes admin-server process state: synchronization, client lifetime, operation/action tracking, startup/shutdown, auto-shutdown, name resolution, auto-open, and minimum refresh scope.

Important APIs/types/functions: `CLIENTINFO` stores client name, resolved address, and last ping. `OPERATION` stores active action metadata and start tick. `AfsAdmSvr_Enter()`/`Leave()` guard shared state. `AfsAdmSvr_AttachClient()`, `DetachClient()`, `PingClient()`, and `fIsValidClient()` manage client handles. `AfsAdmSvr_BeginOperation()`/`EndOperation()` track actions and post callbacks. `AfsAdmSvr_GetOperation()`/`GetOperations()` return action snapshots. `AfsAdmSvr_Startup()` initializes AfsClass and notification callback; `AfsAdmSvr_AutoShutdownThread()` stops RPC listening when idle. `AfsAdmSvr_AutoOpen_ThreadProc()` opens and refreshes the default cell.

Control flow: startup registers the AfsClass notification callback and starts the idle-shutdown monitor. RPC handlers validate client ids, begin an operation when needed, call AfsClass work, and end operations through helper wrappers. The shutdown thread periodically detaches stale clients, checks active operations/clients/idle time, and stops RPC listening if auto-shutdown is enabled.

State and persistence: static process state includes operational flag, critical section, client array, callback object, auto-shutdown state, operation array, action counter, and minimum refresh scope. There is no durable persistence; AfsClass cache contents live in memory.

Dependencies/integration: integrates with Windows sockets/RPC, `AfsClass_Initialize`, `CELL::OpenCell`, admin callback posting, `TaAfsAdmSvrProperties` refresh hooks, list helpers, and logging.

Risks and test signals: client ids are raw `CLIENTINFO*` pointers, so stale pointers are rejected only by list membership and ping age. `AfsAdmSvr_AutoShutdownThread()` calls `AfsAdmSvr_DetachClient()` while already holding the same non-recursive critical section, which is a deadlock risk unless the platform behavior or call path avoids it. First-use critical-section initialization is unsynchronized. Tests should cover stale client detachment, operation callback start/finish, auto-shutdown idle timing, command-line auto-open scope, and invalid client rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGeneral.cpp -->
