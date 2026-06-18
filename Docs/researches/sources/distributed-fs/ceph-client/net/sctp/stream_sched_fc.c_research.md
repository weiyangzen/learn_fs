# sources/distributed-fs/ceph-client/net/sctp/stream_sched_fc.c

## Purpose
Implements Fair Capacity (`SCTP_SS_FC`) and Weighted Fair Queueing (`SCTP_SS_WFQ`) schedulers from RFC 8260 sections 3.5 and 3.6. Both use a per-stream cumulative length metric; WFQ adds configurable stream weights.

## Important APIs, Types, And Functions
Exports `sctp_sched_ops_fc_init` and `sctp_sched_ops_wfq_init`. Important helpers are `sctp_sched_fc_init`, `sctp_sched_fc_init_sid`, `sctp_sched_fc_sched`, `sctp_sched_fc_enqueue`, `sctp_sched_fc_dequeue`, and `sctp_sched_fc_dequeue_done`. Per-stream state lives in `sctp_stream_out_ext.fc_list`, `fc_length`, and `fc_weight`; global ordering is `stream->fc_list`.

## Control Flow
Initialization creates a global fair-capacity list and initializes each stream extension with length zero and weight one. Enqueue schedules the stream that owns the datamsg if not already present, ordered by normalized `fc_length / weight`. Dequeue selects `out_curr` when pinned, otherwise the first stream in the fair list, then removes the chunk from global and stream lists. After dequeue, the stream's length increases by the sent skb length, large counters are normalized before overflow, empty streams are unscheduled, and non-empty streams are repositioned by weighted normalized length.

## State And Persistence
All scheduler state is volatile per association. WFQ weight is persisted only in the stream extension while the association exists.

## Dependencies And Integration Points
Uses the common scheduler helpers in `stream_sched.c`, the outqueue datamsg layout, and `SCTP_SO(stream, sid)->ext` allocated by stream code.

## Risks
Risk centers on weighted comparison overflow, list insertion around the sentinel when the list is empty, counter normalization changing relative fairness, and maintaining identical behavior for FC and WFQ except for non-default weights.

## Test Signals
Send mixed-size messages across streams, verify WFQ weight changes affect order, test counter normalization near `U32_MAX`, unschedule empty streams, and switch into/out of FC/WFQ with already queued chunks.
