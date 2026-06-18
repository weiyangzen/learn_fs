<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_rx_stats.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_rx_stats.c

## Purpose
Demonstrates retrieving detailed RX runtime statistics from an RX debug endpoint.

## Important APIs, Types, And Functions
The core calls are `afsclient_RXDebugOpenPort`, `util_RXDebugRxStats`, and `afsclient_RXDebugClose`. The returned data includes `afs_RXDebugRxStats_t` and supported-stat metadata.

## Control Flow
The sample parses target host/port, initializes libadmin, opens RX debug, calls `util_RXDebugRxStats`, closes the handle, and prints available counters, timings, and packet statistics according to the supported-stat flags.

## State And Persistence
It reads live RX process counters and writes no state. Local state is one handle and one stats snapshot.

## Dependencies And Integration Points
It integrates with RX debug stats RPCs and sample build libraries for client/admin utility support.

## Risks And Test Signals
Version and support-bit handling are the primary concerns. Tests should cover services with full stats, partial stats, and unsupported debug calls, plus port validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_rx_stats.c -->
