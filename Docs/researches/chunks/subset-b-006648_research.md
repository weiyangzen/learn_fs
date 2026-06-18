# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-interconnect.json lines 1-6280

## Scope

This chunk covers the first 6,280 lines of the Cascade Lake X uncore interconnect PMU event table used by `perf`. It starts at the opening JSON array and includes complete event records for all `IRP` and `M2M` entries present in this range, then begins the `M3UPI` section. The line boundary stops at the opening brace for `UNC_M3UPI_M2_BL_CREDITS_EMPTY.IIO5_NCB`, so this chunk is not independently parseable JSON; the adjacent chunk must supply the rest of that object and the remaining file.

The covered range contains 599 `EventName` records: 76 for `IRP`, 445 for `M2M`, and 78 for `M3UPI`. These are declarative perf PMU aliases, not executable Ceph or kernel logic.

## Purpose

The file provides Cascade Lake X model-specific aliases for Intel uncore interconnect performance counters. During the perf build, the PMU event tooling consumes this JSON with the other `tools/perf/pmu-events/arch/x86/cascadelakex` files and generates lookup tables that let users request symbolic events such as `UNC_I_COHERENT_OPS.RFO`, `UNC_M2M_DIRECTORY_LOOKUP.SNP`, or `UNC_M3UPI_HORZ_RING_AD_IN_USE.LEFT_EVEN` instead of raw event encodings.

The chunk describes three hardware-facing namespaces. `IRP` tracks inbound request pipeline behavior around coherent PCIe/device traffic, peer-to-peer transactions, snoop responses, and IRP queue pressure. `M2M` tracks mesh-to-memory/cache-and-memory-subsystem behavior, including directory lookups, memory-controller read/write traffic, ring use, queue occupancy, tracker pressure, credits, and stalls. The beginning of `M3UPI` mirrors many CMS credit and ring-use events for a UPI-facing mesh agent and starts the M2-to-M3UPI credit-empty family.

## Important Schema and Data Surface

Each event record follows the perf PMU event JSON schema. Common fields in this chunk are `EventName`, `BriefDescription`, `PublicDescription`, `Counter`, `EventCode`, `UMask`, `Unit`, `PerPkg`, and `Experimental`. `Deprecated` appears on six `M2M` aliases that point users toward replacement credit-cycle events.

`Unit` is the main integration selector. `IRP` events use counters `0,1`; `M2M` generally uses counters `0,1,2,3`; `M3UPI` uses counters `0,1,2` in the covered range. Every record in this range is package-scoped with `PerPkg: "1"`, so generated perf aliases are intended for uncore package PMUs rather than per-core PMUs.

`EventCode` and `UMask` encode the raw hardware selector. Event families are represented by repeated `EventCode` values with different `UMask` subselectors. Examples include `UNC_I_COHERENT_OPS.*` at event code `0x10`, M2M transgress credit selectors such as `UNC_M2M_AG0_AD_CRD_ACQUIRED.TGR0` through `.TGR5`, channel selectors such as `.CH0` through `.CH2`, and ring-direction selectors such as `.LEFT_EVEN`, `.LEFT_ODD`, `.RIGHT_EVEN`, and `.RIGHT_ODD`.

The `Experimental` flag is widespread, especially for lower-level queue, credit, and ring events. Consumers should treat these as hardware/debug-oriented events whose semantics may be less stable than high-level events. The deprecated aliases are `UNC_M2M_RPQ_CYCLES_NO_SPEC_CREDITS.CHN0..CHN2` and `UNC_M2M_WPQ_CYCLES_NO_REG_CREDITS.CHN0..CHN2`; their descriptions direct users to `UNC_M2M_RPQ_CYCLES_SPEC_CREDITS.*` and `UNC_M2M_WPQ_CYCLES_REG_CREDITS.*`.

## Important Event Families

`UNC_I_*` families cover IRP cache total occupancy, IRP clockticks, coherent operations, FAF queue inserts/occupancy/fullness, all inbound/outbound IRP inserts, miscellaneous fast/slow path events, peer-to-peer inserts/occupancy/transactions, snoop response classes, transaction classes, transmit-control queue inserts/occupancy/full cycles, credit stalls, and outbound data/request queue pressure. The descriptions distinguish transaction counters from occupancy counters that accumulate outstanding work per cycle.

`UNC_M2M_*` is the dominant part of this chunk. It includes CMS agent AD/BL credit acquisition and occupancy by transgress, M2M bypass ingress/egress counts, clockticks, direct-to-core and direct-to-UPI taken/not-taken/override events, directory hit/miss/lookup/update families, egress ordering and fast-asserted cycles, horizontal and vertical AD/AK/BL/IV ring-use events, IMC read/write classes, packet matching, persistent-memory read/write queue credit cycles, prefetch CAM pressure, ring bounces and sink starvation, receive/transmit queue inserts/occupancy/full/non-empty cycles, RxR/TxR bypass and starvation, tracker/write-tracker pressure, TxC AD/AK/BL credits and queue state, and WPQ/RPQ credit classes.

`UNC_M3UPI_*` begins near the end of the chunk. The covered records include CMS agent 0/1 AD and BL credit acquisition/occupancy by transgress, CHA AD credit-empty variants, clockticks, direct-to-core/direct-to-UPI sent counters, egress ordering, fast-asserted cycles, horizontal AD/AK/BL/IV ring-use variants, and the first M2 BL credit-empty aliases for IIO destinations. The `IIO5_NCB` record starts at the chunk boundary and is completed in the next chunk.

## Control Flow

There is no runtime control flow inside this JSON file. The operational flow is data-driven:

