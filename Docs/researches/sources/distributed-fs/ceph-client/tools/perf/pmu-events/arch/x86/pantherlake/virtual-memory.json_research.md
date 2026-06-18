# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/virtual-memory.json

## Purpose

`virtual-memory.json` defines Panther Lake perf events for data and instruction translation behavior. It contains 34 event rows: 20 for `cpu_core` and 14 for `cpu_atom`. The catalog covers DTLB load misses, DTLB store misses, ITLB misses, second-level TLB hits, page-walk starts or completions, page-walk active cycles, page-walk pending occupancy, and a load-blocked-on-DTLB-miss signal.

## Important APIs, Types, and Data Fields

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, and optional `CounterMask`. Families are `DTLB_LOAD_MISSES`, `DTLB_STORE_MISSES`, `ITLB_MISSES`, and `LD_BLOCKS.DTLB_MISS`. The same logical event names appear with different encodings for `cpu_core` and `cpu_atom`; for example `DTLB_LOAD_MISSES.STLB_HIT` is present for both units. Core rows include page-size-specific completions for 4K, 2M/4M, and 1G where applicable, while atom rows include `MISS_CAUSED_WALK` and selected completion rows.

## Control Flow and Data Flow

Build-time flow is the standard perf PMU path: `jevents.py` parses the JSON, converts `Unit` to the PMU selector, and emits event-table metadata. Runtime flow starts when perf programs the requested alias on the relevant hybrid PMU. Translation hardware then increments counters when demand loads, stores, or instruction fetches miss first-level TLBs, hit the STLB, trigger page walks, or spend cycles with busy page miss handlers.

The event families form a diagnostic progression. `STLB_HIT` identifies first-level TLB misses that were resolved without a full walk. `WALK_COMPLETED*` counts completed page walks by access type and page size. `WALK_ACTIVE` and `WALK_PENDING` expose cycle/occupancy pressure rather than transaction counts. `LD_BLOCKS.DTLB_MISS` links translation misses to load blocking behavior.

## State and Persistence Behavior

The file persists static aliases and default sample periods only. Runtime TLB contents, page tables, and PMU counter values are external state. `CounterMask` on active-cycle rows is semantically important because it changes a raw event into a thresholded cycle condition. Hybrid `Unit` state is also important: atom rows and core rows cannot be merged by name without respecting their different encodings and available counters.

## Dependencies and Integration Points

This file depends on Panther Lake core and atom PMU support, perf's generated PMU tables, and kernel exposure of hybrid PMUs. It integrates with `perf stat`, `perf record`, virtual-memory tuning, huge-page validation, code-footprint analysis, and memory-latency investigation. It complements Panther Lake pipeline stall rows and cache/memory rows by separating address-translation cost from cache-hit and DRAM-latency cost.

## Risks and Edge Cases

The main risk is comparing unlike units: walk completions are event counts, while active and pending rows are cycle or occupancy style measurements. Page-size-specific rows must be interpreted in the context of actual mappings. Some event names are duplicated across `cpu_core` and `cpu_atom`; deduplication by `EventName` would lose the correct hardware encoding. Page walks can include faulting walks where descriptions say so, so counts are not always successful translations. Workload migration across hybrid cores can obscure per-unit attribution.

## Test Signals

Validation should parse the JSON, build generated tables, and expose aliases through `perf list` for Panther Lake hybrid PMUs. Random pointer-chasing should raise DTLB load walk counters. Store-heavy sparse workloads should raise store-side rows. Huge-page runs should shift 4K walk completions toward larger-page counters. Large code-footprint workloads should affect ITLB rows. A test should verify `WALK_ACTIVE` behaves like cycle pressure while `WALK_COMPLETED` behaves like transaction counts.
