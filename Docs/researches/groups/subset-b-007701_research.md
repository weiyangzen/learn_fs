# Research: subset-b-007701

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_callback.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_callback.c

## Purpose
`cm_callback.c` implements the Windows OpenAFS cache manager callback service and local callback lifecycle. It receives file-server callback-break RPCs, tracks callback-grant races, exposes AFS callback/debug RPC entry points, renews or expires cached callback state, and optionally gives callbacks back to file servers during shutdown or network transitions. The core invariant is that a cached `cm_scache_t` may be trusted only while its callback server and expiration state are current, or while read-only volume callback rules deliberately preserve validity.

## Important APIs and Types
Key exported cache-manager routines are `cm_InitCallback`, `cm_HaveCallback`, `cm_StartCallbackGrantingCall`, `cm_EndCallbackGrantingCall`, `cm_GetCallback`, `cm_CheckCBExpiration`, `cm_CallbackNotifyChange`, `cm_GiveUpAllCallbacks*`, and the callback RPC server functions `SRXAFSCB_*`. The file owns `cm_callbackLock`, `cm_callbackCount`, `cm_activeCallbackGrantingCalls`, and `cm_racingRevokesp`; `cm_racingRevokes_t` records callback breaks that may race with outstanding callback-granting RPCs. Global flags include `cm_OfflineROIsValid`, `cm_giveUpAllCBs`, and `cm_shutdown`.

## Control Flow
Incoming `SRXAFSCB_CallBack` maps the Rx peer to a file server/cell, then dispatches per-FID breaks to `cm_RevokeCallback` or volume breaks to `cm_RevokeVolumeCallback`. Both record a racing revoke before scanning scache buckets, then discard matching callbacks, invalidate redirector objects, and issue SMB notify-change events. `SRXAFSCB_InitCallBackState*` handles server-wide callback loss by recording a cancel-all race marker and scanning all cached vnodes from that server. `cm_GetCallback` obtains `CM_SCACHESYNC_FETCHSTATUS | CM_SCACHESYNC_GETCALLBACK`, starts race tracking, drops the scache lock for `RXAFS_FetchStatus`, uses `cm_Analyze` for retry/failover, then merges status only if `cm_EndCallbackGrantingCall` did not detect a racing revoke.

## State and Persistence
Callback state lives in memory on `cm_scache_t` (`cbServerp`, `cbExpires`, `cbIssued`) and for pure read-only volumes on `cm_volume_t` (`cbExpiresRO`, `cbServerpRO`, `creationDateRO`, `volumeSizeRO`). No durable callback state is written. A registry setting, `CallBack Notify Change Delay`, is read dynamically to delay notifications by at most five seconds.

## Dependencies and Integration Points
This file integrates with Rx callback RPC stubs, `cm_scache`, `cm_volume`, `cm_server`, `cm_conn`, redirector invalidation (`RDR_InvalidateObject`, `RDR_InvalidateVolume`), SMB notifications, freelance root handling, event/logging helpers, and XDR allocation for debug RPC replies.

## Risks and Test Signals
Race safety depends on strict lock ordering and balanced active-callback counts; tests should force callback breaks while `FetchStatus` is in flight and verify stale callbacks are not installed. Expiration tests should cover pure RO volumes, offline/all-down volumes, server multihoming, redirector invalidation, and SMB change notifications. Risk areas include long global scache scans, registry reads on every notification, pointer truncation in debug RPCs, and callback-server reference ownership in `cm_EndCallbackGrantingCall`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_callback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_callback.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_callback.h

## Purpose
`cm_callback.h` defines the public interface for callback management in the Windows cache manager. It declares the request/race-tracking structures, callback acquisition flags, file notification filter constants, exported callback lifecycle APIs, and global callback flags shared by the daemon, connection, and scache layers.

## Important APIs and Types
`cm_callbackRequest_t` captures the callback counter at the start of a callback-granting RPC, the start time used to compute expiration, and the server that granted the callback. `cm_racingRevokes_t` is the queued record for revokes that arrive while callback-granting calls are active; it stores a queue node, FID, callback count, and cancellation flags. `CM_RACINGFLAG_CANCELALL`, `CM_RACINGFLAG_CANCELVOL`, and `CM_RACINGFLAG_ALL` describe revoke scope. `CM_CALLBACK_MAINTAINCOUNT` and `CM_CALLBACK_BULKSTAT` tune `cm_EndCallbackGrantingCall` behavior. `FILE_NOTIFY_GENERIC_DIRECTORY_FILTER` and `FILE_NOTIFY_GENERIC_FILE_FILTER` define notification masks used when callback loss must wake Windows consumers.

