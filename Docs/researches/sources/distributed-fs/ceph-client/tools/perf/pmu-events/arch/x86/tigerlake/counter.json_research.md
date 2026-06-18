# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/counter.json

## Purpose
`counter.json` is a Tiger Lake counter inventory file rather than an event list. It declares how many fixed and generic counters are available for each PMU unit known to the Tiger Lake perf event tables.

## Important APIs, Types, and Fields
The file is a JSON array of three objects. Each object has `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The entries declare `core` with 4 fixed and 8 generic counters, `ARB` with 0 fixed and 2 generic counters, and `CLOCK` with 1 fixed and 0 generic counters. Values are mostly strings, with one numeric fixed-counter value for `CLOCK`; consumers must tolerate both numeric and string representations if the broader perf schema permits them.

## Control Flow and Data Flow
During perf PMU event generation, this metadata informs counter availability for Tiger Lake units. It does not map event names to selectors. Runtime scheduling uses this inventory indirectly when perf determines whether a requested set of events can fit on hardware counters or must be multiplexed.

## State and Persistence Behavior
The file is static metadata and stores no runtime state. Its values affect scheduling assumptions but do not persist measurement data. Incorrect counts can create persistent user-visible behavior in generated perf tables, such as unexpected multiplexing or impossible scheduling constraints.

## Dependencies and Integration Points
The file depends on perf's architecture PMU metadata loader and must agree with Tiger Lake hardware and kernel PMU exposure. It integrates with all Tiger Lake event JSON files because event definitions reference `Counter` sets that assume the declared counter resources.

## Risks and Edge Cases
The mixed string/integer representation is a schema consistency risk for strict parsers. If a future tool assumes every file in this directory is an event list with `EventName`, it will fail on this metadata file. Counter counts must stay aligned with the model; overstating counters can cause generated tables to advertise combinations perf cannot schedule, while understating them can cause unnecessary multiplexing.

## Test Signals
Validate JSON syntax and run the perf PMU event generation path. A targeted schema test should confirm that counter metadata files are parsed separately from event arrays. On Tiger Lake, `perf stat` with more than eight programmable core events can confirm multiplexing behavior, while fixed events such as instructions and cycles should continue to schedule through fixed counters.
