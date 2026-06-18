# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-cache.json

Purpose: defines two Meteor Lake uncore cache events for HAC CBO table-of-requests allocation accounting: `UNC_HAC_CBO_TOR_ALLOCATION.ALL` and `UNC_HAC_CBO_TOR_ALLOCATION.DRD`. These expose all TOR allocations and coherent data-read allocations into the HAC CBO queue.

Important APIs/types/functions: static perf PMU JSON descriptors with `EventName`, `EventCode` `0x35`, `UMask` values `0x8` and `0x1`, `Counter` `0,1`, `Unit` `HAC_CBO`, `PerPkg` `1`, and `BriefDescription`. The schema is interpreted by `jevents.py`; there are no local functions.

Control flow: build tooling converts the two JSON rows into generated perf aliases. At runtime perf resolves the uncore event name, targets the `HAC_CBO` PMU, applies the counter constraint, and counts package-level uncore queue allocation activity while the perf session is active.

State and persistence: no source-level mutable state. Hardware counter state exists in uncore PMU registers and is package scoped because `PerPkg` is set. Counts are transient unless perf records them into its output.

Dependencies and integration points: depends on Meteor Lake uncore PMU naming, the HAC CBO hardware unit, and perf's generated PMU event tables. These cache events integrate with adjacent uncore interconnect and memory files to explain off-core traffic pressure.

Risks: the file is tiny, so any field typo has a large blast radius for this category. `PerPkg` must remain present so tooling and users do not interpret counts as per-core. Event names encode CBO/HAC terminology that must match kernel PMU names. The `DRD` event excludes prefetches according to its description, so using it as total read demand requires care.

Test signals: JSON validation, generated-table diff, `perf list` visibility for `UNC_HAC_CBO_TOR_ALLOCATION.*`, and hardware smoke tests on Meteor Lake uncore PMUs. Compare `ALL` versus `DRD` under memory-read workloads to catch swapped umasks.
