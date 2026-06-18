# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/counter.json

## Purpose

`counter.json` documents the number of fixed and generic counters available for BroadwellX core and uncore PMU units. It records the counter capacity for `core`, `CBOX`, `HA`, `IRP`, `PCU`, `QPI`, `R2PCIe`, `R3QPI`, `SBOX`, `UBOX`, and `iMC` units.

## Important APIs, types, and schema

Each entry has `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The core entry declares 3 fixed counters and 4 generic counters. Most uncore units declare 0 fixed counters and 2 to 4 generic counters, with `UBOX` and `iMC` each declaring 1 fixed counter plus generic counters. This schema is metadata, not the normal `EventName`/`MetricName` event schema.

## Control flow and integration

In the current `jevents.py` path, records without `EventName` or `MetricName` instantiate `JsonEvent` objects but are not appended to `_pending_events` or `_pending_metrics`. As a result, this file is still read during preprocessing, but it does not create generated `struct pmu_event` or `struct pmu_metric` rows. Its practical integration value is as machine-readable PMU capacity documentation adjacent to the BroadwellX event lists; external tools or future perf logic could use it to reason about scheduling pressure across core and uncore PMUs.

## State and persistence behavior

The file contains static capability metadata only. It does not persist runtime state and, in the observed generator, has no generated-table side effect beyond successful JSON parsing.

## Dependencies

The file depends on BroadwellX PMU unit naming matching the surrounding uncore event files and perf's convention that `Unit` strings map to PMU names. It is adjacent to generated and hand-authored event JSON that may use unit names like CBOX, HA, PCU, QPI, SBOX, UBOX, and iMC.

## Risks

The main risk is assuming this file affects perf scheduling when the present generator ignores entries without `EventName` or `MetricName`. If downstream automation expects counter capacities from generated perf tables, it will not get them from this path. Another risk is stale capacity metadata: incorrect generic/fixed counts can mislead documentation or external scheduling analysis even though normal perf builds pass.

## Test signals

At minimum, `jq empty counter.json` should pass and a `jevents.py` build should continue to ignore these records without errors. A stronger guard is to assert that adding or editing this file does not change generated event/metric table counts unless generator support for counter-capacity records is intentionally added.
