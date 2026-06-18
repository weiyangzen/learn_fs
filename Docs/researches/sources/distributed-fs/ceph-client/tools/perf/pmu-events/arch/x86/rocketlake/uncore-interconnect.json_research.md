# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/uncore-interconnect.json

## Purpose
This JSON file defines eight Rocket Lake uncore interconnect PMU event aliases for perf. The events describe arbitration/coherency tracker request counts and occupancy measurements for the uncore arbiter/data paths. They are used directly by users interested in SoC/interconnect behavior and indirectly by system-level memory and uncore metrics in `rkl-metrics.json`.

## Data shape and important fields
The file is a JSON array of 8 event objects. The observed keys are `EventName`, `BriefDescription`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `Experimental`.

The aliases are:

- `UNC_ARB_COH_TRK_REQUESTS.ALL`
- `UNC_ARB_DAT_OCCUPANCY.ALL`
- `UNC_ARB_DAT_OCCUPANCY.RD`
- `UNC_ARB_REQ_TRK_OCCUPANCY.DRD`
- `UNC_ARB_TRK_OCCUPANCY.ALL`
- `UNC_ARB_TRK_OCCUPANCY.RD`
- `UNC_ARB_TRK_REQUESTS.ALL`
- `UNC_ARB_TRK_REQUESTS.RD`

All entries use `Unit` `arb` and `PerPkg` `1`, marking them as package-level uncore events rather than per-logical-CPU core events. All entries have `Experimental` `1`, which signals that the definitions may be less stable or less generally supported than normal core aliases. They use uncore counters `0,1,2,3` with event codes such as `0x81`, `0x83`, and `0x84`, and umasks for all/read/demand-read variants.

## Control flow and integration
The file is declarative. `jevents.py` converts each object into a generated `pmu_event` entry with uncore PMU unit metadata. At runtime, perf matches the event's `Unit` to PMUs whose names wildcard-match the unit, exposes the aliases in `perf list`, and programs the relevant uncore arbiter PMU when the user or a metric requests them.

`rkl-metrics.json` references several of these names, including `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_DAT_OCCUPANCY.RD`, `UNC_ARB_TRK_OCCUPANCY.RD`, `UNC_ARB_TRK_REQUESTS.ALL`, and `UNC_ARB_TRK_REQUESTS.RD`. That creates a direct integration path from this file into memory bandwidth, latency, and SoC-level derived metrics.

## State, persistence, and dependencies
The file has no mutable local state. Its persisted build product is generated event-table data. Runtime state is in the uncore arbiter PMU counters, which are package-scoped and may be shared across CPUs. The `PerPkg` flag matters because aggregation semantics differ from per-thread or per-core events.

The file depends on Rocket Lake exposing an `arb` uncore PMU compatible with these event encodings. It also depends on perf's uncore PMU unit matching and on correct package aggregation in metric evaluation.

## Risks
The `Experimental` marker is the main risk signal. These counters may be unavailable, renamed by kernel PMU drivers, or not stable across steppings. Because the events are package-level, incorrect aggregation can double-count or under-count when metrics are collected per CPU instead of per package.

Metric formulas that combine core and uncore events can be hard to schedule and interpret. If uncore events are missing, formulas in `rkl-metrics.json` may fail resolution or silently fall back only where `has_event(...)` guards exist.

## Test signals
Useful checks include `jq empty uncore-interconnect.json`, generated `jevents` output inspection for `unit = "arb"` and `perpkg = true`, and `perf list` on Rocket Lake to confirm the uncore aliases appear under an uncore arbiter PMU. Runtime smoke tests should pin aggregation to package scope and verify representative events such as `UNC_ARB_TRK_REQUESTS.ALL` and `UNC_ARB_DAT_OCCUPANCY.RD` can be counted. Metric tests should cover formulas that reference these aliases.
