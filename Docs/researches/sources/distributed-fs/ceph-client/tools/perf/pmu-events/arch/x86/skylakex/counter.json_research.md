
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/counter.json

## Purpose

This file defines the counter capacity table for Skylake-X PMU units. It has 10 rows mapping each PMU `Unit` to the number of fixed counters and generic programmable counters available. Units are `core`, `CHA`, `IIO`, `IRP`, `UPI`, `M2M`, `iMC`, `M3UPI`, `PCU`, and `UBOX`.

The table gives perf's generated metadata a model-specific view of counter resources. For example, `core` has 3 fixed counters and 4 generic counters, `iMC` and `UBOX` each have 1 fixed counter, and most uncore units expose 2 to 4 generic counters with no fixed counters.

## Important Schema Fields and APIs

Each row contains:

- `Unit`: PMU unit name.
- `CountersNumFixed`: count of fixed-function counters for that unit, stored as a string in the JSON.
- `CountersNumGeneric`: count of generic programmable counters for that unit, stored as a string.

This file is not an event list and has no `EventName`, `EventCode`, or `UMask`. It is a resource descriptor consumed by the perf PMU event generation and scheduling metadata path alongside the event JSON files.

## Control Flow and Data Flow

At build time, the Skylake-X directory is scanned and this table is parsed with the rest of the model metadata. The generated perf metadata can use the counts to describe or reason about how many counters exist for each PMU unit. At runtime, these counts inform whether groups of events are likely to fit and help represent PMU unit capabilities consistently with the event descriptors.

There is no internal control flow. The data flow is static resource metadata -> generated C tables -> perf scheduling/listing behavior.

## State and Persistence

The file stores static hardware capacity facts. It does not change at runtime and does not persist sampled state. Generated perf artifacts embed or derive from these values until perf is rebuilt.

## Dependencies and Integration Points

The table integrates with Skylake-X raw event files such as `cache.json`, `floating-point.json`, uncore cache/interconnect/I/O/memory/power files, and metrics that schedule groups across core and uncore PMUs. It depends on unit names matching the `Unit` values used in event descriptors and the kernel PMU names expected by perf.

## Risks

Wrong counter counts can lead to unrealistic metric grouping assumptions, poor scheduling diagnostics, or confusing perf output. Unit-name mismatches are especially risky because they break the relationship between event descriptors and capacity descriptors. Since values are encoded as strings, consumers must parse numeric content consistently; nonnumeric edits would likely fail generation or produce invalid metadata.

## Test Signals

Validation should parse JSON and compare unit names against units used by Skylake-X event files. Runtime signals include `perf list` visibility for unit-scoped events and successful scheduling of event groups that fit within the declared generic/fixed counter capacity. A useful static check is confirming exactly one row for each expected unit and nonnegative integer values in both counter fields.
