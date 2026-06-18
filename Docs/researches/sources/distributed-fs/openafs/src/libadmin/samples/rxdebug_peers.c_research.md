<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_peers.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_peers.c

## Purpose
Demonstrates iterating RX debug peer records for a remote RX service.

## Important APIs, Types, And Functions
The sample uses `afsclient_RXDebugOpenPort`, `util_RXDebugPeersBegin/Next/Done`, and `afsclient_RXDebugClose`. It prints `afs_RXDebugPeer_t` data plus `afs_RXDebugPeerStats_t` support flags returned with each iteration.

## Control Flow
`main` parses host/port, initializes libadmin, opens RX debug, starts peer iteration, prints each peer's address, port, packet/rtt/congestion/window statistics where supported, verifies `ADMITERATORDONE`, then closes the iterator and handle.

## State And Persistence
The program is read-only and transient. Iterator state lives in util admin; output is a live snapshot of RX peer state.

## Dependencies And Integration Points
It depends on RX debug support in the target service and the libadmin utility iterator abstraction.

## Risks And Test Signals
The main risks are assuming optional peer statistics are present and incomplete cleanup on failures. Good signals include output for services with multiple peers, older services with fewer supported fields, and no-peer iterator completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_peers.c -->
