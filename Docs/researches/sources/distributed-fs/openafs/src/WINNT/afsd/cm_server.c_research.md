# sources/distributed-fs/openafs/src/WINNT/afsd/cm_server.c

## Purpose
`cm_server.c` manages known VLDB and file servers for the Windows cache manager. It tracks server identity, reachability, capabilities, ranking/preference, per-server volume references, server-reference lists used by cells/volumes, network-interface ranking inputs, and diagnostic dumps.

## Important APIs and functions
- Global locks/state: `cm_serverLock`, `cm_syscfgLock`, `cm_serversAllFirstp`, `cm_serversAllLastp`, `cm_numFileServers`, `cm_numVldbServers`, interface arrays, and `cm_LanAdapterChangeDetected`.
- `cm_NewServer()`, `cm_FindServer()`, `cm_FindServerByIP()`, and `cm_FindServerByUuid()` create or find server objects.
- `cm_GetServer()`, `cm_PutServer()`, and no-lock variants maintain server refcounts.
- `cm_PingServer()`, `cm_CheckServersSingular()`, `cm_CheckServersMulti()`, and `cm_CheckServers()` probe reachability and capabilities.
- `cm_RankServer()`, `cm_RankUpServers()`, and `cm_SetServerIPRank()` compute active server rank from admin preference, local network proximity, random jitter, and RX performance statistics.
- `cm_NewServerRef()`, `cm_InsertServerList()`, `cm_ChangeRankServer()`, `cm_RandomizeServer()`, `cm_FreeServerList()`, and `cm_AppendServerList()` maintain sorted server reference lists.
- `cm_MarkServerDown()`, `cm_ForceNewConnectionsAllServers()`, `cm_ServerClearRPCStats()`, and capability flag setters update connection and server state.
- `cm_DumpServers()` and `cm_ServerEqual()` support diagnostics and identity comparisons.

## Control flow
Server creation first searches for an existing server by address/type, attaches UUID/cell metadata if missing, or allocates a new server and links it into the global list. Unless probing is suppressed, new servers are initially marked down, ranked, and pinged.

Pinging obtains an unauthenticated connection when networking is available, performs the VLDB or file-server probe, updates up/down state, capabilities, volume online/offline status, connection state, and rank. Multi-check mode batches file-server `RXAFS_GetCapabilities` probes and VLDB `VL_ProbeServer` probes using `multi_Rx`, while singular mode pings each selected server individually. Registry value `MultiCheckServers` selects the mode.

Ranking updates local IP rank from interface/subnet comparisons, incorporates admin rank if present, folds in RX peer RPC timing and congestion-window data, adds jitter, and then reorders volume or cell server lists if the rank changes enough.

## State and persistence behavior
Server state is in memory and protected by `cm_serverLock`, per-server `mx`, and `cm_syscfgLock`. It records address, type, connection list, flags, capabilities, cell pointer, refcount, ping concurrency, ranks, served volume IDs, down time, and UUID. Persistence is indirect: admin preferences and multi-check behavior may come from registry/DNS/user commands, but this file itself does not write persistent state.

## Dependencies and integration points
It depends on RX connections and peer stats, VLDB/file-server RPC probes, cell and volume modules (`cm_ChangeRankVolume`, `cm_ChangeRankCellVLServer`, `cm_FindVolumeByID`, `cm_UpdateVolumeStatus`), connection garbage collection, Windows registry access, network interface discovery via `syscfg_GetIFInfo`, and OSI locks/queues. It is the server-selection backbone for volume and connection code.

## Risks and edge cases
- `cm_CheckServersMulti()` allocates several arrays without checking each allocation before use.
- `cm_DumpServers()` calls `ctime(&tsp->downTime)` and trims the returned string even when the server is up; if `ctime` returns NULL this would fail.
- `cm_NewServer()` logs a two-cell association path that dereferences `tsp->cellp` and `cellp`; malformed calls with NULL can be unsafe in that branch.
- Ranking uses floating point/log and random jitter; tests need tolerances rather than exact ranks.
- The list-free paths deliberately drop `cm_serverLock` in `cm_FreeServer()` to obey lock hierarchy, so refcount races must be covered.
- Background probe creation passes `cm_PingServer` to `pthread_create`; signature compatibility depends on platform typedefs/build settings.

## Test signals
Tests should cover server creation deduplication by IP/port/type/UUID, cell attachment, up/down transitions, capability update, multi-check and singular probe paths, network-interface ranking, admin rank precedence, sorted insertion and reranking of server refs, deletion with nonzero refs, volume-ID tracking, no-network behavior, and server equality with and without UUID support.
