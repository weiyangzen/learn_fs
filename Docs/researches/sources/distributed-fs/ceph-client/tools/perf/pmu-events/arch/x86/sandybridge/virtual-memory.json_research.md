## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/virtual-memory.json

### Purpose
`virtual-memory.json` defines 16 Sandy Bridge virtual memory and TLB events. It covers DTLB load/store misses, STLB hits, page-walk completion and duration, EPT walk cycles, ITLB flush and miss behavior, and DTLB/STLB flush events.

### Important APIs, Types, And Data Fields
The file uses the standard event schema:

- `EventName` includes `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, `EPT.WALK_CYCLES`, `ITLB.ITLB_FLUSH`, `ITLB_MISSES.*`, and `TLB_FLUSH.*`.
- `EventCode`, `UMask`, and `Counter` define selector encoding and counter availability.
- `BriefDescription` and, for some entries, `PublicDescription` provide help text.
- `SampleAfterValue` provides sampling defaults.

There are no functions/classes; the JSON event records are consumed by perf.

### Control Flow And Data Flow
Perf generates named TLB/virtual-memory events from the array. Runtime users can count or sample TLB miss and page-walk behavior. `snb-metrics.json` references this file through metrics such as `tma_dtlb_load` and `tma_itlb_misses`, which combine STLB hit and walk-duration events with top-down fetch/memory bottleneck categories.

### State And Persistence
This file persists static PMU event metadata. Runtime TLB state and counter values are not stored here.

### Dependencies And Integration Points
The definitions depend on Sandy Bridge DTLB, STLB, ITLB, EPT, and page-walk PMU semantics. Integration points include perf event listing, top-down memory TLB and fetch-latency metrics, and group taxonomy keys such as `MemoryTLB`, `BigFootprint`, and `tma_issueTLB`.

### Risks
TLB metrics are sensitive to event-name stability and walk-duration semantics. If `DTLB_LOAD_MISSES.STLB_HIT`, `DTLB_LOAD_MISSES.WALK_DURATION`, `ITLB_MISSES.STLB_HIT`, or `ITLB_MISSES.WALK_DURATION` are renamed or misencoded, top-down TLB metrics can fail or misclassify bottlenecks. EPT-related events may be workload/hypervisor dependent, so tests should not assume nonzero counts.

### Test Signals
Validate JSON, ensure generated perf output includes DTLB/ITLB/STLB names, run metric expression tests for `tma_dtlb_load` and `tma_itlb_misses`, and use hardware smoke tests with TLB-stressing workloads where available.
