<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_clear_process.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_clear_process.c

## Purpose
Implements a sample `rxstat clear process` command that clears process-level RPC statistics on a selected RX service.

## Important APIs, Types, And Functions
The structure mirrors `rxstat_clear_peer.c`, but `util_RPCStatsClear` is invoked with `RXSTATS_ClearProcessRPCStats`. Command options are `-cell`, `-server`, `-port`, and optional `-localauth`.

## Control Flow
The handler parses command options, validates the UDP port, gets either local-auth or existing tokens, opens the execution cell and RPC stats connection, clears all process counters with `AFS_RX_STATS_CLEAR_ALL`, and closes the connection, cell, and token.

## State And Persistence
The only durable effect is resetting process RPC stats on the remote server. No local files are modified.

## Dependencies And Integration Points
It integrates with authenticated RX stats admin RPCs and the `cmd` command parser. The build installs it as one of the shipped rxstat sample tools.

## Risks And Test Signals
Risks match the peer clear sample: broad all-counter reset, incomplete cleanup on intermediate failure, and auth dependency. Test signals are successful reset of process counters, unchanged peer counters, and expected authorization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_clear_process.c -->
