<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/frontend.json

## Purpose
Defines nine Elkhart Lake frontend PMU events covering branch-address clears, decode restriction from wrong predecode length prediction, and instruction-cache access/hit/miss behavior.

## Important APIs, Types, And Functions
The file uses `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. The `BACLEARS.*` group shares event code `0xe6` with different masks for all, conditional, indirect, return, and unconditional branch clears. `ICACHE.*` entries share event code `0x80` for access, hit, and miss outcomes.

## Control Flow
`jevents.py` converts these objects into generated aliases selected by the Elkhart Lake mapfile row. At runtime perf exposes names such as `BACLEARS.ANY`, `DECODE_RESTRICTION.PREDECODE_WRONG`, and `ICACHE.MISS`; collecting them programs the core PMU with the corresponding event and umask.

## State And Persistence
The data is static and persists in generated perf tables. Runtime state is limited to counter values gathered during a perf session.

## Dependencies And Integration Points
Integrates with perf's frontend/topdown reporting. The branch-clear aliases can be correlated with branch retired and branch mispredict events in `pipeline.json`; instruction-cache aliases can be correlated with cache and virtual-memory miss events when diagnosing fetch-side stalls.

## Risks And Edge Cases
All entries are core generic-counter events with no PEBS metadata. Event names must remain stable because scripts and topdown workflows may refer to them directly. The related `BACLEARS.*` masks are easy to transpose, and aggregate `BACLEARS.ANY` must not be confused with the sum of mutually overlapping subevents without checking hardware semantics.

## Test Signals
Run JSON validation and perf build generation. On hardware, `perf stat -e BACLEARS.ANY,ICACHE.ACCESSES,ICACHE.MISS` over branch-heavy and instruction-cache-sensitive workloads should show aliases are available and count plausible non-negative values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/frontend.json -->
