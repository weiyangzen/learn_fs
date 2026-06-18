<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/cache.json

## Purpose
This JSON file defines 38 Ampere emag cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 162-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (24), `PublicDescription` (16), `BriefDescription` (15), `EventCode` (14), `EventName` (14). It contains 24 `ArchStdEvent` aliases, 14 named implementation-defined events, and 14 encoded events. Event or alias names include `L1D_CACHE_RD`, `L1D_CACHE_WR`, `L1D_CACHE_REFILL_RD`, `L1D_CACHE_INVAL`, `L1D_TLB_REFILL_RD`, `L1D_TLB_REFILL_WR`, `L2D_CACHE_RD`, `L2D_CACHE_WR`, `L2D_CACHE_REFILL_RD`, `L2D_CACHE_REFILL_WR`, `L2D_CACHE_WB_VICTIM`, `L2D_CACHE_WB_CLEAN`, and 26 more. Implementation-defined codes run from `0x34` to `0x116` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 23 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/cache.json -->
