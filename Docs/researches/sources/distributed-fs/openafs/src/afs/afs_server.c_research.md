# sources/distributed-fs/openafs/src/afs/afs_server.c

## Purpose

`afs_server.c` owns Cache Manager server and server-address records: liveness state, multihomed address lists, address preference ranking, connection refresh, and server-related performance counters. The file maintains the global server hash table `afs_servers[NSERVERS]`, the server-address hash table `afs_srvAddrs[NSERVERS]`, and allocation/debug counters such as `afs_totalServers` and `afs_totalSrvAddrs`. It is a core integration layer between VLDB/file-server discovery, Rx connections, callback state, volume/cache invalidation, and `afs_stats_cmperf` server up/down accounting.

## Important APIs, Types, and Functions

Important exported routines include `afs_MarkServerUpOrDown`, `afs_ServerDown`, `afs_CountServers`, `ForceAllNewConnections`, `afs_CheckServers`, `afs_LoopServers`, `afs_FindServer`, `afs_random`, `afs_randomMod15`, `afs_randomMod127`, `afs_SortOneServer`, `afs_SortServers`, `afsi_SetServerIPRank`, `afs_GetCapabilities`, `afs_GetServer`, `afs_ActivateServer`, `afs_RemoveAllConns`, and `afs_MarkAllServersUp`. The main data structures come from `afsincludes.h`: `struct server`, `struct srvAddr`, `struct cell`, `struct afs_conn`, `struct unixuser`, `struct volume`, and callback/cache structures. `GetUpDownStats` selects the correct `afs_stats_cmperf.fs_UpDown` or `vl_UpDown` bucket, split by same-cell versus different-cell and by file-server versus VL-server port.

## Control Flow and State

Server-down handling starts in `afs_ServerDown`, which short-circuits if either the logical server or address is already down, calls `afs_MarkServerUpOrDown`, and logs file-server or VL-server loss through `print_internet_address`. `afs_MarkServerUpOrDown` updates `SRVADDR_ISDOWN` on a specific address and `SRVR_ISDOWN` only when all addresses of a multihomed server are down; on recovery, any up address marks the server up, but aggregate uptime stats are updated only when all addresses share the same state. It records downtime start/end, incident counts, duration buckets, and never-down counts.

Periodic probing flows through `afs_CheckServers`, which delegates to `afs_LoopServers` with `CkSrv_GetCaps`. `afs_LoopServers` snapshots `afs_srvAddrs` under `afs_xserver`/`afs_xsrvAddr`, creates Rx connections for eligible addresses, shortens dead time for down servers, and invokes callback functions over arrays of `afs_conn` and `rx_connection`. VL servers are probed separately by `CheckVLServer` using `VL_ProbeServer`; file servers are checked through `RXAFS_GetCapabilities` in `CkSrv_GetCaps`. `CkSrv_MarkUpDown` converts RPC results into server-up/server-down transitions and wakes waiters when needed.

Server lookup and creation are centered on `afs_GetServer`. It first checks existing non-multihomed or UUID/multihomed records under shared locking. If updates are needed, it respects the lock order `afs_xvcb` before `afs_xserver`, obtains `afs_xsrvAddr`, allocates or reuses `struct server` and `struct srvAddr` instances, moves addresses between server records, creates orphan server records for removed multihomed addresses, recomputes address ranks, sorts address lists, updates global stats, optionally fetches capabilities, and returns the canonical server. Address changes trigger `afs_FlushServer`, which resets affected volumes, flushes callbacks, frees callback records, and removes empty server records.

## Dependencies and Integration Points

This file depends on Rx multi-call support (`rx/rx_multi.h`), file-server RPCs (`RXAFS_GetCapabilities`), VLDB RPCs (`VL_ProbeServer`), cell and user lookup (`afs_GetCellStale`, `afs_GetUser`, `afs_PutUser`), connection management (`afs_ConnBySA`, `afs_ConnByHost`, `afs_PutConn`, `ForceNewConnections`), callback/vcache state (`afs_vhashT`, `afs_FlushServerCBs`, `afs_HaveCallBacksFrom`), and volume reset code (`afs_ResetVolumes`). Platform-specific ranking inspects interface tables or user-space interface data, with separate Solaris, Darwin, FreeBSD, OpenBSD, NetBSD, SGI, and generic paths.

## Persistence and Side Effects

No on-disk records are written here directly, but long-lived kernel state is mutated heavily: server/address hash tables, connection vectors, callback records, volume state, address rankings, and performance statistics. Server activation records timestamps and contributes to `afs_stats_cmperf`; server removal frees kernel memory only when address lists are detached. Logs are emitted through `afs_warnall` via `print_internet_address`.

## Risks and Test Signals

The main risks are lock-order regressions, stale server/address aliases during multihomed updates, races between snapshots and connection use, incorrect address ranking on platform-specific network stacks, and stats under/over-counting when partial multihomed outages occur. `afs_GetServer` is especially sensitive because it moves `srvAddr` records, flushes volumes/callbacks, and may call `afs_GetCapabilities` while manipulating locks. Useful tests include simulated VLDB address changes, multihomed partial-failure recovery, server-down/up probes with Rx failures, address ranking with multiple local interfaces, capability fallback on `RXGEN_OPCODE`, and stress tests that run server checks while volume/callback caches are active.
