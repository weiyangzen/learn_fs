# sources/distributed-fs/ceph-client/block/blk-mq.h

## Purpose

`blk-mq.h` is the internal header for the block multiqueue core. It defines software queue state, allocation parameters, tag helpers, queue mapping helpers, dispatch lock wrappers, and internal prototypes shared between `blk-mq.c`, scheduler code, sysfs, debugfs, and tag-management files.

## Important APIs, Types, And Functions

`struct blk_mq_ctxs` owns the per-CPU software queue allocation and kobject. `struct blk_mq_ctx` is the CPU-facing queue with a lock, per-hctx-type request lists, CPU id, mapping indices, hctx pointers, parent queue, and kobject. `struct blk_mq_alloc_data` carries queue, flags, operation flags, shallow depth, cached request batch data, and selected ctx/hctx across request allocation.

The header declares submission, polling, queue exit, request-depth update, wakeup, dispatch, busy-ctx flushing, ctx dequeue, request reference release, request-map allocation/free, sysfs registration, plug flushing, work cancellation, and queue release helpers. Inline mapping helpers include `blk_mq_get_hctx_type()`, `blk_mq_map_queue_type()`, and `blk_mq_map_queue()`. Tag helpers include `blk_mq_tags_from_data()`, `blk_mq_tag_is_reserved()`, `blk_mq_is_shared_tags()`, `blk_mq_get_driver_tag()`, and `blk_mq_put_driver_tag()`.

## Control Flow

Operation flags drive hctx selection: polled I/O uses `HCTX_TYPE_POLL`, reads may use `HCTX_TYPE_READ`, and all else defaults to `HCTX_TYPE_DEFAULT`. Allocation paths fill `blk_mq_alloc_data`, map the current CPU ctx to an hctx, choose scheduler tags or driver tags, and use `blk_mq_tags_from_data()` for the active tag pool. Dispatch paths use `blk_mq_hctx_stopped()` and `blk_mq_hw_queue_mapped()` to decide whether work can run. Driver-budget helpers dispatch into optional `blk_mq_ops` callbacks while returning benign defaults when a driver has no budget implementation.

Shared-tag fairness is handled by active-request counters and `hctx_may_queue()`: if tags are shared and active queues/users are known, the helper derives a per-user depth floor and prevents one hctx or queue from consuming too many tags. The `__blk_mq_run_dispatch_ops()` macro wraps dispatch work in SRCU for blocking tag sets and RCU for nonblocking sets.

## State And Persistence Behavior

All state is transient kernel memory. The header establishes cacheline-aligned ctx structures, active request counters, pending software queue bits, stopped state checks with memory barriers, and dispatch budget tokens carried on requests. The stopped-queue helper contains a memory barrier paired with `blk_mq_start_stopped_hw_queue()` to avoid lost dispatch visibility.

## Dependencies And Integration Points

It depends on public blk-mq definitions from `<linux/blk-mq.h>` and local `blk-stat.h`, plus types from request queues, gendisks, hctxs, tags, schedulers, and debugfs. It is an internal integration layer: external drivers see public blk-mq APIs, while core block files include this header to share non-public helpers.

## Risks And Edge Cases

The key risk is misuse of inline helpers outside their invariants. `blk_mq_get_ctx()` assumes per-CPU ctx lifetime is persistent and does not require preemption stability. `blk_mq_put_driver_tag()` only releases a driver tag when both driver and scheduler tag state indicate one is held. `hctx_may_queue()` can affect fairness and forward progress for shared tags; incorrect flags would over-throttle or starve queues. The dispatch macro must match blocking-vs-nonblocking tag-set behavior, because drivers with blocking `queue_rq()` need SRCU sleepability.

## Test Signals

Compile coverage with different `CONFIG_BLK_MQ`, scheduler, polling, and debugfs options is important because many users are inline. Runtime signals include no lost dispatch when stopping/starting queues, fair tag allocation under shared tag sets, correct poll hctx mapping, and successful sysfs/debugfs hctx registration paths using the declared helpers.
