# sources/distributed-fs/openafs/src/ubik/beacon.c

## Purpose
Implements ubik beaconing and sync-site election. It builds the server list, initializes security connections, sends periodic vote beacons, determines whether the local site has quorum, handles clone/magic-host voting behavior, and exchanges multihomed address information.

## Important APIs, Types, And Functions
Public functions include `ubeacon_Debug`, `ubeacon_AmSyncSite`, `ubeacon_SyncSiteAdvertised`, `ubeacon_InitServerListByInfo`, `ubeacon_InitServerList`, `ubeacon_InitSecurityClass`, `ubeacon_NewVOTEConnection`, `ubeacon_ReinitServer`, `ubeacon_Interact`, `ubeacon_updateUbikNetworkAddress`, and `ubik_SetClientSecurityProcs`. Internal helpers are `amSyncSite`, `ubeacon_InitServerListCommon`, and `verifyInterfaceAddress`. Important globals include `nServers`, `amIMagic`, `amIClone`, `ubik_singleServer`, security callbacks, `addr_globals`, `beacon_globals`, `ubik_quorum`, and `ubik_servers`.

## Control Flow
Initialization verifies the local interface address, initializes a client security class, builds remote `ubik_server` records with separate vote and disk Rx connections, detects clone servers, chooses the lowest-address magic host for tie-breaking, computes quorum, and special-cases single-server cells as sync site. `ubeacon_Interact` loops every `POLLTIME`, skips if another candidate is better, multicasts `VOTE_Beacon` calls, validates returned vote times and connection errors, updates per-server up/vote state, asks the local vote module for a self-vote, and sets or clears sync-site state based on weighted vote totals. Address exchange calls `DISK_UpdateInterfaceAddr` on remotes and updates alternate addresses.

## State And Persistence
The file maintains in-memory cluster membership/election state: server connection lists, vote times, server up/down flags, sync-site expiration, advertised status, epoch time, security class/index, and local interface addresses. It does not directly write the ubik database, but becoming sync site updates `version_globals.ubik_epochTime` under database/version locks.

## Dependencies And Integration Points
It integrates with Rx/rx_multi, rxkad/rxnull security, cell config/netinfo/netrestrict parsing, ubik vote service, ubik disk service, recovery reset/lost-server hooks, `ubik_dbase` locking/version state, and server address utilities. It is tightly coupled with `vote.c`, `recovery.c`, `remote.c`, and `ubik.p.h` internals.

## Risks And Test Signals
Risks include election timing invariants, lock ordering between DB/beacon/address/version locks, stale security token reconnection, multihomed address verification errors, clone quorum handling, and treating anomalous positive vote values as transport/security failures. Tests should cover single-server startup, clone servers, even-sized magic-host tie-break, vote expiry, loss/regain of quorum, netinfo/netrestrict address selection, `DISK_UpdateInterfaceAddr` compatibility errors, token refresh, and recovery reset when sync-site status is lost.
