# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/other.json

## Purpose

`other.json` defines 4 Ivy Bridge miscellaneous core PMU events that do not fit the larger topic files. It covers cycles by privilege level and cycles where L1D/L2 are locked due to uncacheable or split-lock behavior.

## Schema And API Surface

Entries use the standard event fields `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `CounterMask`, `EdgeDetect`, and `SampleAfterValue`. The aliases are `CPL_CYCLES.RING0`, `CPL_CYCLES.RING0_TRANS`, `CPL_CYCLES.RING123`, and `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`.

## Control Flow And Integration

The file is parsed with the Ivy Bridge PMU event set and generated into perf alias tables. Runtime users can count kernel/user privilege-level cycles or lock-induced cycles. These events can support OS-noise analysis, privilege attribution, and lock-contention diagnosis, and may be referenced by broader metrics or manual investigations.

## State And Persistence

The file persists event encodings and modifiers. `CPL_CYCLES.RING0_TRANS` uses edge-detection style semantics to count transitions/intervals rather than raw cycles, so its meaning differs from the other cycle aliases. Runtime state is the PMU counter values collected by perf.

## Dependencies

Dependencies include Ivy Bridge PMU support for CPL cycle and lock cycle events, plus perf support for edge-detect and counter-mask modifiers. It integrates with generated event tables and user-facing perf list/stat paths.

## Risks

Privilege-level events can be misread if perf's user/kernel filters are also applied. Edge-detect semantics on `RING0_TRANS` must be preserved or transition counts become cycle counts. Split-lock and UC-lock cycles may be rare on normal workloads, so a zero result is not sufficient evidence of a broken event.

## Test Signals

Validate JSON and generation. Runtime checks can compare `CPL_CYCLES.RING0` and `CPL_CYCLES.RING123` under syscall-heavy and user-space CPU loops. Split-lock tests require a controlled workload that intentionally triggers split or uncacheable locks, with care because such workloads can have system-wide performance impact.
