<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/core-imp-def.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/core-imp-def.json

## Purpose
HiSilicon Hip08 core implementation-defined event table. It extends the ARM64 core PMU catalog with read/write cache and TLB splits, L1I prefetch counters, frontend fetch/issue bubbles, prefetch request/hit events, and execution or memory stall cycles.

## APIs, Types, and Functions
The JSON mixes standard-style and direct records with `EventName`, `EventCode`, `BriefDescription`, and `PublicDescription`. Important aliases include `L1D_CACHE_RD/WR`, `L1D_CACHE_REFILL_RD/WR`, `L1D_TLB_RD/WR`, `L2D_CACHE_RD/WR`, `L2D_CACHE_REFILL_RD/WR`, `L1I_CACHE_PRF`, `IQ_IS_EMPTY`, `IF_IS_STALL`, `FETCH_BUBBLE`, `PRF_REQ`, `HIT_ON_PRF`, `EXE_STALL_CYCLE`, and `MEM_STALL_*`.

## Control Flow, State, and Persistence
Perf build tooling reads this file when generating the Hip08 PMU event table selected by CPUID `0x00000000480fd010`. Runtime perf aliases are static descriptors for hardware counters; the JSON itself has no state.

## Dependencies and Integration
Depends on Hip08 event-code definitions and the ARM64 mapfile entry. It integrates with `metrics.json`, whose topdown formulas reference many of these implementation-defined events, and with uncore Hip08 DDRC/HHA/L3C files for socket-level diagnosis.

## Risks and Test Signals
Risks include metric expressions breaking if event names change, direct event encodings drifting from firmware, and frontend/memory stall aliases being nonexclusive. Test signals are JSON and `jevents.py` success, `perf list` showing Hip08 names, topdown metric evaluation, and workload tests for cache/TLB pressure, prefetch behavior, fetch stalls, and execution stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/core-imp-def.json -->
