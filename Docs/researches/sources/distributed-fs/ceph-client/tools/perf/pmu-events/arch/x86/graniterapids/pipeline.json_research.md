# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/pipeline.json

## Purpose

`pipeline.json` is the Granite Rapids core pipeline PMU topic file. It contains 125 event-definition objects covering execution, retirement, branch behavior, speculative recovery, top-down slots, stalls, vector instruction retirement, dispatch ports, uop issue/execution/retirement, and cycle activity. The file gives perf human-readable aliases for raw Intel core PMU encodings on Granite Rapids.

This is not executable source. Its purpose is to be compiled by perf's PMU event generator into alias metadata so users can select events by stable names instead of raw event selectors and masks.

## Important APIs, Types, And Event Fields

Each array element matches the perf PMU JSON event schema used by `jevents.py`'s `JsonEvent` model. Important fields in this file include:

- `EventName`: alias names grouped by prefix. The file has families such as `ARITH`, `ASSISTS`, `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `EXE_ACTIVITY`, `INST_RETIRED`, `INT_MISC`, `INT_VEC_RETIRED`, `LD_BLOCKS`, `LSD`, `MACHINE_CLEARS`, `RESOURCE_STALLS`, `RS`, `TOPDOWN`, `UOPS_DISPATCHED`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`.
- `EventCode` and `UMask`: raw event selector and mask. Many related aliases share an event code and differ by unit mask, for example `BR_INST_RETIRED.*` on `0xc4`, `BR_MISP_RETIRED.*` on `0xc5`, `CYCLE_ACTIVITY.*` on `0xa3`, `EXE_ACTIVITY.*` on `0xa6`, `UOPS_EXECUTED.*` on `0xb1`, and `UOPS_DISPATCHED.*` on `0xb2`.
- `Counter`: programmable counter constraints. Most events allow counters `0,1,2,3,4,5,6,7`, while some cycle activity and dispatch/offcore-style events are limited to subsets such as `0,1,2,3`.
- `CounterMask`, `Invert`, and `EdgeDetect`: event modifiers used for cycle threshold, inverted-cycle, and edge-counting semantics. Examples include `ARITH.DIV_ACTIVE`, `CPU_CLK_UNHALTED.PAUSE_INST`, `CYCLE_ACTIVITY.*`, `INT_MISC.CLEARS_COUNT`, `MACHINE_CLEARS.COUNT`, `RS.EMPTY_COUNT`, and several `UOPS_EXECUTED` and `UOPS_RETIRED` cycle events.
- `MSRIndex` and `MSRValue`: extra MSR filtering for records such as `INT_MISC.UNKNOWN_BRANCH_CYCLES` and `UOPS_RETIRED.MS`, both using MSR `0x3F7` with distinct values.
- `RetirementLatencyMin`, `RetirementLatencyMean`, and `RetirementLatencyMax`: PEBS retirement-latency metadata on branch misprediction cost events such as `BR_MISP_RETIRED.COND_TAKEN_COST`, `BR_MISP_RETIRED.INDIRECT_COST`, and `BR_MISP_RETIRED.RET_COST`.
- `SampleAfterValue`: default sample period. The file uses different defaults for high- and low-frequency events, such as larger values for clock/uop-cycle events and lower values for branch cost or clear events.

There are no `MetricGroup` fields in this file; metrics are defined elsewhere, while this file only defines raw event aliases.

## Control Flow

Build control flow starts in `tools/perf/pmu-events/Build`, which selects JSON and CSV inputs and invokes `pmu-events/jevents.py` unless `NO_JEVENTS=1` is set. `jevents.py` parses each JSON object, normalizes the event name, maps schema keys to perf config terms, and emits generated C tables. Field conversion includes `CounterMask` to `cmask=`, `EdgeDetect` to edge detection, `Invert` to inverted counting, `MSRIndex`/`MSRValue` to model-specific extra register programming, and `Unit` to PMU names when present. Because this file is core-only, its records do not use `Unit`; they bind to the core PMU table selected for Granite Rapids.

Runtime flow is CPU selection followed by alias lookup. `arch/x86/mapfile.csv` maps `GenuineIntel-6-A[DE]` to the `graniterapids` directory, so a Granite Rapids perf build can expose these event aliases through `perf list` and resolve user event names to raw PMU config at `perf stat` or `perf record` time.

## State And Persistence Behavior

The file has no mutable runtime state. It is persistent source metadata that becomes generated C data during the perf build. Any modification persists into the perf binary after regeneration and changes alias availability, descriptions, default sample periods, or raw event programming. Runtime event counts are read from hardware PMU counters; this JSON only determines how perf programs and names those counters.

## Dependencies And Integration Points

Primary dependencies are the Intel Granite Rapids PMU specification, the perf PMU JSON schema, `jevents.py`, `pmu-events/Build`, and the x86 mapfile entry for Granite Rapids. It integrates with top-down analysis through `TOPDOWN.*` slot events and with PEBS cost analysis through `BR_MISP_RETIRED.*_COST` retirement-latency records. It also interacts with perf's event scheduler through `Counter` constraints and with the MSR programming path for MSR-filtered aliases.

The event families are designed to complement sibling topic files. For example, cache miss cycle events in this file are core pipeline stall signals, while uncore cache request and occupancy events live in `uncore-cache.json`; assists specific to miscellaneous traps are split between `pipeline.json` and `other.json`.

## Risks And Edge Cases

The highest risk is incorrect hardware encoding. A wrong `UMask`, `CounterMask`, `Invert`, or `EdgeDetect` can produce plausible but wrong counts. Events that share the same `EventCode` are particularly sensitive because a one-bit mask error changes the semantic within the same family. PEBS branch cost events are also sensitive: their descriptions state that they fire on the instruction immediately following the mispredicted branch and use the PEBS `Retire_Latency` field, so consumers must not treat them as ordinary branch retired events without understanding the cost sampling semantics.

MSR-filtered events are another edge case. `INT_MISC.UNKNOWN_BRANCH_CYCLES` and `UOPS_RETIRED.MS` depend on MSR `0x3F7` programming; if the generator's MSR lookup or runtime support changes, these aliases may fail while ordinary event-code aliases still work. Counter constraints can affect grouping: events limited to counters `0,1,2,3` may fail to schedule in groups that would otherwise appear valid.

Some events intentionally use inverted cycle semantics (`Invert`) or edge counting (`EdgeDetect`). These are easy to regress in schema translation tests because the event name may still appear even when the generated config modifier is wrong.

## Test Signals

Baseline tests are JSON parsing and x86 `jevents.py` generation. Stronger checks include verifying generated aliases and encodings in `pmu-events.c`, running perf's PMU event/metric tests where available, and checking `perf list` on Granite Rapids for representative families: `br_inst_retired.*`, `br_misp_retired.*_cost`, `cycle_activity.*`, `topdown.*`, `uops_dispatched.port_*`, and `uops_retired.*`. Hardware smoke tests should try grouped scheduling of counter-constrained events and a PEBS-capable sampling command for a branch cost event to confirm retirement-latency metadata remains usable.
