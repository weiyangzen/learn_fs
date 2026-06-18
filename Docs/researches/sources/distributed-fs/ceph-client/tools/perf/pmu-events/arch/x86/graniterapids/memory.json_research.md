<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/memory.json

## Purpose
Granite Rapids x86 perf PMU event table for memory, offcore, load latency, transactional memory, and memory-ordering observation. The 50 JSON objects provide raw aliases used directly by users and indirectly by Granite Rapids metrics to reason about cache-miss stalls, demand data/code/RFO offcore responses, memory locality, store sampling, and RTM/transaction abort causes.

## APIs, Types, and Functions
The file uses the same perf PMU event JSON schema as other architecture event tables. Fields include `EventName`, `EventCode`, `UMask`, `Counter`, optional `CounterMask`, `MSRIndex`, `MSRValue`, `Data_LA`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. It defines data, not functions or local types.

The event families are:
- `CYCLE_ACTIVITY.*` and `MEMORY_ACTIVITY.*` counters for cycles or execution stalls while L1D, L2, or L3 miss demand loads are outstanding.
- `MACHINE_CLEARS.MEMORY_ORDERING` for machine clears triggered by memory-ordering conflicts.
- `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` thresholds from 4 through 2048 cycles and `MEM_TRANS_RETIRED.STORE_SAMPLE`, using `Data_LA` and MSR threshold programming through `MSRIndex` `0x3F6`.
- `OCR.*` offcore response aliases for demand code reads, demand data reads, RFOs, reads-to-core, and write estimates. Many use combined `EventCode` values `0x2A,0x2B`, paired offcore MSRs `0x1a6,0x1a7`, and different `MSRValue` response masks for DRAM, L3 miss, local/remote DRAM, local socket, remote memory, and local cluster/cache variants.
- `OFFCORE_REQUESTS.*` and `OFFCORE_REQUESTS_OUTSTANDING.*` demand-data L3 miss request and occupancy events.
- `RTM_RETIRED.*` and `TX_MEM.*` events for restricted transactional memory start/commit/abort and capacity/conflict abort reasons.

## Control Flow, State, and Persistence
Perf parses the JSON array into event aliases for Granite Rapids. At runtime an alias maps to an event select, umask, counter constraints, counter mask, optional latency-address sampling flag, and optional MSR selector. Offcore response events require programming the offcore response MSR mask named by `MSRIndex`/`MSRValue`. Load latency threshold aliases require programming the latency threshold MSR value. The JSON itself has no mutable state; persistence is source control plus generated perf alias tables.

This file feeds many formulas in `gnr-metrics.json`. Examples include `tma_dram_bound`, `tma_mem_latency`, `tma_l1_bound`, `tma_l2_bound`, `tma_l3_bound`, `tma_cxl_mem_bound`, `tma_false_sharing`, `tma_info_memory_latency_load_l3_miss_latency`, `tma_info_memory_mix_offcore_read_l3m_pki`, `tma_info_memory_soc_r2c_dram_bw`, and NUMA/locality bandwidth formulas. The memory activity stall counters also sit under the top-down backend/memory hierarchy.

## Dependencies and Integration
The file depends on perf's PMU event schema, Intel Granite Rapids event encodings, PEBS/load-latency support for `Data_LA` events, and offcore response MSR programming support. Integration points are `perf list`, `perf stat`, `perf record` sampling for load/store latency, the metric engine, and raw offcore response handling. It must stay consistent with formula references in `gnr-metrics.json` and with sibling cache/TLB/uncore event files that provide companion events in the same memory metrics.

Counter restrictions matter. Some cycle/stall events are limited to counters `0,1,2,3`; load-latency threshold events allow counters `1..7`; store sampling specifies counter `0`; and OCR events allow `0..3` while programming offcore MSRs. Perf scheduling must respect these constraints when a metric group combines many memory aliases.

## Risks
Offcore and latency events have high risk because multiple aliases share the same base event but differ only by MSR response mask or threshold. A single wrong `MSRValue` changes the semantic category while still producing counts. `Data_LA` events are sampling-oriented and may not behave like ordinary counting events on all perf paths. Counter conflicts are likely in large metric groups because memory metrics combine core, offcore, PEBS, and uncore counters. Several public descriptions include topology caveats such as Sub-NUMA Cluster behavior; formulas and human interpretation need to account for SNC/local-cluster modes. Transactional-memory events may be low or unsupported depending on platform configuration and workload, so metrics should tolerate zeros.

## Test Signals
Validation starts with JSON parsing and perf event-table generation. Runtime smoke tests should confirm `perf list` exposes the aliases and `perf stat -e` accepts representative events from each family: `MEMORY_ACTIVITY.STALLS_L1D_MISS`, `MEMORY_ACTIVITY.STALLS_L3_MISS`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128`, `OCR.DEMAND_DATA_RD.L3_MISS`, `OCR.READS_TO_CORE.REMOTE_MEMORY`, `OFFCORE_REQUESTS_OUTSTANDING.L3_MISS_DEMAND_DATA_RD`, and `RTM_RETIRED.ABORTED`. Metric-level tests should run memory-bound, cache-resident, remote-NUMA, and transactional-memory workloads where available, checking that memory-bound TMA nodes and bandwidth/latency formulas move in expected directions and do not emit parse errors, NaNs, or impossible negative values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/memory.json -->
