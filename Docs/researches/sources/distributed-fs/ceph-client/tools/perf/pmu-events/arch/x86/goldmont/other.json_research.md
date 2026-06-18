# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/other.json

## Purpose

`other.json` defines 5 Goldmont core PMU events that do not fit cleanly into the cache, front-end, floating-point, or memory files. It covers broad fetch stalls, ITLB-related fetch stalls, and hardware interrupt delivery or masking.

## Important APIs, Types, and Data Fields

Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Events are `FETCH_STALL.ALL`, `FETCH_STALL.ITLB_FILL_PENDING_CYCLES`, `HW_INTERRUPTS.MASKED`, `HW_INTERRUPTS.PENDING_AND_MASKED`, and `HW_INTERRUPTS.RECEIVED`. `FETCH_STALL.ALL` has no `UMask`; the more specific ITLB stall and interrupt rows use `UMask` values.

## Control Flow and Data Flow

Perf ingests the aliases and programs Goldmont core counters. Runtime data identifies cycles where fetch cannot provide bytes while the decoder queue can accept them, cycles where ITLB fill is the fetch-stall reason, cycles where interrupts are masked, cycles where pending interrupts remain masked, and counts of received hardware interrupts.

## State and Persistence Behavior

The file persists static PMU metadata only. Runtime interrupt and fetch-stall counts are per-core and interval-local. Interrupt counters are especially sensitive to OS scheduling, interrupt affinity, and kernel configuration.

## Dependencies and Integration Points

These definitions depend on Goldmont core PMU support and integrate with perf front-end stall analysis, ITLB/fetch diagnosis, interrupt-latency investigations, and OS/kernel performance studies. They complement `frontend.json` I-cache and branch-clear rows and `cache.json` I-cache-fill stall rows.

## Risks and Edge Cases

`FETCH_STALL.ITLB_FILL_PENDING_CYCLES` is explicitly not the same as page-walk cycles to retrieve an instruction translation, so it should not be substituted for ITLB page-walk events. `FETCH_STALL.ALL` includes multiple causes and needs more specific events for attribution. Hardware interrupt events are system-noise-sensitive and may reflect unrelated devices or kernel activity. `HW_INTERRUPTS.RECEIVED` uses a much smaller default sample period than the cycle events.

## Test Signals

Validation should include JSON parsing and perf list exposure. Instruction-footprint and ITLB-pressure workloads should increase fetch-stall rows. Interrupt-heavy workloads, controlled interrupt affinity, or timer tests should affect interrupt received/masked rows. Cross-checking `FETCH_STALL.ALL` against `FETCH_STALL.ITLB_FILL_PENDING_CYCLES` and cache/front-end stall events provides a useful consistency signal.
