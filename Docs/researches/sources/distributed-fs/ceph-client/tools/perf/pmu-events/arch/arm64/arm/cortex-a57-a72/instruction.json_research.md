<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/instruction.json

## Purpose
This JSON file defines 22 Arm cortex-a57-a72 retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 69-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (22). It contains 22 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, `TTBR_WRITE_RETIRED`, `LDREX_SPEC`, `STREX_PASS_SPEC`, `STREX_FAIL_SPEC`, `LD_SPEC`, `ST_SPEC`, `LDST_SPEC`, and 10 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 22 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/instruction.json -->
