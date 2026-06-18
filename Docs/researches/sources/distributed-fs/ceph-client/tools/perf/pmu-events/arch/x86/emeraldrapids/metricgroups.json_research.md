# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/metricgroups.json

## Purpose

`metricgroups.json` is a static perf PMU metadata file for the x86 Emerald Rapids CPU model. It maps metric group names to human-readable descriptions so perf's generated event tables can present and filter related metrics by category. The file is not executable Ceph code; it is part of the vendored Linux `tools/perf` event database under the Ceph client source tree.

The file contains 143 JSON object entries. Most legacy-style group names, such as `Backend`, `Frontend`, `Pipeline`, `MemoryBound`, `Branches`, `PortsUtil`, `HPC`, and `Summary`, use the shared description `Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet`. Top-down groups `TopdownL1` through `TopdownL6` and `tma_L1_group` through `tma_L6_group` describe the hierarchy levels used by Intel Top-down Microarchitecture Analysis. The remaining `tma_*_group` keys describe contributors to specific TMA categories, such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, `tma_ports_utilization_group`, and `tma_retiring_group`.

## Important APIs, Types, and Data

The schema is a flat JSON object: each property key is a metric group identifier and each value is a display description string. There are no functions, classes, or runtime APIs in this file. The important contract is the key namespace consumed by perf's PMU event tooling and by metric definitions elsewhere in the same Emerald Rapids directory.

The group names act as references for metric categorization. Camel-case names preserve older or user-facing groups, while lowercase `tma_*` names align with generated top-down metric identifiers and issue categories. The descriptions are intentionally short because detailed formulas and event encodings live in the metric and event JSON files rather than in this group index.

## Control Flow

There is no local control flow. At build or runtime, perf's PMU event parser loads architecture/model JSON data, associates metrics with group names, and uses this file to resolve group descriptions for listing, filtering, and display. If a metric references one of these groups, this object supplies the group label text shown to users and tools.

## State and Persistence Behavior

The file is immutable source metadata. It does not persist runtime state, counters, or measurements. Its contents are compiled into or loaded by perf tooling as part of the CPU PMU event database. Any stateful behavior happens in perf's event parser and generated tables, not in this JSON file.

## Dependencies and Integration Points

This file depends on perf's PMU JSON schema and the Emerald Rapids event/metric set around it. It integrates with Linux `tools/perf/pmu-events` generators, the x86 CPU model mapping logic, `perf list`, `perf stat -M`, metric grouping, and top-down metric presentation. It also indirectly integrates with Intel's Top-down Microarchitecture Analysis taxonomy, since most group descriptions and names mirror that spreadsheet-driven hierarchy.

## Risks and Edge Cases

The file is schema-light, so typos are the primary risk. A misspelled group key can silently break grouping for metrics that expect the canonical name, or create duplicate-looking categories. Duplicate semantic names are also possible: for example, both `MachineClears` and `Machine_Clears` exist, as do `MemoryBW` and `Memory_BW`, so downstream consumers must treat keys as exact identifiers rather than normalized labels.

Because the descriptions are generic, they do not validate whether all referenced TMA groups actually have corresponding metrics. Drift between this file and metric definition files can leave stale groups in `perf list` or omit descriptions for new metrics. JSON object ordering may be preserved for readability in source, but consumers should not depend on it.

## Test Signals

Useful validation signals include `python3 -m json.tool` or an equivalent JSON parser, perf PMU event generation tests, `perf list --details` on Emerald Rapids mappings, and metric-group filtering checks that ensure each metric group referenced by metric definitions has a description here. Diffing this file against the upstream Linux perf Emerald Rapids copy is also a strong drift signal for this vendored source tree.
