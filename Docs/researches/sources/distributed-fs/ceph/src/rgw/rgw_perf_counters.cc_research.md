# sources/distributed-fs/ceph/src/rgw/rgw_perf_counters.cc

## Purpose
`rgw_perf_counters.cc` registers and manages RGW performance counters for frontend requests, operation-level per-user/per-bucket/global metrics, persistent topic queue metrics, and lifecycle per-bucket metrics.

## Important APIs, Types, And Functions
It defines global `PerfCounters *perfcounter`, builder helpers `add_rgw_frontend_counters()`, `add_rgw_op_counters()`, `add_rgw_topic_counters()`, lifecycle builder `add_lc_counters()`, init/stop APIs `rgw_perf_start()` and `rgw_perf_stop()`, operation counter cache helpers in `rgw::op_counters`, `persistent_topic_counters::CountersManager`, and `lc_counters::get()`.

## Control Flow
Startup calls `frontend_counters_init()`, optionally creates user, bucket, and lifecycle `PerfCountersCache` objects based on config, then initializes global op counters. Operation code asks `rgw::op_counters::get(req_state*)` for cached user and bucket counters and updates user, bucket, and global counters through `inc()`/`tinc()`. Topic counters are created per topic and removed in the manager destructor. Shutdown removes and deletes registered counters and caches.

## State And Persistence
Counters are in-memory perf-counter objects registered with Ceph's perf counter collection, not durable metadata. Label keys are built from users, tenants, buckets, and topics. Lifecycle per-bucket counters are debug-priority because labeled counters are not always exposed by mgr Prometheus paths.

## Dependencies And Integration Points
This file depends on `common/perf_counters`, `PerfCountersCache`, `perf_counters_key`, `CephContext`, config options, and `req_state` user/bucket fields. `rgw_process.cc` increments frontend queue and request counters. Pubsub and lifecycle paths consume the topic/lifecycle counters.

## Risks And Test Signals
Risks include counter id mismatches with the header enum, leaks or dangling registration on shutdown, null user/bucket assumptions in `get()`, cache key cardinality, and negative increments represented as unsigned counter operations. Test signals include daemon startup/shutdown under counter caches enabled/disabled, per-user/per-bucket metric creation with tenants, persistent-topic counter lifecycle, lifecycle counter lookup, and metric name/id stability.
