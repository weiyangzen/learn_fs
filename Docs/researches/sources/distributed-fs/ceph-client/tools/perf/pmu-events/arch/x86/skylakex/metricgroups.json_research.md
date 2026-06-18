# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/metricgroups.json

## Purpose

`metricgroups.json` is a dictionary of metric-group descriptions for Skylake Server. It does not define counter events. Instead, it maps 138 group names to human-readable descriptions used by perf's metric listing and metric-group display paths.

Most entries are short descriptions imported from Intel's Top-down Microarchitecture Analysis metrics spreadsheet. The file includes broad groups such as `Frontend`, `Backend`, `MemoryBound`, `Pipeline`, `Power`, and `Summary`, legacy/grouping labels such as `Bv*`, and generated top-down hierarchy groups such as `TopdownL1` through `TopdownL6` and `tma_*_group`.

## Important Schema, APIs, and Groups

Unlike event files, this file is a JSON object rather than an array. Keys are metric group names and values are descriptions. `jevents.py` treats files ending in `metricgroups.json` specially in `preprocess_one_file()`: it loads the object, appends NUL terminators, interns both key and description into the shared big C string, and stores them in `_metricgroups`.

Important names include:

- Top-level analysis buckets: `Frontend`, `Backend`, `BadSpec`, `Retire`, `MemoryBound`, `Pipeline`, `HPC`, `Power`, and `Summary`.
- Memory-oriented groups: `Mem`, `MemOffcore`, `MemoryBW`, `MemoryLat`, `MemoryTLB`, `Memory_BW`, and `Memory_Lat`.
- Front-end and code groups: `DSB`, `DSBmiss`, `FetchBW`, `FetchLat`, `IcMiss`, `LSD`, `MicroSeq`, and `CodeGen`.
- Top-down hierarchy aliases: `TopdownL1` through `TopdownL6` and `tma_L1_group` through `tma_L6_group`.
- Category-specific TMA groups: `tma_frontend_bound_group`, `tma_memory_bound_group`, `tma_branch_mispredicts_group`, `tma_ports_utilization_group`, `tma_machine_clears_group`, and related `tma_issue*` groups.

## Control Flow and Integration

`metricgroups.json` is only consumed during the preprocessing pass. It is explicitly skipped by `process_one_file()` so it does not create PMU event entries. The collected `_metricgroups` mapping is emitted into generated perf data that supports listing metric group descriptions.

The integration point is perf metric discovery and printing. `builtin-list.c` has dedicated logic for metric groups, and `perf stat -M <metric-or-group>` relies on metric metadata generated from the PMU event tree. The group descriptions help users interpret available metric bundles but do not define formulas themselves.

## State and Persistence Behavior

The source file is static metadata. Generated descriptions are persisted in the built perf binary through interned C strings. There is no runtime mutable state in this file. Changing a description affects `perf list metricgroups` style output, while changing a key can affect group lookup and user command compatibility.

## Dependencies

Dependencies include:

- `jevents.py` special handling for `metricgroups.json`.
- Metric definitions in adjacent or generated metrics files that reference these group names.
- `metricgroup.c`, `builtin-list.c`, and `builtin-stat.c` behavior for showing and selecting metric groups.
- Naming compatibility with Intel top-down metric naming conventions.

## Risks and Edge Cases

The key names are effectively user-facing API. Renaming `MemoryBound`, `TopdownL1`, or a `tma_*_group` can break scripts using `perf stat -M` or filtering `perf list metricgroups`.

Several groups are near-duplicates or compatibility variants, such as `MachineClears` and `Machine_Clears`, `MemoryBW` and `Memory_BW`, and `MemoryLat` and `Memory_Lat`. These are likely intentional compatibility aliases; cleanup that normalizes names could remove useful entry points.

Because all values are descriptions, JSON syntax validation is necessary but insufficient. A typo in a key may not fail the build, but the group would no longer describe or match the intended metrics.

## Test Signals

Useful checks are:

- `jq 'keys | length' metricgroups.json`, currently 138.
- Build perf and confirm `jevents.py` accepts the object form.
- `perf list metricgroups` to verify group names and descriptions are visible.
- `perf stat -M TopdownL1` and representative `tma_*` group invocations on supported systems.
- Grep metric JSON/generated metric output for references to key names after any rename.
