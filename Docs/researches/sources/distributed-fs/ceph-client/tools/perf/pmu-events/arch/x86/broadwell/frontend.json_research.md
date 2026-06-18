# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/frontend.json

## Purpose
Broadwell frontend PMU event table for Linux `perf`. The file is a JSON array of 28 events describing branch resteers, DSB-to-MITE switch penalties, instruction cache activity, IDQ delivery sources, microcode sequencer delivery, and top-down frontend under-delivery.

These events feed frontend-bound and fetch-latency/fetch-bandwidth metrics in `bdw-metrics.json`, especially `tma_frontend_bound`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_dsb`, `tma_mite`, `tma_dsb_switches`, `tma_ms_switches`, `tma_icache_misses`, `tma_branch_resteers`, and DSB coverage helper metrics.

## Important APIs, Types, and Functions
The event object schema contains:

- `EventName`: aliases such as `BACLEARS.ANY`, `DSB2MITE_SWITCHES.PENALTY_CYCLES`, `ICACHE.HIT`, `IDQ.DSB_UOPS`, `IDQ.MITE_UOPS`, `IDQ.MS_UOPS`, `IDQ_UOPS_NOT_DELIVERED.CORE`, and thresholded `IDQ_UOPS_NOT_DELIVERED.CYCLES_*` variants.
- `EventCode`: key codes include `0xe6` for BACLEARS, `0xAB` for DSB-to-MITE switches, `0x80` for instruction cache, `0x79` for IDQ source/delivery events, and `0x9C` for not-delivered frontend slots.
- `UMask`: subevent mask selecting the frontend source or condition.
- `Counter`: all rows allow counters `0,1,2,3`.
- `CounterMask`: used for cycle/threshold forms, including IDQ delivery cycles, all-DSB/all-MITE 4-uop or any-uop cycles, MS switches, and not-delivered thresholds.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue`: user-facing descriptions and sampling metadata.

There are no functions. The main event families are `IDQ.*` delivery-source aliases, `IDQ_UOPS_NOT_DELIVERED.*` top-down frontend availability aliases, and `ICACHE.*` instruction-cache aliases.

## Control Flow
Perf parses the JSON into Broadwell event maps, then programs selected aliases into generic core counters at runtime. Metrics combine the raw counts into frontend categories. For example, `tma_frontend_bound` divides `IDQ_UOPS_NOT_DELIVERED.CORE` by top-down slots, `tma_fetch_latency` uses the zero-uop-delivered threshold event, `tma_dsb` and `tma_mite` compare any-uop cycles against 4-uop cycles for DSB/MITE paths, and `tma_icache_misses` uses `ICACHE.IFDATA_STALL`.

The event data distinguishes count events from cycle-qualified events. `IDQ.DSB_UOPS` counts delivered uops, while `IDQ.DSB_CYCLES` and `IDQ.ALL_DSB_CYCLES_*` count cycles meeting delivery conditions. This distinction is the central control signal for correct metric formulas.

## State and Persistence Behavior
The JSON is static architecture metadata. Runtime state is limited to PMU counter configuration and collected counts. No data is persisted back to the source file.

Frontend event values are sensitive to workload instruction layout, branch predictor state, DSB/uop-cache residency, legacy decode path use, microcode sequencer activity, and backend stalls. `IDQ_UOPS_NOT_DELIVERED.*` descriptions explicitly exclude cases where the backend stalls the frontend, so interpretation depends on pipeline state during the sampled interval.

## Dependencies and Integration Points
This file integrates with the Broadwell PMU-events generator and with `bdw-metrics.json` frontend and branch metrics. It also integrates with other event files: branch-mispredict metrics combine frontend resteer signals with branch retired/mispredict and machine-clear events from other tables; top-down frontend metrics combine these events with slot and clock helper metrics.

At user level, the aliases are exposed through `perf list`, `perf stat -e`, `perf record -e`, and `perf stat -M` when metric expressions reference them.

## Risks
Important risks include:

- Cmask interpretation: many frontend rows are cycle-qualified threshold events. Treating them as raw uop counts produces incorrect ratios.
- Similar IDQ aliases differ subtly: `IDQ.MITE_UOPS`, `IDQ.MITE_ALL_UOPS`, `IDQ.MITE_CYCLES`, and `IDQ.ALL_MITE_CYCLES_*` are not interchangeable.
- DSB/MITE descriptions note bypass and merge behavior; counts can include uops that bypass the IDQ, which can surprise users expecting only queued uops.
- `IDQ_UOPS_NOT_DELIVERED.*` depends on backend-not-stalled conditions. It is a top-down input, not a standalone proof that the frontend alone caused slowdown.
- `BACLEARS.ANY` is a broad front-end resteer signal and should be interpreted with branch mispredict and machine clear events.
- Architectural specificity matters: DSB, MITE, IDQ, and top-down slot semantics are Broadwell-era definitions and should not be copied to unrelated CPU generations.

## Test Signals
Validation signals include JSON parse success, generated PMU-event map tests, `perf list` presence for `IDQ_UOPS_NOT_DELIVERED.CORE`, `IDQ.DSB_UOPS`, `IDQ.MITE_UOPS`, `ICACHE.IFDATA_STALL`, and `DSB2MITE_SWITCHES.PENALTY_CYCLES`, plus runtime `perf stat` checks on representative frontend aliases. Metric validation should run `perf stat -M tma_frontend_bound,tma_fetch_latency,tma_fetch_bandwidth,tma_dsb,tma_mite,tma_icache_misses` and confirm all referenced aliases resolve. Targeted instruction-cache and branch-stress microbenchmarks can provide stronger behavioral signals.
