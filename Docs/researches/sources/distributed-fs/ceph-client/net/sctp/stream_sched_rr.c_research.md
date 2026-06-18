# sources/distributed-fs/ceph-client/net/sctp/stream_sched_rr.c

## Purpose
Implements round-robin stream scheduling for SCTP outgoing streams. It keeps a circular list of streams with pending chunks and chooses the next stream after each completed datamsg.

## Important APIs, Types, And Functions
Exports `sctp_sched_ops_rr_init`. Internal helpers are `sctp_sched_rr_init`, `sctp_sched_rr_init_sid`, `sctp_sched_rr_sched`, `sctp_sched_rr_unsched`, `sctp_sched_rr_next_stream`, `sctp_sched_rr_enqueue`, `sctp_sched_rr_dequeue`, and `sctp_sched_rr_dequeue_done`.

## Control Flow
Initialization creates `stream->rr_list` and clears `rr_next`. Enqueue inserts a stream extension once into the active list and initializes `rr_next` when the first stream becomes active. Dequeue uses `stream.out_curr` if a non-interleavable message is in progress, otherwise `rr_next`. Dequeue completion advances `rr_next` and removes the stream when its per-stream outq is empty.

## State And Persistence
State is in-memory only: `stream->rr_list`, `stream->rr_next`, and each extension's `rr_list` membership.

## Dependencies And Integration Points
Depends on stream extension allocation, common scheduler dequeue/list helpers, and outqueue chunk placement onto per-stream queues.

## Risks
The empty-list path is sensitive: advancing before removing the last stream must leave `rr_next` null. Other risks are duplicate list insertion, stale list nodes after scheduler switch, and fairness disruption when `out_curr` pins fragmented messages.

## Test Signals
Exercise one-stream, two-stream, and many-stream queues; enqueue duplicate datamsgs on an active stream; drain the last stream; switch schedulers; and compare order with/without fragmented messages.
