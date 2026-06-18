## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/cache.json

**Purpose:** Grand Ridge cache topic with 58 events for L1 dirty eviction, L2 line states and requests, LLC/longest-latency cache references, instruction-fetch and load memory-bound stalls, load hit levels through L3/WCB, memory scheduler blocking, load latency thresholds, split/locked accesses, STLB misses, store latency, offcore response (`OCR.*`) demand data/RFO snoop states, and topdown I-cache frontend bound.

**Schema and important records:** Uses standard event fields plus `MSRIndex`/`MSRValue` for `OCR.*` records and `Data_LA` on precise load-related records. `MEM_UOPS_RETIRED.LOAD_LATENCY_GT_*` spans thresholds from greater than 4 to greater than 2048 cycles. `MEM_BOUND_STALLS_LOAD.*` and `MEM_BOUND_STALLS_IFETCH.*` provide stall attribution by cache level.

**Control flow and integration:** `jevents.py` maps MSR-backed OCR selectors through the same offcore MSR conversion path and emits all records as Grand Ridge cache-topic `pmu_event` rows. `grr-metrics.json` references many of these names for load-store, memory-execution, and IO/memory bandwidth metrics.

**State and persistence:** Static event metadata. Offcore selector values and load-latency threshold encodings are persisted in generated event strings; actual counts are session-scoped.

**Dependencies:** Depends on Grand Ridge core PMU and OCR encodings, counter resources in `counter.json`, and uncore event availability for metrics that combine core cache aliases with CHA/IMC/IIO events.

**Risks:** OCR MSR selectors and load-latency threshold masks are high-risk fields because errors produce plausible but wrong measurements. Metrics in `grr-metrics.json` will fail or mislead if referenced event names are renamed.

**Test signals:** JSON/build validation; `perf list cache` for Grand Ridge table. Metric parser tests should cover `grr-metrics.json` expressions using `MEM_BOUND_STALLS_*`, `MEM_LOAD_UOPS_RETIRED.*`, and `OCR.*`; runtime offcore smoke tests should verify MSR selector programming.
