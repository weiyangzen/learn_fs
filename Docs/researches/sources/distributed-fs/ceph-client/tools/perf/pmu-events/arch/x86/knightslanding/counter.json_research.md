# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/counter.json

## Purpose

`counter.json` declares the counter capacity for Knights Landing PMU units. Unlike the other files in this directory, it is not an event list. It tells perf's event-table tooling how many fixed and generic counters exist for each KNL monitoring unit so event constraints and uncore unit descriptions can be interpreted correctly.

The file contains seven unit records: `core`, `CHA`, `EDC_ECLK`, `EDC_UCLK`, `iMC_DCLK`, `iMC_UCLK`, and `M2PCIe`.

## Important APIs, Types, and Schema

The schema is a top-level JSON array of PMU unit descriptors. Each descriptor has:

- `Unit`: the PMU unit name used by perf event-map tooling and KNL uncore integration.
- `CountersNumFixed`: number of fixed counters for that unit.
- `CountersNumGeneric`: number of programmable generic counters for that unit.

The `core` row declares `CountersNumFixed: "3"` and `CountersNumGeneric: "2"`, matching the two generic core counters referenced by the sibling event files through `Counter: "0,1"` and the fixed-counter events in `pipeline.json`. The uncore rows declare zero fixed counters and four generic counters for CHA, EDC, iMC, and M2PCIe units.

## Control Flow and Data Flow

Perf's PMU event generation reads this file alongside event JSON files. The generator associates event descriptors with the counter capacity of their unit. During runtime scheduling, perf uses the generated constraints to decide whether a requested set of events can fit on the available fixed and programmable counters.

There is no executable control flow inside the file. The data-flow dependency is from these unit capacity rows into event validation, event scheduling, and user diagnostics when perf reports unavailable or conflicting events.

## State and Persistence Behavior

This is static hardware metadata. It persists KNL PMU topology in source form and has no mutable runtime state. The only notable persistence issue is type consistency: most numeric values are encoded as strings, while `iMC_UCLK.CountersNumGeneric` is encoded as the JSON number `4`. Consumers need to tolerate both forms or the file should be normalized to one representation.

## Dependencies and Integration Points

`counter.json` is integrated with all KNL event files in this directory. Core events in `cache.json`, `floating-point.json`, `frontend.json`, `memory.json`, and `pipeline.json` constrain themselves to programmable counters `0,1` or fixed counters. Uncore event files outside this work item may rely on the CHA, EDC, iMC, and M2PCIe unit capacities.

The unit names must match names expected by perf's PMU event-map generator and runtime PMU discovery. Renaming a unit is therefore a compatibility change, not a documentation-only edit.

## Risks and Edge Cases

The mixed string/number representation for `CountersNumGeneric` is a concrete schema risk. Strict parsers expecting all counter counts as strings may reject the `iMC_UCLK` row, while strict numeric parsers may reject the other rows. Existing perf tooling is generally permissive, but research and validation scripts should account for this irregularity.

Wrong counter counts cause higher-level failures that are not obvious from this file alone: valid events may be rejected as unschedulable, or invalid event groups may be accepted and later fail at open time. Since this file carries no descriptions, incorrect unit names or counts can be hard to diagnose from user-facing `perf list` output.

## Test Signals

Validation should include JSON parsing, schema checks for exactly `Unit`, `CountersNumFixed`, and `CountersNumGeneric`, and a normalization check that all counter counts can be parsed as non-negative integers. Integration tests should confirm generated KNL tables expose two generic core counters, three fixed core counters, and four generic counters for each declared uncore unit.
