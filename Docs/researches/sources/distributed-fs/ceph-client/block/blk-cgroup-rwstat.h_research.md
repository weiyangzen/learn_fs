# sources/distributed-fs/ceph-client/block/blk-cgroup-rwstat.h

## Purpose

`blk-cgroup-rwstat.h` declares and partially implements legacy blkcg read/write statistics. It provides stat categories, storage types, and inline add/read/reset/total/aux helpers used by older blkcg policies.

## Important APIs, Types, And Functions

`enum blkg_rwstat_type` defines read, write, sync, async, discard, count, and total categories. `struct blkg_rwstat` stores per-CPU counters and auxiliary atomic counters. `struct blkg_rwstat_sample` is a snapshot array.

Inline helpers are `blkg_rwstat_read_counter()`, `blkg_rwstat_add()`, `blkg_rwstat_read()`, `blkg_rwstat_total()`, `blkg_rwstat_reset()`, and `blkg_rwstat_add_aux()`. Out-of-line functions cover init/exit, printing, and recursive sum.

## Control Flow, State, And Persistence

`blkg_rwstat_add()` classifies an operation as discard/write/read and sync/async, then adds to the matching per-CPU counters with a large batch size because drift is acceptable. `blkg_rwstat_read()` samples local counters only. `blkg_rwstat_read_counter()` and recursive paths include aux counters so dead child stats persist in recursive views. Reset clears both local and aux state.

## Dependencies And Integration Points

The header depends on `blk-cgroup.h`, request operation helpers, `percpu_counter`, and blkcg policy data. It is included by BFQ and legacy rwstat implementation code.

## Risks And Test Signals

The helpers are legacy and unsuitable for exact instantaneous accounting. `blkg_rwstat_total()` sums read plus write, while the printing helper's total includes discard. Test classification, reset, aux propagation, total semantics, and builds with legacy users enabled.
