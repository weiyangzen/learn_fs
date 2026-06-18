<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_supported_stats.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_supported_stats.c

## Purpose
Demonstrates querying which RX debug statistic classes a target service supports.

## Important APIs, Types, And Functions
It defines `Usage`, `ParseArgs`, and `main`, and calls `afsclient_Init`, `afsclient_RXDebugOpenPort`, `util_RXDebugSupportedStats`, and `afsclient_RXDebugClose`. The output is an `afs_RXDebugStats_t` support mask/record.

## Control Flow
After argument validation, the program opens RX debug on the supplied host/port, fetches supported-stat information, closes the handle, and prints whether basic, version, peer, connection, and RX stats are available.

## State And Persistence
No state is modified. It reads capability information from the remote RX service.

## Dependencies And Integration Points
It provides a compatibility probe for the other `rxdebug_*` samples and depends on libadmin RX debug utility APIs.

## Risks And Test Signals
The sample relies on support fields staying aligned with util admin definitions. Tests should query both modern and older services and ensure unsupported classes are reported rather than causing later detailed calls to be attempted blindly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_supported_stats.c -->
