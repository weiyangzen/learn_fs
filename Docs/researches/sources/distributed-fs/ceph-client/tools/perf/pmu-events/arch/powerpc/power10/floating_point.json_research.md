# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/floating_point.json

## Purpose
This 13-entry POWER10 floating-point topic file defines completed floating-point operation counters. It distinguishes total FLOPs, 1/2/4/8-FLOP instructions, FMA and non-FMA, scalar and vector, single precision, math and non-math, and double/quad precision events.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. `PM_FLOP_CMPL` at `0x100F4` is the broad count; `PM_DPP_FLOP_CMPL` at `0x4D05C` covers double-precision or quad-precision instruction completion.

## Control Flow And Integration
These rows are ingested with other POWER10 PMU JSON files and emitted into the generated model table. Runtime integration is direct perf alias use for FLOP accounting and potential metric formulas that derive compute intensity.

## State, Dependencies, Risks, And Tests
The file is static. Dependencies are POWER10 FP/VSU PMU semantics and correct interpretation of multi-FLOP instruction accounting. Risks include users summing overlapping events, event-code transcription errors, and descriptions that do not fully explain vector-lane scaling. Test signals include JSON validity, `perf list PM_FLOP_CMPL`, and numeric sanity checks on FP-heavy microbenchmarks.
