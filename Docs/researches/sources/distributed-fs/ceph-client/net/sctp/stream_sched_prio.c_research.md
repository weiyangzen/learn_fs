# sources/distributed-fs/ceph-client/net/sctp/stream_sched_prio.c

## Purpose
Implements SCTP priority stream scheduling. Streams are grouped by priority, priority groups are served in ascending priority order, and streams within a priority are round-robined.

## Important APIs, Types, And Functions
Exports `sctp_sched_ops_prio_init`. Important helpers include `sctp_sched_prio_get_head`, `sctp_sched_prio_set`, `sctp_sched_prio_sched`, `sctp_sched_prio_unsched`, `sctp_sched_prio_dequeue`, and `sctp_sched_prio_dequeue_done`. `struct sctp_stream_priorities` holds a priority group, active stream list, next stream pointer, and reference count.

## Control Flow
Each stream extension references a priority head. Setting a priority allocates or reuses a head, unschedules the stream if active, switches the reference, then reschedules it if needed. Enqueue schedules the stream into its priority group's active list and schedules the group into the global `prio_list` if this is its first active stream. Dequeue chooses the current pinned stream or the first scheduled priority group's next stream. Completion advances the group's round-robin pointer and unschedules streams that have no queued data.

## State And Persistence
Priority heads and per-stream references live for the association only. Reference counts free unused priority groups when streams change priority or are freed.

## Dependencies And Integration Points
Uses stream scheduler common helpers, stream extensions, outqueue datamsg queues, and priority values set via scheduler socket options.

## Risks
Risks include reference leaks or premature frees of priority heads, invalid next pointers when unscheduling the current stream, preserving sorted priority-group order, and ensuring scheduler switch cleanup clears extension scheduler fields.

## Test Signals
Set multiple streams to the same and different priorities, change priority while queued, dequeue fragmented messages, empty the last stream in a priority group, switch schedulers, and validate priority head refcounts with stream free.
