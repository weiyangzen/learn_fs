<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_admsvr.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/al_admsvr.cpp

Purpose: bridges AfsAppLib and `TaAfsAdmSvrClient.lib`, letting applications that load AfsAppLib use the same initialized admin-server client context through exported wrapper functions.

Important APIs/types/functions: static state tracks `fUseAdminServer` and `idAdminServerClient`. `AfsAppLib_OpenAdminServer()` closes any previous connection, calls `asc_AdminServerOpen()`, and stores the assigned client id. `AfsAppLib_CloseAdminServer()` calls `asc_AdminServerClose()`. `AfsAppLib_GetAdminServerClientID()` returns the active id or zero. The rest of the file exports `AfsAppLib_asc_*` wrappers for list helpers, admin server open/close, credentials, local cell/error translation, actions/listeners, cell operations, object search/properties/listeners/refresh, random keys, fast property access, critical-section access, user mutations, and group mutations.

Control flow: applications call `AfsAppLib_OpenAdminServer()` once, then direct or macro-remapped `asc_*` calls enter the wrapper functions and reach the library's initialized client implementation.

State and persistence: only process-local admin-server connection state. The remote server and client library maintain the actual RPC/cache state.

Dependencies/integration: includes `TaAfsAdmSvrClient.h` and `AfsAppLib.h`; wrappers mirror the public admin-client API and are declared/remapped by `al_admsvr.h`.

Risks and test signals: wrappers are pass-through, so signature drift between `TaAfsAdmSvrClient` and AfsAppLib can silently break consumers. The open/close state is global and not synchronized. Tests should verify every wrapper delegates correct arguments, open failure reports status, close is idempotent, macro-remapped callers share the same client id, and user/group wrappers update cache through the underlying client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_admsvr.cpp -->
