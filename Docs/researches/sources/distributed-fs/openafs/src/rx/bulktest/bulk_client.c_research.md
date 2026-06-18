# sources/distributed-fs/openafs/src/rx/bulktest/bulk_client.c

Purpose: legacy asynchronous bulk transfer stress client for Rx.

Important APIs/types/functions: `InterruptSignal`, `GetIpAddress`, `async_work`, `async_BulkProc`, `async_BulkTest`, `FetchFile`, `StoreFile`, and `main`.

Control flow: parses host and file operations, creates a null-security Rx connection, schedules one LWP process per requested file/count via `async_BulkTest`, performs repeated fetch or store calls in `async_BulkProc`, waits for `async_nProcs` to drain, prints Rx stats, and finalizes.

State/persistence: creates temporary files under `/usr/tmp`, reads/writes requested files, tracks global `async_nProcs` and `myHostName`.

Dependencies/integration: LWP process creation/sleep/wakeup, generated bulk stubs, `bulk_io.c`, Rx stats/security, DNS and file APIs.

Risks: old K&R prototypes, memory leaks for `async_work` and strings, incorrect `fprintf` calls missing stream in error paths, global counter races without explicit lock, and hard-coded `/usr/tmp`. Test signals are concurrent fetch/store loops, SIGINT stats output, and completion wait behavior.
