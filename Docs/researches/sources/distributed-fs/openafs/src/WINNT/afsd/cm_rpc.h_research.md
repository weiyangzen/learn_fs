# sources/distributed-fs/openafs/src/WINNT/afsd/cm_rpc.h

## Purpose
`cm_rpc.h` declares the afsd RPC token side-channel interface used by the Windows cache manager and includes the MIDL-generated RPC declarations.

## Important APIs
- `cm_RegisterNewTokenEvent(afs_uuid_t uuid, char sessionKey[8], clientchar_t *)` registers a pending session-key handoff.
- `cm_FindTokenEvent(afs_uuid_t uuid, char sessionKey[8], clientchar_t **)` consumes a pending handoff.
- `RpcInit()` starts the RPC server.
- `RpcShutdown()` stops it.

## Control flow and state behavior
This header only declares functions. Runtime state is implemented in `cm_rpc.c` as a global token-event list protected by a mutex and a listener shutdown event.

## Dependencies and integration points
It includes `afsrpc.h`, which must provide the RPC interface, UUID type, and generated server/client declarations. It also depends on `clientchar_t` from the cache-manager string layer.

## Risks and edge cases
The API exposes raw 8-byte session-key buffers and pointer ownership for SID strings; callers must follow the implementation's ownership convention exactly. No length is passed for the session key because the protocol fixes it at 8 bytes.

## Test signals
Compile and RPC IDL compatibility tests should verify declarations match the generated interface. Runtime behavior is covered by `cm_rpc.c` tests for registration, lookup, and server lifecycle.
