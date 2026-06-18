# sources/distributed-fs/ceph/src/rgw/rgw_perf_counters.h

## Purpose
`rgw_perf_counters.h` declares the RGW perf counter id ranges and counter-management APIs used by the daemon and feature modules.

## Important APIs, Types, And Functions
It exports `perfcounter`, `rgw_perf_start()`, and `rgw_perf_stop()`. Enum ranges define frontend counters (`l_rgw_*`), operation counters (`l_rgw_op_*`), persistent topic counters (`l_rgw_persistent_topic_*`), and lifecycle per-bucket counters (`l_rgw_lc_per_bucket_*`). `rgw::op_counters::CountersContainer` carries optional user and bucket counter handles, with `get()`, `inc()`, and `tinc()` helpers. `rgw::persistent_topic_counters::CountersManager` owns a topic counter object. `rgw::lc_counters::get()` returns per-bucket lifecycle counters.

## Control Flow
The header establishes ids consumed by builder functions in the `.cc` file. Callers do not construct counters directly except through manager/helper APIs.

## State And Persistence
The header defines no state besides external declarations. Numeric ids are effectively ABI-like inside the daemon because they must match builder registration and metric consumers.

## Dependencies And Integration Points
It depends on common forward declarations, `rgw_common.h`, `PerfCountersCache`, and perf-counter key helpers. Request processing, lifecycle, pubsub, and operation implementations integrate through these declarations.

## Risks And Test Signals
Risks include adding ids outside ranges, changing order without updating builders, or calling helpers before `rgw_perf_start()`. Tests should verify startup registration, metric availability, and counter increments from representative object, bucket, lifecycle, and pubsub flows.
