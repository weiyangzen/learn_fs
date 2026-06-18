## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/floating-point.json

**Purpose:** Goldmont Plus floating-point topic with three events: floating-point divide busy cycles, machine clears caused by FP assists, and retired FP divide uops. These aliases help diagnose long-latency FP division and assist-driven pipeline disruption.

**Schema and important records:** Records use the standard `pmu_event` fields. `CYCLES_DIV_BUSY.FPDIV` counts FP divider busy cycles, `MACHINE_CLEARS.FP_ASSIST` counts FP-assist machine clears, and `UOPS_RETIRED.FPDIV` is PEBS-capable retired FP divide uop accounting.

**Control flow and integration:** Build-time `jevents.py` places the records into the Goldmont Plus event table under the floating-point topic. At runtime they are listed and programmed by name through the generic PMU event-table lookup functions.

**State and persistence:** Static event metadata only. Runtime counts are accumulated in PMU counters during perf sessions and are not persisted by the JSON layer.

**Dependencies:** Depends on the Goldmont Plus PMU event encodings and counter resources in `counter.json`. Metrics or ad hoc analyses can combine these with cycle and instruction events from `pipeline.json`.

**Risks:** The small file is easy to overlook during model updates; stale FP assist/divide encodings would undermine floating-point bottleneck analysis. `MACHINE_CLEARS.FP_ASSIST` semantics must stay aligned with pipeline machine-clear aliases.

**Test signals:** `jq` validity; perf jevents build; `perf list floating` includes all three names. Runtime validation can use FP-divide-heavy microbenchmarks and compare `CYCLES_DIV_BUSY.FPDIV` with `UOPS_RETIRED.FPDIV`.
