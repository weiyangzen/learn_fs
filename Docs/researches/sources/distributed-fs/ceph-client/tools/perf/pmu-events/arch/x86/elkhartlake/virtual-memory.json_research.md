<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/virtual-memory.json

## Purpose
Provides 31 Elkhart Lake virtual-memory and TLB PMU aliases. It covers DTLB load/store misses, ITLB misses, page-walk completion by page size, STLB hits, PDE-cache misses, EPT walks/violations, and TLB-related retired memory uops.

## Important APIs, Types, And Functions
Uses `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, `Counter`, `PEBS`, and `Data_LA`. Groups include `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, `ITLB_MISSES.*`, `EPT.*`, `MEM_UOPS_RETIRED.STLB_MISS_*`, `ITLB.ITLB_FLUSH`, and `LD_BLOCKS.STORE_FORWARD`.

## Control Flow
The Elkhart Lake mapfile row causes `jevents.py` to include this file in the generated core PMU event table. Runtime perf users can select aliases for page-walk and TLB behavior. For entries marked `PEBS` and `Data_LA`, perf descriptions advertise precise sampling and address availability where supported.

## State And Persistence
No mutable source state exists. Generated aliases persist in perf; runtime state is counter programming and possible PEBS records with data linear addresses for selected load/store TLB miss events.

## Dependencies And Integration Points
Integrates with memory and cache analysis: TLB misses can explain apparent backend stalls or memory latency. EPT entries are relevant for virtualization workloads. The parser's `Data_LA` handling appends address-support text to generated descriptions.

## Risks And Edge Cases
Four entries carry `PEBS`, and three carry `Data_LA`; incorrect precision metadata affects sampling guidance. Page-size-specific umasks can be easily confused. Virtualization and kernel settings may restrict EPT visibility or counter availability.

## Test Signals
Validate JSON, build generated tables, and check `perf list DTLB_LOAD_MISSES` plus `perf list ITLB_MISSES`. Hardware tests should include a TLB-stressing workload, and precise sampling smoke tests should verify address-bearing events are accepted with appropriate modifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/virtual-memory.json -->
