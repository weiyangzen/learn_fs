<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_enable_process.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_enable_process.c

## Purpose
Implements a sample command to enable process-level RPC statistics collection on a selected RX service.

## Important APIs, Types, And Functions
The handler is identical in structure to the peer enable command but calls `util_RPCStatsStateEnable` with `RXSTATS_EnableProcessRPCStats`.

## Control Flow
Command parsing gathers `-cell`, `-server`, `-port`, and `-localauth`; the handler validates the port, opens authenticated admin state, enables process stats, and closes the opened handles.

## State And Persistence
It changes the remote service's process-stat collection state. No local data is persisted.

## Dependencies And Integration Points
It is part of the installed rxstat sample suite and depends on libadmin client/util APIs plus RX stats constants.

## Risks And Test Signals
Tests should query process state before and after enable, check that peer state is not accidentally changed, and verify auth and port validation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_enable_process.c -->
