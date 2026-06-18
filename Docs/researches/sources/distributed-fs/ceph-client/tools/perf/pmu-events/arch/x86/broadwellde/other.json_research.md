# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/other.json

## Purpose
Small Broadwell-DE catalog for miscellaneous privilege-level and lock-duration events that do not fit the main cache, memory, frontend, floating-point, or pipeline buckets. It defines 4 events: `CPL_CYCLES.RING0`, `CPL_CYCLES.RING0_TRANS`, `CPL_CYCLES.RING123`, and `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`.

## Important APIs, Types, and Functions
All entries use standard perf PMU fields: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. One event uses `CounterMask` plus `EdgeDetect` for ring-0 transition counting. There are no functions; the alias names are the exported interface.

## Control Flow
Perf programs these events directly when requested. Metrics may use privilege cycle information for OS/kernel utilization analysis, while split-lock uncacheable lock duration complements cache lock and split-lock signals from the cache file.

## State and Persistence
The file has no runtime state. Runtime behavior is simple counter collection with one transition-style event that depends on edge detection. Persistent semantics are privilege-level cycle attribution and split-lock duration visibility.

## Dependencies and Integration
The file integrates with system and OS-oriented metrics in `bdwde-metrics.json`, especially kernel utilization and lock-contention analysis. It depends on perf's support for event masks, counter masks, and edge detection.

## Risks
Privilege cycle interpretation depends on kernel/user filtering and workload context. Ring transition counts can be misunderstood as total kernel time, and split-lock duration is a narrow signal that should be correlated with `SQ_MISC.SPLIT_LOCK` and lock-cycle events from `cache.json`.

## Test Signals
Validate JSON, confirm the four aliases are listed by perf, run privilege-level cycle counts on user-only and syscall-heavy workloads, and run split-lock tests only in controlled environments where platform policy allows observation without disrupting the system.