1. Perf's PMU event generation tooling reads the JSON array for the Cascade Lake X architecture directory.
2. Each object is normalized into generated C event tables, preserving the unit, event code, umask, counter constraints, descriptions, and flags.
3. At runtime, perf selects the Cascade Lake X table through the x86 model map and exposes matching aliases in `perf list`.
4. When a user requests one of these aliases, perf maps `Unit` to the corresponding uncore PMU namespace and programs the event selector from `EventCode`, `UMask`, and any additional user terms supported by the PMU driver.

Event grouping and scheduling are constrained by the `Counter` field. For example, many M2M aliases can only schedule on four M2M counters and M3UPI aliases on three M3UPI counters, so large groups may fail or be multiplexed.

## State and Persistence Behavior

The file has no mutable state, allocation, persistence layer, or side effects. Its persistent behavior is the source-controlled hardware event contract and the generated perf tables built from it.

Runtime counter state lives in the kernel uncore PMU drivers and hardware counters. The JSON distinguishes event classes that should be interpreted differently: transaction/insert events count occurrences, occupancy events accumulate outstanding entries over cycles, full/non-empty events count cycles in a queue state, and credit-empty/no-credit events count backpressure conditions. Derived metrics such as average occupancy, pressure, or latency must pair compatible numerator and denominator events, usually with clockticks or insert/allocation counters.

`PerPkg: "1"` means counts are package-level. Multi-socket systems need per-package interpretation, and tooling should avoid presenting these as per-core values.

## Dependencies and Integration Points

This chunk depends on the perf PMU events schema and the `tools/perf/pmu-events` generation pipeline, including the Cascade Lake X architecture directory and x86 model map. It also depends on generated perf event tables, parse-events alias lookup, `perf list`, and the kernel uncore PMU drivers that expose compatible `IRP`, `M2M`, and `M3UPI` PMU instances.

The hardware dependency is Intel Cascade Lake X uncore semantics. The aliases assume the documented meaning of IRP request queues, CMS/M2M transgress credits, directory states, memory channels, ring directions, IIO targets, UPI-facing mesh agents, and PMM queue credits. The JSON names and descriptions are user-facing, so spelling changes or stale hardware terminology propagate directly into perf output and any scripts or dashboards that match event names.

There is no direct Ceph integration in this file despite its location under the checked-out Ceph client source tree. It is inherited perf tooling data used when building or researching the embedded Linux perf sources.

## Risks and Edge Cases

The chunk boundary is an important reconciliation risk. Line 6280 opens a new object for `UNC_M3UPI_M2_BL_CREDITS_EMPTY.IIO5_NCB` but does not include its fields or closing brace. Any validator or merger must read chunks 2 and 3 before treating the full source as valid JSON.

The file mixes occurrence counters, occupancy counters, cycle counters, credit counters, and deprecated aliases. Summing unlike families or comparing raw occupancy counts directly to transaction counts can produce misleading performance conclusions.

Counter constraints are tight. `IRP` exposes only counters `0,1`, `M3UPI` uses `0,1,2`, and `M2M` uses `0,1,2,3`; groups with many aliases from the same unit can exceed hardware scheduling capacity.

The `Experimental` field appears on most records in this chunk. User tooling should avoid assuming these aliases are stable metrics across CPU generations, even where names resemble Skylake X or later server uncore files.

Deprecated records remain present for compatibility but should not be preferred in new metrics. Replacement descriptions are embedded only in `BriefDescription`, so automated tooling that ignores descriptions may continue to surface stale names.

Many event names encode topology-specific selectors such as channels, transgresses, ring side/direction, IIO targets, and packet classes. Counts can be zero or misleading if the selected hardware block is absent, disabled, mapped differently on a SKU, or not exercised by the workload.

## Test Signals

Static validation should confirm that the complete file, after all chunks are merged, is valid JSON and that every object has the required perf PMU fields for its alias type. A useful chunk-level check is that lines 1-6280 contain 599 event names split as 76 `IRP`, 445 `M2M`, and 78 `M3UPI` records, with six deprecated M2M aliases.

Build validation should run the perf PMU event generation path and ensure the generated Cascade Lake X tables include representative aliases from all covered units: `UNC_I_COHERENT_OPS.RFO`, `UNC_I_SNOOP_RESP.*`, `UNC_M2M_DIRECTORY_LOOKUP.*`, `UNC_M2M_IMC_READS.*`, `UNC_M2M_TRACKER_OCCUPANCY.*`, `UNC_M2M_HORZ_RING_AD_IN_USE.*`, `UNC_M3UPI_AG0_AD_CRD_ACQUIRED.TGR0`, and `UNC_M3UPI_M2_BL_CREDITS_EMPTY.IIO4_NCB`.

Runtime smoke tests on Cascade Lake X hardware should verify that `perf list` exposes the aliases under the expected uncore PMU units and that simple `perf stat` runs can program one event per unit without parse errors. Scheduling tests should intentionally request oversized groups from a single unit to confirm perf reports multiplexing or counter constraint failures as expected.

Semantic tests should pair occupancy with insert or clocktick events, exercise memory traffic for M2M IMC and tracker events, exercise PCIe/device traffic for IRP transaction and queue events, and generate inter-socket or UPI traffic where possible for M3UPI credit and ring-use events. Deprecated aliases should be checked for continued parseability while new tests prefer the replacement credit-cycle names.

## Cross-Chunk Notes

This is chunk 1 of 3 for `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-interconnect.json`. The final per-file report should merge this document with `subset-b-006649` and `subset-b-006650`, especially to complete the `M3UPI` section and validate the full JSON array.
