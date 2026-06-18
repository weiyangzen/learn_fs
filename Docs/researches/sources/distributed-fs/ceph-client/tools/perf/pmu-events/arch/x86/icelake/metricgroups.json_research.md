# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/metricgroups.json

## Purpose

This file supplies descriptions for 138 Ice Lake metric groups. It is the companion metadata for `icl-metrics.json`, making metric group listings readable in `perf list metricgroup` and related output. The groups cover general analysis buckets, Intel Top-Down Microarchitecture Analysis levels, bottleneck-view groups, issue-taxonomy groups, and per-category child groups.

## Important APIs, Types, And Data

Unlike the event JSON files, this file is a JSON object rather than an array. Each key is a metric group name and each value is its description string. Keys include broad groups such as `Backend`, `Frontend`, `Mem`, `Offcore`, `Power`, `Pipeline`, `Summary`, `Branches`, `Compute`, `Flops`, `MemoryBW`, `MemoryLat`, `MemoryTLB`, and `LockCont`; Top-Down groups such as `TopdownL1` through `TopdownL6`, `TmaL1`, `TmaL2`, `TmaL3mem`, and `tma_L*_group`; bottleneck-view groups such as `BvBC`, `BvBO`, `BvCB`, `BvFB`, `BvMB`, `BvML`, `BvMP`, `BvMS`, `BvMT`, `BvOB`, and `BvUW`; and issue groups such as `tma_issueBW`, `tma_issueTLB`, `tma_issueBM`, `tma_issueFB`, and `tma_issueSyncxn`.

Most values are standardized descriptions such as "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet", "Metrics for top-down breakdown at level N", "Metrics contributing to ... category", or "Metrics related by the issue $...".

## Control Flow

`jevents.py` treats files ending in `metricgroups.json` specially. It loads the object mapping, stores group-description pairs in its metricgroup map, and emits sorted generated metadata into `pmu-events.c`. The normal event-loop path intentionally skips `metricgroups.json` so these entries are not interpreted as events or metrics.

At runtime, perf list and metricgroup display code can look up a group name and print the generated description. Metric computation still comes from metric entries in `icl-metrics.json`; this file only documents and organizes the group namespace.

## State And Persistence Behavior

The file persists descriptive metadata only. Runtime state is the generated group-description lookup table compiled into perf. There is no mutable state, no counters, and no formulas. A stale description can mislead users but does not change the measured values.

## Dependencies And Integration Points

This file depends on the group names used by `icl-metrics.json`; a group description has user value only if metrics reference the same string in their semicolon-separated `MetricGroup` fields. It integrates with `jevents.py` metricgroup parsing, generated `pmu-events.c`, `builtin-list.c`, and any command that prints metric group descriptions. The build also generates `extra-metricgroups.json` for some architectures, so this static file shares the same group-description contract.

## Risks And Edge Cases

Shape is the main schema risk: converting this object into an array like normal event files would break metricgroup parsing. Misspelled keys do not necessarily break builds, but they create orphan descriptions or leave active metric groups undescribed. Similar names such as `MemoryBW` and `Memory_BW`, `MemoryLat` and `Memory_Lat`, or `MachineClears` and `Machine_Clears` are intentional compatibility/user-facing surfaces and should not be normalized casually. Descriptions containing `$issue...` tokens are documentation strings, not variables to expand.

## Test Signals

Validate with `jq empty metricgroups.json`, then run `jevents.py` generation and `perf test pmu-events`. `perf list metricgroup` or `perf list --details` should show descriptions for representative groups such as `TopdownL1`, `Frontend`, `MemoryBW`, `BvML`, and `tma_issueTLB`. Cross-checking active groups from `icl-metrics.json` against keys in this file is a useful orphan/missing-description test.
