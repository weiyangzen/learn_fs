# sources/distributed-fs/openafs/src/butc/butc_prototypes.h

## Purpose
`butc_prototypes.h` declares thread-entry functions and selected globals for the Tape Coordinator. It complements `butc_internal.h` by collecting functions that are passed to LWP/pthread creation or used across coordinator modules.

## Important APIs, Types, And Functions
It declares thread routines `dbWatcher()`, `Dumper()`, `DeleteDump()`, `Restorer()`, `Labeller()`, `ScanDumps()`, `saveDbToTape()`, `restoreDbFromTape()`, and `KeepAlive()`. It also exposes `butc_confdir` and `allow_unauth` from `tcmain.c`.

## Control Flow
The header has no runtime control flow. Its function signatures all use `void *(*)(void *)`-style thread entrypoints, making them suitable for the coordinator's LWP/pthread abstraction.

## State And Persistence
It does not own state, but the declared routines drive major persistent operations: dumping/restoring volumes, saving/restoring the backup database, scanning dump tapes, and asynchronously flushing database entries. The declared globals control configuration and authentication policy access from modules outside `tcmain.c`.

## Dependencies And Integration Points
This header links coordinator modules around task execution and keepalive behavior. It must stay aligned with the actual implementations in `dbentries.c`, `dump.c`, `lwps.c`, `recoverDb.c`, `tcudbprocs.c`, and `tcmain.c`.

## Risks And Test Signals
Risks are wrong thread signatures or stale externs causing build failures or undefined behavior at thread creation. Compile tests with the coordinator's supported threading model are the main signal. Functional signals include successful launch of dump, restore, label, scan, database save/restore, keepalive, and watcher tasks.
