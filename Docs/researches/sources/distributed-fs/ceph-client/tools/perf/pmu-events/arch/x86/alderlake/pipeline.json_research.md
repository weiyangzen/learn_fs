# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/pipeline.json

## Purpose

This 208-entry file is the largest Alder Lake event catalog in the group. It defines pipeline, branch, clock, topdown, uop, reservation-station, machine-clear, serialization, arithmetic divider, load-block, and retirement events for perf. It supplies the raw event aliases behind many topdown and pipeline-efficiency metrics. The hybrid split is 121 `cpu_core` entries and 87 `cpu_atom` entries.

## Important APIs, Types, and Data

The file uses the standard perf event object fields plus `CounterMask`, `Deprecated`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue`. It has 22 deprecated entries, 36 counter-mask records, five edge-detect records, six inverted records, and two MSR-backed records. Major families include `ARITH`, `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `EXE_ACTIVITY`, `INST_RETIRED`, `INT_MISC`, `INT_VEC_RETIRED`, `LD_BLOCKS`, `LSD`, `MACHINE_CLEARS`, `RESOURCE_STALLS`, `RS`, `RS_EMPTY`, `SERIALIZATION`, `TOPDOWN`, `TOPDOWN_BAD_SPECULATION`, `TOPDOWN_BE_BOUND`, `TOPDOWN_FE_BOUND`, `TOPDOWN_RETIRING`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`.

Core-side topdown events include slot accounting such as `TOPDOWN.SLOTS`, `TOPDOWN.BACKEND_BOUND_SLOTS`, `TOPDOWN.BAD_SPEC_SLOTS`, `TOPDOWN.BR_MISPREDICT_SLOTS`, and `TOPDOWN.MEMORY_BOUND_SLOTS`. Atom-side topdown families expose issue-slot categories for frontend bound, backend bound, bad speculation, and retiring. Branch families include both generic and specific taken, conditional, indirect, call, return, and mispredict variants.

## Control Flow

The file is declarative. Perf parses it into alias descriptors, then routes event requests by PMU unit. The runtime measurement flow varies by qualifier: normal records program event select/umask, counter-mask records require threshold configuration, edge/invert records change predicate semantics, and MSR-backed records require selector MSR programming. Topdown metrics combine these aliases with formulas from metric files to compute hierarchy percentages.

## State and Persistence Behavior

The persistent state is the alias set, event encodings, deprecation markers, sampling periods, and topdown vocabulary. Runtime counter state is in PMU hardware and perf session data. Deprecated entries are retained for compatibility but should not drive new metric formulas. Clock events such as `CPU_CLK_UNHALTED.*` are foundational normalization inputs, so changes to their encodings have broad downstream impact.

## Dependencies and Integration Points

This catalog integrates with perf's generated pmu-events tables, `perf stat`, `perf record`, `perf list`, branch analysis, topdown metric formulas, hybrid PMU routing, and metric grouping. It depends on kernel support for Alder Lake fixed and programmable counters, topdown slot events, branch retired/mispred retired events, counter masks, edge detect, and invert semantics. It also provides dependencies for `metricgroups.json` topdown/TMA groups and the adjacent metric expression files.

## Risks

The highest risk is hybrid semantic mismatch: core and atom topdown events use different names and counting domains, so formulas must not blindly combine them. Deprecated branch and divider aliases can preserve old workflows but may produce inconsistent guidance compared with replacement names. Counter-mask/invert events are easy to misinterpret as raw counts. Topdown slot accounting is sensitive to SMT, halted cycles, fixed-counter availability, and multiplexing. Duplicate event names across units require perf to select the intended PMU.

## Test Signals

Tests should include JSON parsing, generated table compilation, `perf list` coverage, and encoding checks for representative branch, clock, topdown, uop, machine-clear, and divider events. Runtime smoke tests should include branch-heavy, branch-mispredict-heavy, divider-heavy, vector/integer pipeline, spin-wait, and backend-stall workloads. Metric tests should verify topdown level percentages are sane, sum constraints hold where expected, and unavailable unit-specific aliases are reported clearly.
