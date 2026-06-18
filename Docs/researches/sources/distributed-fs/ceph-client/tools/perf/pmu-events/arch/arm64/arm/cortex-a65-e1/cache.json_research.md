<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/cache.json

## Purpose
This JSON file defines 56 Arm cortex-a65-e1 cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 237-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (34), `PublicDescription` (22), `EventCode` (22), `EventName` (22), `BriefDescription` (22). It contains 34 `ArchStdEvent` aliases, 22 named implementation-defined events, and 22 encoded events. Event or alias names include `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_ALLOCATE`, `L1D_TLB`, and 44 more. Implementation-defined codes run from `0xC0` to `0xF7` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 34 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/cache.json -->
