<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/memory.json

## Purpose
Defines Emerald Rapids raw PMU events for memory stalls, load latency sampling, offcore response classifications, transactional memory behavior, and cache/memory request attribution. These records support memory-bound topdown analysis, NUMA locality diagnostics, bandwidth/latency metrics, and TSX/RTM memory-conflict inspection in perf.

## Important APIs, Types, And Functions
- Top-level type: JSON array of 55 event records.
- Common fields: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`.
- Optional programming and sampling fields: `CounterMask`, `Data_LA`, `MSRIndex`, `MSRValue`, and `PublicDescription`.
- Major event families:
  - `CYCLE_ACTIVITY.STALLS_L3_MISS` and `MEMORY_ACTIVITY.*` for stall cycles while cache-miss demand loads are outstanding.
  - `MACHINE_CLEARS.MEMORY_ORDERING` for machine clears caused by memory-ordering conflicts.
  - `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` and `.STORE_SAMPLE` for PEBS/data-linear-address sampling using `EventCode` `0xcd`, `Data_LA`, and latency threshold MSR `0x3F6`.
  - `OCR.*` offcore response events using `EventCode` `0x2A,0x2B`, MSR indices `0x1a6,0x1a7`, and encoded response filters for code reads, data reads, RFOs, hardware prefetches, streaming writes, reads to core, DRAM, local/remote memory, SNC DRAM, L3 miss, and write-estimate categories.
  - `OFFCORE_REQUESTS.*` and `OFFCORE_REQUESTS_OUTSTANDING.*` for L3-miss demand data read counts and occupancy.
  - `RTM_RETIRED.*` and `TX_MEM.*` for TSX/RTM starts, commits, aborts, and abort causes.

## Control Flow
Perf loads these records as Emerald Rapids memory event definitions. Simple stall and transactional events program event select/umask fields directly. Load latency and store sample events also program PEBS/data address support and MSR filter `0x3F6` to select a latency threshold. Offcore response events program paired offcore MSR filters (`0x1a6`, `0x1a7`) with model-specific response bitmasks, then count matching requests through the declared event code pair. Derived metrics consume these records to compute memory-bound fractions, load latency, memory bandwidth, NUMA locality, offcore miss rates, store/RFO pressure, and TSX abort breakdowns.

## State And Persistence
The file persists only static PMU metadata. Runtime state includes event scheduling, offcore MSR filter programming, PEBS data-address capture, sampled load/store records, and accumulated counts. Offcore and load-latency events rely on hardware filter state, so simultaneous measurements can be constrained by shared MSRs, available counters, and perf grouping decisions.

## Dependencies And Integration Points
- Consumed by Linux perf's pmu-events pipeline for the Emerald Rapids x86 model.
- Feeds metrics in `emr-metrics.json` such as `tma_memory_bound`, `tma_l1_bound`, `tma_l2_bound`, `tma_l3_bound`, `tma_dram_bound`, `tma_mem_latency`, `tma_mem_bandwidth`, `tma_local_mem`, `tma_remote_mem`, `tma_data_sharing`, `tma_lock_latency`, memory bandwidth metrics, LLC miss latency metrics, and NUMA read locality metrics.
- Depends on Intel Emerald Rapids definitions for memory activity, MEM_TRANS_RETIRED latency thresholds, offcore response filter encodings, RTM/TSX events, SNC-mode interpretation, and PEBS data linear address behavior.
- Integrates with perf memory profiling, `perf mem`, `perf stat` metric groups, and server tuning workflows that distinguish local DRAM, remote DRAM, remote memory, SNC DRAM, L3 misses, and write estimates.

## Risks And Edge Cases
- Offcore response records have dense `MSRValue` bitmasks. A single-bit transcription error can produce a syntactically valid event with a different memory-source meaning.
- Several OCR descriptions are topology-dependent. In Sub NUMA Cluster mode, "local" and "SNC_DRAM" have different interpretations than in non-SNC mode.
- Load latency events are randomly selected PEBS samples and report dispatch-to-completion latency that can exceed pure memory latency; they should not be treated as deterministic exact latencies.
- `Data_LA` events require support for data linear address capture and may be unavailable or restricted depending on kernel, privilege, PEBS setup, and virtualization.
- Offcore MSR filters are shared resources; measuring multiple offcore categories in one group can fail, multiplex, or require separate runs.
- Some events are constrained to counters `0,1,2,3` or only counter `0` for store sampling, which affects derived metric schedulability.

## Test Signals
- JSON syntax validation should pass and every offcore/load-latency event should retain its `MSRIndex` and `MSRValue`.
- `perf list` should expose the `MEMORY_ACTIVITY`, `MEM_TRANS_RETIRED`, `OCR`, `OFFCORE_REQUESTS`, `RTM_RETIRED`, and `TX_MEM` event names on the Emerald Rapids table.
- `perf stat -e MEMORY_ACTIVITY.STALLS_L3_MISS,OFFCORE_REQUESTS.L3_MISS_DEMAND_DATA_RD,OCR.DEMAND_DATA_RD.LOCAL_DRAM` should parse on supported hardware.
- Memory-latency microbenchmarks should increase the corresponding `LOAD_LATENCY_GT_*` buckets and L3-miss stall events.
- NUMA placement tests should change local versus remote OCR categories, and TSX workloads should exercise the RTM/TX_MEM abort and commit counters.
- Derived memory metrics should continue resolving all referenced event names after edits to this file or to `emr-metrics.json`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/memory.json -->
