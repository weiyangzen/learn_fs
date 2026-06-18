# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-sync.h

## Purpose
Defines the sync-coalescing context structure and declares the coalescing API used by DBPF queueing and worker code.

## Important APIs, Types, And Functions
`dbpf_sync_context_t` tracks `sync_counter`, `non_sync_counter`, `coalesce_counter`, a mutex, and a `sync_queue`. Prototypes cover context init/destroy, coalesce on service completion, enqueue/dequeue counter updates, and collection watermark/mode setters.

## Control Flow
Queue code calls enqueue/dequeue hooks as operations enter/leave the global queue. The worker calls `dbpf_sync_coalesce` after a metadata service routine returns. Management `setinfo` calls watermark and mode setters.

## State And Persistence
The structure is in-memory only. It controls when persistent DB syncs occur but does not itself own DB handles.

## Dependencies And Integration Points
Includes DBPF op queue, perf counter headers, and DBPF collection types. It couples queue state, worker completion, and collection configuration.

## Risks And Test Signals
Risks are declaration drift with `dbpf-sync.c`, callers treating counters as authoritative without locks, and missing initialization for each TROVE context. Tests should initialize/destroy all contexts and run coalescing under concurrent queue operations.
