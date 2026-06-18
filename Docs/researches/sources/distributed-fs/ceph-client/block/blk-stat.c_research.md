# sources/distributed-fs/ceph-client/block/blk-stat.c

## Purpose

`blk-stat.c` implements block request latency statistics callbacks. It lets consumers register bucketed callbacks that collect per-CPU request completion latency samples during a timer window, then aggregate them and invoke a policy callback. It also provides generic queue-level accounting enable/disable independent of callbacks.

## Important APIs, Types, And Functions

`struct blk_queue_stats` owns the callback list, lock, and accounting reference count. Request-stat helpers are `blk_rq_stat_init()`, `blk_rq_stat_add()`, and `blk_rq_stat_sum()`. `blk_stat_add()` records a completed request into active callbacks. `blk_stat_alloc_callback()`, `blk_stat_add_callback()`, `blk_stat_remove_callback()`, and `blk_stat_free_callback()` manage callback lifetime. `blk_stat_enable_accounting()` and `blk_stat_disable_accounting()` toggle the `QUEUE_FLAG_STATS` fast-path gate for users that only need request time/size accounting. `blk_alloc_queue_stats()` and `blk_free_queue_stats()` manage queue stats allocation.

## Control Flow

A consumer allocates a callback with a timer function, bucket function, bucket count, and private data, then adds it to a queue. Adding initializes all per-CPU buckets, links the callback via RCU, and sets `QUEUE_FLAG_STATS`. During request completion, blk-mq calls `blk_stat_add()` when the request has stats enabled; it computes latency from `rq->io_start_time_ns`, enters RCU, pins the current CPU, walks active callbacks, maps the request to a bucket, and accumulates the latency sample in the per-CPU bucket. When the callback timer fires, `blk_stat_timer_fn()` initializes aggregate buckets, sums all online CPU buckets into the aggregate, resets per-CPU buckets, and calls the consumer's timer function.

Removal unlinks the callback under the stats lock, clears `QUEUE_FLAG_STATS` if there are no callbacks and no accounting users, and synchronously deletes the timer. Freeing is RCU-delayed so readers that saw the callback list entry complete safely.

## State And Persistence Behavior

All stats are in memory. Samples are held in per-CPU `blk_rq_stat` arrays until the timer aggregates and resets them. Aggregate buckets store min, max, mean, sample count, and batch sum. The queue flag is reference-like: callbacks and explicit accounting users can keep it set. There is no durable persistence.

## Dependencies And Integration Points

It depends on RCU lists, per-CPU allocation, timers, blk-mq completion timestamps, and queue flags. Consumers include latency-control and writeback-throttling style policies that need rolling latency windows.

## Risks And Edge Cases

Mean aggregation deliberately ignores overflow by returning early if sample count wraps. Only online CPUs are summed at timer fire, so CPU hotplug behavior depends on per-CPU buffers being initialized across possible CPUs and active samples on offline CPUs not being expected for future windows. Callback removal must delete the timer before freeing. `blk_stat_add()` assumes `q->stats` exists and callbacks remain RCU-valid. Accounting enable/disable must remain balanced or stats overhead may stay enabled or be disabled too early.

## Test Signals

Tests should cover callback add/remove/free under I/O, timer aggregation across CPUs, bucket functions returning `-1`, concurrent accounting enable/disable, no callback leaks at queue teardown, and consumers seeing sane min/max/mean under synthetic latency distributions.
