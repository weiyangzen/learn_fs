<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/pipeline.json

## Purpose
This JSON file defines 9 Ampere ampereonex front-end, back-end, resource, TLB, and pipeline stall events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 42-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (7), `BriefDescription` (5), `Errata` (3), `PublicDescription` (2), `EventCode` (2), `EventName` (2). It contains 7 `ArchStdEvent` aliases, 2 named implementation-defined events, and 2 encoded events. Event or alias names include `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`, `STALL_FRONTEND_TLB`, `STALL_BACKEND_TLB`. Implementation-defined codes run from `0x815c` to `0x8167` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 3 entries carry errata notes: `Errata AC03_CPU_29`, `Errata AC03_CPU_29`, `Errata AC03_CPU_29`; 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/pipeline.json -->
