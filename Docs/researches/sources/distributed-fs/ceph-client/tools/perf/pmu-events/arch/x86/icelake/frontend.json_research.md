# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/frontend.json

## Purpose

This file is the Ice Lake client frontend-event catalog for Linux `perf`. It contains 39 core PMU event records used to diagnose instruction fetch, decode, decoded-stream-buffer delivery, MITE delivery, microcode sequencer delivery, instruction-cache/tag stalls, and frontend-retired latency buckets. The x86 mapfile selects this `icelake` directory for `GenuineIntel-6-7[DE]` model matches, so these aliases become the frontend part of Ice Lake perf event tables.

## Important APIs, Types, And Data

The file is data, not executable code. Its API is the perf PMU JSON event schema consumed by `tools/perf/pmu-events/jevents.py`: `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `MSRIndex`, `MSRValue`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Representative event families are `BACLEARS`, `DECODE`, `DSB2MITE_SWITCHES`, `FRONTEND_RETIRED`, `ICACHE_16B`, `ICACHE_64B`, `ICACHE_DATA`, `ICACHE_TAG`, `IDQ`, and `IDQ_UOPS_NOT_DELIVERED`.

Several entries have special programming fields. `FRONTEND_RETIRED.*` events share `EventCode` `0xc6`/`UMask` `0x1` and distinguish DSB, ITLB, L1I, L2, STLB, and latency-threshold behaviors through `MSRIndex` `0x3F7` and different `MSRValue` encodings. `DSB2MITE_SWITCHES.COUNT` and `IDQ.MS_SWITCHES` use edge detection, while cycle-qualified IDQ and uop-delivery events use `CounterMask` values to count cycles meeting a delivery threshold rather than simple occurrences.

## Control Flow

Build-time control starts in the perf PMU event build rules, which invoke `pmu-events/jevents.py` over the x86 architecture tree. `jevents.py` loads this JSON array, normalizes each object into a generated event record, lowercases aliases, translates `EventCode`, `UMask`, `CounterMask`, `EdgeDetect`, `MSRIndex`, `MSRValue`, and sample period fields into perf event strings, and emits compact C tables in generated `pmu-events.c`.

Runtime perf commands do not parse this JSON. `perf list` displays generated aliases and descriptions, while `perf stat -e`/`perf record -e` resolve frontend event names through the compiled table and program the CPU PMU with the generated config and MSR filter fields.

## State And Persistence Behavior

The JSON persists static hardware-event metadata in source control. Mutable state is external: hardware counters, PEBS/frontend filters, and perf file descriptors exist only while perf is running. The default `SampleAfterValue` and frontend MSR filter values persist into generated aliases and affect sampling/programming defaults, but no counter samples or derived state are stored in this file.

## Dependencies And Integration Points

This file integrates with `arch/x86/mapfile.csv`, `pmu-events/Build`, `pmu-events/jevents.py`, generated `pmu-events.c`, `pmu-events.h`, `builtin-list.c`, `builtin-stat.c`, and metric expressions in `icl-metrics.json` that reference frontend events such as `IDQ_UOPS_NOT_DELIVERED.CORE`, `IDQ.DSB_UOPS`, `IDQ.MITE_UOPS`, `DSB2MITE_SWITCHES.PENALTY_CYCLES`, `ICACHE_DATA.STALLS`, and `FRONTEND_RETIRED.*`. It also supports the user-facing top-down frontend-bound, fetch-latency, fetch-bandwidth, DSB, MITE, and microcode-sequencer metrics.

## Risks And Edge Cases

The highest-risk fields are the `MSRIndex`/`MSRValue` encodings for `FRONTEND_RETIRED.*`; a bad value can silently select the wrong latency or miss qualifier while still producing counts. `CounterMask` and `EdgeDetect` fields change event meaning from counts to threshold cycles or transitions. Frontend events often share selectors, so duplicate or near-duplicate aliases rely on the full generated configuration being preserved. Metrics that subtract or divide frontend subcategories can become misleading if any raw event is unavailable, multiplexed heavily, or programmed on the wrong Ice Lake model.

## Test Signals

Useful checks include `jq empty frontend.json`, `jevents.py` generation for x86 Ice Lake, `perf test pmu-events`, and `perf list` checks for aliases such as `frontend_retired.latency_ge_64`, `idq.dsb_uops`, and `idq_uops_not_delivered.core`. Runtime signals include frontend-stressing workloads, instruction-cache pressure tests, and metric expansion tests for top-down frontend categories. Generated output should preserve MSR filters for all `FRONTEND_RETIRED` records and edge/cmask fields for switch and delivery-cycle events.
