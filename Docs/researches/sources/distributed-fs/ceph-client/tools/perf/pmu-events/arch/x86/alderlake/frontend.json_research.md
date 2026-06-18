# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/frontend.json

## Purpose

This 46-entry catalog describes Alder Lake frontend PMU events for branch-target clears, decode stalls, decoded-stream-buffer to MITE switches, frontend-retired latency and miss classifications, instruction-cache accesses and misses, instruction-cache tag/data stalls, IDQ delivery by source, IDQ bubbles, and uops-not-delivered cycles. It is primarily a support table for frontend-bound topdown analysis and lower-level frontend debugging in perf.

## Important APIs, Types, and Data

The file uses standard perf event fields plus `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue` on selected events. It has 43 `cpu_core` records and 3 `cpu_atom` records. `FRONTEND_RETIRED.*` records use MSR `0x3F7` with different values to classify DSB misses, ITLB misses, L1I/L2 misses, latency thresholds from 1 through 512 cycles, microcode-sequencer flows, STLB misses, and unknown branches. `IDQ_BUBBLES.CYCLES_FE_WAS_OK` and `IDQ_UOPS_NOT_DELIVERED.CYCLES_FE_WAS_OK` combine inversion and counter masks to isolate cycles where the frontend was not the limiting condition.

## Control Flow

Perf reads these descriptors during pmu-events table generation and later uses them when a user requests an alias or when a metric expression references a frontend event. Runtime control is driven by the PMU unit and any extra MSR programming. Frontend-retired classifications are especially dependent on the auxiliary MSR value; perf must program both the base event and the classification selector for the result to mean what the alias says.

## State and Persistence Behavior

The JSON persists event semantics, selector values, and sampling periods. Hardware counters hold transient counts per perf session. MSR selector fields are persistent catalog data but transient hardware programming state during measurement. Because many frontend metrics are ratios against slots, cycles, or retired events, name stability and field stability are important for metric reproducibility.

## Dependencies and Integration Points

The table integrates with perf's Alder Lake event alias generation, hybrid PMU selection, `perf list`, topdown frontend metrics, instruction-cache analysis, branch-resteer analysis, and microcode-sequencer diagnostics. It depends on kernel and hardware support for frontend retired classification through MSR `0x3F7`, event qualifiers like `EdgeDetect` and `Invert`, and counter-mask handling. It is tightly related to `pipeline.json` topdown slot events and to `metricgroups.json` frontend/TMA group names.

## Risks

MSR-backed events are vulnerable to selector drift: the JSON can remain syntactically valid while pointing at the wrong frontend class. Hybrid asymmetry is another risk because most entries are `cpu_core`; metrics must not assume atom coverage exists. Counter-mask and invert events can be misread as simple occurrence counts when they are cycle or threshold predicates. Frontend latency threshold events overlap conceptually, so formulas must avoid double-counting without documented hierarchy.

## Test Signals

Tests should include schema validation, generated table checks for MSR selectors, `perf list` alias presence, and targeted workloads that stress I-cache misses, ITLB misses, branch resteers, DSB/MITE transitions, and microcode-heavy instruction sequences. Metric validation should confirm frontend-bound formulas resolve all required aliases on `cpu_core` and either provide atom alternatives or mark the metric unavailable on atom PMUs.
