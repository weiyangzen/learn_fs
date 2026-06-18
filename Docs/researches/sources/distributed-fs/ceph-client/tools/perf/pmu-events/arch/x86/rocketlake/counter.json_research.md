# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/counter.json

## Purpose

`counter.json` is Rocket Lake PMU topology metadata. It does not define named hardware events. Instead, it declares how many fixed and generic counters are available for each PMU unit represented in this model: `core`, `ARB`, and `CLOCK`.

## Important APIs, Types, and Data Fields

The file is a JSON array of three objects using `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. `core` declares 4 fixed counters and 8 generic counters. `ARB` declares 0 fixed and 2 generic counters. `CLOCK` declares 1 fixed and 0 generic counters. Unlike event catalogs, rows do not have `EventName`, `EventCode`, `UMask`, descriptions, or sampling periods.

## Control Flow and Data Flow

There is no executable control flow and no runtime counting definition in the file itself. Perf build tooling reads this as model metadata alongside event JSON files. Downstream scheduling and display logic can use the declared counter capacities to understand how many events can be programmed on a PMU before multiplexing or grouping constraints apply.

## State and Persistence Behavior

The persistent state is the declared counter capacity per unit. Runtime counter allocation is external to this file and depends on requested event groups, kernel scheduling, and active perf sessions. The mixed numeric representation is notable: most values are strings, while `CLOCK.CountersNumFixed` appears as a JSON number `1`; consumers must tolerate both.

## Dependencies and Integration Points

This file depends on the Rocket Lake PMU model and perf's PMU-events metadata parser. It integrates with the other Rocket Lake event files by describing capacity rather than event semantics. It is especially relevant when users group many `cache.json`, `frontend.json`, `memory.json`, or `floating-point.json` events and perf must schedule them on finite counters.

## Risks and Edge Cases

Treating this file as a normal event list would be wrong because there are no aliases to expose. Type inconsistency between string and numeric counter counts can break strict parsers. Counter capacities are model-level facts; if they are inaccurate, perf may produce misleading scheduling expectations. `ARB` and `CLOCK` units have specialized capacities and should not be conflated with core counters.

## Test Signals

Validation should parse the JSON and confirm exactly three rows with the expected units. Generator tests should verify the file does not create bogus `EventName` aliases. Counter scheduling smoke tests can request event groups larger than eight generic core events and observe multiplexing, while fixed-counter checks should confirm fixed core and clock resources are modeled separately.
