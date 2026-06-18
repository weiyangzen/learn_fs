## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/floating-point.json

**Purpose:** Panther Lake floating-point and vector execution event topic with 40 PMU records. It covers FP divider activity, FP assists, core vector-arithmetic dispatch ports, retired FP arithmetic operation classes, atom retired FP instruction/FLOP classes, atom FP/vector-integer execution ports, and FP assist machine clears.

**Schema and important records:** Standard PMU fields include `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `CounterMask`, `SampleAfterValue`, and descriptions. `ARITH.FPDIV_ACTIVE` is intentionally duplicated for atom and core with different event codes and semantics. Core `FP_ARITH_OPS_RETIRED.*` records classify scalar, vector, 128-bit, 256-bit, single, double, and combined FLOP-width groups, with descriptions warning that DAZ/FTZ MXCSR flags should be set and that some FMA/DPP instructions count as multiple operations. Atom records use `FP_FLOPS_RETIRED.*`, `FP_INST_RETIRED.*`, and `FP_VINT_UOPS_EXECUTED.*` to expose equivalent but unit-specific accounting.

**Control flow and integration:** The perf generator converts each object into a Panther Lake floating-point event. Runtime selection is unit-routed: core users see core FP arithmetic and dispatch events, atom users see atom FP instruction/FLOP and execution-port events. Counter masks on divider active events make them cycle-style occupancy/presence measurements. The records integrate with perf's topic filtering (`perf list floating-point`) and with metrics that estimate FP intensity, vector width mix, divide pressure, and assist overhead.

**State and persistence:** Static event metadata. Runtime FP counts depend on programmed counters and workload instruction mix. There is no local persistence beyond generated PMU tables and default sample periods.

**Dependencies:** Depends on Panther Lake core/atom FP pipelines and perf's x86 event parser. Correct interpretation also depends on architectural state noted in descriptions, especially MXCSR DAZ/FTZ flags for core `FP_ARITH_OPS_RETIRED.*`. Counter availability comes from `counter.json`.

**Risks:** FLOP-style events are easy to misinterpret as instruction counts because vector width and FMA/DPP weighting differ by record. Core and atom use different event families, so cross-unit comparisons need normalization. Missing or altered descriptions would remove important caveats about DAZ/FTZ and multi-count operations. Duplicate `ARITH.FPDIV_ACTIVE` must not be collapsed across units.

**Test signals:** Build-time JSON validation should preserve all 40 records. `perf list floating-point` should show both core and atom families. Runtime smoke tests can run scalar, vector, and divide-heavy loops and verify that corresponding retire/dispatch/divider counters move. Metric tests should check any FP throughput formulas against vector-width weighting and atom/core unit selection.
