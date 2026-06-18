# sources/distributed-fs/openafs/src/ubik/recovery.c

## Purpose
Implements ubik recovery: crash log replay, local database initialization, determining when a server has a current database, probing down peers, finding the best database version after election, fetching it to the sync site, relabeling newly initialized databases, and distributing the current database to other servers.

## Important APIs, Types, And Functions
Public functions are `urecovery_ResetState`, `urecovery_LostServer`, `urecovery_AllBetter`, `urecovery_AbortAll`, `urecovery_CheckTid`, `urecovery_Initialize`, `urecovery_Interact`, and `DoProbe`. Internal helpers are `ReplayLog` and `InitializeDB`. Important globals include `ubikPrimaryAddrOnly`, `urecovery_state`, `ubik_dbase`, `ubik_servers`, `ubik_quorum`, and `ubik_currentTrans`.

## Control Flow
Startup calls `urecovery_Initialize`, which holds the DB lock, replays any committed log, truncates the log, and reads or creates the database label. The recovery thread loops every few seconds, probes down servers periodically, exits early unless this site is sync site, polls up non-clone servers for versions, proceeds only after contacting quorum, fetches the best version via `DISK_GetFile` if local state is stale, writes the incoming database to a temporary file with an invalid label, renames and labels it on success, upgrades epoch 1 newly initialized databases to epoch 2 after quorum, and sends the current database to peers with stale versions via `DISK_SendFile`.

## State And Persistence
Persistent state includes database files, temporary fetch files, labels, and the replayed/truncated log. In-memory recovery state is a bitmask indicating sync-site, found-db, have-db, relabeled-db, and sent-db progress, plus per-server version/current/up fields. Fetch failures can invalidate local version to `0.0`; successful sends mark remote current state.

## Dependencies And Integration Points
The file is tightly coupled to `disk.c` log format, physical database callbacks, `beacon.c` sync-site/quorum/up status, `vote.c` sync/version knowledge, Rx bulk calls generated from `ubik_int.xg`, server connection/address state, transaction abort/end logic, and platform rename behavior.

## Risks And Test Signals
Risks include log format drift, recovery proceeding only after quorum version probes, temporary-file rename failure paths, invalidating old data after fetch failure, long waits for `DBWRITING`, multi-interface probe connection replacement, and frequent low-level logging while peers are down. Tests should cover committed and uncommitted log replay, new database labeling, sync-site election followed by best-version discovery, fetch success/failure, send-to-peer success/failure, down-server probing over alternate interfaces and primary-only mode, remote transaction tid mismatch aborts, and `urecovery_AllBetter` for sync and non-sync sites.
