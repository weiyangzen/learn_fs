<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/data-fabric.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/data-fabric.json

## Purpose
Defines AMD `amdzen1` DFPMC per-package data-fabric aliases for remote outbound traffic and DRAM-channel controller traffic selection.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 12 records: 12 raw event aliases and 0 derived metrics. Schema fields present are `EventCode`, `EventName`, `PerPkg`, `PublicDescription`, `UMask`, `Unit`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `DFPMC`. Representative names: `remote_outbound_data_controller_0`, `remote_outbound_data_controller_1`, `remote_outbound_data_controller_2`, `remote_outbound_data_controller_3`, `dram_channel_data_controller_0`, `dram_channel_data_controller_1`, `dram_channel_data_controller_2`, `dram_channel_data_controller_3`, `dram_channel_data_controller_4`, `dram_channel_data_controller_5`, plus 2 more.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `data-fabric` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen1` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. Unit-specific routing depends on `unit_to_pmu()` mappings for `DFPMC`; missing `Unit` means the default core PMU. Entries with `PerPkg` require package-level aggregation behavior in perf's uncore/sys PMU handling.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. AMD uncore-style units such as `L3PMC` and `DFPMC` depend on kernel PMU naming and package aggregation support; unsupported systems may list aliases that cannot be scheduled.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `remote_outbound_data_controller_0`, `remote_outbound_data_controller_1`, `remote_outbound_data_controller_2`, `remote_outbound_data_controller_3`, `dram_channel_data_controller_0`, `dram_channel_data_controller_1`, plus 6 more. On matching hardware, run `perf stat -e` for events such as `remote_outbound_data_controller_0`, `remote_outbound_data_controller_1`, `remote_outbound_data_controller_2`, `remote_outbound_data_controller_3`, `dram_channel_data_controller_0`, plus 7 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/data-fabric.json -->
