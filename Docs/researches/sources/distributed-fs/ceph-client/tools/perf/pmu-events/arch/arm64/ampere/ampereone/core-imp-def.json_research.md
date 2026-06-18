<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/core-imp-def.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/core-imp-def.json

## Purpose
This JSON file defines 96 Ampere ampereone implementation-defined core events for front-end, back-end, cache, branch, MMU, and microarchitectural analysis for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 579-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (96), `EventCode` (96), `EventName` (96), `BriefDescription` (96). It contains 0 `ArchStdEvent` aliases, 96 named implementation-defined events, and 96 encoded events. Event or alias names include `L2_PREFETCH_REFILL`, `L2_PREFETCH_UPGRADE`, `BPU_HIT_BTB`, `BPU_CONDITIONAL_BRANCH_HIT_BTB`, `BPU_HIT_INDIRECT_PREDICTOR`, `BPU_HIT_RSB`, `BPU_UNCONDITIONAL_BRANCH_MISS_BTB`, `BPU_BRANCH_NO_HIT`, `BPU_HIT_BTB_AND_MISPREDICT`, `BPU_CONDITIONAL_BRANCH_HIT_BTB_AND_MISPREDICT`, `BPU_INDIRECT_BRANCH_HIT_BTB_AND_MISPREDICT`, `BPU_HIT_RSB_AND_MISPREDICT`, and 84 more. Implementation-defined codes run from `0x10A` to `0xD90D` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/core-imp-def.json -->
