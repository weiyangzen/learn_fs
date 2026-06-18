<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/pipeline.json

## Purpose
This JSON file defines 14 Arm cortex-a55 front-end, back-end, resource, TLB, and pipeline stall events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 81-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (12), `EventCode` (12), `EventName` (12), `BriefDescription` (12), `ArchStdEvent` (2). It contains 2 `ArchStdEvent` aliases, 12 named implementation-defined events, and 12 encoded events. Event or alias names include `STALL_FRONTEND`, `STALL_BACKEND`, `STALL_FRONTEND_CACHE`, `STALL_FRONTEND_TLB`, `STALL_FRONTEND_PDERR`, `STALL_BACKEND_ILOCK`, `STALL_BACKEND_ILOCK_AGU`, `STALL_BACKEND_ILOCK_FPU`, `STALL_BACKEND_LD`, `STALL_BACKEND_ST`, `STALL_BACKEND_LD_CACHE`, `STALL_BACKEND_LD_TLB`, and 2 more. Implementation-defined codes run from `0xE1` to `0xEC` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 2 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/pipeline.json -->
