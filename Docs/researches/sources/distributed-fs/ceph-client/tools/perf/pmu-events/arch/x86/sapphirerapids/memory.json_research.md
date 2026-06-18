# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/memory.json

## Purpose
`memory.json` defines 55 Sapphire Rapids core PMU events for memory stalls, load latency sampling, DRAM/local/remote/SNC/PMM offcore responses, L3-miss demand reads, RTM retirement, and TSX memory abort causes. It complements `cache.json`: `cache.json` covers cache hits/snoops/cache-source responses, while this file emphasizes memory-service paths and latency.

## Important APIs, types, and schema fields
Event objects use `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`, with `CounterMask`, `MSRIndex`, `MSRValue`, and `Data_LA` where needed. `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` events use event `0xcd`, umask `0x1`, counters `1-7`, MSR `0x3F6`, threshold-specific `MSRValue`, and `Data_LA=1`. OCR memory-response events use `EventCode` `0x2A,0x2B`, `UMask` `0x1`, and offcore MSRs `0x1a6,0x1a7`.

## Control flow and integration
Build-time generation turns the JSON into perf's Sapphire Rapids PMU table. Runtime event parsing programs normal core event selectors and, for OCR or load-latency threshold events, the associated MSR filter/threshold. `perf record` can use `Data_LA` events for address-aware sampling. Top-down memory-bound metrics and memory bandwidth/latency groups can consume events such as `MEMORY_ACTIVITY.STALLS_L3_MISS`, `OCR.READS_TO_CORE.LOCAL_DRAM`, and `OFFCORE_REQUESTS_OUTSTANDING.L3_MISS_DEMAND_DATA_RD`.

## State and persistence behavior
The file persists hardware event encodings and memory locality semantics. It does not persist measurements. Runtime state includes PEBS/load-latency sampling configuration, offcore response MSR values, transactional memory status, and counter values. The threshold ladder for load latency (`GT_4` through `GT_1024`) is encoded as data and should be treated as an ordered set.

## Dependencies
Dependencies include Sapphire Rapids offcore response semantics, PEBS load latency facility, RTM/TSX PMU events, perf's extra-MSR event handling, and the core counter inventory from `counter.json`. This file integrates with `cache.json` OCR naming conventions and with metric groups such as `MemoryBound`, `MemoryBW`, `MemoryLat`, `MemOffcore`, `tma_memory_bound_group`, `tma_mem_latency_group`, and `tma_dram_bound_group`.

## Risks and edge cases
OCR filter mistakes can swap local/remote, DRAM/PMM, or SNC-close/distant meanings with no syntax failure. Load-latency events are constrained to counters `1-7`, not counter `0`, and have address-sampling implications via `Data_LA`; violating that shape can break PEBS workflows. RTM/TSX event availability depends on platform/kernel support and CPU configuration. Some names use historical technologies such as PMM, so downstream metrics should handle platforms where the hardware path is absent or counts remain zero.

## Test signals
Run `jq empty`, generated-table builds, and perf PMU parse tests. Hardware validation should include pointer-chasing latency tests, local versus remote NUMA memory access, SNC configurations when available, RTM/TSX microbenchmarks, and `perf record` checks for load-latency address sampling. Static checks should assert all `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` thresholds use `MSRIndex` `0x3F6`, `Data_LA=1`, and counters `1-7`.
