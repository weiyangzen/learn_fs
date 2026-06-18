# sources/distributed-fs/ceph/src/osd/osd_perf_counters.h

## Purpose

`osd_perf_counters.h` declares numeric performance-counter IDs for the OSD subsystem and factory functions that build the corresponding `PerfCounters` sets. It is the shared contract between metric registration and the many OSD call sites that increment counters by enum value.

## Important APIs and Types

`enum osd_counter_idx_t` reserves the `10000` range for main OSD counters, including client operation counts/bytes/latencies, read/write/rw breakdowns, delayed ops, replica reads, subops, recovery messages, map cache, storage stats, cache-tiering, object context cache, PG info, scrub reservation, watch timeouts, and scrub IO/result/reservation counters for replicated and EC pools. The file declares `build_osd_logger(CephContext*)`. A second anonymous enum starting at `20000` declares peering-state latency and invalidation counters plus `build_recoverystate_perf(CephContext*)`. A third anonymous enum starting at `20500` declares labeled scrub counters and `build_scrub_labeled_perf(CephContext*, std::string label)`.

## Control Flow

There is no executable control flow in the header. The enum order defines numeric IDs consumed by `osd_perf_counters.cc` registration and by callers invoking `PerfCounters::inc()`, `tinc()`, `hinc()`, and related update methods. Adding a counter requires adding the enum constant and registering it in the matching builder.

## State and Persistence Behavior

The header declares process-local metric IDs only. Counter values are runtime state inside `PerfCounters`; they are not persisted by these declarations. The numeric and string schema is externally observable through Ceph admin sockets and monitoring integrations.

## Dependencies and Integration Points

The header includes common Ceph forward declarations and perf counter builder types. It is included throughout OSD code wherever counters are updated: primary op handling, OSD queueing, peering-state machinery, scrubber code, and recovery/backfill code. `pg_scrubber.h` maps replicated and EC scrub counter groups to these IDs.

## Risks and Test Signals

Risks include accidentally reordering IDs, failing to register a declared ID, using an ID from the wrong counter set, and breaking external monitoring by changing names in the implementation. Because enum values are positional, inserting counters in the middle can affect consumers expecting stable numeric IDs. Test signals include build-time registration coverage, perf dump schema validation, monitoring integration tests, and workloads that exercise each counter family.
