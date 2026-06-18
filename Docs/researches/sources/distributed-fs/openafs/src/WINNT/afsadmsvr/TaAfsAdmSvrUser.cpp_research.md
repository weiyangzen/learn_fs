<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrUser.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrUser.cpp

Purpose: implements server-side RPC handlers for AFS user account mutation.

Important APIs/types/functions: `AfsAdmSvr_ChangeUser()` compares requested KAS/PTS fields with cached `ASOBJPROP` and builds `USERPROPERTIES.dwMask`. `AfsAdmSvr_SetUserPassword()` chooses clear-string or encryption-key overload of `AfsClass_SetUserPassword()`. `AfsAdmSvr_UnlockUser()`, `CreateUser()`, and `DeleteUser()` call the corresponding AfsClass functions and track actions.

Control flow: mutating calls build an `ASACTION`, begin operation tracking, log the request, validate the client, perform AfsClass work, and end the operation. Create and delete operate on KAS and/or PTS according to supplied flags. Successful create re-tests cell properties because max user id can change.

State and persistence: no file-local state. Persistent effects are KAS/PTS account changes through AfsClass. Cache state is updated indirectly by property-test calls and AfsClass notifications.

Dependencies/integration: depends on current-property cache, action tracking, AfsClass user APIs, Windows `SYSTEMTIME` comparison, `ENCRYPTIONKEYLENGTH`, and admin-server logging.

Risks and test signals: `ChangeUser()` assumes both KAS and PTS property substructures are populated when comparing fields. Fixed string copies require bounded names/passwords. Tests should cover no-op mask generation, each mutable flag, account-expiration time comparisons, key-string vs raw-key password setting, unlock failures, create/delete combinations, and invalid client ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrUser.cpp -->
