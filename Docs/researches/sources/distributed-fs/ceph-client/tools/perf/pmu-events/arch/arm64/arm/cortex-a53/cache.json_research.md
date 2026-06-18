<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/cache.json

## Purpose
This JSON file defines 5 Arm cortex-a53 cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 28-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `EventCode` (5), `EventName` (5), `BriefDescription` (5). It contains 0 `ArchStdEvent` aliases, 5 named implementation-defined events, and 5 encoded events. Event or alias names include `PREFETCH_LINEFILL`, `PREFETCH_LINEFILL_DROP`, `READ_ALLOC_ENTER`, `READ_ALLOC`, `EXT_SNOOP`. Implementation-defined codes run from `0xC2` to `0xC8` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/cache.json -->
