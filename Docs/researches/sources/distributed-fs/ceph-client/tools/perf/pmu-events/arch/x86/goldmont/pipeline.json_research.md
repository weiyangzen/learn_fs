## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/pipeline.json

**Purpose:** Goldmont pipeline PMU topic with 40 core events for branch retirement and misprediction, unhalted/reference cycles, divider occupancy, retired instructions/uops, frontend delivery gaps, backend issue slot pressure, load blocking, and machine clears. It gives `perf list` and `perf stat -e` symbolic names such as `BR_INST_RETIRED.ALL_BRANCHES`, `UOPS_NOT_DELIVERED.ANY`, and `MACHINE_CLEARS.SMC`.

**Schema and important records:** Every item is a `pmu_event` source record using `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `SampleAfterValue`, and optional `PEBS`. Fixed-counter events are encoded through `Counter` values like `Fixed counter 0/1/2` for `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.CORE`, and `CPU_CLK_UNHALTED.REF_TSC`; programmable variants use explicit event encodings and counter lists. PEBS-capable entries include retired branches, retired loads blocked, and retired uops.

**Control flow and integration:** `jevents.py` loads this topic while traversing the `goldmont` model directory, turns each JSON object into `JsonEvent`, derives the topic from `pipeline.json`, and emits compact C strings and `struct pmu_event` entries. Runtime lookup flows through `perf_pmu__find_events_table`, then `pmu_events_table__find_event` or iteration APIs used by `perf list`.

**State and persistence:** The file has no runtime mutation. Its persisted state is the event catalog compiled into the perf binary; sampling behavior is controlled later by perf and kernel PMU programming.

**Dependencies:** Depends on Intel Goldmont event encodings, perf's PMU JSON schema, and x86 mapfile CPU matching. Metrics in other files may refer to these names, especially `CPU_CLK_UNHALTED.*`, `INST_RETIRED.*`, branch, uop, and machine-clear events.

**Risks:** Incorrect `EventCode`, `UMask`, fixed-counter mapping, or PEBS annotation silently misprograms hardware counters or makes precise sampling unavailable/misleading. The distinction between fixed and programmable aliases must remain consistent because events like `INST_RETIRED.ANY` and `INST_RETIRED.ANY_P` have different collection constraints.

**Test signals:** Validate JSON syntax and schema with `jq`; build perf with jevents enabled; use `perf list` on a matching Goldmont CPU or generated-table tests to confirm event aliases. Spot-check branch/uop/cycle aliases with `perf stat -e` and verify fixed counter aliases are not emitted as programmable-only events.
