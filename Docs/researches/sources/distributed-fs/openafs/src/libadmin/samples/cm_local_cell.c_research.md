<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_local_cell.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/cm_local_cell.c

## Purpose
Demonstrates retrieving the local cell name reported by a remote cache manager.

## Important APIs, Types, And Functions
The functions are `Usage`, `ParseArgs`, and `main`. The sample uses `afsclient_Init`, `afsclient_NullCellOpen`, `afsclient_CMStatOpenPort`, `util_CMLocalCell`, `afsclient_CMStatClose`, and `afsclient_CellClose`, with output stored in `afs_CMCellName_t`.

## Control Flow
The program parses `<host> <port>`, initializes libadmin, opens a null cell and CM stats connection, calls `util_CMLocalCell`, closes resources, and prints the returned cell name with the target host and port.

## State And Persistence
No durable state is touched. Runtime state is limited to one connection, one cell handle, and a cell-name buffer.

## Dependencies And Integration Points
It depends on the client admin and utility admin libraries and the cache manager stats RPC endpoint. It is a small executable built by the samples makefile.

## Risks And Test Signals
The same early-exit leak pattern applies. Test signals are argument validation, successful local-cell retrieval from a running cache manager, and a failed call to an inactive or wrong port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_local_cell.c -->
