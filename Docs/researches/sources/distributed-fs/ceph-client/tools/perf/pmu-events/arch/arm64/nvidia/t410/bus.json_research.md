<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/bus.json

## Purpose
NVIDIA T410 bus and CHI activity topic. It exposes generic bus access/cycle/read/write/request/retry aliases plus T410-specific L2 CHI channel busy counters.

## APIs, Types, and Functions
The file uses standard `ArchStdEvent` names for `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`, `BUS_REQUEST_REQ`, and `BUS_REQUEST_RETRY`, and direct `EventCode` records `L2_CHI_CBUSY0` through `L2_CHI_CBUSY3`.

## Control Flow, State, and Persistence
Build-time generation resolves standard bus aliases and stores direct CHI event codes. Runtime perf sessions program the selected aliases on T410 core PMUs. The JSON itself is immutable metadata.

## Dependencies and Integration
Depends on ARM64 standard bus events, T410 CHI event encodings, and CPUID mapfile selection. It integrates with cache and memory metrics, especially `bus_bandwidth` and backend memory-bound calculations.

## Risks and Test Signals
Risks include CHI channel busy counters being difficult to aggregate, standard bus events not mapping cleanly to fabric bandwidth, and retry events indicating contention without identifying source. Test signals include alias generation, memory bandwidth tests increasing read/write access counts, contention tests increasing retries or CHI busy counts, and metric formulas producing plausible bandwidth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/bus.json -->
