<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_disable_peer.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_disable_peer.c

## Purpose
Implements a sample command to disable collection of peer RPC statistics on a selected RX service.

## Important APIs, Types, And Functions
The handler `rxstat_disable_peer` uses the same command/auth/connection setup as the clear commands and calls `util_RPCStatsStateDisable(conn, RXSTATS_DisablePeerRPCStats, &st)`.

## Control Flow
It parses `-cell`, `-server`, `-port`, and `-localauth`; validates port; obtains a token; opens the cell and RPC stats port; disables peer stats collection; closes all handles; and returns command-parser status.

## State And Persistence
It changes remote in-process RX stats collection state for peer counters. The persistence duration depends on the target daemon's RX stats implementation, not this sample.

## Dependencies And Integration Points
It depends on RX stats service support and administrative authorization. It is linked and optionally installed by `samples/Makefile.in`.

## Risks And Test Signals
Disabling stats can hide later observability, so tests should restore state afterward. Signals include query-before/query-after showing peer stats disabled, process stats unaffected, and failure with invalid auth or unsupported target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_disable_peer.c -->
