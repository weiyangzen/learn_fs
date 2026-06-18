<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/instruction.json

## Purpose
This JSON file defines 34 Ampere ampereonex retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 129-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (26), `PublicDescription` (8), `EventCode` (8), `EventName` (8), `BriefDescription` (8). It contains 26 `ArchStdEvent` aliases, 8 named implementation-defined events, and 8 encoded events. Event or alias names include `SW_INCR`, `ST_RETIRED`, `LD_SPEC`, `ST_SPEC`, `LDST_SPEC`, `DP_SPEC`, `ASE_SPEC`, `VFP_SPEC`, `PC_WRITE_SPEC`, `BR_IMMED_RETIRED`, `BR_RETURN_RETIRED`, `CRYPTO_SPEC`, and 22 more. Implementation-defined codes run from `0xd210` to `0xd10a` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 26 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/instruction.json -->
