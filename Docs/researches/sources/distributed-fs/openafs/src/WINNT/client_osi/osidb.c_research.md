<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidb.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osidb.c

Purpose: Implements the server side of the OSI remote debugging RPC interface. It exposes ping, format lookup, logical fd open/read/close, and server initialization for local OSI diagnostic collections.

Important APIs, types, and functions: `osi_maxCalls` defaults to `OSI_MAXRPCCALLS`. `debugType` is the RPC object type UUID. `dbrpc_Ping` is a no-op health check. `dbrpc_GetFormat` looks up an `osi_fdType_t` and an `osi_fdTypeFormat_t` by name, region, and index. `dbrpc_Open` allocates a debug fd by type name and returns it in an `osi_remHyper_t`. `dbrpc_GetInfo` resolves the fd and calls its `GetInfo` op. `dbrpc_Close` closes and frees the fd. `osi_InitDebug` initializes OSI, fd support, RPC protocol sequences, interface registration, object UUID typing, endpoint registration, and optionally starts listening under `OSISTARTRPCSERVER`.

Control flow and state: RPC calls are thin dispatchers over the fd registry in `osifd.c`. Open creates a process-local 32-bit fd id and projects it into a 64-bit wire field. GetInfo initializes counts to zero before dispatching so failure paths do not leak stale data. Initialization is guarded by `osi_Once`; only the first successful caller performs RPC registration.

Persistence and dependencies: No disk persistence is used. Runtime state lives in the Microsoft RPC endpoint mapper, registered bindings, fd registries, and the exported object UUID. Dependencies include `windows.h`, `rpc.h`, generated `dbrpc.h`, OSI initialization, fd APIs, and `osi_uid_t` UUID values.

Integration points: Remote UI code in `osidebug.c` calls the generated `dbrpc_*` methods. Debuggable subsystems register fd types such as `type`, `sleep`, `lock`, and `log:<name>` with format descriptors. AFS service startup can call `osi_InitDebug` with an instance UUID so external tools can bind to a specific process.

Risks: `dbrpc_GetFormat` uses `strncpy` without explicit null termination if the source exactly fills the target. The fd number is only locally unique and stored in the low 32 bits. RPC registration errors abort initialization but there is no cleanup of earlier registration steps. The server exposes process diagnostics through RPC; endpoint exposure and ACL behavior are not visible in this file.

Test signals: Exercise `osi_InitDebug` idempotence, endpoint registration failure paths, opening unknown types (`OSI_DBRPC_NOFD` / `NOENTRY`), iterating known fd types, format EOF behavior, GetInfo count initialization, and Close on invalid fds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidb.c -->
