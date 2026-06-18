# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientBind.cpp

Purpose: implements client-side binding to the admin server and fallback process launch.

Important APIs/types/functions: `BindToAdminServer()` composes an RPC string binding for TCP endpoint `AFSADMSVR_ENDPOINT_DEFAULT`, validates it, and optionally retries for 15 seconds. `UnbindFromAdminServer()` disconnects and frees the global binding handle. `ForkNewAdminServer()` locates and `WinExec`s `TaAfsAdmSvr.exe Timed Manual`. `ValidateBinding()` temporarily assigns `hBindTaAfsAdminSvr` and calls `AfsAdmSvr_Connect()`. `ResolveAddress()` resolves hostnames to IPv4 strings.

Control flow: binding first tries the well-known endpoint, because namespace export may fail on some Windows versions. If validation succeeds, the binding becomes global. If binding fails with call-failed and caller can wait, it sleeps/retries. Local open code can fork a hidden timed/manual server and then bind again.

State/persistence: mutates global generated RPC binding handle `hBindTaAfsAdminSvr`. Launching the server creates a separate process; no file persistence.

Dependencies/integration: depends on Winsock, Windows RPC, generated admin-server binding globals, command constants in `TaAfsAdmSvr.h`, and client open logic.

Risks/test signals: endpoint 1025 can collide, `ResolveAddress()` has simplistic numeric-IP detection, and `UnbindFromAdminServer()` shadows `status` inside `RpcTryExcept`. Tests should cover remote address, local auto-fork, retry timeout, invalid binding rollback, hostname resolution failures, and RPC exception paths.
