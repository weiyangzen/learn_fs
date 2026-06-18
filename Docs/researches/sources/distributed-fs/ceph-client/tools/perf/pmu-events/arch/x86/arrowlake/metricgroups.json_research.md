# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/metricgroups.json

## Purpose

`metricgroups.json` defines human-readable descriptions for Arrow Lake metric group names. Unlike the neighboring event files, it is not an array of event records. It is a JSON object with 148 key/value pairs where each key is a metric group name and each value is a short description.

Perf uses this data to describe groups listed by `perf list metricgroups` and selected by `perf stat -M <group>`. It does not define metric formulas; metric expressions live in files such as `arl-metrics.json` and generated `extra-metrics.json` files.

## Important APIs, types, and data shape

The schema is:

```json
{
  "GroupName": "Description"
}
```

`jevents.py` has special handling for filenames ending in `metricgroups.json`: it loads the object, iterates each group name, interns both the group and description into the generated big C string table, and stores them in `_metricgroups`. Later `print_metricgroups()` writes a sorted C lookup table and a generated `describe_metricgroup(const char *group)` function that performs binary search over the sorted group names.

Group names include legacy/top-level labels such as `Backend`, `Frontend`, `Mem`, `Flops`, `HPC`, `Summary`, and `TopdownL1` through `TopdownL6`, plus many `tma_*_group` labels such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, `tma_ports_utilization_group`, and `tma_store_bound_group`. There are also issue-oriented names such as `tma_issueBW`, `tma_issueLat`, and `tma_issueTLB`.

## Control flow and integration

The control flow differs from regular event JSON files:

1. During preprocessing, `jevents.py` detects `item.name.endswith('metricgroups.json')`.
2. It calls `json.load` and expects an object whose keys are group names.
3. For each key, it asserts the group name length is greater than one, appends C-string terminators, and stores group/description strings as metric strings.
4. It returns early, so the file is not passed through `read_json_events`.
5. At code-generation time, `print_metricgroups()` sorts the collected group names and emits the `metricgroups` offset table plus `describe_metricgroup()`.
6. Runtime perf list/stat paths use that generated function to show descriptions for metric groups.

Because generated lookup uses binary search over sorted group names, exact spelling and case are the public API.

## State and persistence behavior

The file has no runtime state. Its contents persist through generated `pmu-events.c` and the compiled perf binary. Group descriptions are static string data in the generated big C string table. Adding, renaming, or removing a key changes which metric groups can be described, but it does not by itself create or remove the underlying metrics.

## Dependencies and integration points

The file depends directly on `jevents.py` special-case parsing. It also depends on metric names and metric groups emitted by Arrow Lake metric definitions. The descriptions are useful only when group names match `MetricGroup` fields used by metrics. Build rules can also generate `extra-metricgroups.json` from `intel_metrics.py`, and `jevents.py` treats all metricgroups files similarly.

Runtime integration points include `builtin-list.c` for metric group listing and `util/metricgroup.c` for metric group expansion and top-down maximum-level handling. User-facing commands include `perf list metricgroups`, `perf list --details`, and `perf stat -M`.

## Risks and edge cases

The major risk is schema confusion. This file must remain a JSON object, not an event array. Treating it like the other Arrow Lake JSON files breaks parsing because string descriptions do not have event keys. Conversely, moving metric formulas into this file would be ignored by the metricgroup parser.

Descriptions are mostly generic, many reading "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet." That is valid but low-information. If group names are renamed without updating metric definitions, `describe_metricgroup()` may return descriptions for groups that no metrics use, or metrics may reference groups with no description.

Case and punctuation are significant. Both `TopdownL1` and `tma_L1_group` style names exist, as do similarly named `MachineClears` and `Machine_Clears`. Automated normalization could collapse distinct public group names and break user scripts.

## Test signals

Validation starts with `jq type`, which should return `"object"`, and `jq 'keys | length'`, which should return 148 for the current file. A perf build with jevents enabled should generate `describe_metricgroup()`. Runtime checks should include `perf list --raw-dump metricgroups`, `perf list metricgroups`, and representative group descriptions for `TopdownL1`, `Frontend`, `Mem`, `tma_memory_bound_group`, and `tma_ports_utilization_group`. `tools/perf/tests/shell/stat_all_metricgroups.sh` is a useful broad integration test because it iterates metric groups exposed by perf.
