# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/other.json

## Purpose

`other.json` defines 4 BroadwellX core PMU events that do not fit the larger topic files: privilege-level cycle accounting and split/uncacheable lock duration. These events support operating-system overhead and lock-contention investigations.

## Important APIs, types, and schema

Entries use the standard event schema: `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. The three `CPL_CYCLES.*` events use event code `0x5C` with different umasks and, for `CPL_CYCLES.RING0_TRANS`, edge detection plus `cmask=1`. `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION` uses event code `0x63` and tracks cycles where L1/L2 are locked due to uncacheable or split lock behavior.

## Control flow and integration

The build assigns these records to the `other` topic and emits them into the BroadwellX core event table. The kernel/OS metrics in `bdx-metrics.json` use related privilege-cycle events such as kernel CPI/utilization formulas, while lock latency Top-down metrics rely on lock and memory events across this file and `cache.json`.

## State and persistence behavior

This file is static metadata. Its persistent effect is generated alias rows in `pmu-events.c`; runtime behavior is normal PMU counter programming with `edge` and `cmask` applied where present.

## Dependencies

Dependencies include BroadwellX core PMU support for CPL cycle and lock-cycle events, perf's event-field mapping, and higher-level metrics that interpret privileged cycles or lock latency.

## Risks

Privilege-level cycle events can be confused with process/kernel filtering because they count architectural ring state, while perf event modifiers such as `:k` and `:u` filter at a different layer. The split-lock event identifies expensive lock behavior but cannot by itself identify the offending address or instruction. Incorrect edge/cmask encoding on `RING0_TRANS` would change it from transition counting to duration-like counting.

## Test signals

Validation should include JSON parsing, generated aliases for `cpl_cycles.ring0`, `cpl_cycles.ring0_trans`, and `lock_cycles.split_lock_uc_lock_duration`, plus runtime smoke checks under syscall-heavy and lock-heavy workloads. Metric checks should verify OS/kernel utilization formulas that combine privileged-cycle aliases expand successfully.
