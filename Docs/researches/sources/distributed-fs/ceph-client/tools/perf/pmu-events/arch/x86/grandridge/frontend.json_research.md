## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/frontend.json

**Purpose:** Grand Ridge frontend topic with five events for branch-address clears, frontend-retired ITLB misses, instruction-cache accesses/misses, and micro-sequencer busy cycles.

**Schema and important records:** Standard event records. `BACLEARS.ANY` feeds branch-mispredict diagnostics; `FRONTEND_RETIRED.ITLB_MISS` gives frontend retirement attribution; `ICACHE.ACCESSES` and `.MISSES` feed instruction-cache miss metrics; `MS_DECODED.MS_BUSY` exposes microcode sequencer pressure.

**Control flow and integration:** Converted by `jevents.py` into Grand Ridge event-table rows. `grr-metrics.json` references `ICACHE.MISSES`, `BACLEARS.ANY`, and frontend topdown events for Ifetch and TMA metrics.

**State and persistence:** Static alias metadata; runtime counter state is session-local.

**Dependencies:** Depends on Grand Ridge frontend PMU encodings and topdown pipeline events such as `TOPDOWN_FE_BOUND.*`. Integrated with virtual-memory events for ITLB analysis.

**Risks:** Grand Ridge names differ from Goldmont Plus (`BACLEARS.ANY` vs `BACLEARS.ALL`, `MS_DECODED.MS_BUSY` vs `MS_ENTRY`), so cross-model metric reuse must use model-specific names. Missing aliases will break metrics by name.

**Test signals:** `jq` and jevents build; metric parser tests for expressions using `ICACHE.MISSES` and `BACLEARS.ANY`; `perf list frontend` on Grand Ridge mapping.
