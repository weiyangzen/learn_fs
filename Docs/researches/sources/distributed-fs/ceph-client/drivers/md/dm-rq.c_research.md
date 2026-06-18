# sources/distributed-fs/ceph-client/drivers/md/dm-rq.c

## Purpose
Implements request-based Device Mapper support on top of blk-mq. It owns per-request `dm_rq_target_io` state, maps original requests through request-capable targets, prepares cloned requests, handles partial clone-bio completion, requeue policy, request statistics, and blk-mq queue setup.

## Important APIs, Types, And Functions
`struct dm_rq_target_io` carries the mapped device, selected target, original and cloned requests, `union map_info`, stats aux data, partial byte accounting, and optional target-private per-IO storage. Main entry points are `dm_mq_init_request_queue()`, `dm_mq_cleanup_mapped_device()`, `dm_mq_queue_rq()`, `dm_softirq_done()`, `map_request()`, `setup_clone()`, `dm_done()`, and `dm_mq_kick_requeue_list()`.

## Control Flow
`dm_mq_queue_rq()` rejects IO during suspend, resolves the immutable or live-table target, checks `busy()`, starts stats and the md reference, initializes `tio`, and calls target `clone_and_map_rq()`. Remapped requests are cloned and submitted with `blk_insert_cloned_request()`. Completion travels from clone `end_io` to the original request's blk-mq completion, where optional target `rq_end_io()` decides complete, incomplete, immediate requeue, or delayed requeue.

## State And Persistence
State is runtime-only: module parameters, blk-mq tag set, per-request private data, clone lifetime, stats aux data, and md references held while IO is in flight. There is no on-disk state.

## Dependencies And Integration Points
Depends on `dm-core.h`, `dm-rq.h`, blk-mq, DM mempools, DM table lookup, and DM stats. Request-based targets integrate through `clone_and_map_rq`, `release_clone_rq`, `rq_end_io`, `busy`, `per_io_data_size`, and immutable target selection.

## Risks
Completion ordering and reference balance are the main risks. The original request must not end before clone cleanup, requeue paths must undo stats and md refs exactly once, and resource failures must not leak cloned requests. Request-based DM assumes a single immutable target as enforced by `dm-table.c`.

## Test Signals
Exercise request-based targets under normal IO, suspend/resume, resource-pressure requeues, delayed requeues, target `busy()`, request stats, discard/write-zeroes target errors, and blk-mq debug/KASAN checks for double completion or leaked requests.
