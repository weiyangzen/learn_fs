# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvr.cpp

Purpose: implements the core server-side RPC entry points declared by `ITaAfsAdmSvr.idl` for connection, credentials, cell/object lookup, object property cache access, refresh invalidation, callbacks, and random key generation.

Important APIs/types/functions: `AfsAdmSvr_Connect/Ping/Disconnect` manage client cookies. Credential APIs wrap `afsclient_TokenQuery`, `afsclient_TokenGetExisting`, `afsclient_TokenGetNew`, and cell credential assignment. Cell APIs call `CELL::OpenCell()`/`CloseCell()`. Object find/get APIs dispatch to `AfsAdmSvr_Search_*`, `AfsAdmSvr_GetCurrentProperties()`, `AfsAdmSvr_ObtainFullProperties()`, and list helpers. `AfsAdmSvr_CallbackHost()` runs the callback manager, and `AfsAdmSvr_GetRandomKey()` delegates to `AfsClass_GetRandomKey()`.

Control flow: most entry points begin an operation, validate `idClient`, perform type checks with `GetAsidType()`, call the AFS class/client subsystem, write `pStatus` on failure through helper macros, and end the operation. Search refreshes scope when requested, uses optimized one-user/one-group lookup where possible, then dispatches based on search scope type and requested object type. Property queries return data only when the server version is newer unless `RETURN_DATA_ALWAYS` is requested.

State/persistence: server state includes client registrations, operation/action tracking, opened cell identities, credentials bound to cells, object property caches, and callback queues. Persistent changes are delegated to AFS cell operations and token management.

Dependencies/integration: depends on winsock headers, roken, AFS client libraries, `AfsClass`, `AfsAppLib`, generated RPC types, and many internal admin-server helpers from `TaAfsAdmSvrInternal.h`.

Risks/test signals: every RPC boundary depends on client-cookie validation and correct `AfsAdmSvr_EndOperation()` balancing. Some copy operations use fixed `STRING` buffers. `asc_CredentialsSet()` clients send plaintext passwords to this interface. Tests should cover invalid ASID/client combinations, search dispatch matrix, cache version filtering, full-property upgrade, operation cleanup on failures, callback host shutdown, and RPC exception behavior from clients.