## Control Flow
Callers wrap callback-returning RPCs with `cm_StartCallbackGrantingCall` and `cm_EndCallbackGrantingCall`. They use `cm_HaveCallback` as a cheap validity predicate and `cm_GetCallback` to fetch status and install a callback if needed. The daemon calls `cm_CheckCBExpiration`, and server/network shutdown paths call `cm_GiveUpAllCallbacks*`.

## State and Persistence
The header exposes `cm_callbackLock`, `cm_OfflineROIsValid`, `cm_giveUpAllCBs`, and `cm_shutdown`; all are process-memory controls. Persistence is intentionally absent because callbacks are server leases, not cache-disk metadata.

## Dependencies and Integration Points
The header depends on `osi.h`, `cm_scache.h`, AFS callback protocol structures, server/user/request types declared elsewhere, and Windows `FILE_NOTIFY_CHANGE_*` constants. It is consumed by files that fetch status, process file-server callbacks, run background expiration, or drain callbacks before server teardown.

## Risks and Test Signals
Consumers must observe the locking and active-count contract implied by `cm_callbackRequest_t`; mismatched start/end calls can leak race records or underflow counts. Tests should verify build visibility of all callback APIs, correct flag propagation for bulk status, and no accidental persistence assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_callback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_cell.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_cell.c

## Purpose
`cm_cell.c` manages in-memory cell objects for the Windows cache manager. It resolves cell names from registry, CellServDB, or DNS; maintains VLDB server references; performs prefix and ID lookup; initializes/restores cell tables; and handles mutable cell server-list refresh while preserving stable cell names and IDs.

## Important APIs and Types
The file operates on `cm_cell_t` and `cm_cell_rock_t` from `cm_cell.h`. Main APIs include `cm_GetCell`, `cm_GetCell_Gen`, `cm_FindCellByID`, `cm_UpdateCell`, `cm_AddCellProc`, `cm_InitCell`, `cm_ShutdownCell`, `cm_ValidateCell`, `cm_CreateCellWithInfo`, hash-table add/remove helpers, `cm_ChangeRankCellVLServer`, and `cm_DumpCells`. `cm_cellLock` protects global cell lists and hashes; each cell also has `cellp->mx` for flags and timeout fields.

## Control Flow
`cm_GetCell_Gen` normalizes the requested name, strips trailing dots, checks the name hash, then falls back to unambiguous prefix matching. If `CM_FLAG_CREATE` is supplied and no existing cell is found, it allocates from the free list or `cm_data.cellBaseAddress`, populates VL servers via `cm_SearchCellRegistry`, `cm_SearchCellFileEx`, or DNS, resolves duplicate full names, inserts the cell into name/ID hashes, and sets up linked-cell relationships. `cm_UpdateCell` refreshes invalid, empty, or expired VL server lists and randomizes same-rank servers.

## State and Persistence
Cells live in cache-manager memory under `cm_data`: `allCellsp`, `freeCellsp`, name/ID hash tables, `currentCells`, and `maxCells`. Server-list data can be refreshed from persistent registry or CellServDB inputs, or from DNS with TTL-driven expiration. The cell object itself persists only as part of the cache manager's mapped data region; mutexes and VL server lists are reinitialized on restart.

## Dependencies and Integration Points
This module integrates with `cm_config.c` for cell source lookup, `cm_server` for VL server creation/ranking/list ownership, DNS lookup controls (`cm_dnsEnabled`), volume lookup through cell IDs, and freelance mode for `Freelance.Local.Cell`.

## Risks and Test Signals
Risk concentrates in lock conversion, duplicate-name races, server references temporarily attached to a discarded cell, and DNS/registry/file fallback behavior. Test signals include exact-name and prefix matching, ambiguous-prefix rejection, trailing-dot normalization, linked-cell recursion protection, DNS TTL invalidation, free-list reuse, and validation failures for corrupted cell lists or hash membership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_cell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_cell.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_cell.h

