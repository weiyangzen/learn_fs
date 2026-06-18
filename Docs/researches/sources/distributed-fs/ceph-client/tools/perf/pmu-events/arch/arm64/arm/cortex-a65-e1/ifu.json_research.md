<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/ifu.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/ifu.json

## Purpose
This JSON file defines 20 Arm cortex-a65-e1 instruction-fetch-unit wait, micro-TLB, micro-op cache, and linefill events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 123-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (20), `EventCode` (20), `EventName` (20), `BriefDescription` (20). It contains 0 `ArchStdEvent` aliases, 20 named implementation-defined events, and 20 encoded events. Event or alias names include `IFU_IC_MISS_WAIT`, `IFU_IUTLB_MISS_WAIT`, `IFU_MICRO_COND_MISPRED`, `IFU_MICRO_CADDR_MISPRED`, `IFU_MICRO_HIT`, `IFU_MICRO_NEG_HIT`, `IFU_MICRO_CORRECTION`, `IFU_MICRO_NO_INSTR1`, `IFU_MICRO_NO_PRED`, `IFU_FLUSHED_TLB_MISS`, `IFU_FLUSHED_EXCL_TLB_MISS`, `IFU_ALL_THRDS_RDY`, and 8 more. Implementation-defined codes run from `0xD0` to `0xE4` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/ifu.json -->
