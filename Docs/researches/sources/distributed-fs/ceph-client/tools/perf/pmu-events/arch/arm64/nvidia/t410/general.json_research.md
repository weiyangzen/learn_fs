<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/general.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/general.json

## Purpose
NVIDIA T410 general event topic exposing core cycle, constant counter cycle, and CPU slot counters. These are central denominators for topdown metrics and IPC-style calculations.

## APIs, Types, and Functions
The records are `ArchStdEvent` aliases `CPU_CYCLES` and `CNT_CYCLES`, plus `CPU_SLOT` with direct T410 metadata. Fields include `ArchStdEvent`, `EventName`, `EventCode`, and `PublicDescription` depending on the record.

## Control Flow, State, and Persistence
Perf generation resolves standard aliases and emits the slot event into the T410 table. At runtime, metrics in `metrics.json` use these counters as denominators for slots, cycles, SMT/ST mode, and IPC calculations.

## Dependencies and Integration
Depends on ARM64 common cycle events, T410 slot event encoding, and mapfile selection. It integrates directly with nearly every T410 metric.

## Risks and Test Signals
Risks include slot semantics changing with SMT mode, users confusing `CNT_CYCLES` with core cycles, and divide-by-zero in metrics when counters are not scheduled together. Test signals are `perf stat` for the three aliases, metric evaluation for topdown groups, and frequency/SMT tests showing expected cycle and slot relationships.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/general.json -->
