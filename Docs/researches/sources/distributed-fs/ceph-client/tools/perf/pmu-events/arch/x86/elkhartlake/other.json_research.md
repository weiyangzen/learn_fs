<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/other.json

## Purpose
Collects 22 Elkhart Lake PMU events that do not fit the main cache, memory, frontend, pipeline, floating-point, or virtual-memory topic files. The file covers bus-lock behavior, deprecated C0 memory stall aliases, hardware interrupts, and additional offcore-response categories.

## Important APIs, Types, And Functions
Uses standard event fields plus `Deprecated`, `EdgeDetect`, `MSRIndex`, and `MSRValue`. `BUS_LOCK.*` entries share event `0x63`; `HW_INTERRUPTS.*` entries use event `0xcb`; `OCR.*` entries use offcore-response MSR filters. Two hardware interrupt entries use edge detection.

## Control Flow
At build time, `jevents.py` emits these objects into the Elkhart Lake generated event table. Runtime perf exposes compatibility aliases such as deprecated `BUS_LOCK.CYCLES_OTHER_BLOCK` and preferred aliases such as `BUS_LOCK.BLOCK_CYCLES`, `BUS_LOCK.LOCK_CYCLES`, `BUS_LOCK.SELF_LOCKS`, and `HW_INTERRUPTS.RECEIVED`.

## State And Persistence
No source-level mutable state. Generated aliases persist in perf's compiled tables. Runtime state includes PMU counters and, for `OCR.*`, offcore filter MSR values.

## Dependencies And Integration Points
Integrates with lock-contention analysis, interrupt-rate analysis, and memory-bound stall diagnosis. The deprecated `C0_STALLS.*` aliases point users toward `MEM_BOUND_STALLS.*` events in `cache.json`, so cross-file naming consistency matters.

## Risks And Edge Cases
Six entries are deprecated, so tooling should preserve them for compatibility while descriptions guide users to replacements. `BUS_LOCK.ALL` and `BUS_LOCK.SELF_LOCKS` have blank `UMask` fields; parser defaults must encode them correctly. Edge-detected interrupt counts can differ from level/cycle-style events and should not be mixed without understanding semantics.

## Test Signals
Validate JSON and generated output. Run `perf list BUS_LOCK` and `perf list HW_INTERRUPTS` on a matching table. Lock-heavy and interrupt-heavy workloads should produce plausible counts; deprecated aliases should still resolve without breaking scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/other.json -->
