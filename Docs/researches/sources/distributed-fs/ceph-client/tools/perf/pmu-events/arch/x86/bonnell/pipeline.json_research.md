# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/pipeline.json

## Purpose

This file defines 45 Bonnell pipeline events. It covers branch decode and retirement, branch prediction and misprediction types, unhalted clocks, divider and multiplier activity, dispatch blocking, retired instructions and uops, machine clears, reissue conditions, resource stalls, and store forwarding.

## Important APIs, Types, And Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `PEBS`, and `BriefDescription`. Families include `BOGUS_BR`, `BR_INST_DECODED`, `BR_INST_RETIRED`, `BR_INST_TYPE_RETIRED`, `BR_MISSP_TYPE_RETIRED`, `CPU_CLK_UNHALTED`, `CYCLES_DIV_BUSY`, `DISPATCH_BLOCKED`, `DIV`, `INST_RETIRED`, `MACHINE_CLEARS`, `MUL`, `REISSUE`, `RESOURCE_STALLS`, `STORE_FORWARDS`, and `UOPS_RETIRED`. `BR_INST_RETIRED.MISPRED` and `INST_RETIRED.ANY_P` are PEBS-capable.

## Control Flow

`jevents.py` converts the JSON records into generated aliases selected for Bonnell family/model rows. PEBS metadata updates descriptions for precise-capable events. Runtime perf resolves branch, clock, execution, and stall aliases from the generated table and programs the underlying PMU.

## State And Persistence Behavior

The file persists event definitions and default periods. Hardware pipeline state is sampled or counted only during perf runs. Precise-event capability is metadata; actual PEBS buffer behavior is managed outside the JSON by perf and the kernel.

## Dependencies And Integration Points

Integration points include x86 mapfile selection, `jevents.py`, generated PMU tables, perf list/stat/record, and test fixtures for generated event descriptors. These events support pipeline bottleneck and branch behavior analysis on Bonnell CPUs.

## Risks And Edge Cases

Branch event suffixes distinguish predicted/not-taken/taken/mispredicted/type-specific forms; mask mistakes can invalidate derived rates. Some events count cycles, some instructions, and some uops, so combining them requires unit awareness. PEBS markings must match hardware support. Old Bonnell behavior may be hard to validate on modern systems.

## Test Signals

Validate JSON, generated event strings, and PEBS description handling. Branch-heavy, divider-heavy, multiplier-heavy, store-forwarding, and stall microbenchmarks should move representative aliases. `perf test pmu-events` should catch malformed generated entries or duplicate aliases.
