# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/pipeline.json

## Purpose

This JSON file is the Arrow Lake pipeline-event catalog for Linux `perf`. It contains 306 core PMU event records covering arithmetic divider activity, assists, backend stalls, branch retirement and misprediction, unhalted clocks, cycle activity, execution activity, retirement, integer/vector uops, load blocks, loop stream detector behavior, machine clears, memory stalls, top-down slots, dispatch, issue, execution, and retirement pipeline categories. The x86 mapfile binds the `arrowlake` model directory to `GenuineIntel-6-C[56]`, so these records are selected for Arrow Lake family/model matches during perf PMU table generation.

## Important APIs, Types, And Data

The file is data, not executable code. Its effective API is the perf PMU event JSON schema consumed by `tools/perf/pmu-events/jevents.py`. Important fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `Invert`, `SampleAfterValue`, `Unit`, `BriefDescription`, `PublicDescription`, `MSRIndex`, `MSRValue`, `Deprecated`, and `Errata`. `Unit` values split hybrid Arrow Lake events across `cpu_core`, `cpu_atom`, and `cpu_lowpower`; `jevents.py` converts those to PMU names used in generated event tables.

Major event families include `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `INST_RETIRED`, `LD_BLOCKS`, `MACHINE_CLEARS`, `TOPDOWN_*`, `UOPS_*`, `INT_MISC`, `INT_UOPS_EXECUTED`, and `INT_VEC_RETIRED`. Several logical names intentionally repeat with different event encodings or units, such as branch-retired, branch-mispredicted, top-down, clock, and divider events.

## Control Flow

At build time, `jevents.py` loads this array with `json.load(..., object_hook=JsonEvent)`. Each record is normalized into a `JsonEvent`: `EventName` is lowercased, `EventCode` becomes `event=...`, nonzero `UMask` becomes `umask=...`, `CounterMask` becomes `cmask=...`, `EdgeDetect` becomes `edge=...`, `Invert` becomes `inv=...`, and `SampleAfterValue` becomes `period=...`. `Unit` is translated into a PMU table key, then sorted generated `compact_pmu_event` entries are emitted into `pmu-events.c`.

At runtime, perf does not parse this JSON directly. Perf commands such as `perf list`, `perf stat -e`, and metric expansion read the compiled PMU event tables and match aliases against detected Arrow Lake core, atom, or low-power PMUs.

## State And Persistence Behavior

The JSON file persists architectural event metadata in source control. Runtime counter state is not stored here; perf opens hardware PMU file descriptors based on the generated event string. Deprecation and errata fields are persistent metadata that affect displayed descriptions and event quality warnings but do not create mutable program state.

## Dependencies And Integration Points

This file integrates with `arch/x86/mapfile.csv`, `jevents.py`, `pmu-events.h`, generated `pmu-events.c`, `tools/perf/util/pmu.c`, `builtin-list.c`, Python perf event listing, and PMU event tests. It also depends on Arrow Lake hardware event definitions matching Intel documentation and on hybrid PMU naming being compatible with the kernel-exposed PMU names.

## Risks And Edge Cases

Duplicate event names are valid only when separated by PMU or disambiguating fields; duplicates under the same generated PMU table can trigger `jevents.py` duplicate assertions. Hybrid unit mistakes can put a core-only event on atom PMUs or the reverse. Incorrect `CounterMask`, `EdgeDetect`, `Invert`, MSR fields, or periods silently changes perf measurement semantics. Deprecated entries such as `BR_INST_RETIRED.IND_CALL`, `LOAD_HIT_PREFETCH.HW_PF`, `MACHINE_CLEARS.SLOW`, and `TOPDOWN_FE_BOUND.ITLB` remain compatibility surfaces. Errata-tagged branch events, including ARL010 and ARL011 cases, need careful user-facing descriptions because the event can be architecturally present but not always trustworthy.

## Test Signals

Useful validation includes `jq empty` on the JSON, running `jevents.py` generation for x86 Arrow Lake, building `tools/perf`, `perf test pmu-events`, checking `perf list` for representative lowercased aliases, and validating generated event strings for branch, top-down, clock, and uop events on Arrow Lake-like PMU names. Regression tests should cover duplicate-name handling across `cpu_core`, `cpu_atom`, and `cpu_lowpower`.
