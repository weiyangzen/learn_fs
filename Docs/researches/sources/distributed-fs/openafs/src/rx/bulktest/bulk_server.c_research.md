# sources/distributed-fs/openafs/src/rx/bulktest/bulk_server.c

Purpose: legacy Rx bulk test server.

Important APIs/types/functions: `InterruptSignal`, `main`, `BULK_FetchFile`, `BULK_StoreFile`, global `bulk_operationNumber`, and `Quit`.

Control flow: initializes Rx, registers null-security `BULK` service, sets max procs to five, starts the server, and exposes fetch/store RPC handlers that stream files through `bulk_io.c`. SIGINT prints Rx stats before exiting.

State/persistence: operation counter, server-side file reads/writes/truncation, and Rx service state.

Dependencies/integration: generated bulk server stubs, `bulk_io.c`, Rx service/security APIs, signal handling, and POSIX files.

Risks: unauthenticated arbitrary path access; non-atomic global operation counter across server procs; old K&R prototypes and format usage; `Quit` treats message as format string. Test signals are concurrent client stress, SIGINT stats, and fetch/store error paths.
