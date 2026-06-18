# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/memory.json

## Purpose
This 28-entry POWER10 memory file covers reload source transfer PMCs, DERAT/DTLB misses by page size, load completion, load L3-miss pending cycles, TLBIE snoop cycles, PTESYNC, LARX, and LSU store finish behavior. It complements datasource and frontend files with MMU and memory-ordering detail.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. The first event, `PM_XFER_FROM_SRC_PMC1`, references MMCR3-selected source fields and MMCR1 demand/prefetch behavior; the final event, `PM_SNOOP_TLBIE_WAIT_MMU_CYC`, counts LSU wait cycles for MMU invalidation.

## Control Flow And Integration
`jevents.py` emits the entries for POWER10 model tables. Runtime perf users combine these aliases with datasource, marked, and frontend events to diagnose translation misses, reload sources, and TLB invalidation stalls.

## State, Dependencies, Risks, And Tests
The file is static. Dependencies are POWER10 MMCR field semantics, page-size naming, and kernel PMU access to complex encodings. Risks include MMCR-dependent descriptions being overlooked, overlap with `frontend.json` TLB events, and wide event-code formatting errors. Test signals include JSON validation, generated C table checks, and targeted memory/TLB invalidation benchmarks.
