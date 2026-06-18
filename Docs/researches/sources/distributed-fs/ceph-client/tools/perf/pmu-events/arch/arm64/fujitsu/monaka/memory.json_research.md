<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/memory.json

## Purpose
Monaka memory-operation topic selecting generic load/store access aliases. It provides high-level counters for all memory access instructions and memory reads.

## APIs, Types, and Functions
The file contains two `ArchStdEvent` entries: `MEM_ACCESS` and `MEM_ACCESS_RD`, both with local descriptions tying them to `LDST_SPEC` and `LD_SPEC` semantics. There are no direct event codes or executable APIs.

## Control Flow, State, and Persistence
`jevents.py` resolves the aliases during perf build. Runtime perf sessions select these aliases after Monaka CPU matching; the JSON has no state.

## Dependencies and Integration
Depends on the ARM64 standard event catalog. It integrates with cache, TLB, and stall files as denominator events for load/store intensity, miss ratios, and backend-memory-bound interpretations.

## Risks and Test Signals
Risks include ambiguity between architecturally executed memory instructions and actual cache/fabric transactions, and lack of a write-only alias in this topic. Test signals are successful standard event resolution, load-only and store-only microbenchmarks showing expected behavior, and consistency with `LD_SPEC`, `ST_SPEC`, and `LDST_SPEC` from `spec_operation.json`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/memory.json -->
