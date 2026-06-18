# sources/distributed-fs/openafs/src/butc/dbentries.c

## Purpose
`dbentries.c` buffers and asynchronously flushes Tape Coordinator backup database updates. Dump, tape, and volume operations enqueue BUDB entry structures while backup work proceeds; `dbWatcher()` drains those queues and calls the BUDB client APIs to create/finish dumps, use/finish tapes, and add volumes.

## Important APIs, Types, And Functions
The module owns two double-linked queues: `savedEntries` for the current dump workflow and `entries_to_flush` for watcher-ready updates. `threadEntry()` and `threadEntryDir()` allocate a queue node plus copied entry payload. Public queue producers are `useDump()`, `finishDump()`, `useTape()`, `finishTape()`, and `addVolume()`. `flushSavedEntries()` moves or drops queued entries based on dump status. `waitDbWatcher()` blocks until the watcher is idle and the flush queue is empty. `dbWatcher()` is the long-running thread entrypoint that applies queued updates to BUDB.

## Control Flow
Producer functions build `budb_dumpEntry`, `budb_tapeEntry`, or `budb_volumeEntry` payloads and enqueue them. Allocation retries up to five times, sleeping a minute between attempts if the watcher is active. `flushSavedEntries()` has special handling for `DUMP_NORETRYEOT`: it removes the just-used tape because the first volume exceeded tape capacity and the tape will be reused. It then drops volume entries on failed dumps while preserving dump/tape metadata for watcher processing. `dbWatcher()` initializes both queues, loops forever, drains `entries_to_flush`, dispatches by `dlq_type`, and sleeps for two seconds when idle. Volume entries are batched up to `MAXVOLUMESTOADD` for `bcdb_AddVolumes()`; a negative batch failure disables batching and falls back to `bcdb_AddVolume()` one entry at a time.

## State And Persistence
Runtime state is the two queues, `dbWatcherinprogress`, `addvolumes`, and `addedDump`. Persistent state changes are made through BUDB client calls: `bcdb_CreateDump()`, `bcdb_FinishDump()`, `bcdb_UseTape()`, `bcdb_FinishTape()`, `bcdb_AddVolumes()`, and `bcdb_AddVolume()`. The `addedDump` flag suppresses dependent tape/volume finishing when dump creation failed.

## Dependencies And Integration Points
The file depends on OpenAFS queue helpers (`dlq*`), LWP/pthread sleep abstractions, `budb_client` APIs, coordinator error logging, and BUDB entry structures. It is integrated with dump/tape workflows through prototypes in `butc_internal.h` and with thread startup through `butc_prototypes.h`.

## Risks And Test Signals
There is no explicit locking around the queues in this file, so correctness depends on the broader coordinator threading model or serialized producer access. Allocation retry paths can still dereference null if both allocations never succeed after the loop, so low-memory behavior is sensitive. `flushSavedEntries()` assumes the first saved entry is `DLQ_USETAPE` for `DUMP_NORETRYEOT`. Test signals include successful dump/tape/volume enqueue and flush, failed dump dropping volume entries, no-retry-EOT tape removal, duplicate dump ID handling, batch add success, batch add negative fallback, watcher idle waiting, and shutdown paths that call `waitDbWatcher()`.
