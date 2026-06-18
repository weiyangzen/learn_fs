# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/frontend.json

## Purpose

This file defines 78 POWER8 raw events for branch/front-end behavior, instruction dispatch and completion, instruction-cache reload source attribution, instruction-side page table entry sourcing, IERAT/ITLB/ISLB misses, pump prediction for instruction fetch, concurrent thread run instructions, and transactional-memory instruction accounting.

## APIs, types, and schema

Entries use `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`. Representative events include `PM_BR_CMPL`, `PM_BR_MPRED_CMPL`, `PM_IC_DEMAND_CYC`, `PM_IERAT_RELOAD_*`, `PM_INST_CMPL`, `PM_INST_DISP`, `PM_INST_FROM_*`, `PM_IPTEG_FROM_*`, `PM_ISLB_MISS`, `PM_ITLB_MISS`, `PM_L1_ICACHE_MISS`, `PM_L1_ICACHE_RELOADED_ALL`, `PM_THRD_CONC_RUN_INST`, `PM_TM_TRANS_RUN_INST`, and `PM_TM_TX_PASS_RUN_INST`.

## Control flow and integration

Perf build generation compiles these front-end events into PMU tables. Runtime users can select individual events or use them in metrics that analyze branch prediction, instruction sourcing, and translation. The instruction sourcing taxonomy mirrors the POWER8 data-cache source taxonomy but applies to instruction fetches and instruction-side PTE loads.

## State and persistence

The file has no mutable state. Event names, event codes, and descriptions persist into generated perf metadata. Because this file covers many front-end concepts, it is a major source for `perf list` output on POWER8.

## Dependencies

Dependencies include POWER8 front-end, branch, instruction cache, ERAT/TLB/SLB, pump prediction, and transactional-memory PMU semantics. Integration is through `jevents.py`, generated `pmu-events.c`, perf list/stat, and any scripts or metrics referencing these event names.

## Risks

The event taxonomy is broad and includes topology-specific sourcing, transaction state, and translation behavior; users can misinterpret overlapping categories. Some descriptions mention older POWER behavior or wording quirks, so hardware documentation remains necessary. Event-code errors can break branch-miss and instruction-cache investigations. Transactional-memory counters may be unavailable or uninteresting on configurations that do not exercise TM.

## Test signals

Use JSON validation, uniqueness checks, generated PMU builds, and runtime `perf list` checks. Hardware smoke tests should cover branch counters, `PM_L1_ICACHE_MISS`, `PM_INST_FROM_L2/L3/LMEM/RMEM/DMEM`, and translation misses such as `PM_ITLB_MISS` or `PM_ISLB_MISS`.
