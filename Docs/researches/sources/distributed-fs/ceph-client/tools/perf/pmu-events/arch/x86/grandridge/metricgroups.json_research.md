## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/metricgroups.json

**Purpose:** Grand Ridge metric-group description map with 21 group names used by `grr-metrics.json`. It gives human-readable descriptions for `perf list metricgroups` and metric grouping UI/output.

**Schema and important records:** Unlike event and metric arrays, this file is a JSON object mapping group name to description string. Groups include broad spreadsheet-derived groups (`Flops`, `Ifetch`, `Load_Store_Miss`, `Mem_Exec`, `Power`, `Summary`, `load_store_bound`), topdown levels (`TopdownL1`, `TopdownL2`, `TopdownL3`), internal TMA level groups (`tma_L1_group`, `tma_L2_group`, `tma_L3_group`), and contributor groups for backend, bad speculation, core bound, frontend bound, ifetch bandwidth/latency, machine clears, and resource bound.

**Control flow and integration:** `jevents.py` loads metric-group descriptions into `_metricgroups`; generated perf code exposes them through `describe_metricgroup`. Runtime `perf list metricgroups` and metric display paths use these descriptions when presenting groups from `grr-metrics.json`.

**State and persistence:** Static description metadata only. It has no counters, formulas, or mutable state.

**Dependencies:** Must stay synchronized with `MetricGroup` values in `grr-metrics.json`. Semicolon-delimited metric groups rely on each component name being present here for good descriptions.

**Risks:** This object-shaped schema differs from the array schema used by most PMU JSON files; generic tooling that assumes arrays will fail. Missing group descriptions do not necessarily break collection, but they degrade discoverability and may signal stale metric taxonomy.

**Test signals:** Validate as a JSON object, not an event array. Run `perf list metricgroups` or generated `describe_metricgroup` tests and compare every group referenced by `grr-metrics.json` against this map.
