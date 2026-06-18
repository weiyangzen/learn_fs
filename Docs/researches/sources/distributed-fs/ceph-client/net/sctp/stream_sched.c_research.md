# sources/distributed-fs/ceph-client/net/sctp/stream_sched.c

## Purpose
Defines the common SCTP stream scheduler API and the built-in FCFS scheduler. It owns scheduler registration, scheduler switching, per-stream scheduler value get/set, and common dequeue bookkeeping for all scheduler implementations.

## Important APIs, Types, And Functions
Exports `sctp_sched_ops_register`, `sctp_sched_ops_init`, `sctp_sched_set_sched`, `sctp_sched_get_sched`, `sctp_sched_set_value`, `sctp_sched_get_value`, `sctp_sched_dequeue_done`, `sctp_sched_dequeue_common`, `sctp_sched_init_sid`, and `sctp_sched_ops_from_stream`. The central interface is `struct sctp_sched_ops`.

## Control Flow
`sctp_sched_ops_init` registers FCFS, PRIO, RR, FC, and WFQ implementations in a static table. Scheduler switching frees old scheduler state, initializes the new scheduler and existing stream extensions, then re-enqueues one representative datamsg per queued message. FCFS itself dequeues either the current unfinished message stream or the first chunk in the global outqueue. `sctp_sched_dequeue_done` preserves `stream.out_curr` for multi-fragment messages when the peer lacks interleaving, ensuring one message is completed before scheduler fairness can pick another stream.

## State And Persistence
State is in-memory per association outqueue and per stream extension. `outqueue.sched` points to the active ops table; `stream.out_curr` pins a partially dequeued datamsg.

## Dependencies And Integration Points
Integrates with `sctp_outq`, datamsg chunk lists, stream extension allocation in `stream.c`, and all concrete schedulers. Socket options or association setup call the set/get APIs.

## Risks
Risks include scheduler switch rollback leaving stale extension fields, incorrect `out_curr` handling breaking message atomicity when ndata is unavailable, missing stream extension allocation before scheduler value set, and outqueue length mismatch if common dequeue is bypassed.

## Test Signals
Switch schedulers with queued data, send fragmented messages with and without peer interleaving, set/get scheduler values on valid and invalid stream ids, inject init failures during scheduler switch, and assert `out_qlen` and chunk list membership after dequeue.
