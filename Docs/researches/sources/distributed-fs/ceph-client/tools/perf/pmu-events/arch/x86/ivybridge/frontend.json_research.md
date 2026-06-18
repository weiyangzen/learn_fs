# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/frontend.json

## Purpose

`frontend.json` defines 30 Ivy Bridge front-end events for branch resteers, instruction-cache activity, Decode Stream Buffer behavior, MITE delivery, microcode sequencer delivery, IDQ occupancy, and uops not delivered. It supplies the primary event aliases used to diagnose front-end bandwidth and latency limits.

## Schema And API Surface

Entries use `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `CounterMask`, `SampleAfterValue`, and for selected edge/cycle events `EdgeDetect` and `Invert`. Major families are `IDQ`, `IDQ_UOPS_NOT_DELIVERED`, `ICACHE`, `DSB2MITE_SWITCHES`, `DSB_FILL`, and `BACLEARS`. Representative aliases include `IDQ.DSB_UOPS`, `IDQ.MITE_UOPS`, `IDQ.MS_UOPS`, `IDQ.EMPTY`, `IDQ_UOPS_NOT_DELIVERED.CORE`, `ICACHE.IFETCH_STALL`, and `BACLEARS.ANY`.

## Control Flow And Integration

The generator emits aliases into the Ivy Bridge PMU table. Runtime perf opens these as core events and applies counter-mask, invert, or edge-detect modifiers where specified. `ivb-metrics.json` relies on this file for topdown front-end metrics including `tma_frontend_bound`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_dsb`, `tma_dsb_switches`, and `tma_icache_misses`.

## State And Persistence

The JSON persists event selection and modifier semantics. Some entries count cycles meeting delivery thresholds, while others count uops or events; this distinction is essential for metrics that divide by clock or slot denominators. Runtime state is per-core/thread PMU counter values.

## Dependencies

Dependencies include Ivy Bridge front-end PMU definitions, perf support for event modifiers, and metric formulas in `ivb-metrics.json`. It also interacts conceptually with branch and pipeline event files outside this work item because front-end topdown formulas use branch mispredict and machine clear signals.

## Risks

Counter masks and inversion flags are easy to get wrong and can invert a metric's meaning. IDQ, DSB, MITE, and MS aliases are tightly coupled to topdown formulas, so renames or semantic changes can break metrics. Some descriptions distinguish uop counts from cycles; mixing these in formulas can create plausible but wrong percentages.

## Test Signals

Validation includes JSON parsing, `jevents.py` generation, and metric parser checks. Runtime tests can compare instruction-cache miss workloads, branch-heavy workloads, and DSB-friendly loops. `perf stat -M` topdown front-end metrics should remain computable on Ivy Bridge without missing-event errors.
