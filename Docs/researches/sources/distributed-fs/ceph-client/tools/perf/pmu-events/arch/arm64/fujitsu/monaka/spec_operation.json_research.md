<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/spec_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/spec_operation.json

## Purpose
Monaka speculative and architecturally executed operation topic. It covers branch prediction, instruction and operation speculation, exclusive loads/stores, loads/stores, data processing, ASIMD/VFP/crypto, PC writes, branch forms, barriers, predicate/inter-element/inter-register operations, DC ZVA, addressing modes, micro-op split, integer arithmetic, and non-floating-point operation classes.

## APIs, Types, and Functions
Most records are `ArchStdEvent` aliases. Direct Monaka events include `PRD_SPEC`, `IEL_SPEC`, `IREG_SPEC`, `BC_LD_SPEC`, `DCZVA_SPEC`, `EFFECTIVE_INST_SPEC`, `PRE_INDEX_SPEC`, `POST_INDEX_SPEC`, and `UOP_SPLIT`. Standard aliases include `BR_MIS_PRED`, `BR_PRED`, `INST_SPEC`, `OP_SPEC`, `LD_SPEC`, `ST_SPEC`, `LDST_SPEC`, `DP_SPEC`, `CRYPTO_SPEC`, and barrier events.

## Control Flow, State, and Persistence
`jevents.py` resolves standard aliases and emits direct event encodings for the Monaka PMU table. Runtime perf counter programming is driven by the selected aliases; no file-level state exists.

## Dependencies and Integration
Depends on ARM64 common event definitions and Monaka-specific operation counters. It integrates with retired, cycle, pipeline, memory, SVE, and FP operation topics to distinguish executed, speculated, and retired work.

## Risks and Test Signals
Risks include confusing speculative operation counts with retired instruction counts, aggregate events overlapping subfamilies, and architecture references in descriptions requiring ARMv9 interpretation. Test signals are generated table success, branch-mispredict and barrier microbenchmarks, load/store addressing-mode tests, integer multiply/divide loops, and sanity checks that `EFFECTIVE_INST_SPEC` excludes MOVPRFX as described.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/spec_operation.json -->
