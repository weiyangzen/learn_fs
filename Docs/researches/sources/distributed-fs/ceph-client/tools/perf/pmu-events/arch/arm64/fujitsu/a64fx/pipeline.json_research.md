<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/pipeline.json

## Purpose
A64FX pipeline PMU topic table. It exposes frontend/backend stall aliases, execution pipeline valid-cycle counters, predicate population counters, L1/L1I/L2 pipeline valid and completion counters, tagged-address request counters, and gather/scatter flow counters for vector memory operations.

## APIs, Types, and Functions
The file is a JSON array of perf event records. Two entries use `ArchStdEvent` (`STALL_FRONTEND`, `STALL_BACKEND`) resolved from ARM64 architecture-standard tables; the rest define A64FX-specific `EventName`/`EventCode` values such as `EAGA_VAL`, `EXA_VAL`, `FLA_VAL`, `L1_PIPE0_COMP`, `L1_PIPE_COMP_GATHER_2FLOW`, and `L2_PIPE_COMP_ALL`.

## Control Flow, State, and Persistence
The table is parsed at perf build time into generated event descriptors. Runtime selection is by the A64FX CPUID mapfile entry, after which the aliases become static PMU event names. There is no runtime state in the JSON; all behavior comes from perf alias lookup and the hardware counters.

## Dependencies and Integration
Depends on standard ARM64 event resolution for the stall entries and A64FX hardware support for event codes in the 0x1A0, 0x240, 0x260, 0x2B0, and 0x330 ranges. It integrates with SVE and cache files when analyzing vector memory pipeline utilization and gather/scatter expansion.

## Risks and Test Signals
Risks include invalid `ArchStdEvent` references, architecture-standard events changing names, and misinterpreting predicate count semantics where full predicates are corrected to 16. Test signals are `jevents.py` resolution success, no duplicate alias conflicts, `perf stat` runs that show pipeline valid counts rising under scalar, SVE, gather, scatter, and L2 traffic workloads, and ratios that remain plausible against total cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/pipeline.json -->
