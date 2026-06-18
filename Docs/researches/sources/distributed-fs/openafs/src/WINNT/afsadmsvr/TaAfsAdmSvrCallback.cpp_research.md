# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCallback.cpp

Purpose: manages server-to-client callback delivery for admin-server events, currently action start/finish notifications.

Important APIs/types/functions: `CALLBACKDATA` stores callback type, finished flag, and optional copied `ASACTION`. `AfsAdmSvr_CallbackManager()` owns the callback loop. `AfsAdmSvr_PostCallback()` queues callback data and signals the event. `AfsAdmSvr_StopCallbackManagers()` requests shutdown. `AfsAdmSvr_FreeCallbackData()` releases copied action data.

Control flow: the first manager creates a manual-reset event and hash list. The manager waits, stops if requested, otherwise copies queued callbacks to a local list while holding the admin lock, clears the shared queue/event, releases the lock, invokes generated callback functions with exceptions swallowed, frees each item, and repeats. The last manager deletes the list and closes the event.

State/persistence: static struct `l` stores event handle, callback list, stop flag, and manager count. No disk persistence.

Dependencies/integration: depends on admin-server locking (`AfsAdmSvr_Enter/Leave`), OpenAFS `HASHLIST`, generated RPC callback `AfsAdmSvrCallback_Action()`, and action structures from the IDL.

Risks/test signals: callbacks are best-effort and exceptions are suppressed, so clients can miss notifications without server failure. `fStopManagers` is not reset when a new manager starts after shutdown. Tests should cover concurrent posting, no-lock callback invocation, manager start/stop cycles, callback exception swallowing, and queue cleanup.
