# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/metricgroups.json

## Purpose

`metricgroups.json` maps 124 metric group names to human-readable group descriptions for BroadwellX. It provides display and discovery text for generic groups such as `Backend`, `Frontend`, `Mem`, `Power`, `TopdownL1`, and for detailed Top-down group identifiers such as `tma_backend_bound_group`, `tma_fetch_latency_group`, and `tma_ports_utilized_3m_group`.

## Important APIs, types, and schema

Unlike event files, this is a single JSON object whose keys are group names and whose values are descriptions. `jevents.py` treats files ending in `metricgroups.json` specially: `preprocess_one_file()` loads the object directly, adds each key and description to the compact metric string table, and stores them in the global `_metricgroups` mapping. These values back the generated `describe_metricgroup()` behavior declared in `pmu-events.h`.

## Control flow and integration

The file is read during the preprocessing phase before generated C output is emitted. It is not processed by `process_one_file()` as an event table and does not create `pmu_event` or `pmu_metric` rows. Instead, it supplements `MetricGroup` values used throughout `bdx-metrics.json`, enabling perf list/reporting paths to describe groups. The keys mirror both legacy group names and generated Top-down group names; this dual coverage allows metrics to be found by broad topics and by hierarchical Top-down categories.

## State and persistence behavior

The file contains static display metadata. Its persistent effect is generated string data and a metric-group description lookup in `pmu-events.c`. There is no runtime mutation.

## Dependencies

The file depends on group names in `bdx-metrics.json` remaining consistent. It also depends on `jevents.py` special-casing the `metricgroups.json` suffix and on perf display code using `describe_metricgroup()`.

## Risks

Missing group keys do not necessarily break metric generation, but they reduce discoverability and can cause blank or generic descriptions in user-facing output. Stale descriptions are a documentation risk: many values are generic, and detailed group names need to match the semantics of their associated metrics. Because the file is an object rather than an array, accidental conversion to event-list format would make `jevents.py` handle it incorrectly.

## Test signals

Validation should include `jq type metricgroups.json` returning `object`, a build that regenerates metric-group descriptions without assertion failures, and a comparison between all semicolon-delimited groups in `bdx-metrics.json` and keys present in this file. Runtime smoke tests should check `perf list` or JSON list output for representative group descriptions such as `TopdownL1`, `tma_memory_bound_group`, and `Power`.