## Purpose
`cm_cell.h` defines the Windows cache manager's cell object contract: identity, global linkage, hash linkage, VLDB server references, mutable flags, DNS expiration, linked-cell name, hash macros, and the public lookup/update APIs used throughout the cache manager.

## Important APIs and Types
`cm_cell_t` contains `magic`, `cellID`, global/name/ID/free list links, fixed cell `name`, `vlServersp`, mutex `mx`, `flags`, `timeout`, and `linkedName`. Flags identify DNS-derived server lists, invalid VL servers, freelance cells, and hash membership. `CM_CELL_NAME_HASH` and `CM_CELL_ID_HASH` map names/IDs into `cm_data` hash tables. Public routines include initialization/shutdown/validation, lookup by name or ID, server-rank changes, hash insertion/removal, server-add callback `cm_AddCellProc`, update and create-with-info paths.

## Control Flow
Most callers enter through `cm_GetCell`/`cm_GetCell_Gen` or `cm_FindCellByID`; these return cells that may have been refreshed by `cm_UpdateCell`. Configuration import and administrative updates use `cm_CreateCellWithInfo`, while config parsers pass discovered VL servers to `cm_AddCellProc`.

## State and Persistence
The header describes in-memory structures only. Persistent cell sources live in registry, CellServDB, and DNS, but the fields here cache their resolved results and expiration. `name` is documented as immutable once set, while `flags`, `timeout`, `vlServersp`, and `linkedName` have explicit lock ownership.

## Dependencies and Integration Points
The type references `cm_serverRef_t`, `cm_server_t`, `struct sockaddr_in`, and global `cm_data` sizing. It is central to connection selection, volume lookup, callback server ownership, and configuration enumeration.

## Risks and Test Signals
Consumers must respect the split between `cm_cellLock`, `cm_serverLock`, and `cellp->mx`. Tests should cover hash-table membership flags, cellID hash behavior, name length boundaries, DNS invalidation flags, and linked-cell name handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_cell.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_config.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_config.c

## Purpose
`cm_config.c` reads and writes Windows OpenAFS client configuration related to cells. It supports CellServDB file parsing/enumeration, registry CellServDB schema lookup/enumeration/update, DNS AFSDB/SRV lookup, root-cell and generic service parameter writes, and safe-ish CellServDB replacement helpers.

## Important APIs and Types
Public search APIs are `cm_SearchCellFile`, `cm_SearchCellFileEx`, `cm_SearchCellRegistry`, and `cm_SearchCellByDNS`; enumeration APIs are `cm_EnumerateCellFile` and `cm_EnumerateCellRegistry`. Persistence helpers include `cm_AddCellToRegistry`, `cm_WriteConfigString`, `cm_WriteConfigInt`, `cm_OpenCellFile`, `cm_AppendPrunedCellList`, `cm_AppendNewCell`, `cm_AppendNewCellLine`, `cm_CloseCellFile`, `cm_GetCellServDB`, `cm_GetRootCellName`, and `cm_GetConfigDir`. Local helpers parse key/value pairs and suppress lookups for probable Windows module names such as `.dll` and `.exe`.

## Control Flow
File lookup opens CellServDB, finds exact or unique partial cell matches, records linked-cell names, then parses server lines into hostnames or IPv4 literals and calls the supplied `cm_configProc_t`. Registry lookup opens `HKLM\...\OpenAFS\Client\CellServDB`, handles exact or unique prefix cell keys, reads `LinkedCell` and `ForceDNS`, then enumerates server keys, resolving `HostName`, `Rank`, `IPv4Address`, and optional VL port. DNS lookup calls `getAFSServer("afs3-vlserver", "udp", ...)` and emits configured server addresses and ranks.

## State and Persistence
This file is the persistence boundary for cell configuration. Registry writes are non-volatile under the OpenAFS client service key. CellServDB updates write `CellServDB.new`, prune old cell sections, append new content, then rename the new file over `CellServDB`. Root cell and generic config values are read/written under the service parameter registry subkey.

## Dependencies and Integration Points
It depends on Windows registry APIs, Shlwapi recursive key deletion, Winsock name resolution, StrSafe routines, `afssw_GetClientCellServDBDir`, OpenAFS DNS helpers, and callback function pointers consumed by `cm_cell.c`.

