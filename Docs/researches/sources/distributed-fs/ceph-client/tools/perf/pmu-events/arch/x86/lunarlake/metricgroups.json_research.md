# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/metricgroups.json

## Purpose

`metricgroups.json` is the Lunar Lake metric-group description table for perf. Unlike the event files in the same directory, it is a JSON object, not an array: 148 metric-group names map to human-readable descriptions. Most legacy group names such as `Backend`, `Frontend`, `MemoryBound`, `Pipeline`, `TopdownL1` through `TopdownL6`, and `TmaL*` use descriptions from Intel's Top-down Microarchitecture Analysis spreadsheet, while newer `tma_*_group` entries describe the category that a top-down metric contributes to. Issue-oriented groups such as `tma_issueL1`, `tma_issueTLB`, and `tma_issueSyncxn` preserve the spreadsheet issue tokens used by Intel's generated metric set.

## Important APIs, Types, And Data Shape

The data contract is a flat string-to-string JSON object. The important "API" is the exact key spelling because metric definitions in sibling generated metric files refer to these names via their `MetricGroup` strings. `tools/perf/pmu-events/jevents.py` treats files ending in `metricgroups.json` specially: `preprocess_one_file()` loads the object, appends C-string terminators, stores names and descriptions in the generator's big string table, and records them in `_metricgroups`. `print_metricgroups()` then emits a sorted C array and the generated `describe_metricgroup(const char *group)` binary-search helper.

## Control Flow

At build time, the PMU event generator walks model directories under `pmu-events/arch/x86`. When it reaches this file, it does not call the normal event parser. Instead it loads the mapping, records every group name and description, and returns before event-table processing. Later, generated perf code can answer `perf list metricgroups` or print group descriptions by calling `describe_metricgroup()`.

## State And Persistence

The source file contains static metadata only. Persistent runtime state is limited to generated C tables baked into the perf binary. Ordering in the source object is not semantically important because `jevents.py` sorts the generated table, but key identity is persistent and case-sensitive.

## Dependencies And Integration Points

The file depends on the perf PMU event generation schema and on metric definitions elsewhere using matching group names. Integration points include `jevents.py`, generated `pmu-events.c`, `builtin-list.c` metricgroup listing, and `util/metricgroup.c` top-down handling. It complements event files such as Lunar Lake `pipeline.json` and metric expression generators such as `intel_metrics.py`.

## Risks

The main risk is name drift: if a metric references a group name not present here, perf can still collect events but group descriptions and listing UX degrade. A second risk is shape drift: this file must remain an object, while most neighboring files are arrays. Duplicate JSON keys would be collapsed by the parser before generation. Descriptions containing unexpected escapes or embedded terminators would affect the generated big C string table.

## Test Signals

Useful checks are `jq type` returning `object`, a stable key count of 148 for this snapshot, successful `jevents.py` generation, and `perf list --raw-dump metricgroups` including the expected Lunar Lake group names. Runtime smoke tests should verify that `describe_metricgroup()` finds representative old and new names such as `Backend`, `TopdownL1`, `tma_backend_bound_group`, and `tma_issueTLB`.
