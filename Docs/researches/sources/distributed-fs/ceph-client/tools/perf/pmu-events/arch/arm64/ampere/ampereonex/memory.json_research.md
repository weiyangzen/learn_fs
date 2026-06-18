<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/memory.json

## Purpose
This JSON file defines 12 Ampere ampereonex load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 44-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (11), `BriefDescription` (2), `Errata` (1), `PublicDescription` (1), `EventCode` (1), `EventName` (1). It contains 11 `ArchStdEvent` aliases, 1 named implementation-defined events, and 1 encoded events. Event or alias names include `LD_RETIRED`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `LD_ALIGN_LAT`, `ST_ALIGN_LAT`, `MEM_ACCESS`, `MEMORY_ERROR`, `LDST_ALIGN_LAT`, `MEM_ACCESS_CHECKED`, `MEM_ACCESS_CHECKED_RD`, `MEM_ACCESS_CHECKED_WR`, `BPU_FLUSH_MEM_FAULT`. Implementation-defined codes run from `0x121` to `0x121` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 1 entries carry errata notes: `Errata AC04_CPU_21`; 10 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/memory.json -->