## Risks and Test Signals
Important tests should cover exact and ambiguous partial matches, linked-cell parsing, ForceDNS fallthrough, registry schema edge cases, DNS suppression for module-like names or no-TLD names, IPv4 literal fallback, long line/name boundaries, and CellServDB replacement behavior. Risks include mixed case-insensitive comparisons, legacy `gethostbyname`, partial failure cleanup, and `cm_CloseCellFile` unlink/rename ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_config.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_config.h

## Purpose
`cm_config.h` provides default Windows cache-manager configuration constants and declares the cell/configuration access functions implemented by `cm_config.c`. It is the interface used by cell initialization, administrative tools, and service startup code to locate and update client configuration.

## Important APIs and Types
Defaults include cache size, block size, async store size, cell count, stat count, chunk size, daemon count, server thread count, and trace buffer size. `cm_configFile_t` aliases `FILE`, `cm_configProc_t` receives resolved server addresses/hostnames/ranks, and `cm_enumCellProc_t` receives enumerated cell names. The header declares file, registry, DNS, and write helpers plus `AFS_THISCELL`, `AFS_CELLSERVDB_UNIX`, and `AFS_CELLSERVDB` names.

## Control Flow
Callers typically obtain a root cell with `cm_GetRootCellName`, search one or more sources for a cell with `cm_SearchCellRegistry`, `cm_SearchCellFileEx`, or `cm_SearchCellByDNS`, and receive each server through a callback such as `cm_AddCellProc`. Administrative changes use registry write helpers or the open/append/close file sequence for CellServDB.

## State and Persistence
The declared functions read and write registry values and CellServDB files, but the header itself contains no storage. The defaults are compile-time values used when registry or command-line configuration is absent.

## Dependencies and Integration Points
The interface requires Windows networking structures, `stdio.h` unless `__CM_CONFIG_INTERFACES_ONLY__` is set, and `CELL_MAXNAMELEN` expectations from the cell layer. It is consumed by `cm_cell.c`, startup configuration, and management paths that create cells.

## Risks and Test Signals
Tests should verify ABI compatibility of callback signatures, default values used by startup, buffer sizes promised by the APIs, and correct behavior when `__CM_CONFIG_INTERFACES_ONLY__` excludes implementation-facing declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_conn.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_conn.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_conn.h

## Purpose
`cm_conn.h` declares the Windows cache manager's connection and request-analysis contract. It defines timeout defaults, connection objects, per-request retry/error tracking, AFS volume special errors, capability helpers, and the APIs used by filesystem operations to obtain and analyze Rx connections.

## Important APIs and Types
`cm_conn_t` stores list linkage, server pointer, Rx connection pointer, held user, mutex, refcount, ucell generation, flags, and crypt level. `cm_req_t` stores request start time, categorized error state, retry counters, flags, and path context from SMB or redirector callers. Flags include no-retry, forced-new-connection, source markers, WOW64, volume-updated, and offline-volume-check markers. Exported routines include initialization, `cm_Analyze`, server/volume/FID connection selection, Rx connection reference retrieval, GC, server availability, and connection forcing.

## Control Flow
Callers pass a `cm_req_t` through connection acquisition and RPC retry loops. A successful `cm_ConnFromFID` or `cm_ConnFromVolume` returns a held `cm_conn_t` that is normally released by the following `cm_Analyze` call. Callers use `SERVERHAS64BIT`/`SERVERHASINLINEBULK` macros to gate file-server feature use and mark unsupported features via the corresponding setters.

## State and Persistence
The header exposes timeout globals and `rx_pmtu_discovery`, all in-process runtime settings initialized elsewhere. Request state is transient per operation; connection state is transient per server/user/security tuple.

## Dependencies and Integration Points
It includes `cm_server.h` and Rx headers, references user, FID, cell, volume, server-ref, callback, fetch-status, and volsync structures, and provides constants used by SMB/redirector-facing operations.

## Risks and Test Signals
Tests should validate request flag behavior, refcount ownership expectations, timeout defaults for SMB versus redirector mode, replicated connection separation, and handling of AFS special volume errors. Header changes are high blast radius because most RPC call sites depend on these signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_conn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_daemon.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_daemon.c

