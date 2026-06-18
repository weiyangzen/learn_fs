<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_query_peer.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_query_peer.c

## Purpose
Implements a sample command to query whether peer RPC statistics collection is enabled on a target RX service.

## Important APIs, Types, And Functions
The handler calls `util_RPCStatsStateGet(conn, RXSTATS_QueryPeerRPCStats, &state, &st)` and prints an `afs_RPCStatsState_t` as enabled or disabled.

## Control Flow
`main` registers `-server` and `-port` with the command parser. The handler validates the port, initializes libadmin, opens a null cell and RPC stats connection, queries peer stats state, closes the connection and cell, and returns command status.

## State And Persistence
No mutation occurs. It reads remote peer-stat collection state.

## Dependencies And Integration Points
It is a diagnostic companion to the peer enable/disable/clear/get samples and depends on RX stats query support.

## Risks And Test Signals
Tests should verify state matches after enable/disable operations, invalid ports fail, and unsupported services return a meaningful libadmin status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_query_peer.c -->
