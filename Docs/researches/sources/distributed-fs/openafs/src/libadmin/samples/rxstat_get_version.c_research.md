<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_version.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_version.c

## Purpose
Implements a sample command to query the RX stats interface version from a selected service.

## Important APIs, Types, And Functions
`rxstat_get_version` uses `cmd_OptionAsString`, `cmd_OptionAsInt`, `afsclient_Init`, `afsclient_NullCellOpen`, `afsclient_RPCStatOpenPort`, `util_RPCStatsVersionGet`, `afsclient_RPCStatClose`, and `afsclient_CellClose`.

## Control Flow
The command requires `-server` and `-port`, validates the port, opens a null cell and RPC stats connection, retrieves `afs_RPCStatsVersion_t`, closes resources, and prints the version number.

## State And Persistence
It is read-only and creates no persistent state.

## Dependencies And Integration Points
It integrates with libadmin RPC stats connection handling and the OpenAFS command parser.

## Risks And Test Signals
The sample is a low-impact compatibility check. Signals are correct version output from known RX stats services, failure on unsupported endpoints, and no resource leaks under normal completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxstat_get_version.c -->
