# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/cache.json

## Purpose

This file is the Bonnell cache-event catalog for perf. It contains 93 events covering L1D references and evictions, L2 address/data bus activity, L2 instruction fetch states, L2 load/store requests by MESI state, line fills and evictions, locks, request rejection, no-request cycles, and retired load cache-miss signals.

## Important APIs, Types, And Data

The file uses `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Unlike Arrow Lake records, these Bonnell core events generally omit `Unit`; absent unit maps through `jevents.py` to the default core PMU table. Event families include `L1D_CACHE`, `L2_DATA_RQSTS`, `L2_IFETCH`, `L2_LD`, `L2_LD_IFETCH`, `L2_LINES_IN`, `L2_LINES_OUT`, `L2_LOCK`, `L2_REJECT_BUSQ`, `L2_RQSTS`, `L2_ST`, and `MEM_LOAD_RETIRED`.

## Control Flow

The build-time flow reads the JSON array, creates `JsonEvent` objects, converts selectors and masks to generated perf event strings, and emits Bonnell entries selected by the `GenuineIntel-6-(1C|26|27|35|36)` mapfile row. Runtime perf resolves aliases from the generated table for Bonnell-family systems.

## State And Persistence Behavior

The source persists static event definitions for old Intel Atom/Bonnell systems. Runtime cache state and counters live in hardware. `SampleAfterValue` persists as default sampling periods in generated aliases, but perf users can override sampling and counting behavior.

## Dependencies And Integration Points

Dependencies include the x86 mapfile Bonnell row, `jevents.py`, generated PMU event tables, perf alias lookup, and tests that compare generated event fields. The cache events integrate with `perf list`, `perf stat`, and performance analysis of cache hierarchy behavior on Bonnell-class CPUs.

## Risks And Edge Cases

Many L2 families differ only by MESI mask or request type, so mask transposition is a realistic risk. Some event names encode `.SELF` or MESI state distinctions that users may mistake for system-wide counts. Absent `Unit` means accidental introduction of unit fields or duplicate names can alter table placement. Older hardware availability makes runtime validation harder.

## Test Signals

Use JSON validation and generated-table tests. Representative generated aliases should include L1D references, L2 MESI request variants, L2 line-in/out variants, lock events, and `MEM_LOAD_RETIRED` cache-miss entries. On Bonnell hardware, cache-stress microbenchmarks should move L1/L2 reference and miss counters in expected directions.
