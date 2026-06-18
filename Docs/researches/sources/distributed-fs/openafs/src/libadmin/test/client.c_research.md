<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/client.c -->
# sources/distributed-fs/openafs/src/libadmin/test/client.c

## Purpose
Implements the client-related `afscp` subcommands. It exercises libadmin client APIs for local cell lookup, mount point creation, AFS server discovery, RX stats state/list/clear/version operations, and cache-manager stats queries.

## Important APIs, Types, And Functions
The file defines interface-function mappings for RXAFS, RXAFSCB, BOZO, KAA/KAM/KAT, PR, RXSTATS, ubik disk/vote, VL, and volserver interfaces, including NT-specific `pthread_once` initialization. Command handlers include `DoClientLocalCellGet`, `DoClientMountPointCreate`, `DoClientAFSServerGet`, `DoClientAFSServerList`, `DoClientRPCStatsStateGet/Enable/Disable`, `DoClientRPCStatsList`, `DoClientRPCStatsClear`, `DoClientRPCStatsVersionGet`, `DoClientCMGetServerPrefs`, `DoClientCMListCells`, `DoClientCMLocalCell`, `DoClientCMClientConfig`, and `SetupClientAdminCmd`.

## Control Flow
Client commands use the global authenticated `cellHandle` prepared by `afscp.c`. RPC stats commands convert `-process` either to an `afs_stat_source_t` through a prefix match or to a numeric port, convert `-stat_type` to peer/process, open the proper RPC stats connection, then query, enable, disable, list, clear, or get version. Listing prints interface headers and per-function counters. CM commands open the cache-manager stats port, iterate server preferences or cells, or fetch local-cell/config snapshots. `SetupClientAdminCmd` registers every syntax and attaches common auth options.

## State And Persistence
Many operations are read-only, but mount point creation writes into AFS namespace state and RX stats enable/disable/clear mutates remote service stats state. Local transient state includes RX connections, iterators, function-list mappings, and output structs.

## Dependencies And Integration Points
It depends on generated RPC interface headers for function names, `afs_clientAdmin.h`, `afs_utilAdmin.h`, RX/rxstat, cellconfig, bosint, ubik, and `common.h`. It integrates the standalone sample patterns into one command-driven test harness.

## Risks And Test Signals
Visible risks include a typo in the enum value `afs_proc_tESS_STATS`, prefix matching that accepts abbreviated process names and may be ambiguous, no port range enforcement in `GetStatPortFromString`, duplicated `afs_uint32 taddr` declaration in `Print_afs_CMServerPref_p` in this checkout, and some `printf` calls using `as->parms[PORT].items->data` even when `-port` is optional and absent. Tests should cover every registered syntax, optional port defaults, named and numeric process selection, peer/process stats transitions, partial clear flags, mount point creation, iterator completion, and Windows function-list initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/client.c -->
