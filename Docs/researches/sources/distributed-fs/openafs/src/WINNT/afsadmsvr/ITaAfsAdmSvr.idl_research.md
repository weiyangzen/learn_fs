# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/ITaAfsAdmSvr.idl

Purpose: MIDL RPC contract for the OpenAFS Windows administration server interface.

Important APIs/types/functions: defines `ITaAfsAdminSvr` with UUID `ae274620-dea3-11d1-bfb3-00a024c0d1ef`, implicit binding handle `hBindTaAfsAdminSvr`, and imports `ITaAfsAdmSvrTypes.idl`. Operations cover client lifecycle (`Connect`, `Disconnect`, `Ping`), credentials (`Crack/Get/Set/Push`), local cell and error translation, action queries, cell open/close, object find/get/refresh, callback hosting and action callback, random key generation, user/group administration, cell property changes, and refresh-rate configuration.

Control flow: clients connect to obtain an `idClient`, keep it alive with ping every `csecAFSADMSVR_CLIENT_PING`, open a cell with credentials, query or mutate objects, receive callbacks through `AfsAdmSvr_CallbackHost()`, and disconnect. Many calls return Boolean-like `int` plus an out `ULONG *pStatus` for detailed errors.

State/persistence: the IDL defines remote state handles: client cookies, credential handles, ASID object identifiers, server-side object caches, and action lists. Persistence is in the server and underlying AFS cell, not the IDL.

Dependencies/integration: depends on MIDL, RPC runtime, and the shared types file. Generated headers/stubs are consumed by server implementations (`TaAfsAdmSvr*.cpp`) and client wrappers (`TaAfsAdmSvrClient*.cpp`).

Risks/test signals: interface compatibility is critical because IDL changes affect generated ABI and marshaling. Passwords are accepted as plain `STRING` parameters. Tests should include MIDL generation, client/server round trips, callback thread behavior, allocation/free semantics for returned lists, invalid client cookies, and cross-version compatibility.
