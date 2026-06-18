# sources/distributed-fs/ceph-client/block/blk-stat.h

## Purpose

`blk-stat.h` declares the block latency statistics callback interface and inline activation helpers. It is the contract between blk-mq completion accounting and consumers that need bucketed latency windows.

## Important APIs, Types, And Functions

`struct blk_stat_callback` contains an RCU list node, timer, per-CPU bucket array, bucket function, bucket count, aggregate bucket array, timer callback, private data, and RCU head. Public functions allocate/free queue stats, add latency samples, enable/disable accounting, allocate/add/remove/free callbacks, and manipulate `struct blk_rq_stat`. Inline helpers are `blk_stat_is_active()`, `blk_stat_activate_nsecs()`, `blk_stat_activate_msecs()`, and `blk_stat_deactivate()`.

## Control Flow

Consumers allocate a callback, add it to a request queue, then activate it for a time window with nanosecond or millisecond helpers. While the timer is pending, completion accounting calls the bucket function for each eligible request and records latency in the current CPU's bucket. Timer expiry aggregates samples and invokes the consumer callback. Deactivation synchronously deletes the timer.

## State And Persistence Behavior

The header defines transient in-memory callback state only. Timer pending state is the active/inactive indicator. Per-CPU and aggregate arrays are owned by the implementation and freed after RCU grace.

## Dependencies And Integration Points

It includes block device definitions, ktime/jiffies conversion, RCU, and timers. It is included by `blk-mq.h`, `blk-stat.c`, and block policies that consume latency statistics.

## Risks And Edge Cases

Consumers must remove a callback before freeing it and must not add one callback to multiple queues. Timer activation uses jiffies conversion, so very small windows round according to kernel timer behavior. Bucket functions must validate request types and return `-1` for ignored requests to avoid corrupting unrelated buckets.

## Test Signals

Compile coverage, callback lifecycle tests, activation/deactivation timing, RCU-safe removal under concurrent completion, and bucket-count bounds checks in consumers are the primary signals.
