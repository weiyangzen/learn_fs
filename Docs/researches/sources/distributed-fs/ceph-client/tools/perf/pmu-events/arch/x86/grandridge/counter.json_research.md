## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/counter.json

**Purpose:** Grand Ridge PMU counter-capacity descriptor for core and uncore PMUs. It declares `core` as three fixed and eight generic counters, plus several uncore units with four generic counters and no fixed counters.

**Schema and important records:** Array of unit records using `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. Units are `core`, `B2CMI`, `CHA`, `IMC`, `IIO`, `IRP`, `PCU`, and `CHACMS`. `PCU` has numeric `CountersNumGeneric` while most others encode counts as strings, so consumers must tolerate both JSON number and string forms.

**Control flow and integration:** Included in the model directory during jevents processing. Runtime event grouping and metric scheduling rely on these capacities when metrics use core events together with uncore aliases referenced by `grr-metrics.json`.

**State and persistence:** Static PMU resource metadata. It does not represent counter values or runtime state.

**Dependencies:** Must match Grand Ridge hardware PMU topology. The uncore unit list supports metrics for memory bandwidth, IO bandwidth, C-state residency, SMI, and uncore frequency.

**Risks:** Incorrect capacity causes perf to make poor grouping/multiplexing decisions. The mixed numeric/string representation for `CountersNumGeneric` is a compatibility risk for strict validators.

**Test signals:** JSON parse; jevents build; run `perf list` and metric scheduling tests for both core and uncore metrics. A schema lint should explicitly accept or normalize string/integer counter counts.
