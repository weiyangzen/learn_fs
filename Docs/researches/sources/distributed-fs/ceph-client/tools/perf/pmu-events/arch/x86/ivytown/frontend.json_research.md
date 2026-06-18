# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/frontend.json

Purpose: Defines 30 Ivy Town frontend PMU aliases covering branch resteers, DSB-to-MITE switches, DSB fill pressure, instruction cache behavior, IDQ delivery paths, microcode sequencer delivery, and frontend under-delivery. These events feed topdown frontend-bound analysis.

Important APIs/types/functions: Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `Invert`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Families include `BACLEARS`, `DSB2MITE_SWITCHES`, `DSB_FILL`, `ICACHE`, `IDQ`, and `IDQ_UOPS_NOT_DELIVERED`. Several aliases use `CounterMask` to count cycles with a delivery threshold; `IDQ.MS_DSB_OCCUR` and `IDQ.MS_SWITCHES` use edge detection to count occurrences.

Control flow: Perf's generated table exposes these aliases for core PMU scheduling. Runtime lookup maps frontend event names to event select/unit mask/counter-mask combinations. `ivt-metrics.json` uses them for `tma_frontend_bound`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_dsb`, `tma_dsb_switches`, `tma_mite`, `tma_ms_switches`, `tma_icache_misses`, and microcode sequencer metrics.

State and persistence: Static metadata only. Runtime frontend delivery and stall state is in hardware counters and perf samples.

Dependencies/integration: Depends on Ivy Town frontend PMU semantics and perf handling of `CounterMask`, `Invert`, and `EdgeDetect`. It integrates with pipeline events such as `UOPS_ISSUED` and with metric expressions that normalize frontend events by thread or core clocks.

Risks: Many aliases share event code `0x79` with different unit masks and counter masks; small field errors silently change the delivery path being counted. Cycle-threshold aliases should not be interpreted as raw uop totals. Edge-detected occurrence events and duration events have different units despite similar names. Topdown metrics are sensitive to these aliases because frontend-bound formulas subtract or normalize by delivery capacity.

Test signals: Validate event fields and generated aliases, especially `CounterMask`, `EdgeDetect`, and `Invert`. Run metric-resolution tests for frontend topdown formulas. On hardware, compare DSB/MITE/ICACHE counters with microbenchmarks that fit in the decoded-uop cache versus instruction-cache-thrashing or branch-heavy workloads.
