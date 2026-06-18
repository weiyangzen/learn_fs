<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/mmu.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/mmu.json

## Purpose
This JSON file defines 7 Arm cortex-a75 MMU page-table-walk and translation-cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 45-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (7), `EventCode` (7), `EventName` (7), `BriefDescription` (7). It contains 0 `ArchStdEvent` aliases, 7 named implementation-defined events, and 7 encoded events. Event or alias names include `MMU_PTW`, `MMU_PTW_ST1`, `MMU_PTW_ST2`, `MMU_PTW_LSU`, `MMU_PTW_ISIDE`, `MMU_PTW_PLD`, `MMU_PTW_CP15`. Implementation-defined codes run from `0xE0` to `0xE6` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/mmu.json -->
