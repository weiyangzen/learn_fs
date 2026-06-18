<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_client_config.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/cm_client_config.c

## Purpose
Demonstrates querying a cache manager's client configuration through the libadmin CM statistics interface.

## Important APIs, Types, And Functions
The file defines `Usage`, `ParseArgs`, and `main`. It uses `afsclient_Init`, `afsclient_NullCellOpen`, `afsclient_CMStatOpenPort`, `util_CMClientConfig`, `afsclient_CMStatClose`, and `afsclient_CellClose`. The main data structure is `afs_ClientConfig_t`.

## Control Flow
The program accepts `<host> <port>`, validates the port in the 1..65535 range, initializes libadmin, opens a null cell handle, opens an RX connection to the cache-manager stats port, fetches configuration, closes the connection and cell, then prints version, cache count, chunk size, cache size, settime, and memory-cache fields.

## State And Persistence
It persists nothing. Runtime state is the parsed server name/port, a null cell handle, an RX connection, status code, and one configuration snapshot.

## Dependencies And Integration Points
It depends on roken, pthread on NT, RX headers, `afs_clientAdmin.h`, and `afs_utilAdmin.h`. It integrates with a remote cache manager that supports the CM stats RPCs.

## Risks And Test Signals
The sample exits immediately on errors and does not close already-open handles on later failures. It prints only the v1 union fields, so newer config versions would need updates. Test signals are correct usage rejection, out-of-range port rejection, successful `util_CMClientConfig`, and clean output against a known cache manager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/cm_client_config.c -->
