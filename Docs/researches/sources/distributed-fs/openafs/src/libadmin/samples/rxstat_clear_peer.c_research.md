<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_clear_peer.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_clear_peer.c

## Purpose
Implements a sample `rxstat clear peer` command that clears peer RPC statistics on a selected RX service.

## Important APIs, Types, And Functions
The command handler `rxstat_clear_peer` is registered by `main` through `cmd_CreateSyntax`. It uses `cmd_OptionAsString`, `cmd_OptionAsInt`, `cmd_OptionAsFlag`, `afsclient_Init`, `afsclient_TokenPrint` or `afsclient_TokenGetExisting`, `afsclient_CellOpen`, `afsclient_RPCStatOpenPort`, `util_RPCStatsClear`, `afsclient_RPCStatClose`, `afsclient_CellClose`, and `afsclient_TokenClose`.

## Control Flow
The command requires `-cell`, `-server`, and `-port`, with optional `-localauth`. It validates the port, obtains server tickets from the local keyfile or existing user tokens, opens the cell and RPC stats connection, clears all peer counters via `RXSTATS_ClearPeerRPCStats` and `AFS_RX_STATS_CLEAR_ALL`, then closes resources.

## State And Persistence
It mutates remote RX peer-stat counters by resetting them. Local state is only authentication, cell, and connection handles.

## Dependencies And Integration Points
It depends on the OpenAFS `cmd` parser, server config directory `AFSDIR_SERVER_ETC_DIR`, RX stats constants, and authenticated libadmin RPC stats APIs.

## Risks And Test Signals
It always clears all peer counters and has no partial-clear option. Failure paths may leave earlier handles open. Tests should verify auth modes, port range rejection, peer counters resetting to zero, and permission failure with insufficient tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_clear_peer.c -->
