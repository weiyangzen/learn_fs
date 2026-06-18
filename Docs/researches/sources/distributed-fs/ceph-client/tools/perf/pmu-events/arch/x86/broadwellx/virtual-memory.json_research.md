# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/virtual-memory.json

## Purpose

This file is the BroadwellX core PMU event table for virtual-memory and TLB behavior in Linux `perf`. It contains 38 event records and intentionally omits `Unit`, so `jevents.py` maps them to `default_core` rather than an uncore PMU. The aliases cover DTLB load misses, DTLB store misses, ITLB misses, EPT walk cycles, ITLB flushes, page-walker load sources, and TLB flushes.

The file is declarative input to the perf PMU-events generator. It supplies public aliases and sampling defaults for memory-translation analysis, including page-walk cause/completion/duration by access type and page size.

## Schema And Public API

Common fields are `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and sometimes `PublicDescription`. The file also uses `Errata` extensively. Twenty-five records cite errata: most cite `BDM69`, and some page-walker load records cite `BDM69, BDM98`. There is no `PerPkg` because these are core PMU events, not package uncore events.

Important families include load-side, store-side, and instruction-side TLB miss aliases; STLB hits split by page size; page walks caused and completed by page size; page-walk duration; `EPT.WALK_CYCLES`; `ITLB.ITLB_FLUSH`; `PAGE_WALKER_LOADS.*`; and `TLB_FLUSH.*`.

## Control Flow And Integration

During perf build, `jevents.py` parses this JSON and turns each object into generated core-PMU aliases. `EventName` is lowercased, `EventCode` and `UMask` become event terms, `SampleAfterValue` becomes `period=<value>`, descriptions are embedded, and `Errata` text is appended to descriptions as specification-update notes.

At runtime, the BroadwellX CPU map selects this table for family/model `GenuineIntel-6-4F`. Since `Unit` is absent, PMU matching uses the default core PMU marker. Commands such as `perf list`, `perf stat -e dtlb_load_misses.walk_completed`, and `perf record -e itlb_misses.walk_duration` resolve through generated aliases to model-specific raw core events.

## State And Persistence

The file has no mutable state. Its persistent effect is the generated alias table and default sampling periods compiled into perf. Runtime counter readings and samples are transient hardware state. The public alias names, errata notes, and default periods are stable until the JSON changes and perf is regenerated.

Because many aliases share an event code and differ only by `UMask`, the state users observe depends heavily on correct mask selection. Page-size-specific aliases are particularly sensitive to mask correctness.

## Dependencies, Risks, And Test Signals

The file depends on BroadwellX core PMU support, perf's JSON schema and generator, the BroadwellX mapfile, and kernel support for programming the listed model-specific event selectors. Correct interpretation depends on BroadwellX TLB hierarchy, page-walk hardware, STLB behavior, EPT support for virtualization, page sizes in use, and errata documented by Intel specification updates.

Errata preservation is the main documentation risk. `jevents.py` appends errata strings to generated descriptions, so removing `Errata` fields would silently remove important correctness caveats from `perf list`. Mask-driven families are another risk: a typo can produce a plausible alias that measures the wrong page-walk condition. Useful checks are `jq empty`, `jq 'length'` returning 38, generator output preserving errata and default-core routing, and runtime tests for `DTLB_LOAD_MISSES.WALK_COMPLETED_4K`, `DTLB_STORE_MISSES.WALK_DURATION`, `ITLB_MISSES.STLB_HIT`, `EPT.WALK_CYCLES`, `PAGE_WALKER_LOADS.DTLB_MEMORY`, and `TLB_FLUSH.STLB_ANY`.
