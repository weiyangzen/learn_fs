<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/retired.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/retired.json

## Purpose
Monaka retired-operation topic selecting standard retirement aliases. It covers software PMU increments, retired instructions, context-ID writes, retired branches, branch mispredictions, architecturally executed operations, and retired micro-operations.

## APIs, Types, and Functions
The file uses `ArchStdEvent` entries for `SW_INCR`, `INST_RETIRED`, `CID_WRITE_RETIRED`, `BR_RETIRED`, `BR_MIS_PRED_RETIRED`, `OP_RETIRED`, and `UOP_RETIRED`, each with local descriptions.

## Control Flow, State, and Persistence
Build-time standard alias resolution creates the Monaka event table. Runtime perf measurement is stateless beyond PMU counter values and perf sample records.

## Dependencies and Integration
Depends on `common-and-microarch.json` for standard retirement events. It integrates with cycle accounting, branch/speculation, and IPC calculations where retired instructions or operations serve as denominators.

## Risks and Test Signals
Risks include mixing instruction, operation, and micro-operation counts as if they were interchangeable, and context-ID/write events being privileged or workload-specific. Test signals are successful alias resolution, `perf stat` on simple loops, branch-prediction microbenchmarks increasing branch retired counters, and expected IPC/op-per-cycle relationships against `CPU_CYCLES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/retired.json -->
