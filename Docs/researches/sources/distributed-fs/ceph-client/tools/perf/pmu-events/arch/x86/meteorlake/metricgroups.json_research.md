# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/metricgroups.json

## Purpose

This file is the Meteor Lake metric group description map for perf PMU metrics. Unlike `frontend.json` and `memory.json`, it is not an event array. It is a JSON object mapping metric group names to human-readable descriptions. `jevents.py` treats files named `metricgroups.json` specially and emits a generated lookup table used by perf to describe metric groups.

The file contains 148 group entries. Most legacy group names map to "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet"; topdown level names map to level-specific descriptions; newer `tma_*_group` entries map to category-specific text such as "Metrics contributing to tma_frontend_bound category".

## Important schema fields and generated API surface

The schema is a flat string-to-string map:

- Key: metric group identifier, for example `Backend`, `Frontend`, `MemoryBound`, `TopdownL1`, `tma_frontend_bound_group`, or `tma_issueTLB`.
- Value: user-facing group description.

`jevents.py` special-cases the basename `metricgroups.json` in `preprocess_one_file`. For every map entry, it appends NUL-terminated group and description strings to the generated big C string table, stores offsets in `_metricgroups`, and later emits:

- `static const int metricgroups[][2]`, a sorted offset table.
- `const char *describe_metricgroup(const char *group)`, a binary-search lookup over the generated table.

No event counters are described in this file. There are no `EventName`, `MetricName`, `MetricExpr`, or PMU programming fields here.

## Content and control flow

Generation flow:

1. `jevents.py` sees `metricgroups.json` during the preprocessing walk.
2. The file is loaded as a JSON object, not as event records.
3. Each key is asserted to have length greater than one, then both key and description are stored in the generated string table with metric-string accounting.
4. `_metricgroups` is sorted when `print_metricgroups()` emits the C offset array.
5. Runtime callers use `describe_metricgroup(group)` to retrieve descriptions for display or return `NULL` when the group is unknown.

The map covers several naming generations:

- Broad spreadsheet-derived names such as `Backend`, `BadSpec`, `Frontend`, `MemoryBound`, `Retire`, `Summary`, and `TopdownL*` compatibility names.
- Short topical groups such as `DSB`, `FetchBW`, `FetchLat`, `IcMiss`, `Mem`, `MemoryBW`, `MemoryLat`, `Pipeline`, `Power`, and `PortsUtil`.
- TMA category groups such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, `tma_microcode_sequencer_group`, `tma_retiring_group`, and load/store TLB or utilization groups.
- Issue-link groups such as `tma_issueFB`, `tma_issueLat`, `tma_issueRFO`, and `tma_issueTLB`, whose descriptions identify related issue variables.

## State and persistence behavior

The file is static metadata. It persists into the generated `metricgroups` offset table and the big generated string table inside `pmu-events.c`. Runtime lookup is read-only binary search. There is no mutation, caching, or external storage owned by this JSON file.

The sorting and string offset assignment happen at generation time. That makes duplicate keys impossible in normal JSON object semantics after parsing, but it also means source order is not significant. Changing a description affects user-visible output but not PMU programming.

## Dependencies and integration points

Integration points include:

- `jevents.py` special-case logic for `item.name.endswith('metricgroups.json')`.
- `print_metricgroups()` and generated `describe_metricgroup()`.
- `perf list metricgroups`, metric display code, and Python helpers that present metric group names/descriptions.
- Metric definition files for Meteor Lake and generated Intel metrics that assign metrics into these groups via `MetricGroup` strings.

This file has a looser coupling than event JSON files: a group description can exist even if no current metric uses that group, and a metric can refer to a group missing from this map but then lose descriptive help text.

## Risks and maintenance notes

- Missing or misspelled group keys do not break PMU event programming, but they degrade `perf list` and metricgroup display quality.
- Renaming keys is externally visible because users and scripts may filter metrics by group name.
- Several group names are legacy or compatibility aliases with similar meanings (`MemoryBW` and `Memory_BW`, `MemoryLat` and `Memory_Lat`, `MachineClears` and `Machine_Clears`). Removing apparent duplicates can break existing metric references.
- The generic spreadsheet description is repeated many times. That is expected, but category-specific `tma_*_group` text should remain aligned with the corresponding metric category.
- Since lookup is sorted at generation time, tests should verify generated output rather than relying on JSON source order.

## Test and validation signals

Useful checks are:

- `jq` syntax validation and key count check for 148 entries.
- A perf build that regenerates `pmu-events.c` and emits the `metricgroups` table without duplicate/invalid string issues.
- `perf list metricgroups` or generated output inspection for representative groups such as `TopdownL1`, `Frontend`, `MemoryBound`, `tma_frontend_bound_group`, and `tma_memory_bound_group`.
- Metric parse/list tests should confirm metrics that reference these groups still display group descriptions.
- Review of group references in Meteor Lake metric files should catch stale names that are absent from this map or unused descriptions that may be obsolete.
