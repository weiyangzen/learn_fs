# File Research: sources/block-storage/linux-dm/drivers/md/dm-rq.c

## Purpose

`dm-rq.c` implements request-based Device Mapper support on blk-mq. It creates the request queue/tag set, initializes per-request target I/O state, asks request-based targets to clone and map requests, dispatches cloned requests, handles partial bio completions, target endio decisions, requeue paths, statistics, and queue quiesce/unquiesce helpers.

## Request State

Each request has a `struct dm_rq_target_io` in the blk-mq PDU. It stores the mapped device, target, original request, clone request, deferred work field, error, target `map_info`, stats auxiliary data, start duration, sector count, and completed byte count.

Clone bios are allocated with a front-padded `struct dm_rq_clone_bio_info`, linking original bio, target I/O, and embedded clone bio. This supports partial completion accounting for cloned requests.

## Mapping And Completion

`dm_mq_queue_rq()` rejects requests during suspend, finds the immutable or live target, checks target busy state, starts the original request, initializes target I/O, sets `tio->ti`, and calls `map_request()`.

`map_request()` calls the target’s `clone_and_map_rq()`. Remapped requests are prepared with `blk_rq_prep_clone()`, traced, and inserted with `blk_insert_cloned_request()`. Resource errors clean up the clone and requeue the original. Submitted, requeue, delay-requeue, and kill outcomes are handled according to DM map return codes.

Clone completion reaches `end_clone_request()`, which completes the original request through blk-mq softirq. `dm_softirq_done()` calls `dm_done()` for mapped clones, allowing target `rq_end_io()` to return done, incomplete, immediate requeue, or delayed requeue. Completion updates stats, releases clone resources through target `release_clone_rq()`, ends the original request, and drops the mapped-device reference.

## Queue Setup

`dm_mq_init_request_queue()` allocates and initializes a blk-mq tag set with stacking/merge flags, configurable queue depth and hardware queue count, and PDU size equal to `dm_rq_target_io` plus any immutable target per-I/O data. Cleanup frees the tag set.

Module parameters include reserved request-based I/Os, blk-mq hardware queues, queue depth, and compatibility-only `use_blk_mq`.

## Invariants And Risks

- `dm_get()` in `dm_start_request()` must be balanced by `dm_put()` through `rq_completed()` at every completion or requeue path.
- Target-specific per-I/O data lives immediately after `dm_rq_target_io` when `per_io_data_size` is configured.
- Partial completion uses `blk_update_request()` rather than `blk_mq_end_request()` to preserve clone/original ordering.
- Target endio is skipped for unmapped clone failures marked with `RQF_FAILED`.
- Resource errors must unprepare and release clone requests before requeueing.
- Discard/write-same/write-zeroes target errors can disable unsupported features on the mapped device.

## Test Focus

Test map return codes, clone allocation failure, insert resource errors, target busy requeue, suspend requeue, partial bio completion, clone bio error propagation, rq_end_io requeue/delay/incomplete paths, stats accounting balance, per-I/O PDU setup, feature disabling on target errors, queue depth parameter bounds, and cleanup after init failures.
