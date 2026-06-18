
# sources/distributed-fs/openafs/src/ubik/vote.c

`vote.c` implements Ubik's vote/election state machine and debug RPCs. It enforces the lease-style invariant that a site cannot vote yes for two different sync-site candidates within `BIGTIME`, tracks the current sync-site claim, excludes clone servers from candidacy, and exposes current state to `udebug`.

Important APIs are `uvote_ShouldIRun`, `uvote_GetSyncSite`, `SVOTE_Beacon`, `SVOTE_Debug`, `SVOTE_XDebug`, `SVOTE_SDebug`, `SVOTE_XSDebug`, old debug variants, `uvote_Init`, `uvote_set_dbVersion`, `uvote_eq_dbVersion`, and `uvote_HaveSyncAndVersion`. `vote_globals` stores last yes vote time/host/state, current sync host/time, lowest host seen, and the sync site's db version/tid.

Election control flow begins with beacons. `SVOTE_Beacon` maps the caller to a primary Ubik address, rejects unknown hosts, recognizes clones, updates the lowest eligible host, refreshes or expires current sync-host knowledge, applies heuristics to avoid election loops, and grants a yes vote only when the prior yes lease is expired or the same host is renewing. On a yes vote it records the candidate's version and tid, then calls `urecovery_CheckTid` under the database lock so stale write transactions are aborted when a new tid arrives.

`uvote_ShouldIRun` tells the beacon module whether this server should seek votes: clones never run, valid other sync sites suppress candidacy, and lower-address valid candidates defer this host. `uvote_GetSyncSite` returns the last yes host only while its sync-site claim is still within `SMALLTIME`. Debug functions package vote, beacon, disk, lock, recovery, active write, tid, epoch, interface, and peer states into generated RPC structs, with old-struct compatibility.

State is in-memory and time-based; no direct disk persistence occurs here, but db version/tid values influence recovery and remote version-label acceptance. Dependencies include `ubik_servers`, `ubik_host`, `amIClone`, `beacon_globals`, `udisk_Debug`, `ulock_Debug`, `ubeacon_Debug`, and Rx caller identity. Risks include subtle time-skew assumptions, primary-address mapping correctness, election-loop prevention, and old debug casts. Test signals include clone behavior, unknown-host beacon rejection, lower-host deferral, BIGTIME vote lockout, sync-site expiry, db version comparisons, and debug RPC compatibility.
