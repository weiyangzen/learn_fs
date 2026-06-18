# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/cache.json

## Purpose
Broadwell-DE core cache and offcore memory event catalog for perf. It defines 76 raw event aliases covering L1D replacement and pending misses, L2 requests/transitions/line fills, LLC reference and miss proxies, load hit levels, snoop outcomes, split locks, store queue fullness, offcore requests, and offcore response selection.

## Important APIs, Types, and Functions
The data entries use the perf PMU event schema: every event has `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Optional fields model hardware restrictions and sampling behavior: `CounterMask` on 7 events, `AnyThread` on 1 event, `PEBS` plus `Data_LA` on 22 precise load-address events, and `Errata` on 20 entries. Important event families are `L1D`, `L1D_PEND_MISS`, `L2_RQSTS`, `L2_TRANS`, `LONGEST_LAT_CACHE`, `MEM_LOAD_UOPS_RETIRED`, `MEM_LOAD_UOPS_L3_HIT_RETIRED`, `MEM_LOAD_UOPS_L3_MISS_RETIRED`, `MEM_UOPS_RETIRED`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `OFFCORE_RESPONSE`, and `SQ_MISC`.

## Control Flow
Perf parses this file into aliases that users can request directly or indirectly through metrics. For a direct event, perf programs the listed event select, umask, counter mask, PEBS flag, and offcore MSR configuration when present. For derived metrics in `bdwde-metrics.json`, these aliases become operands in formulas for L1/L2/L3 bound, DRAM bound, data sharing, contested accesses, split loads/stores, DTLB behavior, memory-level parallelism, and cache bandwidth.

## State and Persistence
The JSON has no runtime state. Persistent semantics live in event names and encodings. The `OFFCORE_RESPONSE` entry is stateful at programming time because perf must combine the event with an offcore response MSR value, while PEBS/Data_LA events create sampled records with data addresses when used in sampling mode.

## Dependencies and Integration
The file integrates with perf's x86 PMU JSON loader, the Broadwell-DE core PMU, PEBS support, and offcore response MSR programming. It is consumed heavily by the memory and top-down metrics file. Counter availability is constrained by `counter.json`, with most events accepting generic counters 0 through 3 and some pending-miss duration events limited to counter 2.

## Risks
Risks include incorrect offcore response programming, PEBS/Data_LA events being used on kernels or privilege settings that do not expose precise address records, errata-marked events being trusted too broadly, and alias overlap between hit/miss/reference events leading to double counting in derived formulas. Counter-specific events can fail to schedule when grouped with other counter-restricted events.

## Test Signals
Test with `jq empty`, `perf list` aliases for each major family, and `perf stat -e` smoke runs for L1D, L2, LLC, offcore, and split-lock events. Sampling tests should verify PEBS events produce data address records. Metric tests should confirm memory-bound formulas using `MEM_LOAD_UOPS_RETIRED.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, and `MEM_LOAD_UOPS_L3_*` expand without unresolved aliases.
