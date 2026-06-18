<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/branch.json

## Purpose
This JSON file defines 23 Ampere ampereonex branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 126-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (18), `EventCode` (18), `EventName` (18), `BriefDescription` (18), `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 18 named implementation-defined events, and 18 encoded events. Event or alias names include `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`, `BR_MIS_PRED`, `BR_PRED`, `BR_SKIP_RETIRED`, `BR_IMMED_TAKEN_RETIRED`, `BR_INDNR_TAKEN_RETIRED`, `BR_IMMED_PRED_RETIRED`, `BR_IMMED_MIS_PRED_RETIRED`, `BR_IND_PRED_RETIRED`, `BR_IND_MIS_PRED_RETIRED`, and 11 more. Implementation-defined codes run from `0x8107` to `0x811f` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/branch.json -->
