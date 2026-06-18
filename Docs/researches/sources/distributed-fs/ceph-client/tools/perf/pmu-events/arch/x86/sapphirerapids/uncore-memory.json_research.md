# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-memory.json

## Purpose

This 403-entry JSON catalog defines Sapphire Rapids package-level uncore memory PMU events for Linux `perf`. It covers three uncore units: 161 `iMC` events for standard integrated memory controllers, 67 `MCHBM` events for HBM memory-channel controller behavior, and 175 `M2HBM` events for mesh-to-HBM and directory/fabric behavior. The file lets users and metrics request named aliases for DRAM/HBM CAS traffic, activate/precharge behavior, queue occupancy, power-state memory events, directory hit/miss/update states, direct-to-core/direct-to-UPI paths, prefetch CAM activity, tracker pressure, and read/write pending queues instead of hand-programming event select and mask fields.

## Important APIs, Types, and Data

The schema is the perf PMU event-object schema: `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, optional `PublicDescription`, and several less common fields such as `FCMask`, `PortMask`, and `Experimental`. Every event is package scoped through `PerPkg: 1` and is constrained to counters `0,1,2,3`. Major `iMC` and `MCHBM` families include `UNC_M*_ACT_COUNT`, `UNC_M*_CAS_COUNT`, `UNC_M*_CAS_ISSUED_REQ_LEN`, `UNC_M*_PRE_COUNT`, `UNC_M*_RDB_*`, `UNC_M*_RPQ_*`, and `UNC_M*_WPQ_*`. `iMC` also adds PMM queue, power, refresh, scrub/buffer, and tag-check families. `M2HBM` adds directory hit/miss/update, `DIRECT2CORE`, `DIRECT2UPI`, distress, ingress/egress queue, prefetch CAM, tracker, and write-tracker families.

## Control Flow

There is no executable control flow in this file. Perf's pmu-events build/runtime path reads the array, maps each record to the Sapphire Rapids model, and exposes aliases under the corresponding uncore PMU unit. When a user requests an alias, perf selects the `Unit`, programs `EventCode`, `UMask`, filter masks, and one of the allowed counters, then aggregates at package scope. Metrics and operators interpret related aliases together, for example read/write CAS counts for bandwidth, activate/precharge counts for row locality, and queue occupancy/inserts for memory-controller pressure.

## State and Persistence Behavior

The persistent state is the checked-in alias-to-encoding contract and the distinction between `iMC`, `MCHBM`, and `M2HBM` counting domains. Runtime counter state lives only in uncore PMU hardware during a perf session and is shared by all work on the package. The package-scoped nature means counts are not attributable to a single task without careful workload isolation. HBM, PMM, and directory/fabric events also persist platform assumptions: unavailable units or disabled HBM modes may expose no counters or zero counts even though the JSON parses.

## Dependencies and Integration Points

This file integrates with `tools/perf/pmu-events` JSON parsing, generated perf event tables, `perf list`, `perf stat`, Sapphire Rapids uncore PMU kernel drivers, and higher-level memory bandwidth/locality metrics. It complements core-side cache/TLB event files by measuring controller and fabric traffic after requests leave cores. Downstream usage depends on Intel's uncore PMU programming model, kernel support for the named uncore units, and SKU/firmware exposure of HBM, PMM, and memory power telemetry.

## Risks

The largest risk is semantic drift in event encodings: a valid `EventCode`/`UMask` pair can still count the wrong HBM channel, request type, or directory state. Some aliases intentionally overlap as aggregate and per-channel variants, so metric formulas can double-count if they sum both. Blank `UMask` fields on some `M2HBM` write and non-inclusive variants need parser support and manual validation against hardware docs. HBM and PMM events are platform dependent, and package-level uncore counts are noisy on shared systems. Queue occupancy events often need normalization by clockticks; treating them as simple transaction counts can mislead analysis.

## Test Signals

Useful checks include JSON parsing with perf's pmu-events tooling, `perf list` coverage for `iMC`, `MCHBM`, and `M2HBM` aliases on Sapphire Rapids, and event encoding comparisons against Intel reference tables. Runtime smoke tests should use memory streaming read/write workloads, HBM-local workloads where available, and multi-socket traffic to exercise directory/direct-to-UPI events. Metric tests should verify CAS-to-byte conversion, aggregate versus per-channel consistency, package aggregation, and graceful absence when a platform lacks HBM or PMM support.
