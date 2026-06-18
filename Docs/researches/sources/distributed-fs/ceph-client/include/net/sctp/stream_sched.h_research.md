# sources/distributed-fs/ceph-client/include/net/sctp/stream_sched.h

## Purpose
This header defines the SCTP outbound stream scheduler abstraction and registration/init APIs for scheduler algorithms such as priority, round-robin, fair-capacity, and weighted fair queueing.

## Important APIs, Types, And Functions
`struct sctp_sched_ops` supplies callbacks for scheduler `set`, `get`, `init`, `init_sid`, `free`, enqueue/dequeue, dequeue completion, scheduling-all, and per-stream value get/set. Public APIs choose and query schedulers (`sctp_sched_set_sched()`, `sctp_sched_get_sched()`), configure stream values, notify dequeue completion, initialize stream ids, register scheduler ops, and initialize built-in scheduler families.

## Control Flow
Outbound chunks enter `sctp_outq` and are enqueued through the selected scheduler. Dequeue picks the next eligible chunk/stream; `sctp_sched_dequeue_done()` and `sctp_sched_dequeue_common()` update scheduler-specific stream state after transmission.

## State And Persistence
Scheduler state persists in `sctp_stream` and `sctp_stream_out_ext` lists/weights/priorities plus `sctp_outq::sched`. Per-stream values may represent priority, weight, or algorithm-specific controls.

## Dependencies And Integration Points
It integrates with `struct sctp_association`, `sctp_outq`, `sctp_chunk`, `sctp_stream`, and SCTP socket options that set stream scheduler type or values.

## Risks And Test Signals
Risks include starvation, list corruption, scheduler changes with queued data, uninitialized stream extensions, and value interpretation mismatches. Test signals include multi-stream send fairness, priority/round-robin behavior, scheduler socket options, stream add/reset, and retransmission interaction.
