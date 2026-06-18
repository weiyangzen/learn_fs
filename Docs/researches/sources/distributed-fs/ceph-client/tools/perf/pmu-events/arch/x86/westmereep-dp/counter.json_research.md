<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/counter.json

## Purpose

`counter.json` records Westmere EP DP PMU counter topology for perf. It declares the number of fixed and generic programmable counters available on the `core` PMU, which constrains event scheduling and grouping for the rest of the architecture's event catalogs.

## Important APIs, Types, and Data Fields

The file is a one-object JSON array with `Unit: core`, `CountersNumFixed: 4`, and `CountersNumGeneric: 4`. It is capability metadata, not a normal event list: it intentionally has no `EventName`, `EventCode`, `UMask`, descriptions, or sample periods.

## Control Flow and Data Flow

There is no control flow. Perf's PMU event tooling reads the topology metadata and uses it when generating or validating architecture-specific PMU tables. At runtime, the scheduler uses the available fixed and generic counter counts to decide whether requested events can be grouped directly or must be multiplexed/rejected.

## State and Persistence Behavior

The file persists static topology metadata only. It does not track active events, counter values, overflow state, or perf session results. The counts are architecture-level constraints that should remain stable for this PMU model.

## Dependencies and Integration Points

The metadata depends on Westmere EP DP core PMU architecture and integrates with sibling event files such as `cache.json`. It is relevant to all perf flows that schedule multiple core events, especially groups containing cache events with explicit `Counter` restrictions or fixed-counter events from other topic files.

## Risks and Edge Cases

Tools must treat this as a counter-topology file, not as an event catalog. If a parser requires `EventName`, it will reject this valid metadata. If the fixed or generic counter counts are wrong, perf may overpromise event grouping, underuse available counters, or multiplex unnecessarily. Numeric values are stored as strings, so consumers need to parse them carefully.

## Test Signals

Validation should include JSON parse success, schema compatibility for topology-only files, and perf scheduling tests that confirm four generic core events can be counted without multiplexing when counter-specific constraints permit. Regression tests should ensure event-list generation does not display this object as a normal PMU event and that sibling cache events respect the declared generic counter count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/counter.json -->
