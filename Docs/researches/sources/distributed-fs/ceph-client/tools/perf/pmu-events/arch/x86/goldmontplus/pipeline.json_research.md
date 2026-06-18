## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/pipeline.json

**Purpose:** Goldmont Plus pipeline topic with 42 events. It is the Goldmont pipeline set plus additional machine-clear and precise-retirement coverage such as `INST_RETIRED.PREC_DIST` and `MACHINE_CLEARS.PAGE_FAULT`.

**Schema and important records:** Standard `pmu_event` fields with PEBS on precise retirement/load-blocking/uop records. Families include retired and mispredicted branches, unhalted/reference cycles, divider busy cycles, fixed and programmable retired instruction aliases, backend issue-slot pressure, load blocking (`4K_ALIAS`, `STORE_FORWARD`, `UTLB_MISS`), machine clears, and retired/issued uops.

**Control flow and integration:** `jevents.py` converts the JSON to C event-table rows, deriving topic from the filename. Runtime perf uses the generated table selected by x86 mapfile CPUID matching for Goldmont Plus.

**State and persistence:** Persistent static catalog. Runtime counts and sampling records are maintained by perf/kernel PMU paths, not by this file.

**Dependencies:** Depends on `counter.json` for fixed/generic capacity, and on related cache/frontend/memory/virtual-memory topics for full bottleneck analysis. Grandridge metrics use similar event families but with newer topdown names, so cross-model renames must be deliberate.

**Risks:** Goldmont and Goldmont Plus are similar enough that accidental copy-forward is plausible. The two extra records must stay model-appropriate. PEBS and fixed-counter distinctions are important for precise sampling and event grouping.

**Test signals:** JSON validation; perf jevents generation; `perf list pipeline` on matching CPU. Compare event inventory with Goldmont to verify intentional additions (`INST_RETIRED.PREC_DIST`, `MACHINE_CLEARS.PAGE_FAULT`) rather than accidental drift.
