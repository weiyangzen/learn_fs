<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/tlb.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/tlb.json

## Purpose
Monaka TLB topic table. It includes standard L1/L2 instruction and data TLB access/refill/walk events plus implementation-defined page-size split counters for 4K, 64K, 2M, 32M, 512M, 1G, and 16G pages, walk pressure per cycle, walk steps, and block/page/large/small result classes.

## APIs, Types, and Functions
The file mixes `ArchStdEvent` aliases (`L1I_TLB_REFILL`, `L1D_TLB_REFILL`, `L1D_TLB`, `L1I_TLB`, `L2D_TLB_REFILL`, `L2D_TLB`, `DTLB_WALK`, `ITLB_WALK`, and walk-derived aliases) with direct Monaka `EventName`/`EventCode` records such as `L1I_TLB_4K`, `L1D_TLB_REFILL_2M`, `L2I_TLB_1G`, and `L2D_TLB_REFILL_16G`.

## Control Flow, State, and Persistence
Build-time generation resolves standard events and preserves the direct page-size event encodings. Runtime perf programs counters by alias for Monaka cores. The JSON is static and stores no measured state.

## Dependencies and Integration
Depends on ARM64 standard TLB events and Monaka-specific page-size encodings. It integrates with frontend/backend stall aliases, cache events, and memory access events to diagnose translation overhead and page-size effects.

## Risks and Test Signals
Risks include page-size counters not matching OS page mappings due to huge-page split/merge behavior, walk-derived aliases overlapping, and unsupported page-size encodings on firmware revisions. Test signals are successful generation, workloads pinned to 4K versus huge pages, ITLB pressure from large code footprints, DTLB pressure from random access, and stall correlation with `STALL_FRONTEND_TLB` and `STALL_BACKEND_TLB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/tlb.json -->
