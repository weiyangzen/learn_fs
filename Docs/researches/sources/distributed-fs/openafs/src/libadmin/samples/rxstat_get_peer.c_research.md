<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_peer.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_peer.c

## Purpose
Implements a sample command to retrieve and print peer-level RX RPC statistics from a target service.

## Important APIs, Types, And Functions
`GetPrintStrings` maps RX interface IDs to human-readable interface names and generated function-name arrays (`RXAFS_function_names`, `PR_function_names`, `VL_function_names`, `BOZO_function_names`, etc.). `rxstat_get_peer` opens a null cell and RPC stats connection, starts `util_RPCStatsGetBegin(conn, RXSTATS_RetrievePeerRPCStats, ...)`, loops with `util_RPCStatsGetNext`, and closes with `util_RPCStatsGetDone`.

## Control Flow
The command accepts `-server` and `-port`. Each returned `afs_RPCStats_t` represents one function index. When index zero appears, the sample prints a new header including remote peer address, port, server/client role, and interface name. For each function it prints invocation counts, bytes sent/received, queue timing, and execution timing, or `Never invoked`.

## State And Persistence
It is read-only. Iterator state is transient and owned by util admin until `Done`.

## Dependencies And Integration Points
It directly includes many RPC interface headers to access function-name arrays and stat-index constants. It integrates with RX stats retrieval RPCs and the OpenAFS `cmd` parser.

## Risks And Test Signals
Risk lies in keeping interface ID mappings and function-count arrays aligned with generated RPC headers. Unknown function indexes are handled, but unknown interfaces only get numeric labels. Tests should retrieve stats from services exposing several interfaces, verify address/role formatting, and check `ADMITERATORDONE` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_peer.c -->
