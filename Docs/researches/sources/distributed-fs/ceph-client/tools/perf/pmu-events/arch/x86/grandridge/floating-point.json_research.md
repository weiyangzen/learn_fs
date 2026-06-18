## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/floating-point.json

**Purpose:** Grand Ridge floating-point topic with 13 events for FP divide active cycles, retired FP FLOPs/instructions by precision and vector width, FP-assist machine clears, and retired FP divide uops.

**Schema and important records:** Standard event records with `CounterMask` on `ARITH.FPDIV_ACTIVE` and `Deprecated` on older compatibility aliases. Event families include `FP_FLOPS_RETIRED.ALL/DP/SP/FP32/FP64`, `FP_INST_RETIRED.128B_*`, `256B_DP`, scalar 32/64-bit aliases, `MACHINE_CLEARS.FP_ASSIST`, and `UOPS_RETIRED.FPDIV`.

**Control flow and integration:** `jevents.py` emits records under the floating-point topic. `grr-metrics.json` depends on these event names for `Flops` group metrics such as `tma_info_core_flopc`, `tma_info_system_gflops`, and FP instruction-mix ratios.

**State and persistence:** Static catalog metadata only. Deprecated markers persist into generated `pmu_event.deprecated` fields so perf can hide or annotate stale aliases as appropriate.

**Dependencies:** Depends on Grand Ridge FP PMU encodings, topdown metrics, and cycle/instruction events in `pipeline.json`.

**Risks:** Deprecated aliases must remain available only as intended; removing them can break metric expressions or user scripts. FLOP versus instruction counts differ, so descriptions and metric formulas must avoid mixing semantic units.

**Test signals:** JSON/build validation; metric parser coverage for Flops metrics; runtime FP scalar/vector microbenchmarks to check expected nonzero precision-specific aliases.
