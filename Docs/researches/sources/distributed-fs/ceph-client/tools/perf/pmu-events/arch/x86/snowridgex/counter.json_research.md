# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/counter.json

## Purpose

`counter.json` is the Snow Ridge X PMU counter-capacity catalog for perf. Unlike event files, it does not define programmable events. It defines how many fixed and generic counters are available for each PMU unit: `core`, `CHA`, `IIO`, `IRP`, `iMC`, `M2M`, `M2PCIe`, `PCU`, and `UBOX`. This metadata helps perf understand platform counter resources when scheduling events across core and uncore units.

## Important APIs, Types, and Data Fields

The file is a JSON array of unit-capacity objects with three fields: `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The `core` unit declares 3 fixed and 4 generic counters. Uncore units are mostly generic-only: `CHA`, `IIO`, `M2M`, `M2PCIe`, and `PCU` each declare 4 generic counters; `IRP` and `UBOX` declare 2 generic counters; `iMC` declares 1 fixed and 4 generic counters. `UBOX` uses a numeric `CountersNumFixed` value of `1` while most other counts are strings, so consumers must tolerate both JSON number and string forms.

## Control Flow and Data Flow

There is no executable control flow. Perf's pmu-events tooling reads these capacity records alongside event catalogs and uses them as static constraints for the Snow Ridge X platform. The data flow is from checked-in JSON to generated tables, then into perf event scheduling decisions and user-facing metadata about PMU units. Event files reference the same unit names, and this file supplies the resource context for those units.

## State and Persistence Behavior

The persistent state is the static list of PMU units and counter counts. Runtime counter allocation, multiplexing, and enabled/running time accounting happen in perf and the kernel; none of that state is persisted here. The file describes hardware capacity, not current availability, so actual sessions can still be constrained by privilege, kernel support, occupied counters, or event incompatibilities.

## Dependencies and Integration Points

This file depends on perf support for counter metadata records in the pmu-events tree. It integrates with Snow Ridge X event files that use `core`, `CHA`, `IIO`, `IRP`, `iMC`, `M2M`, `M2PCIe`, `PCU`, or `UBOX` units. It is especially relevant to grouped perf stat runs, uncore monitoring, and scheduling multiple events where the number of generic counters determines whether multiplexing is needed.

## Risks and Edge Cases

The mixed numeric/string representation of counter counts can reveal fragile parsers. Counter counts are unit-level capacities, not guarantees that every event can run on every counter. If unit names drift from event files, perf may fail to associate events with capacity metadata. The file has no `EventName` rows, so tools that blindly expect event schemas for every JSON file in the directory can mis-handle it.

## Test Signals

Static validation should parse the file and confirm all nine expected units are present with non-negative fixed and generic counts. Generation tests should verify the file is accepted even without `EventName` or `EventCode`. Runtime or integration tests should schedule more events than available generic counters on a Snow Ridge X unit and confirm perf either schedules, multiplexes, or reports constraints consistently with these capacities.
