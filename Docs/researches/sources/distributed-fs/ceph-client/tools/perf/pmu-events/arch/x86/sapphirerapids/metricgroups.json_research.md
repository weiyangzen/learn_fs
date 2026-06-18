# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/metricgroups.json

## Purpose
`metricgroups.json` maps Sapphire Rapids metric group names to short descriptions. Unlike the event JSON files, it is a JSON object rather than an array of event records. It provides grouping labels used by perf's metric listing and UI paths so users can discover metrics by categories such as `Frontend`, `Backend`, `MemoryBound`, `Flops`, `TopdownL1`, and detailed `tma_*_group` categories.

## Important APIs, types, and schema fields
The API is a string-to-string object: keys are metric group identifiers, values are descriptions. There are 143 group entries. Most legacy-style groups share the description "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet"; top-down level groups use descriptions such as "Metrics for top-down breakdown at level 1"; category-specific groups use "Metrics contributing to ... category"; issue groups use "Metrics related by the issue $...".

## Control flow and integration
The perf PMU event generator ingests this object together with metrics files for the same CPU model. Runtime `perf list metricgroups` and metric browsing code can display group names and descriptions. `builtin-list.c` contains logic for metric group printing, filtering, and JSON output; this file supplies the group-name vocabulary and display text. There is no control flow within the file; its keys are lookup labels referenced by metric definitions elsewhere.

## State and persistence behavior
This is static metadata. It persists grouping taxonomy, not metric formulas or measurements. Changing a key can orphan metrics that reference the old group name or alter `perf list` filtering behavior. Changing descriptions affects user-facing help and discoverability but not counter programming.

## Dependencies
The file depends on consistency with Sapphire Rapids metric definition files and perf metric parsing/listing code. It integrates with top-down metrics, issue-oriented TMA groups (`tma_issue*`), and broad group labels used by user workflows (`HPC`, `Server`, `Power`, `SoC`, `Pipeline`, `Mem`, `Offcore`, `Branches`, `CacheHits`, `CacheMisses`).

## Risks and edge cases
Because this file has a different JSON shape, tools that assume every pmu-events JSON file is an array of objects will fail. Group-name drift is the main functional risk: metric expressions can still parse, but list filtering and grouping become incomplete or misleading. Duplicate-looking taxonomy exists intentionally, for example `TopdownL1` and `tma_L1_group`, `MemoryBW` and `Memory_BW`, `MachineClears` and `Machine_Clears`; cleanup that normalizes names may break compatibility.

## Test signals
Validate with `jq type` expecting `object`, not `array`. Cross-check that metric files referencing groups use keys present here. `perf list metricgroups`, `perf list --json metricgroups`, and metric parser tests should show these labels without crashes. Static tests should preserve intentionally similar names and verify no group value is empty.
