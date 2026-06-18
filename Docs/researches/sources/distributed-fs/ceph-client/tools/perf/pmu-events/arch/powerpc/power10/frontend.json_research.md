# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/frontend.json

## Purpose
This 24-entry POWER10 frontend file covers TLB hits/misses by page size, branch completion and prediction, dispatch/issue cancellation, instruction availability, L1 load miss, instruction-from-L3-miss, and vector load/store completion events relevant to frontend and dispatch analysis.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. The first event, `PM_DTLB_HIT_2M`, notes radix translation and MMCR1 behavior; the last event, `PM_PRED_BR_NTKN_COND_DIR`, counts correctly predicted not-taken conditional branches.

## Control Flow And Integration
`jevents.py` emits these rows for POWER10 CPUs selected by mapfile PVR patterns. Runtime consumers use them directly for branch/frontend diagnosis and indirectly when metrics reference branch or instruction-source events.

## State, Dependencies, Risks, And Tests
Static metadata depends on POWER10 MMCR semantics and page-size-specific PMU definitions. Risks include page-size naming drift, overlapping frontend and memory/TLB topics, and descriptions whose conditional MMCR behavior is easy to miss. Test signals are generated alias checks and perf runs under branch-heavy, TLB-heavy, and instruction-cache pressure workloads.
