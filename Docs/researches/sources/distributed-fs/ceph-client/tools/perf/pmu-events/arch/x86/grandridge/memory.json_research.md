## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/memory.json

**Purpose:** Grand Ridge memory topic with 11 events for load-head retirement attribution, memory-ordering machine clears, page-split misaligned memory references, and OCR demand data/RFO L3 misses.

**Schema and important records:** Standard event fields plus `MSRIndex`/`MSRValue` on `OCR.DEMAND_DATA_RD.L3_MISS` and `OCR.DEMAND_RFO.L3_MISS`. `LD_HEAD.*_AT_RET` classifies loads at retirement as L1-bound, L1-miss, page-walk, store-address, other, or any. `MACHINE_CLEARS.MEMORY_ORDERING` and `MISALIGN_MEM_REF.*_PAGE_SPLIT` mirror narrow memory-ordering and page-split diagnostics.

**Control flow and integration:** `jevents.py` emits static event rows and maps OCR MSR selectors to offcore response fields. `grr-metrics.json` uses `LD_HEAD.*` events for memory-execution bottleneck percentages and load-store-bound breakdowns.

**State and persistence:** Static alias and selector metadata; runtime PMU state is transient.

**Dependencies:** Depends on Grand Ridge OCR encodings and pipeline/cache event families. Metrics require these names to remain stable.

**Risks:** `LD_HEAD` attribution feeds derived percentages, so any wrong selector can skew topdown-style diagnostics. OCR L3 miss aliases require correct MSR programming.

**Test signals:** JSON/build validation; metric parser tests for `tma_info_mem_exec_bound_*` and `load_store_bound` metrics; runtime load-miss and page-split microbenchmarks.
