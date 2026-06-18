# sources/distributed-fs/openafs/src/WINNT/afsd/cm_conn.c

## Purpose
`cm_conn.c` owns Rx connection caching, server selection, request retry analysis, timeout configuration, and per-request error interpretation for the Windows cache manager. It translates volume/server/cell state into concrete Rx connections and decides whether failed RPCs should retry, fail over, refresh volume locations, mark servers down, discard callbacks, or surface errors.

## Important APIs and Types
Primary APIs are `cm_InitConn`, `cm_InitReq`, `cm_Analyze`, `cm_GetServerList`, `cm_GetVolServerList`, `cm_ConnByMServers`, `cm_ConnByServer`, `cm_ConnFromFID`, `cm_ConnFromVolume`, `cm_GetRxConn`, `cm_PutConn`, `cm_GCConnections`, `cm_ServerAvailable`, and `cm_ForceNewConnections`. It owns `cm_connLock`, timeout globals (`ConnDeadtimeout`, `HardDeadtimeout`, `IdleDeadtimeout`, `ReplicaIdleDeadtimeout`, `NatPingInterval`, `RDRtimeout`), and feature knobs (`cryptall`, `cm_anonvldb`, `rx_pmtu_discovery`).

## Control Flow
Callers initialize `cm_req_t`, obtain server lists from a FID or volume, and call `cm_ConnByMServers` to walk ranked `cm_serverRef_t` lists while skipping deleted/down/busy/offline servers and honoring `reqp->errorServp`. `cm_ConnByServer` reuses or creates per-server/per-user/per-replication connections, rebuilding Rx connections when credentials or crypto settings change. After an RPC, `cm_Analyze` inspects the returned code, updates request error fields, logs events, forces new connections, refreshes volume locations, marks server refs busy/offline/deleted, discards invalid callbacks, and returns retry guidance.

## State and Persistence
Connection state is in memory under each `cm_server_t->connsp`, with reference counts and mutex-protected Rx handles. Timeout defaults come from compile-time constants, Windows LanmanWorkstation registry values, and OpenAFS service registry values. No connection state is durable.

## Dependencies and Integration Points
The module integrates with Rx/rxkad security classes, Windows registry, SMB redirector timeout behavior, server and volume modules, user token/ucell state, callback acquisition (`cm_callbackRequest_t`), and event logging. File-server capability macros in the header depend on `cm_server` flags.

## Risks and Test Signals
`cm_Analyze` is the main risk surface because retry decisions depend on nuanced AFS, Rx, ubik, and Windows error semantics. Tests should cover token expiry, RX_CALL_DEAD with forced new connections, VNOVOL/VMOVED/VOFFLINE volume updates, all-busy/all-offline/all-down lists, invalid fetch status, PMTU RX_MSGSIZE retry, anonymous VLDB mode, NAT pings, and connection garbage collection with user VC refs.
