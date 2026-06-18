<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/mmu.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/mmu.json

## Purpose
This JSON file defines 28 Ampere ampereonex MMU page-table-walk and translation-cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 171-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `EventCode` (28), `EventName` (28), `BriefDescription` (28), `PublicDescrition` (16), `PublicDescription` (12). It contains 0 `ArchStdEvent` aliases, 28 named implementation-defined events, and 28 encoded events. Event or alias names include `MMU_D_OTB_ALLOC`, `MMU_D_TRANS_CACHE_HIT_S1L2_WALK`, `MMU_D_TRANS_CACHE_HIT_S1L1_WALK`, `MMU_D_TRANS_CACHE_HIT_S1L0_WALK`, `MMU_D_TRANS_CACHE_HIT_S2L2_WALK`, `MMU_D_TRANS_CACHE_HIT_S2L1_WALK`, `MMU_D_TRANS_CACHE_HIT_S2L0_WALK`, `MMU_D_S1_WALK_CACHE_LOOKUP`, `MMU_D_S1_WALK_CACHE_REFILL`, `MMU_D_S2_WALK_CACHE_LOOKUP`, `MMU_D_S2_WALK_CACHE_REFILL`, `MMU_D_S1_WALK_FAULT`, and 16 more. Implementation-defined codes run from `0xD800` to `0xD90D` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include the file uses the misspelled `PublicDescrition` key on some entries. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/mmu.json -->
