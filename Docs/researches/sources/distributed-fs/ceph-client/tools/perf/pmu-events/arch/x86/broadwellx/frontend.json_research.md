# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/frontend.json

## Purpose

`frontend.json` defines 28 BroadwellX frontend PMU events. It covers branch-address clears, DSB-to-MITE switch penalties, instruction-cache hits/misses/stalls, IDQ delivery paths, microcode sequencer delivery, and frontend undersupply cycles.

## Important APIs, types, and schema

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `Invert`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. `jevents.py` converts `CounterMask` to `cmask=`, `EdgeDetect` to `edge=`, `Invert` to `inv=`, and `SampleAfterValue` to `period=` in the generated event string.

Important families include `BACLEARS.ANY`, `DSB2MITE_SWITCHES.PENALTY_CYCLES`, `ICACHE.HIT`, `ICACHE.MISSES`, `ICACHE.IFDATA_STALL`, 17 `IDQ.*` events, and 6 `IDQ_UOPS_NOT_DELIVERED.*` events. Several IDQ events distinguish all cycles with any uops, cycles with four uops, MITE delivery, DSB delivery, LSD delivery, and microcode sequencer delivery.

## Control flow and integration

The build assigns these records to the `frontend` topic and emits them into the BroadwellX core event table. `bdx-metrics.json` uses them in frontend Top-down formulas such as `tma_frontend_bound`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_dsb`, `tma_mite`, `tma_dsb_switches`, `tma_ms_switches`, `tma_icache_misses`, `tma_unknown_branches`, and DSB coverage diagnostics. Runtime perf users can also request these aliases directly to inspect instruction delivery behavior.

## State and persistence behavior

This is static event metadata. Persistent state is the generated alias table; runtime state is the PMU configuration derived from fields such as `cmask`, `edge`, and `inv`. Events with small sample periods, such as branch clears, can produce different sampling overhead characteristics from high-period counting events.

## Dependencies

Dependencies include BroadwellX frontend PMU definitions, the `jevents.py` event-field mapping, and metric expressions in `bdx-metrics.json`. The file also depends on other pipeline and branch events not in this work item for complete Top-down frontend formulas.

## Risks

Frontend events are easy to misread because many count cycles meeting a delivery condition rather than delivered uops. Incorrect `CounterMask`, `Invert`, or `EdgeDetect` values would change cycle classification while still producing syntactically valid JSON. DSB/MITE/LSD metrics combine multiple IDQ events; if any one alias changes, higher-level percentages become invalid. Public descriptions include detailed microarchitectural caveats that should be preserved because short descriptions alone can hide what is actually counted.

## Test signals

Validation should include JSON parsing, generated alias checks for `idq_uops_not_delivered.core`, `idq.all_dsb_cycles_4_uops`, `icache.misses`, and `dsb2mite_switches.penalty_cycles`, and metric expansion for `tma_frontend_bound`, `tma_fetch_latency`, `tma_dsb`, and `tma_mite`. A runtime smoke test can compare instruction-cache stress and tight-loop workloads to ensure frontend miss and DSB-related counters move plausibly.
