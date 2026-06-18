<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/hwpf.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/hwpf.json

## Purpose
Monaka hardware-prefetch topic table. It distinguishes L1D, L2, L3, and L1I prefetch requests by stream, stride, target, other, and next-line classes.

## APIs, Types, and Functions
All records are direct Monaka event definitions with `EventName`, `EventCode`, and `BriefDescription`. Aliases include `L1HWPF_STREAM_PF`, `L1HWPF_STRIDE_PF`, `L1HWPF_PFTGT_PF`, `L2HWPF_STREAM_PF`, `L2HWPF_STRIDE_PF`, `L2HWPF_OTHER`, `L3HWPF_STREAM_PF`, `L3HWPF_STRIDE_PF`, `L3HWPF_OTHER`, and `L1IHWPF_NEXTLINE_PF`.

## Control Flow, State, and Persistence
The JSON is compiled into perf alias tables at build time. Runtime counter state is owned by the PMU during each perf session; the file is only persistent alias metadata.

## Dependencies and Integration
Depends on Monaka prefetch event encodings and integrates with L1/L2/L3 cache access/refill files to evaluate prefetch accuracy, coverage, and possible pollution. It is also useful with pipeline stall counters when prefetcher activity correlates with memory latency.

## Risks and Test Signals
Risks include confusing request counts with useful prefetches, overlapping hardware and software prefetch activity in downstream counters, and vendor-specific semantics for target/other classes. Test signals are successful alias generation, streaming and stride microbenchmarks increasing the expected classes, and cache refill reductions or hit changes that correlate with prefetch request volume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/hwpf.json -->
