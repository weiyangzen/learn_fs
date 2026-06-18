# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/pipeline.json

## Purpose
This JSON file is the Nehalem EP pipeline PMU event table consumed by perf's `pmu-events` generator. It declares 109 core pipeline aliases for arithmetic execution, branch decode/execute/retire, clocks, instruction decode queue behavior, loop stream detector behavior, machine clears, renamer/resource stalls, SIMD uop retirement, and uop decode/issue/execute/retire accounting. The file is byte-identical to the Nehalem EX `pipeline.json`, so its architectural meaning is shared while its source path keeps it selectable for the `nehalemep` CPU-map entry.

## Important APIs, Types, And Fields
The data is an array of event objects, not executable code. The API surface is the perf PMU event schema: `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`, plus optional `PEBS`, `AnyThread`, `EdgeDetect`, `Invert`, and `CounterMask`. Fixed-counter aliases such as `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF` use strings like `Fixed counter 1`, `Fixed counter 2`, and `Fixed counter 3` in `Counter` instead of `EventCode`/`UMask`. Programmable forms such as `CPU_CLK_UNHALTED.THREAD_P` and `CPU_CLK_UNHALTED.REF_P` use event `0x3C`.

## Control Flow
There is no local function control flow. Build-time flow is declarative: `tools/perf/pmu-events/jevents.py` reads the JSON, validates object fields, emits generated `pmu-events.c`, and `Makefile.perf` links the generated object into `libpmu-events.a`. Runtime perf list/record/stat paths then resolve an alias such as `UOPS_RETIRED.ANY` to the event encoding and constraints declared here.

## State And Persistence
The file persists hardware event metadata only. It does not mutate state, but it determines generated static tables shipped in the perf binary. Sampling defaults are mostly `SampleAfterValue: 2000000`. Precise events are marked with `PEBS`, including retired branches, retired instructions, retired SSE uops, and retired uops. Stall cycle aliases rely on `CounterMask`/`Invert`, for example total-cycle style events and no-uop-issued cycle counts.

## Dependencies And Integration Points
The table depends on x86 Nehalem EP PMU semantics and on the x86 `mapfile.csv` selecting the `nehalemep` directory for matching CPUs. It integrates with perf's alias lookup, generated event printing, and tests around generated `pmu-events.c`. Counter constraints matter: several events are available on `0,1,2,3`, while fixed counter aliases bypass generic counters. `AnyThread` appears on selected core-wide issue/execute cycle events, so schedulers and users must account for cross-thread counting semantics.

## Risks
The main risk is silent semantic drift: a wrong `UMask`, `CounterMask`, `Invert`, or fixed-counter string builds cleanly but produces incorrect measurements. Precise `PEBS` values must match kernel support expectations. Because this file duplicates the EX pipeline table, any intentional EP/EX divergence would be hidden unless both paths are reviewed. The spelling in descriptions is not functional, but event names and encodings are parser-sensitive.

## Test Signals
Useful signals are `jq empty`/schema validation, `make -C tools/perf JEVENTS_ARCH=x86` or equivalent generation of `pmu-events.c`, `perf test` cases for generated PMU events, and `perf list` on a Nehalem EP mapping to confirm aliases appear. Spot-check fixed aliases, PEBS aliases, and counter-mask/invert stall aliases because they exercise nontrivial schema fields.
