# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCallback.h

Purpose: declares callback manager APIs for the admin server.

Important APIs/types/functions: defines `CALLBACKTYPE` with `cbtACTION`, declares `AfsAdmSvr_CallbackManager()`, `AfsAdmSvr_PostCallback(CALLBACKTYPE, BOOL, LPASACTION)`, and `AfsAdmSvr_StopCallbackManagers()`.

Control flow: server code starts a callback host loop, posts action callbacks as operations change, and stops managers during shutdown.

State/persistence: no header state; implementation uses a process-global callback queue and event.

Dependencies/integration: includes `TaAfsAdmSvr.h` for shared types. Integrated with generated RPC callback routines and action tracking.

Risks/test signals: adding callback types requires updating both enum and dispatch switch. Compile tests should catch mismatches with `TaAfsAdmSvrCallback.cpp`.
