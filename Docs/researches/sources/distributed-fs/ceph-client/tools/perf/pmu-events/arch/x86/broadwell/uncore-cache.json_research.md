# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/uncore-cache.json

## Purpose

`uncore-cache.json` defines 16 Broadwell uncore cache PMU events for last-level cache/CBOX behavior. It covers L3 lookup outcomes by request type and MESI state, cross-core snoop responses, and the fixed uncore clock counter.

## Important APIs, Types, and Data Fields

The file is a JSON array using uncore-specific schema fields in addition to the normal event fields. Important fields are `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and `PublicDescription`. The main families are `UNC_CBO_CACHE_LOOKUP.*`, `UNC_CBO_XSNP_RESPONSE.*`, and `UNC_CLOCK.SOCKET`. Most rows use `Unit: CBOX`, `Counter: 0,1`, and `PerPkg: 1`; the clock row uses `Counter: FIXED`, `EventCode: 0xff`, and `Unit: cbox_0`.

## Control Flow and Data Flow

There is no code-level control flow. Perf's generated event table exposes these as uncore PMU events rather than per-core events. At runtime, perf maps `Unit` to the relevant uncore PMU instance, configures package-level CBOX counters, and reports counts per package. Cache lookup rows count LLC lookup results; snoop response rows count cross-core snoop outcomes such as hit, hit-modified, and miss.

## State and Persistence Behavior

The file persists static uncore event metadata. It stores no cache state or package counter values. `PerPkg: 1` signals package-level aggregation semantics, which affects how perf presents and aggregates results on multi-socket or multi-package systems.

## Dependencies and Integration Points

The file depends on Broadwell uncore CBOX PMU support and kernel exposure of matching uncore PMU names. It integrates with perf's uncore PMU lookup, `perf stat` package-level measurement, LLC behavior analysis, cross-core data-sharing diagnosis, and memory hierarchy metrics that need LLC hits/misses or HITM snoop evidence.

## Risks and Edge Cases

Uncore unit naming is platform-sensitive. If the kernel exposes CBOX instances with names that do not match generated expectations, events may list but fail to schedule. `PerPkg` aggregation can surprise users expecting per-core attribution. MESI-state filters are dense bitmasks, so umask mistakes can confuse invalid, shared/exclusive, modified, and all-state lookup counts. The fixed `UNC_CLOCK.SOCKET` row uses `cbox_0`, which is a special unit form compared with the other `CBOX` rows.

## Test Signals

Validation should include `perf list` visibility under uncore/CBOX PMUs, `perf stat` acceptance for representative `UNC_CBO_CACHE_LOOKUP.*` and `UNC_CBO_XSNP_RESPONSE.*` rows, and nonzero `UNC_CLOCK.SOCKET` counts during an interval. Cache-stressing workloads should increase lookup counts; cross-core sharing workloads should affect snoop response counters.
