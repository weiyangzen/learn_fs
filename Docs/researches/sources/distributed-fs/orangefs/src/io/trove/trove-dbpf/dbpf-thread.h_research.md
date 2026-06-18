# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-thread.h

## Purpose
Declares DBPF worker-thread functions and completion-queue macros shared by queue, sync, and worker code.

## Important APIs, Types, And Functions
Defines `DBPF_OPS_PER_WORK_CYCLE` as 5, prototypes worker lifecycle and work-cycle functions, and provides `DBPF_COMPLETION_START`, `DBPF_COMPLETION_ADD`, `DBPF_COMPLETION_SIGNAL`, and `DBPF_COMPLETION_FINISH` macros.

## Control Flow
Worker/sync code wraps completion queue insertion with the macros: lock the target context completion queue, set operation state, append the op, signal waiters in threaded builds, and unlock the queue.

## State And Persistence
No state is stored in the header, but the macros mutate per-context completion queues and op states. There is no direct persistent storage behavior.

## Dependencies And Integration Points
Includes TROVE and DBPF types, and references global completion queue arrays defined elsewhere. It is included by `dbpf-thread.c`, `dbpf-op-queue.c`, and `dbpf-sync.c`.

## Risks And Test Signals
Risks include macro side effects, missing lock pairing if callers return early between start/finish, and context-id bounds assumptions. Compile coverage and completion queue concurrency tests are the useful signals.
