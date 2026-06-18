# sources/distributed-fs/ceph/src/osd/osd_perf_counters.cc

## Purpose

`osd_perf_counters.cc` registers the OSD, peering-state, and scrubber performance counters declared in `osd_perf_counters.h`. It maps numeric counter IDs to public metric names, descriptions, priorities, units, average types, and histograms through `PerfCountersBuilder`.

## Important APIs and Functions

`build_osd_logger(CephContext*)` creates the main `osd` counter set. It defines operation latency and request-size histogram axes, registers client op counters, replica read counters, subop/recovery counters, OSD map/cache/storage counters, cache-tier counters, object-context cache counters, PG info counters, watch timeout counters, and scrub IO/reservation/result counters split across replicated and EC pools. `build_recoverystate_perf(CephContext*)` creates `recoverystate_perf` latency and invalidation counters for peering state transitions. `build_scrub_labeled_perf(CephContext*, std::string label)` creates a labeled scrub counter family for shallow/deep and replicated/EC combinations.

## Control Flow

Each builder function constructs a `PerfCountersBuilder` with a name and numeric range, sets default priority as needed, calls `add_u64`, `add_u64_counter`, `add_time_avg`, `add_u64_avg`, or `add_u64_counter_histogram`, and returns `create_perf_counters()`. The main OSD logger starts with useful/critical operation metrics, lowers default priority for debug-only internal metrics, then raises priority for scrub metrics. Histogram configuration is local and declarative: op latency/request-size histograms use log2 scales, while scrub reservation replica-count uses a linear x axis and log2 duration y axis.

## State and Persistence Behavior

The file does not update counters and stores no persistent state. It defines the runtime schema of perf counters exposed by an OSD process. Counter values live inside the returned `PerfCounters` objects and are incremented elsewhere by `PrimaryLogPG`, `OSD`, scrubber, peering, and recovery code.

## Dependencies and Integration Points

It depends on `common/perf_counters.h`, `common/perf_counters_key.h`, `CephContext`, and the counter ID ranges in the header. Integration points found in the OSD tree include `PrimaryLogPG` increments for op latency, bytes, WIP, cache hits, and delayed ops; `OSD.cc` queue/dequeue latency updates; `PeeringState.cc` recovery-state latency updates; and scrubber code using both global scrub IDs and labeled scrub counters.

## Risks and Test Signals

The main risks are ID/name mismatches with the enum, duplicate or missing registrations, unit/priority mistakes that affect monitoring, and histogram axis choices that hide important latency ranges. Since external dashboards may rely on names, renames are compatibility-sensitive. Test signals include perf counter schema tests, daemon startup tests that build all counter sets, `ceph daemon osd.N perf dump` coverage, dashboard/telemetry compatibility checks, and scrub/peering workloads that verify counters move.
