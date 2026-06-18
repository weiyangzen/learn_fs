# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/pipeline.json

## Purpose

This file defines 130 Haswell core pipeline and execution events. It covers arithmetic divider uops, branch execution and retirement, mispredictions, unhalted clocks, cycle activity, instruction retirement, front/back-end stalls, load blocks, LSD behavior, machine clears, move elimination, resource stalls, reorder-buffer/LBR activity, reservation-station emptiness, uop issue/execution/retirement, and per-port dispatch/execution.

## Important APIs, Types, And Data

The records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and descriptions. There is no explicit `Unit`, so entries target the default Haswell core PMU. Event families include `BR_INST_EXEC` with 13 entries, `BR_INST_RETIRED` with 9, `BR_MISP_EXEC` with 9, `BR_MISP_RETIRED` with 4, `CPU_CLK_UNHALTED` and `CPU_CLK_THREAD_UNHALTED`, `CYCLE_ACTIVITY`, `INST_RETIRED`, `IDQ`-related metrics via sibling frontend events, `LD_BLOCKS`, `LSD`, `MACHINE_CLEARS`, `RESOURCE_STALLS`, `UOPS_DISPATCHED_PORT`, `UOPS_EXECUTED`, `UOPS_EXECUTED_PORT`, `UOPS_ISSUED`, and `UOPS_RETIRED`.

The file contains several aliases that share selectors but differ in intended interpretation, such as cycles versus events using counter masks in raw use. Haswell top-down metrics depend heavily on these names.

## Control Flow

At generation time, `jevents.py` loads the array, lowercases aliases, converts event selector and umask into perf event strings, attaches sample periods, and emits compact event table rows. Runtime perf resolves aliases to hardware counter programming. Metrics in `hsw-metrics.json` then combine these counters into top-down ratios such as retiring, frontend bound, bad speculation, backend bound, ports utilization, and branch resteers.

## State And Persistence Behavior

The JSON persists PMU alias definitions. Pipeline occupancy, uop flow, branch behavior, and stall cycles are measured by hardware per run. Sample periods are static defaults but perf users can override them.

## Dependencies And Integration Points

Integration points include Haswell CPU model mapping, `jevents.py`, generated PMU tables, perf stat/record/list flows, and Haswell top-down metrics. The file also depends on Intel event semantics for counter masks and any-thread variants, especially for SMT-aware formulas that distinguish thread and core-wide behavior.

## Risks And Edge Cases

Several events represent cycles, slots, uops, or occurrences with similar names; mixing them in formulas requires careful denominators. SMT and any-thread variants can double-count or undercount if used with the wrong topology assumptions. Port events are particularly sensitive to microarchitecture-specific execution-port mapping. Branch execution events and retired branch events measure different pipeline stages, so ratios across them can be misleading without context.

## Test Signals

Use `jq empty`, x86 event generation, `perf test pmu-events`, and alias checks for representative `UOPS_*`, `BR_*`, `CPU_CLK_*`, and `CYCLE_ACTIVITY.*` events. Runtime validation can use branch-heavy code, divider-heavy code, port-pressure microbenchmarks, and stalled memory workloads to confirm directional changes in the expected counters and top-down metrics.
