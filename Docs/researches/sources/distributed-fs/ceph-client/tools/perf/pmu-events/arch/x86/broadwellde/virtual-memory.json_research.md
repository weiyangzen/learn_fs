# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/virtual-memory.json

## Purpose

`virtual-memory.json` defines Broadwell-DE core PMU aliases for TLB misses, page walks, EPT walks, page-walker memory-source attribution, and TLB flushes. It is the model-specific event table behind symbolic events such as `DTLB_LOAD_MISSES.WALK_COMPLETED_4K`, `ITLB_MISSES.STLB_HIT`, `PAGE_WALKER_LOADS.DTLB_MEMORY`, and `TLB_FLUSH.STLB_ANY`.

The file contains 38 records. Unlike the uncore files in this subset, these are core PMU events and therefore do not carry a `Unit` or `PerPkg` field. Every record has an `EventCode`, `UMask`, `Counter`, `BriefDescription`, and `SampleAfterValue`; 25 records include `Errata: "BDM69"`, warning that the affected Broadwell-DE event semantics have documented errata.

## Important APIs, Types, and Data Shape

The JSON schema fields are consumed by `jevents.py` and compiled into generated `pmu-events.c` rows. Runtime consumers include `perf list`, `perf record`, `perf stat`, `perf report` metadata, and Python PMU event export. The `SampleAfterValue` field is important for sampling defaults: it gives perf a suggested period for sampled use of these core events.

Important families include:

- `DTLB_LOAD_MISSES.*`: load-side DTLB misses, STLB hits, page-walk causes, completed walks by page size, and walk duration.
- `DTLB_STORE_MISSES.*`: store-side equivalents for STLB hits and page walks.
- `ITLB_MISSES.*`: instruction-side miss, STLB-hit, completed-walk, page-size, and walk-duration events.
- `ITLB.ITLB_FLUSH`: instruction TLB flush counts.
- `EPT.WALK_CYCLES`: cycles spent in extended page table walks for virtualization.
- `PAGE_WALKER_LOADS.*`: page-walker loads sourced from L1, L2, L3, or memory, split for DTLB and ITLB where applicable.
- `TLB_FLUSH.DTLB_THREAD` and `TLB_FLUSH.STLB_ANY`: data-thread and shared-TLB flush events.

The repeated `EventCode` values form families selected by masks: `0x08` for DTLB load misses, `0x49` for DTLB store misses, `0x85` for ITLB misses, `0xBC` for page-walker loads, and `0xBD` for TLB flushes. Subevent masks distinguish STLB hit page size, page-walk completion page size, walk duration, or flush target.

## Control Flow

The file has no executable control flow. Its build/runtime flow is:

1. Broadwell-DE CPU model matching selects the `broadwellde` JSON directory.
2. `jevents.py` parses `virtual-memory.json` and emits core PMU event aliases into generated `pmu-events.c`.
3. Perf's PMU alias layer associates these events with the default core PMU for matching Broadwell-DE systems.
4. `perf list` exposes the aliases and descriptions; `perf stat` and `perf record` resolve alias names to raw event selector, mask, counter, and sampling-period metadata.
5. Downstream reports interpret samples or counts as core-level virtual-memory behavior.

Because these are core PMU events, they interact with ordinary per-thread/per-CPU perf targeting, multiplexing, counter constraints, and sample period behavior rather than the package-level uncore matching used by the other three files.

## State and Persistence Behavior

The JSON persists static event metadata. Generated build artifacts persist C representations until rebuild. Runtime state is in perf's alias tables and in programmed core PMU counters or sample streams. `SampleAfterValue` influences the default sampling threshold when users record these events, but the JSON itself does not store collected samples or counts.

Errata metadata is persistent descriptive state: consumers and reviewers should preserve `BDM69` tags because they signal that counts may need caveats or may be unsuitable for some derived metrics.

## Dependencies and Integration Points

The file depends on perf's PMU-event build, the Broadwell-DE x86 mapfile entry, core PMU event parsing, and the kernel's core perf event support. It integrates with TLB and virtual-memory profiling workflows: `perf stat` for aggregate miss/walk/flush counts, `perf record` for sampling high-volume miss events, `perf report` for attributing samples, and `perf list --json` for tooling that discovers event metadata.

It also connects to virtualization analysis through `EPT.WALK_CYCLES`, and to memory hierarchy analysis through page-walker source events. These aliases are often combined with CPU cycles, instructions, cache misses, and memory events to estimate TLB pressure, page-walk cost, huge-page effectiveness, and flush overhead.

## Risks and Edge Cases

The `BDM69` errata tag appears on most walk-causing and walk-completed DTLB/ITLB events. Removing or ignoring those tags can lead users to over-trust affected measurements. Several public descriptions appear copied between load/store/instruction families and contain wording mismatches, such as ITLB descriptions referring to store or DTLB misses; textual cleanup should be careful not to alter encodings unless verified against Intel's table.

Subevent masks are dense and similar across families. A wrong mask can turn a page-size-specific event into a broader or different count while still parsing correctly. The `WALK_COMPLETED` aggregate masks (`0xe`) overlap the individual page-size masks (`0x2`, `0x4`, `0x8`), so tests should check intentional aggregation instead of flagging it as duplicate encoding.

Sampling defaults differ: most events use `100003`, while STLB load hits and some walk events use `2000003`. Changes to `SampleAfterValue` alter record overhead and sample density. As core events, these aliases are also subject to multiplexing and counter availability; `Counter: "0,1,2,3"` permits four generic counters but does not guarantee simultaneous measurement with arbitrary other events.

## Test Signals

Useful validation includes JSON parsing, duplicate-name checks, required `EventCode`/`UMask`/`SampleAfterValue` checks, errata tag preservation, and generator rebuild. Runtime checks should include `perf list DTLB_LOAD_MISSES`, `perf list ITLB_MISSES`, and `perf stat` on representative aliases such as `DTLB_LOAD_MISSES.WALK_DURATION`, `DTLB_STORE_MISSES.STLB_HIT_4K`, `ITLB.ITLB_FLUSH`, `PAGE_WALKER_LOADS.DTLB_MEMORY`, and `TLB_FLUSH.STLB_ANY`. Sampling tests should confirm that `perf record -e <alias>` accepts the generated alias and uses a sane sample period.
