# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-op.h

## Purpose
Defines the queued DBPF operation wrapper, common initialization macro, and allocation/lifecycle prototypes used by DBPF asynchronous operation machinery.

## Important APIs, Types, And Functions
`DBPF_OP_INIT` initializes a `struct dbpf_op` for stack/immediate use and registers an id. `struct dbpf_queued_op_stats` tracks service count. `dbpf_queued_op_t` embeds a mutex, `struct dbpf_op`, completion state, PINT event type/id, manager op id, and qlist link. Prototypes cover allocate/init/free/touch.

## Control Flow
Wrappers either use `DBPF_OP_INIT` for immediate stack operations or `dbpf_queued_op_init` for heap queue entries. The embedded `struct dbpf_op` carries all operation-specific union data and the service callback consumed by the worker loop.

## State And Persistence
The header defines only in-memory operation state. Persistence is indirect through service callbacks that mutate DBs or bstream files.

## Dependencies And Integration Points
Includes quicklist, TROVE, `dbpf.h`, PINT op id support, and id-generator. It is foundational for `dbpf-op-queue.c`, `dbpf-thread.c`, `dbpf-sync.c`, and all DBPF operation wrappers.

## Risks And Test Signals
Risks include macro/initializer drift, id-generator misuse for immediate stack operations, and future additions to `dbpf_queued_op_t` not being initialized consistently. Compile coverage and operation lifecycle tests across immediate and queued modes are the main signals.
