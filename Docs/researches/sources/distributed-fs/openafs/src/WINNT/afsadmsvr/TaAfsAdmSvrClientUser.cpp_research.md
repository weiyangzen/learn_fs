<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientUser.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientUser.cpp

Purpose: implements client-side `asc_User*` wrappers for user mutation RPCs. Each wrapper calls the corresponding server RPC and refreshes or invalidates the local client cache afterward so UI callers see updated properties.

Important APIs/types/functions: `asc_UserChange()`, `asc_UserPasswordSet()`, `asc_UserUnlock()`, `asc_UserCreate()`, and `asc_UserDelete()` wrap `AfsAdmSvr_ChangeUser()`, `AfsAdmSvr_SetUserPassword()`, `AfsAdmSvr_UnlockUser()`, `AfsAdmSvr_CreateUser()`, and `AfsAdmSvr_DeleteUser()`. Password setting accepts either a clear string or `ENCRYPTIONKEYLENGTH` bytes. Successful create/change/unlock/password operations call `asc_ObjectPropertiesGet(GET_ALL_DATA, ...)`.

Control flow: every function enters an `RpcTryExcept` block, performs the mutation, refreshes cache state on success, catches RPC exceptions as `RPC_S_CALL_FAILED_DNE`, and only writes `*pStatus` on failure.

State and persistence: the file stores no private state. Its observable state effect is client cache refresh through `asc_ObjectPropertiesGet()`. Delete deliberately calls a cache-refresh path expected to fail so the cache can remove stale data.

Dependencies/integration: depends on generated admin-server RPC stubs, `TaAfsAdmSvrClientInternal.h`, cache/property helpers, Windows string routines, and the `AFSADMSVR_*USER_PARAMS` structures.

Risks and test signals: success paths do not set `*pStatus`, matching older API style but requiring callers to check the Boolean return. `lstrcpy()` into fixed `STRING` buffers assumes bounded RPC inputs. Tests should cover RPC exception mapping, cache refresh after each successful mutation, delete cache cleanup, password string-vs-key selection, and status propagation only on failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientUser.cpp -->
