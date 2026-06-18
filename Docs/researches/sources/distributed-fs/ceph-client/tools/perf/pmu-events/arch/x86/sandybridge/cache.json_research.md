## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/cache.json

### Purpose
`cache.json` defines 173 Sandy Bridge core PMU events for cache hierarchy behavior: L1D allocation, eviction, replacement, bank conflicts, pending misses, L2 request/fill/writeback traffic, LLC reference/miss events, retired memory uops, offcore requests, offcore outstanding cycles, offcore responses, and split-lock/store-queue conditions. It is the largest file in this group and provides the low-level event names used by `perf stat -e`, `perf record -e`, and higher-level metrics in `snb-metrics.json`.

### Important APIs, Types, And Data Fields
The file is a JSON array of event objects. The effective API is the perf PMU event schema:

- `EventName` is the user-visible perf symbolic event, for example `L1D.REPLACEMENT`, `L2_RQSTS.ALL_DEMAND_DATA_RD`, `LONGEST_LAT_CACHE.MISS`, `MEM_LOAD_UOPS_RETIRED.L1_HIT`, and `OFFCORE_RESPONSE.DEMAND_DATA_RD.LLC_HIT.ANY_RESPONSE`.
- `EventCode` and `UMask` encode the architectural or model-specific event selector.
- `Counter` restricts usable programmable counters. Most events allow `0,1,2,3`; some require counter `2` or use fixed offcore-capable encodings.
- `CounterMask`, `AnyThread`, and `PEBS` add perf event modifiers for thresholded cycle counts, any-thread counting, and precise event sampling.
- `MSRIndex` and `MSRValue` appear on `OFFCORE_RESPONSE.*` events and program Sandy Bridge offcore response MSRs `0x1a6,0x1a7`.
- `BriefDescription` and `PublicDescription` feed perf event help output and generated documentation.
- `SampleAfterValue` supplies default sampling periods for record mode.

There are no local functions or classes. The data is parsed by perf's PMU-events build tools and transformed into generated C tables or runtime JSON event descriptions, depending on the perf version.

### Control Flow And Data Flow
At build time, perf's event tooling reads this array together with sibling Sandy Bridge files. Each object becomes one event record keyed by `EventName`. At runtime, perf resolves a symbolic event to the encoded selector fields, validates counter constraints, and programs the appropriate core PMU register. For offcore response events, perf must also program the offcore filter MSR with `MSRValue`; the same event selector `0xB7, 0xBB` and `UMask 0x1` is reused while the MSR filter distinguishes request/response/snoop classes.

The file also feeds derived metric evaluation indirectly. Metrics such as `tma_dram_bound`, `tma_l3_bound`, `tma_mem_bandwidth`, and `tma_memory_bound` reference events from this file (`MEM_LOAD_UOPS_RETIRED.LLC_HIT`, `MEM_LOAD_UOPS_MISC_RETIRED.LLC_MISS`, `CYCLE_ACTIVITY.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`) and therefore rely on these names staying stable.

### State And Persistence
The file is static source data. It does not persist runtime state. Its persistent state is the set of hardware encodings, descriptions, PEBS flags, sampling periods, and offcore MSR filters committed in the repository. Generated perf artifacts cache these definitions after build, so changes require rebuilding or regenerating perf PMU event tables.

### Dependencies And Integration Points
The file depends on Intel Sandy Bridge PMU semantics: core counters, PEBS support, model-specific offcore response MSRs, and the mapping between event selector bits and cache states. It integrates with:

- perf PMU event parsers and `jevents` style table generation.
- `snb-metrics.json`, whose formulas reference cache and memory events by exact `EventName`.
- `metricgroups.json`, which labels derived metrics that use these events.
- The Linux perf user interface, where event names and descriptions are surfaced.

### Risks
The main risk is silent measurement corruption: incorrect `EventCode`, `UMask`, `Counter`, PEBS, `CounterMask`, `AnyThread`, `MSRIndex`, or `MSRValue` values can still parse but count the wrong hardware condition. Offcore response entries are particularly sensitive because many names share the same visible event selector and differ only by MSR filters. Counter restrictions also matter; events limited to counter `2` or requiring PEBS may fail scheduling or be multiplexed incorrectly if the metadata is wrong. Duplicate or renamed event names would break metrics that reference them.

### Test Signals
Useful validation signals include `jq` parse success, perf PMU schema validation, generated event table diffs, `perf list` showing the expected Sandy Bridge cache/offcore names, and smoke tests that run representative events such as `L1D.REPLACEMENT`, `L2_RQSTS.ALL_DEMAND_DATA_RD`, `MEM_LOAD_UOPS_RETIRED.L1_HIT`, and an `OFFCORE_RESPONSE.*` event on Sandy Bridge-family hardware or an event parser test fixture. Metric validation should check formulas in `snb-metrics.json` that reference cache events.
