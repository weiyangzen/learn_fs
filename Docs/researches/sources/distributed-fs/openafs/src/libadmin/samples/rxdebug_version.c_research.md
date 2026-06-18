<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_version.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_version.c

## Purpose
Demonstrates retrieving the version string exposed by an RX debug endpoint.

## Important APIs, Types, And Functions
The sample uses `afsclient_RXDebugOpenPort`, `util_RXDebugVersion`, and `afsclient_RXDebugClose`, with a local version string buffer.

## Control Flow
It parses `<host> <port>`, initializes libadmin, opens RX debug, asks for the version string, closes the handle, and prints the target and returned version.

## State And Persistence
The program is read-only and retains only a transient RX debug handle and stack buffer.

## Dependencies And Integration Points
It is the smallest RX debug smoke test and integrates with RX debug service support through libadmin.

## Risks And Test Signals
Risks are buffer-size assumptions and fail-fast cleanup. Test signals are successful version output from an RX debug capable daemon and clear failure for a closed or wrong port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_version.c -->
