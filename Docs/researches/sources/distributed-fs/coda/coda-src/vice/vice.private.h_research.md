# sources/distributed-fs/coda/coda-src/vice/vice.private.h

## Purpose

`sources/distributed-fs/coda/coda-src/vice/vice.private.h` is a private server header collecting cross-file prototypes for client/host table management, callback management, error formatting, logging, reintegration retry behavior, and RPC timeout selection.

## Important APIs, Types, and Functions

It declares `CLIENT_InitHostTable`, `CLIENT_Build`, `CLIENT_Delete`, `CLIENT_CleanUpHost`, `CLIENT_GetWorkStats`, `CLIENT_PrintClients`, `CLIENT_CallBackCheck`, `CLIENT_MakeCallBackConn`, `ViceErrorMsg`, `Die`, `GetEtherStats`, `InitCallBack`, `ViceLog`, `DeleteCallBack`, `BreakCallBack`, `DeleteVenus`, `DeleteFile`, `check_reintegration_retry`, and `srv_rpc2_timeout`.

## Control Flow

There is no executable control flow. The header provides compile-time linkage between server modules such as `srvproc2.cc`, callback code, connection-management code, and RPC timeout logic.

## State and Persistence Behavior

No storage is defined here except external references. The declared functions manipulate in-memory client/host/callback state and server retry policy in their implementation files.

## Dependencies and Integration Points

The prototypes depend on `RPC2_Handle`, `RPC2_Integer`, `SecretToken`, `ClientEntry`, `HostTable`, `ViceFid`, and `struct timeval`, which are supplied by the surrounding server headers. It is included by files that need private server internals without exposing them as public Coda client ABI.

## Risks and Edge Cases

There is no include guard, and `InitCallBack` is declared twice. This works only because prototypes are identical, but future signature changes can drift. The variadic `ViceLog(int...)` declaration is nonstandard-looking and relies on compiler compatibility.

## Test Signals

Compile all server translation units with warnings enabled, especially duplicate declarations and C/C++ linkage checks; exercise client build/delete/cleanup and callback teardown paths that consume these prototypes.
