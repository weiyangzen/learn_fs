# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/virtual-memory.json

## Purpose

This file defines 65 Arrow Lake virtual-memory and TLB-related core PMU events. It covers DTLB load and store misses, ITLB misses, page-walk completions by page size, walk pending/active cycles, page-walker memory-source loads, load-head DTLB retirement signals, load blocks, and TLB flushes.

## Important APIs, Types, And Data

Records use the same perf event JSON schema as the pipeline file: `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `Unit`, `BriefDescription`, and `PublicDescription`. Units include `cpu_core`, `cpu_atom`, and `cpu_lowpower`, reflecting Arrow Lake hybrid PMU coverage. Repeated logical names such as `DTLB_LOAD_MISSES.WALK_COMPLETED`, `DTLB_STORE_MISSES.STLB_HIT`, and `ITLB_MISSES.WALK_PENDING` encode per-unit or per-generation variants.

## Control Flow

At generation time, `jevents.py` lowercases event names, converts event selectors and masks into perf config strings, preserves periods from `SampleAfterValue`, and emits separate generated tables by PMU unit. At runtime, perf resolves aliases against the detected core, atom, or low-power PMU and programs the selected TLB/page-walk counter.

## State And Persistence Behavior

The JSON persists event metadata and descriptions, not TLB state. Hardware and kernel PMU file descriptors produce per-run counts. Sample periods persist into generated aliases as default period hints. Repeated names rely on generated table PMU separation to avoid duplicate conflicts.

## Dependencies And Integration Points

This file integrates with Arrow Lake x86 model selection, `jevents.py`, generated PMU tables, `perf list`, `perf stat`, and workflows that diagnose translation overhead, huge-page behavior, instruction fetch misses, page walks, and TLB shootdowns. It depends on kernel PMU names matching `cpu_core`, `cpu_atom`, and `cpu_lowpower` mappings.

## Risks And Edge Cases

Hybrid event differences are the highest risk: same event names can have different event codes, masks, or descriptions across PMU units. Page-size-specific events are easy to misinterpret when huge pages are disabled or mixed. Counter masks on walk-pending events change counts from occurrences to cycles above a threshold. Missing or wrong public descriptions can obscure whether the event counts starts, completions, active cycles, or memory-source loads.

## Test Signals

Validate JSON syntax, generate PMU tables, and check representative aliases for DTLB load/store miss walks, ITLB walks, page-walker loads, and TLB flushes. Runtime signals include synthetic pointer-chasing workloads, huge-page versus 4K-page comparisons, instruction-cache/TLB stress tests, and duplicate-name checks across Arrow Lake PMU units.
