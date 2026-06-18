<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_disable_process.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_disable_process.c

## Purpose
Implements a sample command to disable process-level RPC statistics collection on a selected RX service.

## Important APIs, Types, And Functions
It uses `cmd` parsing, libadmin token/cell helpers, `afsclient_RPCStatOpenPort`, and `util_RPCStatsStateDisable` with `RXSTATS_DisableProcessRPCStats`.

## Control Flow
The command opens an authenticated RPC stats connection to `-server -port`, switches process stats collection off, and closes token, cell, and connection handles.

## State And Persistence
It mutates remote RX stats collection state for process counters. No local persistent state is written.

## Dependencies And Integration Points
The file integrates with the same rxstat command family and OpenAFS admin token model as the peer disable sample.

## Risks And Test Signals
Tests should confirm process state transitions to disabled, peer state remains independent, invalid ports are rejected, and missing privileges fail cleanly. Cleanup leaks on early return remain a sample-code risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_disable_process.c -->
