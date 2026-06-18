# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/arch-std-events.json

## Purpose
Provides a synthetic architecture-standard event used by perf PMU event generator tests. It lets test CPU JSON files reference a common `L3_CACHE_RD` event through `ArchStdEvent` without duplicating event metadata.

## APIs, Types, and Functions
The file contains one event record with `EventCode: 0x40`, `EventName: L3_CACHE_RD`, `BriefDescription`, and `PublicDescription`. In the pmu-events schema, architecture-standard JSONs are looked up by `EventName` when another file uses `ArchStdEvent`.

## Control Flow, State, and Persistence
During jevents test generation, the parser loads architecture root standard events, resolves `ArchStdEvent: L3_CACHE_RD` from child files, and emits the resolved event as if it were present locally. There is no runtime state beyond generated test tables.

## Dependencies and Integration
Integrates with `arch/test/test_soc/cpu/cache.json`, which contains only an `ArchStdEvent` reference. It exercises the standard-event dereference path described in the pmu-events README and covered by perf PMU event tests.

## Risks and Test Signals
Risks are narrow: if lookup-by-name changes, the cache fixture fails or emits incomplete events. Test signals are the perf `pmu-events` unit tests, generated table inspection for `L3_CACHE_RD`, and ensuring the child cache fixture inherits description and event code correctly.
