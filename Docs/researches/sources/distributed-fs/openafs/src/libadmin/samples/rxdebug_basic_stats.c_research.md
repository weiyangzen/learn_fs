<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_basic_stats.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_basic_stats.c

## Purpose
Demonstrates retrieving basic RX debug counters from a target RX service.

## Important APIs, Types, And Functions
The program defines `Usage`, `ParseArgs`, and `main`, opens an RX debug handle with `afsclient_RXDebugOpenPort`, calls `util_RXDebugBasicStats`, closes with `afsclient_RXDebugClose`, and prints fields from `afs_RXDebugBasicStats_t`.

## Control Flow
It parses a host and port, initializes libadmin, opens the RX debug connection, fetches basic stats, closes the handle, and prints packet counts, call counts, connection counts, packet pools, and related basic RX runtime values.

## State And Persistence
The sample reads live RX runtime state and persists nothing. The only owned resources are the RX debug handle and local stats struct.

## Dependencies And Integration Points
It depends on RX/rxstat headers, client admin connection helpers, and util admin RX debug APIs. It is useful as a smoke test for service `rxdebug` support.

## Risks And Test Signals
It assumes the target supports the requested debug RPC and that fields match the printed struct version. Test signals are port validation, successful stats retrieval, and expected failure against a non-RX or non-debug service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_basic_stats.c -->
