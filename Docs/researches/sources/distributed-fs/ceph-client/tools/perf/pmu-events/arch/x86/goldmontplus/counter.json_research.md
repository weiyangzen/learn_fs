## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/counter.json

**Purpose:** Goldmont Plus PMU counter-capacity descriptor. It declares the `core` PMU as having three fixed counters and four generic programmable counters.

**Schema and important records:** This file is not an event table. It is a one-object array with `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The record tells perf's PMU event generation and reporting layer what counter resources are available for the model.

**Control flow and integration:** `jevents.py` and associated PMU metadata processing include `counter.json` alongside topic files for the same CPU directory. Runtime metric scheduling and event grouping decisions can use the generated capacity metadata to understand fixed versus generic counter limits.

**State and persistence:** Persisted as static PMU metadata in generated perf tables. It does not store counts or runtime session state.

**Dependencies:** Must match the Goldmont Plus hardware PMU and the fixed-counter use in `pipeline.json` (`INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.CORE`, `CPU_CLK_UNHALTED.REF_TSC`). It also constrains grouping for cache/offcore and virtual-memory events.

**Risks:** An incorrect generic-counter count can make perf overcommit groups or reject valid event sets. Incorrect fixed-counter count can make fixed aliases appear schedulable when hardware cannot support them.

**Test signals:** Validate JSON; build perf; run grouped `perf stat` workloads that mix fixed and programmable events. Metric scheduling failures or unexpected multiplexing are signals that this descriptor is stale.
