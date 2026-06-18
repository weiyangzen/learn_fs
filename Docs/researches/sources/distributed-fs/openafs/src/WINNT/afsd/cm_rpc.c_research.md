# sources/distributed-fs/openafs/src/WINNT/afsd/cm_rpc.c

## Purpose
`cm_rpc.c` implements the Windows RPC side channel used to transfer AFS session keys between client applications and the AFS service without sending keys in cleartext through pioctl data. A pioctl supplies a UUID, and the RPC call supplies the matching UUID plus session key under RPC packet privacy/authentication.

## Important APIs and functions
- `tokenEvent_t` stores a one-use UUID, DES session key, optional caller SID string, and list link.
- `cm_RegisterNewTokenEvent()` pushes a new token event into the global list under `tokenEventLock`.
- `cm_FindTokenEvent()` finds and removes the matching UUID, returns the session key, and either returns or frees the SID string.
- `AFSRPC_SetToken()` is an RPC manager entry point that impersonates the caller, extracts token statistics and SID, converts the SID to a string, and registers the event.
- `AFSRPC_GetToken()` is an RPC manager entry point that consumes a registered event by UUID.
- `midl_user_allocate()` and `midl_user_free()` provide MIDL allocation hooks.
- `RpcListen()` registers the RPC interface, auth info, and endpoint, then listens until stopped.
- `RpcInit()` initializes the mutex/event and starts the listener thread.
- `RpcShutdown()` stops listening and waits for listener cleanup.

## Control flow
The normal token handoff has two paths converging on `tokenEvents`: `AFSRPC_SetToken()` records a UUID/session-key pair, while the pioctl side later calls `cm_FindTokenEvent()` to consume it. Entries are single-use and removed on successful lookup. The server startup path creates a listener thread, registers `afsrpc_v1_0_s_ifspec`, registers WinNT authentication, registers the endpoint, and calls `RpcServerListen`. Shutdown stops listening and waits on `rpc_ShutdownEvent`, which the listener sets during cleanup.

## State and persistence behavior
Global mutable state consists of `tokenEvents`, `tokenEventLock`, and `rpc_ShutdownEvent`. Token events live only in memory and are not persisted. The SID string is owned by the event until the consumer takes it or lookup frees it. The RPC shutdown event is a named Windows event (`afsd_rpc_ShutdownEvent`).

## Dependencies and integration points
It depends on Windows RPC, SDDL/SID APIs, thread token APIs, the MIDL-generated `afsrpc` interface, OpenAFS threading/event wrappers, `smb_GetUserSID`, and rxkad token structures. It integrates with pioctl token-management code through UUID matching and with SMB/user identity handling through SID capture.

## Risks and edge cases
- `cm_RegisterNewTokenEvent()` does not check `malloc` failure.
- Token events have no timeout or cap; abandoned events can accumulate if the pioctl side never consumes them.
- `AFSRPC_SetToken()` registers an event even if impersonation or SID extraction fails, in which case the SID may be NULL but the session key still enters the list.
- `RpcInit()` calls `CloseHandle(listenThread)` without guarding against `CreateThread` failure; if `listenThread` is NULL, Windows behavior should be checked.
- `RpcListen()` can log `task` after failure only if each failure path assigned it; current assignments cover visible failure jumps.

## Test signals
Tests should cover one-use UUID consumption, missing UUID failure, SID return versus SID free paths, concurrent registration and lookup under lock, RPC listener start/stop, caller impersonation failure, and stale event accumulation under failed or interrupted token setup.
