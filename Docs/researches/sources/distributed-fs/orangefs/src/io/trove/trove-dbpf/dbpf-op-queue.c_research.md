# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-op-queue.c

## Purpose
Implements the global DBPF operation queue and helper routines that move operations through queued, in-service, completed, and dequeued states. It is the bridge between TROVE API wrappers, the DBPF service thread, completion queues, and metadata sync coalescing.

## Important APIs, Types, And Functions
Defines global `QLIST_HEAD(dbpf_op_queue)` and `dbpf_op_queue_mutex`. Queue utilities include `dbpf_op_queue_new`, `dbpf_op_queue_cleanup`, `dbpf_op_queue_add`, `dbpf_op_queue_remove`, `dbpf_op_queue_empty`, and `dbpf_op_queue_shownext`. Operation lifecycle routines include `dbpf_queued_op_queue`, `dbpf_queued_op_queue_nolock`, `dbpf_queued_op_try_get`, `dbpf_queued_op_put`, `dbpf_queued_op_dequeue`, `dbpf_queued_op_dequeue_nolock`, `dbpf_queued_op_put_and_dequeue`, `dbpf_op_init_queued_or_immediate`, `dbpf_queue_or_service`, and `dbpf_queued_op_complete`.

## Control Flow
TROVE wrappers call `dbpf_op_init_queued_or_immediate`; immediate collections receive a caller-owned `dbpf_op`, while normal collections allocate and initialize a `dbpf_queued_op_t`. `dbpf_queue_or_service` either directly invokes metadata service functions and syncs DBs when immediate completion is enabled, or enqueues the operation and returns a generated op id. Enqueue adds the operation to the global queue, sets state to `OP_QUEUED`, increments sync coalescing counters, and signals the DBPF worker condition. Completion ends PINT events and moves operations to the per-context completion queue through macros from `dbpf-thread.h`.

## State And Persistence
All state is in memory: global pending queue, per-op mutex/state/id/event fields, id-generator registration, and sync coalescing counters. Persistent DB state changes are produced by service functions, not by this queue itself, except that immediate completion may force `dbpf_db_sync` for keyval/dspace operations carrying `TROVE_SYNC`.

## Dependencies And Integration Points
Depends on quicklist, id-generator, DBPF op structures, DBPF thread completion macros, sync coalescing, PINT events, and optional pthread condition variables. It is used by keyval, dspace, bstream, and direct-I/O completion code.

## Risks And Test Signals
Risks include state assertions under races, raw pointer lookup by op id, operations left registered after free, immediate-completion behavior differing from threaded behavior, event-end argument mismatch for dspace create, and lock ordering among global queue, op mutex, sync context mutex, and completion queues. Tests should cover queue/dequeue/requeue cycles, cancellation/status polling, immediate completion for keyval/dspace, threaded wakeups, completion queue delivery per context, and sync-coalesced completion of multiple ops.
