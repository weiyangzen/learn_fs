# sources/distributed-fs/openafs/src/rx/bulk.example/bulk_server.c

Purpose: simple Rx server for the bulk file-transfer example.

Important APIs/types/functions: `main`, RPC handlers `BULK_FetchFile`, `BULK_StoreFile`, and `Quit`.

Control flow: initializes Rx on `BULK_SERVER_PORT`, creates a null server security object, registers a `BULK` service using generated `BULK_ExecuteRequest`, limits server procs to two, and starts serving. Fetch opens a named file and streams it; store creates/truncates a named file and receives data.

State/persistence: reads server-side files for fetch and creates/truncates files for store.

Dependencies/integration: generated `bulk.h` server stubs, `bulk_io.c`, Rx service/security APIs, and POSIX file APIs.

Risks: unauthenticated null security plus arbitrary path names make this unsafe outside a controlled example; `Quit` treats format string as data; server returns after `rx_StartServer` only on unexpected failure. Test signals are client fetch/store against the server and permission/error-path checks.
