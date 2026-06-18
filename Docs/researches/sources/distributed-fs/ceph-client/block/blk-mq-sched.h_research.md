# sources/distributed-fs/ceph-client/block/blk-mq-sched.h

## Purpose
`blk-mq-sched.h` declares the internal interface between blk-mq core code, elevators, and scheduler resources. It also provides small inline helpers for optional scheduler callbacks and merge predicates.

## Important APIs, Types, And Functions
It declares scheduler dispatch, merge, lifecycle, resource allocation, and free functions implemented in `blk-mq-sched.c`. `MAX_SCHED_RQ` defines the scheduler request pool size. Inline helpers include `blk_mq_alloc_sched_data()`, `blk_mq_free_sched_data()`, `blk_mq_sched_restart()`, `bio_mergeable()`, `blk_mq_sched_allow_merge()`, `blk_mq_sched_completed_request()`, `blk_mq_sched_requeue_request()`, `blk_mq_sched_has_work()`, `blk_mq_sched_needs_restart()`, `blk_mq_set_min_shallow_depth()`, and `blk_mq_is_sync_read()`.

## Control Flow
The inline helpers guard optional elevator callbacks, so callers can notify schedulers without open-coding NULL checks. `blk_mq_sched_restart()` checks the restart bit before invoking the heavier restart path. `blk_mq_sched_allow_merge()` only calls `allow_merge` for requests using scheduler private state. `blk_mq_set_min_shallow_depth()` walks hctxs and adjusts scheduler tag shallow depth.

## State And Persistence
The header owns no state but defines how queue, hctx, request, and elevator state should be accessed. Inline functions can mutate scheduler tag shallow-depth settings and invoke scheduler callbacks that mutate scheduler-private state.

## Dependencies And Integration Points
It depends on `elevator.h` and `blk-mq.h`, and is included by merge, scheduler, and blk-mq core code that needs scheduler-aware behavior.

## Risks And Test Signals
Risks include calling scheduler callbacks after elevator teardown, dereferencing `sched_tags` when no scheduler tags exist, and inconsistent merge behavior when `RQF_USE_SCHED` is not set. Tests should include elevator-less builds, scheduler callback absence, completion/requeue callback coverage, and shallow-depth updates across every hctx.
