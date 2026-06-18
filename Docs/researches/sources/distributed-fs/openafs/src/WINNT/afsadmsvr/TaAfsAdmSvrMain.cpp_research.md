<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrMain.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrMain.cpp

Purpose: contains the admin-server executable entry point, RPC server registration/listening lifecycle, debug memory window hook, and MIDL allocation callbacks.

Important APIs/types/functions: `main()` initializes Winsock, parses keywords for timed auto-shutdown, manual startup, user/volume scope, and debug mode. It registers `ITaAfsAdminSvr_v1_0_s_ifspec`, attempts endpoint `AFSADMSVR_ENDPOINT_DEFAULT`, registers bindings with the endpoint mapper, starts `AfsAdmSvr_Startup()`, optionally launches `AfsAdmSvr_AutoOpen_ThreadProc()`, then calls `RpcServerListen()`. `MIDL_user_allocate()` and `MIDL_user_free()` route RPC memory through OpenAFS allocation helpers.

Control flow: the process prepares RPC, starts server internals, listens until stopped, then shuts down internals and unregisters RPC interfaces/endpoints. Debug builds can create a thread running memory-manager UI messages.

State and persistence: no private persistent state beyond process RPC registration. Runtime effects are endpoint mapper registration and in-memory AfsClass cache startup.

Dependencies/integration: depends on Windows RPC, Winsock, admin-server internal modules, generated MIDL interface symbol `ITaAfsAdminSvr_v1_0_s_ifspec`, OpenAFS allocation, and command keywords from public headers.

Risks and test signals: `RpcServerUseProtseq()` is called before `RpcServerUseProtseqEp()`, and the endpoint fallback/error handling is unusual because `fExportedBinding` remains false. Tests should cover command-line scope combinations, endpoint already in use, endpoint mapper registration/unregistration, startup failure that still reports errors to clients, and MIDL allocation/free pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrMain.cpp -->
