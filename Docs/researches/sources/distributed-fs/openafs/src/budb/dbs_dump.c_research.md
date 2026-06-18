<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/dbs_dump.c -->
# sources/distributed-fs/openafs/src/budb/dbs_dump.c

## Purpose
Exposes the database dump and header-restore RPCs. It starts a worker to serialize the database through `writeDatabase`, streams chunks to clients, and watches for stalled dump readers.

## Important APIs, Types, And Functions
`DumpDB` implements the streaming RPC; `setupDbDump` runs the writer side; `RestoreDbHeader` merges saved header high-water marks; `dumpWatcher` enforces a timeout; `badEntry` is a placeholder that currently always accepts entries.

## Control Flow
The first `DumpDB` call initializes `dumpSyncPtr`, creates a pipe, starts the database dumper and watcher, and returns data read from the pipe. Subsequent calls read more chunks. A zero-length call refreshes the timeout. End-of-stream closes the read side and clears dump-in-progress state. The watcher cancels/destroys the dumper and aborts the Ubik transaction if clients stop polling.

## State And Persistence
Runtime state lives in global `dumpSync`. The dump itself is generated from a read transaction. `RestoreDbHeader` persists only merged `lastDumpId`, `lastTapeId`, and `lastInstanceId` values after version validation.

## Dependencies And Integration Points
Integrates RPC clients with `db_dump.c`, Ubik transactions, LWP or pthread synchronization, audit events, and `globals.h` dump synchronization fields.

## Risks And Test Signals
Risks include one global dump at a time, pipe/condition synchronization races, timeout cleanup correctness, and pthread path passing `NULL` where the worker expects a write fd. Signals are streaming savedb in chunks, zero-length keepalive, simultaneous dump rejection, timeout abort, and header-restore version mismatch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/dbs_dump.c -->
