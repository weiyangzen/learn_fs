## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/counter.json

**Purpose:** Panther Lake counter topology metadata. It declares how many fixed and generic counters perf should expect for `cpu_atom`, `cpu_core`, and `iMC` PMU units. This small file informs scheduling capacity and validation for the larger event JSON files in the same Panther Lake directory.

**Schema and important records:** The file is a three-object JSON array. `cpu_atom` declares `CountersNumFixed: 7` and `CountersNumGeneric: 8`; `cpu_core` declares `CountersNumFixed: 4` and `CountersNumGeneric: 10`; `iMC` declares `CountersNumFixed: 0` and `CountersNumGeneric: 5`. The fields are numeric strings, matching the perf pmu-events convention used by generated tables.

**Control flow and integration:** Perf's event generation reads this as unit-level metadata rather than as countable events. The resulting tables help perf understand available counter resources when it schedules events from `cache.json`, `frontend.json`, `floating-point.json`, `memory.json`, `other.json`, and any uncore/iMC topic files. The unit names must match the `Unit` fields used by event definitions.

**State and persistence:** Static topology data only. No runtime counters are created here; the generated value persists as compiled metadata and is compared with runtime PMU discovery when perf schedules events.

**Dependencies:** Depends on Panther Lake hybrid PMU naming (`cpu_core`, `cpu_atom`) and integrated memory-controller PMU naming (`iMC`). It must remain consistent with event `Counter` allow-lists: atom events commonly list counters `0..7`, core events list `0..9`, and iMC events rely on the uncore memory-controller capacity.

**Risks:** Wrong counts can cause perf to over-schedule events, reject valid groups, or produce misleading multiplexing behavior. Unit-name drift is especially risky because all nearby event files depend on exact string matching. Treating the string values as free-form text instead of numeric metadata can hide malformed counter declarations.

**Test signals:** JSON/schema validation should confirm exactly three unit records and numeric string counter counts. Generated PMU tables should expose counter capabilities for `cpu_atom`, `cpu_core`, and `iMC`. Runtime grouped `perf stat` tests should verify that core and atom events can be scheduled within their declared generic-counter limits.
