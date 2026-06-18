<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_process.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_process.c

## Purpose
Implements a sample command to retrieve process-level RX RPC statistics from a target service.

## Important APIs, Types, And Functions
Like `rxstat_get_peer.c`, it maps interface IDs through `GetPrintStrings`, but process stats omit the remote host address in the header. The core APIs are `afsclient_RPCStatOpenPort`, `util_RPCStatsGetBegin` with `RXSTATS_RetrieveProcessRPCStats`, `util_RPCStatsGetNext`, `util_RPCStatsGetDone`, and `afsclient_RPCStatClose`.

## Control Flow
The command parses `-server` and `-port`, validates the port, opens a null-cell RPC stats connection, iterates all process stats records, starts a new interface heading when `func_index == 0`, prints function names and timing/counter data, validates iterator completion, and closes resources.

## State And Persistence
The program reads remote process counters and does not modify them.

## Dependencies And Integration Points
It depends on generated RPC interface symbol arrays from fileserver, callback, ptserver, ubik, vldb, bos, kas, and volserver headers. It is built as a standalone sample.

## Risks And Test Signals
Risks are generated-header drift and zero-index grouping assumptions. Tests should compare output with enabled process stats, disabled stats behavior, unknown interface handling, and iterator cleanup on completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_process.c -->