## Purpose
`cm_daemon.c` implements Windows cache manager background threads: periodic maintenance, lock checking, IP-address change monitoring, and asynchronous fetch/store queues. It keeps server/volume/callback/token state fresh and decouples expensive cache I/O work from foreground SMB/redirector operations.

## Important APIs and Types
Global intervals include down/up server checks, volume refresh, callback expiration, lock checks, token cache checks, offline-volume checks, server ranking, redirector extent shaking, hook reloads, and access-cache cleanup. `daemon_state_t` owns one queue, lock, counters, and head/tail pointers for background requests. Public APIs are `cm_InitDaemon`, `cm_DaemonShutdown`, and `cm_QueueBKGRequest`; worker functions include `cm_IpAddrDaemon`, `cm_BkgDaemon`, `cm_LockDaemon`, and `cm_Daemon`.

## Control Flow
`cm_InitDaemon` clamps daemon count to an even value, starts detached IP, maintenance, lock, and per-queue background worker threads, and initializes queue locks. `cm_QueueBKGRequest` chooses a queue by FID hash and read/write operation class, suppresses duplicate fetch/store requests, holds scache/user refs, and wakes a worker. `cm_BkgDaemon` chooses a non-blocking, server-available request from the tail, invokes its procedure, and requeues transient retryable failures. `cm_Daemon` loops every 500 ms and performs scheduled checks for server reachability, volume refresh, callback expiration, token cache cleanup, offline volumes, server ranking, firewall configuration, network-address changes, redirector extents, performance tuning, and optional hook DLL callbacks.

## State and Persistence
Daemon state is in memory only: queues, counters, shutdown events, interval globals, and `daemon_ShutdownFlag`. Intervals are initialized from registry values in `cm_DaemonCheckInit`; no daemon queue contents persist across process restart.

## Dependencies and Integration Points
The file integrates with Rx client thread startup, pthreads, Windows events/services/firewall APIs, IP helper `NotifyAddrChange`, SMB listener and VC handling, redirector buffer management, server/volume/callback/token modules, power-suspend state, and optional `afsdhook` DLLs.

## Risks and Test Signals
Risk areas include queue starvation, requeue loops on persistent failures, duplicate suppression correctness, shutdown waiting, firewall side effects, and address-change timing. Tests should cover even daemon count clamping, fetch/store queue partitioning, transient error requeue, deleted scache handling, suspend behavior, registry interval overrides, and daemon-triggered callback expiration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_daemon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_daemon.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_daemon.h

## Purpose
`cm_daemon.h` declares the public daemon controls and background request contract for the Windows cache manager. It exposes maintenance intervals, daemon count, shutdown/init entry points, and the structure used to queue asynchronous scache work.

## Important APIs and Types
Extern interval variables configure server down/up checks, volume checks, callback checks, lock checks, and token checks. `cm_bkgProc_t` is the callback signature for background jobs and must free its rock according to the header comment. `cm_bkgRequest_t` stores queue linkage, procedure, opaque rock, scache/user references, and a copied `cm_req_t`. Public entry points are `cm_InitDaemon`, `cm_DaemonShutdown`, and `cm_QueueBKGRequest`. `CM_MIN_DAEMONS` and `CM_MAX_DAEMONS` bound worker count and require an even daemon count.

## Control Flow
Foreground cache operations allocate a rock and call `cm_QueueBKGRequest`; daemon workers later invoke the `cm_bkgProc_t` against the held scache/user/request. Startup calls `cm_InitDaemon`, and service shutdown calls `cm_DaemonShutdown` to wake and wait for workers.

## State and Persistence
The header exposes in-process state only. Queued requests, interval variables, and daemon count do not persist; the implementation may initialize intervals from registry settings.

## Dependencies and Integration Points
The types depend on `osi_queue_t`, `cm_scache_t`, `cm_user_t`, and `cm_req_t`. The queue is used by background store, direct write, redirector fetch, and prefetch paths declared elsewhere.

## Risks and Test Signals
Tests should confirm rock ownership, reference ownership, daemon-count bounds, duplicate request behavior in the implementation, and that background procedure failures are correctly requeued or released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_daemon.h -->
