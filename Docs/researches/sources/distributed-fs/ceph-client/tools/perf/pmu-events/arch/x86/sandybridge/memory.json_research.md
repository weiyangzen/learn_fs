## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/memory.json

### Purpose
`memory.json` defines 37 Sandy Bridge memory latency, memory ordering, misalignment, offcore DRAM response, and page-walk events. It complements `cache.json` by focusing on load latency thresholds and LLC-miss-to-DRAM response classes.

### Important APIs, Types, And Data Fields
The file is a JSON array of PMU event objects:

- `EventName` includes `MACHINE_CLEARS.MEMORY_ORDERING`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, `MEM_TRANS_RETIRED.PRECISE_STORE`, `MISALIGN_MEM_REF.*`, `OFFCORE_RESPONSE.*.LLC_MISS.*`, and `PAGE_WALKS.LLC_MISS`.
- `EventCode`, `UMask`, and `Counter` define core event selectors and counter constraints.
- `PEBS` marks precise memory events, including load latency thresholds and precise store sampling.
- `MSRIndex` and `MSRValue` program offcore response MSRs for DRAM/local-DRAM/LLC-hit response filters.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue` provide user-facing and sampling metadata.

No functions/classes are implemented; perf consumes this as declarative event metadata.

### Control Flow And Data Flow
During generation, perf turns each object into a named event. For `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, the event uses PEBS and MSR latency threshold programming such as `MSRIndex 0x3F6` with threshold-specific `MSRValue` values. For `OFFCORE_RESPONSE.*` entries, perf programs the offcore response filter MSRs just as it does for cache offcore hit events. Metrics such as `tma_dram_bound`, `tma_mem_latency`, and bandwidth-oriented top-down views depend on this memory/offcore event family.

### State And Persistence
The file persists static event encodings and filter constants. It has no mutable state. Generated perf tables embed the metadata until regeneration.

### Dependencies And Integration Points
The file depends on Sandy Bridge PEBS memory latency facilities, offcore response filter MSRs, and memory-ordering machine-clear semantics. It integrates with `cache.json` offcore events, `virtual-memory.json` TLB/page-walk data, `snb-metrics.json` memory-bound formulas, and perf's precise sampling support.

### Risks
The highest-risk entries are PEBS latency threshold events and offcore response filters. Wrong `MSRValue` thresholds can shift latency buckets, and wrong offcore filters can classify traffic as DRAM/local DRAM/LLC hit incorrectly. Because many offcore entries share event code/umask, review must compare `MSRValue` rather than only visible event selector fields.

### Test Signals
Use JSON/schema validation, generated event table comparison, `perf list` checks for `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_64` and `OFFCORE_RESPONSE.DEMAND_DATA_RD.LLC_MISS.DRAM`, metric parser tests for memory-bound formulas, and hardware smoke tests for PEBS load-latency sampling where Sandy Bridge support is available.
