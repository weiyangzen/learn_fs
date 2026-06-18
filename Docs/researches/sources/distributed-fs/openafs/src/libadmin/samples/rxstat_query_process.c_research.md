<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_query_process.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_query_process.c

## Purpose
Implements a sample command to query whether process RPC statistics collection is enabled on a target RX service.

## Important APIs, Types, And Functions
The file mirrors `rxstat_query_peer.c` but passes `RXSTATS_QueryProcessRPCStats` to `util_RPCStatsStateGet`.

## Control Flow
The command registers required `-server` and `-port` options, validates the port, opens a null-cell RPC stats connection, queries process stats state, prints enabled/disabled, and closes handles.

## State And Persistence
It is read-only and does not alter local or remote counters.

## Dependencies And Integration Points
It depends on libadmin client/util APIs, RX stats constants, and the command parser. It pairs with the process enable/disable/get/clear commands.

## Risks And Test Signals
Test signals include correct state transitions after process enable/disable, behavior with disabled stats, and clean error returns for unavailable endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_query_process.c -->
