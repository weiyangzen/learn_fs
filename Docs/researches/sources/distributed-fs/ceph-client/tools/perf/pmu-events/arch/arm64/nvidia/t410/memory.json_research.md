<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/memory.json

## Purpose
NVIDIA T410 memory topic selecting standard memory access, remote access, alignment latency, instruction fetch, and per-cycle access counters. It provides high-level load/store/fetch activity and latency anchors for metrics.

## APIs, Types, and Functions
All records are `ArchStdEvent` aliases with public descriptions. Names include `MEM_ACCESS`, `MEMORY_ERROR`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `LDST_ALIGN_LAT`, `LD_ALIGN_LAT`, `ST_ALIGN_LAT`, `INST_FETCH_PERCYC`, `MEM_ACCESS_RD_PERCYC`, and `INST_FETCH`.

## Control Flow, State, and Persistence
Build-time standard alias resolution includes these events in the T410 PMU table. Runtime perf sessions measure counters by alias; no file state exists.

## Dependencies and Integration
Depends on ARM64 common memory and latency event definitions. It integrates with T410 metrics for load/store percentages, load average latency, instruction fetch latency, remote access behavior, and memory-bound diagnosis.

## Risks and Test Signals
Risks include latency events counting accumulated latency rather than event occurrences, remote access visibility being topology-dependent, and memory errors being rare or privileged. Test signals are generation success, aligned versus unaligned access tests, load/store microbenchmarks, remote NUMA traffic where applicable, and metrics that pair per-cycle latency counters with matching access counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/memory.json -->
