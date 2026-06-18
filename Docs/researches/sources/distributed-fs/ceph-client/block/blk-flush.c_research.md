# sources/distributed-fs/ceph-client/block/blk-flush.c

## Purpose
`blk-flush.c` implements the block-layer state machine that decomposes `REQ_PREFLUSH` and `REQ_FUA` writes into preflush, data, and postflush steps according to queue write-cache and FUA capabilities. It merges compatible flush work and serializes actual flush commands so durability ordering is preserved without issuing redundant cache flushes.

## Important APIs, Types, and Functions
Important functions include `blk_insert_flush()`, `blkdev_issue_flush()`, `blk_alloc_flush_queue()`, `blk_free_flush_queue()`, `blk_mq_hctx_set_fq_lock_class()`, `is_flush_rq()`, `flush_end_io()`, `mq_flush_data_end_io()`, `blk_flush_complete_seq()`, `blk_kick_flush()`, and `blk_rq_init_flush()`. The sequence bits are `REQ_FSEQ_PREFLUSH`, `REQ_FSEQ_DATA`, `REQ_FSEQ_POSTFLUSH`, and `REQ_FSEQ_DONE`.

## Control Flow
`blk_insert_flush()` inspects a request's data length, `REQ_PREFLUSH`, `REQ_FUA`, queue write-cache flag, and FUA support. If nothing is needed, empty flushes complete immediately or data requests proceed normally. If data plus postflush is needed, the request's end_io is replaced so data completion re-enters the flush state machine. Other policies queue the request through `blk_flush_complete_seq()`.

Flush queues are double-buffered by `flush_pending_idx` and `flush_running_idx`. Requests that need pre/post flush are placed on the pending list. `blk_kick_flush()` issues one synthetic `REQ_OP_FLUSH | REQ_PREFLUSH` request when no flush is already running, unless data requests are in flight and the pending timeout has not expired. The synthetic flush borrows tags from the first queued request and is placed on `q->flush_list`. `flush_end_io()` accounts the flush, restores tag state, flips the running buffer, and advances all waiting requests to their next sequence step. Data completion decrements `flush_data_in_flight` and continues the sequence.

## State and Persistence
State is in `struct blk_flush_queue`: two flush lists, pending/running indices, a synthetic flush request, `mq_flush_lock`, `flush_data_in_flight`, pending timestamp, and aggregated flush status. Per-request state is `rq->flush.seq`, saved end_io, `RQF_FLUSH_SEQ`, and temporary queue-list placement.

## Dependencies and Integration Points
This file integrates with blk-mq requeueing, request tags, schedulers/elevators, partition flush statistics, `submit_bio_wait()` through `blkdev_issue_flush()`, and queue limits/features. Drivers see either real data requests with adjusted flags or synthetic flush requests generated here.

## Risks
Risks include durability violations from incorrect sequence transitions, tag ownership mistakes, double completion of flush-sequenced requests, starvation when data traffic continuously delays postflushes, recursive lockdep false positives, and scheduler/no-scheduler tag differences. The code relies on one-bio flush/FUA requests and uses timeout-based kicking to avoid indefinite flush deferral.

## Test Signals
Tests should exercise every write-cache/FUA capability matrix, empty flush completion, data-only bypass, preflush+data+postflush ordering, error propagation from synthetic flush to waiting requests, pending timeout under continuous FUA data, scheduler and no-scheduler tag paths, request accounting for flush stats, and teardown of allocated flush queues.
