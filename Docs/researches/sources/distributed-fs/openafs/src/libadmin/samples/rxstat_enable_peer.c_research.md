<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_enable_peer.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_enable_peer.c

## Purpose
Implements a sample command to enable peer RPC statistics collection on a selected RX service.

## Important APIs, Types, And Functions
The command handler calls `util_RPCStatsStateEnable(conn, RXSTATS_EnablePeerRPCStats, &st)` after the standard `cmd` option parsing, token acquisition, cell open, and RPC stats connection sequence.

## Control Flow
It validates `-port`, obtains local-auth or existing tokens for `-cell`, opens `-server` at the requested port, enables peer stat collection, closes connection/cell/token, and returns zero on success.

## State And Persistence
The remote daemon's peer-stat collection state is changed. Local state is transient.

## Dependencies And Integration Points
It depends on OpenAFS admin authentication, RX stats service support, and command-parser registration in `main`.

## Risks And Test Signals
Signals include query state changing from disabled to enabled, later `rxstat_get_peer` producing counters, and proper rejection of unauthorized or unsupported targets. Early errors can skip cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_enable_peer.c -->
