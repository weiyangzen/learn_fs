# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/pipeline.json

## Purpose
This JSON file is the Nehalem EX pipeline PMU event table. It declares 109 aliases for arithmetic units, branch prediction and branch retirement, unhalted clocks, instruction length decoder stalls, instruction queue writes, retired instruction classes, loop stream detector activity, machine clears, resource and renamer stalls, SSE retired uops, and uop decode/execute/issue/retire behavior. It is byte-identical to the Nehalem EP pipeline table.

## Important APIs, Types, And Fields
The file uses the perf event-object schema: `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`, plus `PEBS`, `AnyThread`, `EdgeDetect`, `Invert`, and `CounterMask` for selected events. Fixed aliases identify fixed counters directly. Programmable and fixed forms coexist, for example `INST_RETIRED.ANY` and `INST_RETIRED.ANY_P`, plus fixed and programmable unhalted clock aliases.

## Control Flow
There are no functions or branches in the file. The effective control flow is perf's data ingestion: `jevents.py` parses this model-directory JSON, emits generated C tables, the build links them into perf, and runtime alias lookup uses the generated row to program the PMU. Counter-mask and invert fields alter how the kernel programs event selection for stall-cycle style aliases.

## State And Persistence
The file is static metadata. It persists event encodings and default sampling periods, not measured values. `PEBS` appears on 20 precise retirement-related aliases. `CounterMask`, `Invert`, and `EdgeDetect` appear on derived cycle or edge-count forms such as total cycles, LSD inactive cycles, BACLEAR counts, and core stall cycles.

## Dependencies And Integration Points
It depends on Nehalem EX x86 PMU semantics and the model-selection mapfile. It integrates with generated `pmu-events.c`, `perf list`, event parser aliases, and kernel PMU programming. It also interacts conceptually with `frontend.json` and `floating-point.json`, which break out narrower decode and FP/SIMD event groups.

## Risks
Pipeline events are heavily used for top-down and bottleneck analysis, so incorrect encodings can distort optimization work. The nuanced fields are the riskiest: `Invert`/`CounterMask` define cycle predicates, `AnyThread` changes counting scope, and `PEBS` changes sampling behavior. Because EP and EX copies are identical, synchronization is expected; accidental divergence should be reviewed carefully.

## Test Signals
Run syntax validation and perf PMU event generation. Inspect generated entries for fixed-counter aliases, `PEBS` retired aliases, `AnyThread` stall aliases, and `CounterMask`/`Invert` cycle aliases. `perf list` should expose all 109 names for the Nehalem EX mapping.
