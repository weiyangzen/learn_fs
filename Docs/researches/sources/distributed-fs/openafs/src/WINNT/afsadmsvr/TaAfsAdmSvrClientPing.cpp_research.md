<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientPing.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientPing.cpp

Purpose: maintains the client-side keepalive and callback-host threads for admin-server RPC clients. The ping path prevents the server from considering a client stale; the callback-host path keeps an RPC call open so the server has a context for callbacks.

Important APIs/types/functions: static state stores `hPingThread`, sparse `adwClients`, `cdwClients`, `hCallbackThread`, and callback reference count `cReqCallback`. `StartPingThread()` appends a client id and creates `ClientPingThread()` on first use. `StopPingThread()` clears a client slot. `ClientPingThread()` sleeps `csecAFSADMSVR_CLIENT_PING`, calls `AfsAdmSvr_Ping()`, and drops clients reporting `ERROR_INVALID_HANDLE`. `StartCallbackThread()`/`StopCallbackThread()` reference-count the callback host. `ClientCallbackThread()` runs `AfsAdmSvr_CallbackHost()`.

Control flow: the ping thread loops forever, temporarily leaving the client lock while making each RPC so other client operations can progress. Callback hosting starts when the first requester asks for callbacks and is force-terminated when the count reaches zero.

State and persistence: process-local static thread handles, client-id array, and callback refcount. There is no durable state; stale client entries are only zeroed.

Dependencies/integration: uses admin-client RPC stubs, `RpcTryExcept`, AfsAppLib `REALLOC`, Windows `CreateThread`, `Sleep`, and `TerminateThread`, all synchronized by `asc_Enter()`/`asc_Leave()`.

Risks and test signals: the ping thread has no normal exit and never closes thread handles. `StopCallbackThread()` uses `TerminateThread()`, which can leak RPC/runtime resources if the target is inside RPC. Tests should simulate invalid handles, multiple clients, repeated start/stop callback reference counts, and server shutdown causing `AfsAdmSvr_CallbackHost()` to return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientPing.cpp -->
