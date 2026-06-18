# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-memory.json

## Purpose
`uncore-memory.json` defines Snow Ridge uncore integrated-memory-controller events for `perf list`, `perf stat`, and metric evaluation. The file has 63 event objects focused on iMC DRAM traffic, queue pressure, power-down/self-refresh residency, command scheduling, refreshes, parity errors, read/write pending queues, and memory controller clocks. It also provides two derived aliases, `LLC_MISSES.MEM_READ` and `LLC_MISSES.MEM_WRITE`, scaled as 64-byte requests from CAS read/write counts.

## Important APIs, Types, and Fields
The public interface is the perf PMU event JSON schema. Every entry is a JSON object with fields such as `EventName`, `BriefDescription`, `PublicDescription`, `EventCode`, `UMask`, `Counter`, `Unit`, and `PerPkg`. `Unit` is consistently `iMC`, so the events bind to Snow Ridge memory controller PMUs rather than core PMUs. `Counter` is usually `0,1,2,3`; `UNC_M_CLOCKTICKS_FREERUN` uses fixed/free-running counter metadata. `ScaleUnit` appears on the LLC miss aliases to indicate 64-byte transfer accounting. Forty entries carry `Experimental`, marking them more fragile for user-facing workflows. Two entries also define `MetricName` and `MetricExpr`: `power_channel_ppd` and `power_self_refresh`, each computed as event cycles divided by `UNC_M_CLOCKTICKS` times 100.

## Control Flow and Data Flow
The file has no in-file branches or functions. Build-time flow is: perf's PMU event tooling parses the JSON array, validates known keys, generates architecture-specific event tables, and later exposes each `EventName` as a named event when the current CPU model maps to Snow Ridge. Runtime flow is user driven: a command such as `perf stat -e UNC_M_CAS_COUNT.RD` resolves the name, programs the iMC PMU with `EventCode` and `UMask`, selects one of the listed counters, and aggregates per-package/per-controller counts according to perf's uncore PMU discovery. Metric expressions depend on the presence and correct naming of their referenced base events.

## State and Persistence Behavior
The source file is static repository data. Runtime counter state lives in hardware PMU counters and perf's measurement process, not in the JSON. `PerPkg: 1` tells perf that events are package-scoped; this affects aggregation and can surprise callers expecting per-core behavior. Queue occupancy events such as `UNC_M_RDB_OCCUPANCY`, `UNC_M_RPQ_OCCUPANCY_PCH0/PCH1`, and `UNC_M_WPQ_OCCUPANCY_PCH0/PCH1` count occupancy over cycles, so consumers must divide by corresponding insert or active-cycle events for average residency-style interpretations.

## Dependencies and Integration Points
The file depends on perf's JSON schema support for uncore events, Snow Ridge CPU model mapping, and kernel PMU names for `iMC`. It integrates with sibling Snow Ridge event files and shared perf scripts that generate C tables from JSON. Metric expressions depend on `UNC_M_CLOCKTICKS` and the exact base event names in this file. Downstream tools such as `perf list`, `perf stat --metric-only`, and any generated event aliases rely on the event names remaining stable.

## Risks and Edge Cases
The largest risk is semantic drift between Intel event definitions and the JSON encodings, especially because most entries are marked experimental. Alias names beginning with `LLC_MISSES` may be misread as core LLC events even though they derive from memory-controller CAS counts. `ScaleUnit: 64Bytes` is meaningful only if downstream code uses it consistently for bandwidth or byte conversions. PCH0/PCH1 queue events must not be aggregated blindly with other channels without understanding package topology. The two metric expressions divide by clock ticks, so zero or unavailable `UNC_M_CLOCKTICKS` readings would produce invalid metrics.

## Test Signals
Strong checks are `jq empty` for syntax, perf PMU event-table generation, and `perf list` on a Snow Ridge system showing representative events such as `UNC_M_CAS_COUNT.RD`, `UNC_M_POWER_SELF_REFRESH`, and `LLC_MISSES.MEM_READ`. Runtime smoke tests should use `perf stat -e UNC_M_CLOCKTICKS,UNC_M_CAS_COUNT.RD,UNC_M_CAS_COUNT.WR` on supported hardware and confirm nonzero counts under memory load. Metric tests should verify that `power_channel_ppd` and `power_self_refresh` resolve their base events and render percentages.
