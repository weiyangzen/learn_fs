# sources/distributed-fs/openafs/src/rx/bulk.example/bulk_client.c

Purpose: simple Rx bulk-file-transfer client supporting one fetch or store operation.

Important APIs/types/functions: `GetIpAddress`, `main`, `FetchFile`, and `StoreFile`.

Control flow: parses `-fetch`/`-store` and `-verbose`, resolves host, initializes Rx, creates a null-security connection to `BULK_SERVICE_ID`, starts one call, invokes generated start RPC plus bulk data transfer helper, ends the call, reports throughput, and finalizes Rx.

State/persistence: reads or writes local files, creates/truncates fetch destination, and uses remote filename arguments; no durable state besides files.

Dependencies/integration: generated `bulk.h` client stubs, `rxnull`, Rx calls/connections, XDR/Rx helpers in `bulk_io.c`, libc DNS/file APIs.

Risks: no robust argument null checks before `**argv`; throughput divides by elapsed milliseconds and can divide by zero; errors from transfer helper feed `rx_EndCall` but initial `error` handling is minimal. Test signals are fetch/store between example server and client, missing-file errors, and verbose output.
