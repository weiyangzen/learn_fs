<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientPing.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientPing.h

Purpose: declares the ping and callback-thread lifecycle helpers for the admin-server client library.

Important APIs/types/functions: `StartPingThread(UINT_PTR idClient)`, `StopPingThread(UINT_PTR idClient)`, `StartCallbackThread()`, and `StopCallbackThread()` are the only exported helpers.

Control flow: admin-server open logic starts pinging once it receives a client id, and close/error handling stops pinging. Callback consumers start and stop the callback host around listener registration.

State and persistence: no state is exposed; implementation uses private static arrays and handles.

Dependencies/integration: depends on Windows threading and RPC behavior through the implementation; callers only need the admin-client type set and `UINT_PTR`.

Risks and test signals: the API does not report failures to create threads, so integration tests need to observe behavior indirectly through pings and callbacks rather than return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientPing.h -->
