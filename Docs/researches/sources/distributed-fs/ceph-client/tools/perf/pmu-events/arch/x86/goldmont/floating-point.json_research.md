# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/floating-point.json

## Purpose

`floating-point.json` defines 3 Goldmont core PMU events for floating-point divide pressure and floating-point assists. It lets perf distinguish cycles where the FP divide unit is busy, retired FP divide uops, and pipeline clears caused by FP assists such as denormal handling.

## Important APIs, Types, and Data Fields

The entries use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and optional `PEBS`. Events are `CYCLES_DIV_BUSY.FPDIV`, `UOPS_RETIRED.FPDIV`, and `MACHINE_CLEARS.FP_ASSIST`. `UOPS_RETIRED.FPDIV` is precise-capable with `PEBS: 2`; all rows can use counters `0,1,2,3`.

## Control Flow and Data Flow

Perf parses these rows into event aliases and programs Goldmont core counters. Runtime data distinguishes divider occupancy cycles from retired divide instructions and exceptional assist behavior. The assist row counts machine clears caused by FP operations that need microcode or pipeline replay to produce architecturally correct results.

## State and Persistence Behavior

The file stores only static metadata and default sampling periods. Runtime counts and PEBS records are session-local. The precise retired-uop row may persist richer sample records through perf output files, but not through this JSON.

## Dependencies and Integration Points

These events depend on Goldmont core PMU and PEBS support. They integrate with floating-point performance tuning, denormal/assist diagnosis, top-down pipeline-clear analysis, and perf record/stat workflows. They complement generic uop and machine-clear catalogs by focusing on FP-specific causes.

## Risks and Edge Cases

Divider-busy cycles and retired divide uops answer different questions; high busy cycles may indicate long-latency divides even if retired divide count is modest. FP assists are data-dependent and can be rare unless inputs trigger denormals or other assisted cases. PEBS availability for `UOPS_RETIRED.FPDIV` depends on kernel and hardware support.

## Test Signals

Validation should include JSON parsing and perf alias visibility. Microbenchmarks with repeated floating-point divides should increase divide busy cycles and retired divide uops. Denormal-heavy or assist-triggering workloads should move `MACHINE_CLEARS.FP_ASSIST`. PEBS tests should verify precise sampling for retired FP divides where supported.
