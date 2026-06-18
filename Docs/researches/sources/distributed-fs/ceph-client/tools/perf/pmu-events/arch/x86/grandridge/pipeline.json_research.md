## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/pipeline.json

**Purpose:** Grand Ridge pipeline topic with 76 events. It covers arithmetic divide activity, retired and mispredicted branches, fixed and programmable cycle/instruction counters, load blocking, machine clears, miscellaneous retired events, serialization, topdown retiring/frontend/backend/bad-speculation categories, and retired/issued uops.

**Schema and important records:** Standard event records with `CounterMask` on selected threshold/active-cycle events and `Deprecated` on compatibility aliases (`BR_INST_RETIRED.IND_CALL`, `MACHINE_CLEARS.SLOW`, `TOPDOWN_FE_BOUND.ITLB`). Fixed-counter aliases include `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF_TSC`; programmable variants add `_P` names. Topdown families include `TOPDOWN_RETIRING.ALL_P`, `TOPDOWN_FE_BOUND.*`, `TOPDOWN_BE_BOUND.*`, and `TOPDOWN_BAD_SPECULATION.*`.

**Control flow and integration:** `jevents.py` converts this topic to `pmu_event` rows selected by the Grand Ridge mapfile entry. `grr-metrics.json` is tightly coupled to this file: topdown metrics divide topdown slot events by `6 * CPU_CLK_UNHALTED.CORE`, and many info metrics reference branch, load-block, machine-clear, serialization, and uop aliases here.

**State and persistence:** Static PMU metadata only. Fixed/generic counter programming, multiplexing, and samples are runtime perf/kernel state.

**Dependencies:** Depends on the Grand Ridge core PMU and `counter.json` declaring eight generic counters. Also depends on naming compatibility with metric formulas and frontend/cache/memory topic events.

**Risks:** This is a central dependency for metrics; a single rename or deprecation mishandling can break topdown analysis. Fixed versus programmable aliases must stay correct. Topdown denominator width (`6 * CPU_CLK_UNHALTED.CORE`) in metrics assumes slot semantics matching these events.

**Test signals:** JSON/build validation; metric parser tests for all Topdown groups; `perf stat -M TopdownL1` on Grand Ridge; direct `perf stat -e TOPDOWN_FE_BOUND.ALL_P,TOPDOWN_BE_BOUND.ALL_P,TOPDOWN_RETIRING.ALL_P,TOPDOWN_BAD_SPECULATION.ALL_P` smoke tests.
