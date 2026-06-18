<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/pipeline.json

## Purpose
This JSON file defines 10 Arm cortex-a53 front-end, back-end, resource, TLB, and pipeline stall events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 53-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `EventCode` (10), `EventName` (10), `BriefDescription` (10). It contains 0 `ArchStdEvent` aliases, 10 named implementation-defined events, and 10 encoded events. Event or alias names include `STALL_SB_FULL`, `OTHER_IQ_DEP_STALL`, `IC_DEP_STALL`, `IUTLB_DEP_STALL`, `DECODE_DEP_STALL`, `OTHER_INTERLOCK_STALL`, `AGU_DEP_STALL`, `SIMD_DEP_STALL`, `LD_DEP_STALL`, `ST_DEP_STALL`. Implementation-defined codes run from `0xC7` to `0xE8` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/pipeline.json -->
