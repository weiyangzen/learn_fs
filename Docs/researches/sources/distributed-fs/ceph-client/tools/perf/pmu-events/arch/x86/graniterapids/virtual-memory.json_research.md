# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/virtual-memory.json

## Purpose
This JSON file defines 20 Intel Granite Rapids core PMU events for virtual-memory translation behavior in perf. The events cover DTLB load misses, DTLB store misses, and ITLB misses, including second-level TLB hits, completed page walks by page size, active page-walk cycles, and pending page-walk counts. The source was read as a complete 185-line JSON array.

## Important APIs, Types, and Functions
All rows have `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, and `SampleAfterValue`; entries for active or pending page walks include `CounterMask: "1"`. `Counter` is `0,1,2,3`, and `SampleAfterValue` is consistently `100003`. There are 20 unique event names and three event codes: `0x11` for `ITLB_MISSES.*`, `0x12` for `DTLB_LOAD_MISSES.*`, and `0x13` for `DTLB_STORE_MISSES.*`.

Important aliases include `*.STLB_HIT`, `*.WALK_ACTIVE`, `*.WALK_COMPLETED`, page-size-specific `*.WALK_COMPLETED_1G`, `*.WALK_COMPLETED_2M_4M`, `*.WALK_COMPLETED_4K`, and `*.WALK_PENDING`. `WALK_ACTIVE` and `WALK_PENDING` share unit mask `0x10` within their respective families but differ by counter mask semantics and descriptions, so the full row metadata is required to preserve meaning.

## Control Flow, State, and Persistence
The file is declarative. Build-time flow is `jevents.py` parsing and generated table emission. Runtime flow is perf alias lookup, event scheduling on core programmable counters, and sampling/counting based on the encoded event selector. Unlike the Granite Rapids uncore files, these events are core PMU events and can be used with task, CPU, or system-wide perf modes subject to normal PMU scheduling.

Static state is the alias-to-event-code mapping plus sample-after values and counter masks. `CounterMask: "1"` changes cycle-style interpretations for active/pending page-walk events. The file persists only as generated perf metadata; runtime virtual-memory behavior remains workload and address-space dependent.

## Dependencies and Integration Points
Dependencies include perf's JSON schema, Granite Rapids core PMU definitions, `jevents.py`, and kernel core PMU support. The file integrates with `perf list`, `perf stat`, and potentially `perf record` sampling through the `SampleAfterValue` defaults. It is a source of low-level signals for TLB miss metrics, page-size tuning, huge-page analysis, instruction-fetch pressure, and page-walk overhead investigation.

The event names are shared in style with earlier Intel x86 generations, so external tooling may reference familiar aliases. Maintaining exact names helps scripts compare virtual-memory behavior across CPU models, but semantics must still be checked per generation.

## Risks and Test Signals
Risks include duplicate event-code/unit-mask combinations that depend on counter-mask semantics, stale sample-after defaults, and confusion between completed walks, active cycles, and pending walk occupancy. Page-size-specific aliases are not interchangeable with the aggregate `WALK_COMPLETED` alias, whose unit mask aggregates multiple page sizes. ITLB lacks a 1G page-specific completed event in this file while DTLB load/store include one, which downstream scripts should not assume is a typo without hardware documentation.

Test signals include JSON validation, generated perf table checks, `perf list` visibility for DTLB and ITLB aliases, and workload smoke tests using random memory access, huge pages, and instruction-cache/code-footprint stress. Plausibility checks should show TLB walk events increase with sparse memory access and decrease when huge pages reduce page-walk pressure.
