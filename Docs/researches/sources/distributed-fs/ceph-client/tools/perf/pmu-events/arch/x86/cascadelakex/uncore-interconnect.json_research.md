# Research: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-interconnect.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006648`: lines 1-6280, `Docs/researches/chunks/subset-b-006648_research.md`
- `subset-b-006649`: lines 6281-11953, `Docs/researches/chunks/subset-b-006649_research.md`
- `subset-b-006650`: lines 11954-13859, `Docs/researches/chunks/subset-b-006650_research.md`

## Chunk Research

### subset-b-006648: lines 1-6280

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

### subset-b-006649: lines 6281-11953

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-interconnect.json lines 6281-11953

## Scope

This chunk covers a large middle section of the Cascade Lake Xeon `uncore-interconnect.json` PMU event table. The selected lines describe Intel uncore interconnect events for the `M3UPI` unit: M3 mesh-to-UPI traffic, UPI peer credits, ring usage, ring starvation, receive-control arbitration, transmit-control queues, transmit/receive ring queues, and credit accounting.

The data is declarative JSON metadata consumed by Linux perf's PMU events tooling. It does not define executable functions, classes, or runtime control flow. Each object maps a human-readable perf event name to the low-level event encoding fields that perf later exposes through generated event tables.

The range begins at a complete object for `UNC_M3UPI_M2_BL_CREDITS_EMPTY.IIO5_NCB`. It ends on line 11953 in the middle of the next `UNC_M3UPI_VN0_CREDITS_USED.NCS` object, after `PerPkg` and before that object's remaining fields. The full source file remains valid JSON, but this chunk alone has a trailing partial event that the final merge lane must reconcile with the following chunk.

## Purpose

The purpose of this chunk is to define perf-visible hardware monitoring events for the Cascade Lake Xeon M3UPI uncore block. These events let perf users measure interconnect pressure and backpressure around UPI links and mesh/ring stops, including:

- Credit exhaustion when M3UPI cannot send to M2, UPI peers, or internal TxR paths.
- Ring occupancy, cycles non-empty, cycles full, bypass, NACK, inserts, and starvation on horizontal and vertical AD/AK/BL/IV rings.
- Receive-control arbitration behavior, including lost arbitration, no-credit conditions, packing misses, slot usage, generated flits, held messages, and collisions by virtual network and message class.
- Transmit-control flow-queue occupancy, inserts, cycles non-empty, bypass, and arbitration/speculative-arbitration outcomes.
- Per-package UPI prefetch spawning and VN0 credit-use accounting.

These records are important because uncore interconnect bottlenecks often appear as credit starvation, arbitration loss, or ring occupancy rather than as CPU-core PMU events. The table gives perf enough metadata to program the corresponding uncore PMU counters and present stable symbolic event names.

## Important Schema Fields and Event Families

The event objects in this range use the standard perf JSON PMU schema:

- `EventName`: symbolic name exposed to perf, such as `UNC_M3UPI_RxC_ARB_LOST_VN0.AD_REQ`.
- `EventCode`: hardware event selector, expressed as a hex string.
- `UMask`: unit mask selecting a subcondition or message class; most entries have one, but some base events do not.
- `BriefDescription`: short user-facing summary.
- `PublicDescription`: longer explanation where available. In this chunk, 483 of the 520 `EventName` records have one.
- `Counter`: allowed programmable counters, consistently `0,1,2` for complete events in this chunk.
- `Unit`: `M3UPI` for complete records in this range.
- `PerPkg`: `1`, marking package-scoped uncore events rather than per-core events.
- `Experimental`: present on almost all complete entries, indicating many of these events are not part of perf's most stable event surface.

The chunk contains 520 `EventName` lines. Because of the trailing partial object, only 519 `Unit` lines fall inside the requested range. The complete events are all `M3UPI`.

Major families covered here include:

- `UNC_M3UPI_M2_BL_CREDITS_EMPTY`: the tail of the M2 BL credit-empty group, covering `IIO5_NCB`, aggregate `NCS`, and selected `NCS_SEL`.
- `UNC_M3UPI_MULTI_SLOT_RCVD`: multi-slot flit receive accounting for AD, AK, and BL slots.
- `UNC_M3UPI_RING_BOUNCES_*`, `RING_SINK_STARVED_*`, and `RING_SRC_THRTL`: vertical/horizontal ring bounce and starvation conditions by AD/AK/BL/IV message ring.
- `UNC_M3UPI_RxC_*`: the largest group in this chunk, covering receive-control arbitration, no-credit states, no-AD-request states, occupancy, inserts, collisions, packing misses, VNA credit accounting, generated/sent/not-sent flits, SMI3 prefetch handling, and bypass/held conditions.
- `UNC_M3UPI_RxR_*`: receive-ring queue occupancy, inserts, bypass, busy-starved, credit-starved, and related queue pressure.
- `UNC_M3UPI_STALL_NO_TxR_*`: stalls caused by missing TxR horizontal or vertical credits, split by AD/BL, agent 0/1, and virtual network or message class.
- `UNC_M3UPI_TxC_*`: transmit-control AD/BL flow-queue metrics and arbitration/speculative-arbitration failure or success conditions.
- `UNC_M3UPI_TxR_*`: transmit-ring horizontal and vertical queue metrics, including occupancy, inserts, cycles non-empty/full, bypass, NACK, starved, and ADS-used variants.
- `UNC_M3UPI_UPI_PEER_*_CREDITS_EMPTY`: UPI peer AD/BL credit-empty states split across VNA, VN0, VN1, and AD/BL message classes.
- `UNC_M3UPI_VERT_RING_*_IN_USE`: vertical AD/AK/BL/IV ring-in-use cycle counts split by up/down and even/odd rings where applicable.
- `UNC_M3UPI_UPI_PREFETCH_SPAWN` and `UNC_M3UPI_VN0_CREDITS_USED`: prefetch generation and the start of VN0 credit-use accounting.

The common message-class suffixes are `AD_REQ`, `AD_SNP`, `AD_RSP`, `BL_RSP`, `BL_WB`, `BL_NCB`, and `BL_NCS`. The common virtual-network suffixes are `VN0`, `VN1`, and `VNA`. Ring direction and topology suffixes include `HORZ`, `VERT`, `UP`, `DN`, `EVEN`, and `ODD`; agent-specific variants use `AG0` and `AG1`.

## Control Flow

There is no local control flow in this JSON file. The effective flow is created by perf's PMU-event build and lookup pipeline:

1. The perf build scripts read architecture-specific JSON files under `tools/perf/pmu-events/arch/x86/`.
2. The JSON records are converted into generated C tables used by perf's event lookup code.
3. At runtime, a user names an event, or perf lists available events for a matching CPU model.
4. Perf resolves `EventName` to the table entry for the detected Cascade Lake Xeon model.
5. Perf programs the uncore PMU using `EventCode`, `UMask`, and counter/unit constraints.
6. The kernel/perf uncore PMU driver reads the package-level M3UPI counter values and reports them to the user.

Within this chunk, many records share an `EventCode` and differ only by `UMask`. For example, ring-in-use events use the same event selector for a ring type and use masks to select up/down/even/odd direction, while RxC arbitration families use a shared selector and masks for AD/BL message classes. This grouping means the logical control path is table-driven: perf does not branch on these names directly; it selects the encoded event programmed into the PMU.

## State and Persistence Behavior

The persistent state is the checked-in JSON metadata. The file does not mutate state, allocate memory, perform I/O, or persist runtime data. Its contents are transformed at build time into perf event tables, and those generated tables become the runtime source of truth for symbolic event lookup.

The event data is package-scoped through `PerPkg: "1"`. Counters are constrained to `0,1,2`, so users and tools must treat these as limited uncore resources. Combining many M3UPI events in one perf command can fail or multiplex if the uncore PMU cannot schedule all requested events on the allowed counters.

Most records are marked `Experimental: "1"`. That flag is part of the metadata state exposed to tooling and documentation, and it signals that names or descriptions may be less stable than architecturally documented core events. Downstream consumers should avoid assuming these event names are portable across CPU generations, even though the JSON lives under the `cascadelakex` model directory.

The trailing object at the chunk boundary is a persistence hazard for chunk-level review only. Lines 11948-11953 start `UNC_M3UPI_VN0_CREDITS_USED.NCS` but omit the rest of that JSON object in this slice. The final per-file report should treat the event as complete only after merging with the following chunk.

## Dependencies and Integration Points

This file integrates with Linux perf's PMU events infrastructure rather than with CephFS client runtime code. Although it sits in the repository under `sources/distributed-fs/ceph-client`, the path mirrors or vendors Linux `tools/perf` content.

Key integration points are:

- The perf PMU events JSON parser/generator, which expects valid event objects with fields such as `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `Unit`, and `PerPkg`.
- The x86 CPU model mapping for `cascadelakex`, which determines when these event names are offered for the running machine.
- The uncore PMU driver support for the `M3UPI` unit and its three programmable counters.
- Perf user interfaces such as `perf list`, `perf stat -e`, and metric/reporting paths that display descriptions and program event selectors.
- Adjacent chunks of this same JSON file, because event families are split by line range. This chunk begins after earlier `M3UPI_M2_BL_CREDITS_EMPTY` entries and ends before the rest of `VN0_CREDITS_USED`.

The file depends on Intel's Cascade Lake Xeon uncore event definitions being represented accurately. The correctness of the table is not locally derivable from code in this file; it depends on hardware documentation, upstream Linux perf event data, and validation on supported systems.

## Risks and Edge Cases

The main risk is metadata drift. A wrong `EventCode` or `UMask` silently programs a different hardware condition while preserving a plausible event name and description. These events are low-level enough that such mistakes may only show up as misleading performance analysis rather than immediate test failures.

Description/name mismatches are another risk. This chunk contains repeated families where only a suffix and mask change, so copy/paste mistakes are easy. A notable example pattern is in UPI peer credit-empty events: some brief descriptions mention one message class while the `EventName` suffix names another. Those should be checked against the authoritative uncore event list before using the brief text as documentation.

The `Experimental` flag means consumers should be careful with long-lived automation that depends on exact names. Event availability and semantics can vary across stepping, socket topology, BIOS configuration, and kernel uncore PMU support.

Counter scheduling is constrained. Every complete record in this chunk targets `Counter: "0,1,2"`, but the M3UPI unit may expose multiple instances or links depending on hardware topology. Tooling must handle unavailable units, multiplexing, and package aggregation correctly.

Some events count cycles while others count inserts, flits, credits, arbitration outcomes, or occupancy-like conditions. Comparing raw values across families can be misleading unless normalized by elapsed cycles, unit instance count, or traffic volume.

The chunk boundary itself is an edge case. A line-range consumer that tries to parse only lines 6281-11953 as standalone JSON will fail because the selected range is not a complete JSON array and ends mid-object. Research and reconciliation must use the full source file for syntax validation.

## Test Signals

High-signal validation for this chunk includes:

- The full `uncore-interconnect.json` file parses as valid JSON after any edits.
- Perf's PMU event table generation succeeds for the `cascadelakex` architecture directory.
- Generated tables include the `M3UPI` events from this range with the expected `EventCode`, `UMask`, `Counter`, `PerPkg`, and description fields.
- `perf list` on a matching Cascade Lake Xeon system shows representative events from each family, including RxC arbitration, TxC flow-queue, TxR/RxR queue, ring-in-use, UPI peer credit-empty, and VN0 credit-used families.
- `perf stat -e` can schedule representative M3UPI events on allowed counters without parser errors.
- Hardware sanity checks show nonzero values under relevant traffic: UPI peer credit events under inter-socket pressure, ring occupancy under mesh/ring traffic, and TxR/RxR inserts or cycles-non-empty when the link is active.

For repository-only validation, the best checks are JSON parsing of the full file, perf PMU-events generator tests, and diff review against upstream Linux perf event data for Cascade Lake Xeon.

## Cross-Chunk Notes

This is a chunk-level research artifact only. The final per-file report should merge it with neighboring chunks before drawing whole-file conclusions.

The previous chunk contains earlier `M3UPI_M2_BL_CREDITS_EMPTY` records that precede `IIO5_NCB`. The next chunk is required to complete `UNC_M3UPI_VN0_CREDITS_USED.NCS` and continue the VN0 credit-use family.

### subset-b-006650: lines 11954-13859

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-interconnect.json lines 11954-13859

## Scope

This chunk covers the tail of the Cascade Lake X `uncore-interconnect.json` PMU event table. The range starts inside the `UNC_M3UPI_VN0_CREDITS_USED.NCS` object and continues through the closing `]` of the top-level JSON array. The adjacent preceding lines show that the partial opening object is:

- `UNC_M3UPI_VN0_CREDITS_USED.NCS`, `EventCode` `0x5C`, `UMask` `0x20`, `Counter` `0,1,2`, `Unit` `M3UPI`.

The rest of the chunk contains complete static JSON event records for the `M3UPI`, `M2M`, `UPI`, and `UBOX` uncore units. There are no functions, classes, branches, or local runtime variables in this source file; its behavior is data-driven through perf's PMU event generation and lookup pipeline.

## Purpose

The purpose of this chunk is to expose Cascade Lake X uncore interconnect monitoring events to perf. These records let perf users refer to symbolic event names instead of raw event selectors and unit masks when measuring Ultra Path Interconnect behavior, M3UPI credit pressure, and UBOX package-level events.

The covered event records fall into four broad areas:

- `M3UPI` credit use and credit starvation for VN0 and VN1 message channels.
- One deprecated `M2M` compatibility alias redirecting users from `UNC_NoUnit_TxC_BL.DRS_UPI` to `UNC_M2M_TxC_BL.DRS_UPI`.
- `UPI` link, flow-control, receive-path, transmit-path, power-state, FLIT, header-match, queue, and credit-return events.
- `UBOX` fixed clockticks, legacy event-message receipt, lock/PHOLD cycles, DRNG RACU activity, and outstanding RACU register requests.

All records in this chunk are package-scoped through `"PerPkg": "1"`. Most are marked `"Experimental": "1"`, especially the detailed flow-control, header-match, queue, and UBOX entries. Some records are explicitly `"Deprecated": "1"` and exist to preserve legacy names while pointing users toward newer aliases.

## Important Data Shape and APIs

Each entry is a JSON object in the perf PMU event schema consumed by `tools/perf/pmu-events/jevents.py` during perf table generation. Important fields in this chunk are:

- `EventName`: The symbolic alias source. Perf's generated tables normally expose lower-case aliases derived from these names, such as `unc_upi_txl_flits.all_data`.
- `EventCode`: The raw event selector programmed into the uncore PMU.
- `UMask`: The unit mask that distinguishes subevents under shared selectors, such as message classes, slots, virtual networks, and opcode-match variants.
- `Counter`: The valid counter set. `M3UPI` events use counters `0,1,2`; most `UPI` events use `0,1,2,3`; most `UBOX` programmable events use `0,1`; `UNC_U_CLOCKTICKS` uses the fixed counter.
- `Unit`: The uncore block used for PMU routing. This chunk uses `M3UPI`, `M2M`, `UPI`, and `UBOX`.
- `PerPkg`: Marks the events as package-scoped uncore events in generated metadata.
- `BriefDescription`: The short user-facing description.
- `PublicDescription`: Longer help text where present. Many low-level experimental records omit this field and rely only on the brief description or event name.
- `Deprecated`: Preserves old event aliases while steering users toward current event names.
- `Experimental`: Marks events whose interface or support quality should be treated more cautiously by users and tooling.

The JSON records do not define code-level APIs themselves, but their field names are an API contract with perf's generator and generated lookup code. At build time, `jevents.py` parses these fields into generated PMU event tables. At runtime, perf's PMU event lookup helpers use those generated tables to support `perf list`, `perf stat -e <event>`, metric resolution, and detailed event descriptions.

## Event Families

### M3UPI VN0 and VN1 Credit Events

Lines 11954-12198 finish the M3UPI credit section. The chunk begins inside `UNC_M3UPI_VN0_CREDITS_USED.NCS`; the remaining `VN0_CREDITS_USED` entries cover `REQ`, `RSP`, `SNP`, and `WB`, all with `EventCode` `0x5C` and counters `0,1,2`.

The `UNC_M3UPI_VN0_NO_CREDITS.*` family uses `EventCode` `0x5E` and reports cycles where VN0 credits were unavailable. The masks split the condition by message class:

- `REQ` on AD: `UMask` `0x1`.
- `SNP` on AD: `UMask` `0x2`.
- `RSP` on AD: `UMask` `0x4`.
- `WB` on BL: `UMask` `0x8`.
- `NCB`/data-response wording in the brief text: `UMask` `0x10`.
- `NCS`/non-coherent broadcast wording in the brief text: `UMask` `0x20`.

The `UNC_M3UPI_VN1_CREDITS_USED.*` family uses `EventCode` `0x5D`, and the `UNC_M3UPI_VN1_NO_CREDITS.*` family uses `EventCode` `0x5F`. Both mirror the same message-class masks. The long descriptions explain the core interpretation: requests prefer shared VNA credits and fall back to reserved VN0/VN1 pools to avoid deadlock. The credit-used events count fallback use, while no-credit events count cycles where the relevant reserved pool was unavailable.

These events are diagnostic signals for remote-socket traffic and backpressure. A high VN0/VN1 credit-used count suggests falling back from VNA; high no-credit cycles suggest more severe flow-control pressure.

### Deprecated M2M Alias

Lines 12200-12210 define `UNC_NoUnit_TxC_BL.DRS_UPI`, a deprecated `M2M` record with `EventCode` `0x40`, `UMask` `0x4`, and counters `0,1,2,3`. Its brief description points to `UNC_M2M_TxC_BL.DRS_UPI`.

This is compatibility data. The record should remain parseable and discoverable for users with old event names, but new documentation and tests should prefer the replacement alias.

### UPI Clock, Direct Attempts, Flow Queue, and M3 Blocking

Lines 12212-12466 start the main `UPI` tail section:

- `UNC_UPI_CLOCKTICKS` counts UPI fixed-frequency link clock ticks with `EventCode` `0x1`. Its long description states that the clock is one eighth of the UPI GT/s link speed, making it a natural denominator for UPI rates and occupancy-like interpretations.
- `UNC_UPI_DIRECT_ATTEMPTS.D2C` and `.D2U` use `EventCode` `0x12` to count data-response packets attempting to bypass the CHA and go direct to core or direct to UPI. `D2K` is deprecated in favor of `D2U`.
- `UNC_UPI_FLOWQ_NO_VNA_CRD.*` uses `EventCode` `0x18` and masks for AD, AK, and BL VNA credit conditions, such as `AD_VNA_EQ0`, `AK_VNA_EQ3`, and `BL_VNA_EQ0`.
- `UNC_UPI_L1_POWER_CYCLES` uses `EventCode` `0x21` to count cycles where both link directions are in the L1 shutdown power state.
- `UNC_UPI_M3_BYP_BLOCKED.*` uses `EventCode` `0x14` for bypass blocking reasons, including BGF credit, VNA threshold conditions, BL VNA empty, and global valid blocking.
- `UNC_UPI_M3_CRD_RETURN_BLOCKED` uses `EventCode` `0x16`.
- `UNC_UPI_M3_RXQ_BLOCKED.*` uses `EventCode` `0x15` for receive-queue blocking reasons, including BGF credit, flow queue thresholds, BL VNA empty, and global valid blocking.

These are low-level link-flow-control records. Most lack `PublicDescription`, so event names and masks carry much of the semantic detail. That increases the value of preserving exact names and avoiding accidental alias churn.

### UPI Power-State Handshake and M3 Slot Requests

Lines 12470-12554 define more UPI link-state and request-routing events:

- `UNC_UPI_PHY_INIT_CYCLES` counts cycles where the PHY is outside normal L0/L0c/L0p/L1 states.
- `UNC_UPI_POWER_L1_NACK` and `UNC_UPI_POWER_L1_REQ` count L1 transition NACK and ACK/REQ handshakes with `EventCode` `0x23` and `0x22`.
- `UNC_UPI_REQ_SLOT2_FROM_M3.*` uses `EventCode` `0x46` and masks `VNA` `0x1`, `VN0` `0x2`, `VN1` `0x4`, and `ACK` `0x8`.
- `UNC_UPI_RxL0P_POWER_CYCLES` and `UNC_UPI_RxL0_POWER_CYCLES` report receive-side low-power and full-power link-layer cycles.

The power-state descriptions emphasize that UPI power states are per link and per direction. Consumers comparing Rx and Tx power events must not assume one event covers both directions unless the description explicitly says so, as `UNC_UPI_L1_POWER_CYCLES` does.

### UPI Receive-Path Header, FLIT, Queue, and Credit Events

Lines 12558-13119 define receive-path (`RxL`) events:

- `UNC_UPI_RxL_BASIC_HDR_MATCH.*` uses `EventCode` `0x5` and masks for message classes and opcode-specific matching. Message-class aliases include `NCB`, `NCS`, `REQ`, `RSP_DATA`, `RSP_NODATA`, `SNP`, and `WB`; opcode variants add a high mask bit such as `0x108`, `0x109`, `0x10c`, `0x10d`, `0x10e`, or `0x10f`.
- `UNC_UPI_RxL_BYPASSED.SLOT0`, `.SLOT1`, and `.SLOT2` use `EventCode` `0x31` and count FLITs that bypassed slot-specific receive buffers, which is the intended low-latency common path.
- `UNC_UPI_RxL_CREDITS_CONSUMED_VNA`, `_VN0`, and `_VN1` use event codes `0x38`, `0x39`, and `0x3A` to count RxQ credit consumption by virtual network.
- `UNC_UPI_RxL_FLITS.*` uses `EventCode` `0x3` to count received data, null, idle, LLCRD, LLCTRL, non-data, protocol header, and slot-selected FLITs.
- Deprecated `UNC_UPI_RxL_FLITS.NULL` and `.PROT_HDR` point to `.ALL_NULL` and `.PROTHDR`.
- Deprecated `UNC_UPI_RxL_HDR_MATCH.*` entries point to `UNC_UPI_RxL_BASIC_HDR_MATCH.*`.
- `UNC_UPI_RxL_INSERTS.SLOT*` and `UNC_UPI_RxL_OCCUPANCY.SLOT*` use event codes `0x30` and `0x32` to measure RxQ allocations and accumulated occupancy by slot.
- `UNC_UPI_RxL_SLOT_BYPASS.*` uses `EventCode` `0x33` for cross-slot bypass routing signals such as `S0_RXQ1` and `S2_RXQ1`.

The FLIT families combine type masks with slot masks. For example, `DATA` notes that data FLITs consume all slots, but the counted value depends on enabled slot mask bits. Users and tests should treat these as bitmask-composable hardware encodings, not as independent mutually exclusive counters.

### UPI Transmit-Path Power, Header, FLIT, Queue, and Credit Events

Lines 13123-13732 define transmit-path (`TxL`) records:

- `UNC_UPI_TxL0P_CLK_ACTIVE.*` uses `EventCode` `0x2A` for active clock subcomponents during L0p, including `CFG_CTL`, `RXQ`, `RXQ_BYPASS`, `RXQ_CRED`, `TXQ`, `RETRY`, `DFX`, and `SPARE`.
- `UNC_UPI_TxL0P_POWER_CYCLES`, `_LL_ENTER`, and `_M3_EXIT` use event codes `0x27`, `0x28`, and `0x29`.
- `UNC_UPI_TxL0_POWER_CYCLES` uses `EventCode` `0x26`.
- `UNC_UPI_TxL_BASIC_HDR_MATCH.*` mirrors the receive-side header-match family but uses `EventCode` `0x4` for transmit-path matching.
- `UNC_UPI_TxL_BYPASSED` uses `EventCode` `0x41` to count FLITs that bypass the transmit buffer and pass directly to the UPI link.
- `UNC_UPI_TxL_FLITS.*` uses `EventCode` `0x2` to count transmitted data, null, idle, LLCRD, LLCTRL, non-data, protocol-header, and slot-selected FLITs.
- Deprecated `UNC_UPI_TxL_FLITS.NULL` and `.PROT_HDR` point to `.ALL_NULL` and `.PROTHDR`.
- Deprecated `UNC_UPI_TxL_HDR_MATCH.*` entries point to `UNC_UPI_TxL_BASIC_HDR_MATCH.*` where an equivalent exists. Several deprecated entries, such as `DATA_HDR`, `DUAL_SLOT_HDR`, `LOC`, `NON_DATA_HDR`, `REM`, and `SGL_SLOT_HDR`, have no replacement text beyond "This event is deprecated."
- `UNC_UPI_TxL_INSERTS` and `UNC_UPI_TxL_OCCUPANCY` use event codes `0x40` and `0x42` for transmit flit-buffer allocations and accumulated occupancy.
- `UNC_UPI_VNA_CREDIT_RETURN_BLOCKED_VN01` and `UNC_UPI_VNA_CREDIT_RETURN_OCCUPANCY` use event codes `0x45` and `0x44` to track VNA credit-return blockage and pending-return occupancy.

The transmit queue descriptions parallel the receive queue descriptions: bypass is the normal fast path, while inserts and occupancy indicate buffering, typically due to L0p or link-layer retry conditions. Occupancy values are accumulated queue-depth signals and need a denominator such as clockticks or a not-empty event from nearby data to become averages.

### UBOX Clock, Messages, Locks, PHOLD, DRNG, and RACU

Lines 13736-13859 close the file with `UBOX` entries:

- `UNC_U_CLOCKTICKS` uses `Counter` `FIXED` and `EventCode` `0xff` for UBOX clockticks.
- `UNC_U_EVENT_MSG.*` uses `EventCode` `0x42` with masks for `VLW_RCVD`, `MSI_RCVD`, `IPI_RCVD`, `DOORBELL_RCVD`, and `INT_PRIO`. The long descriptions describe Virtual Logical Wire legacy messages and, for subevents, inter-processor interrupts or message-signaled interrupts.
- `UNC_U_LOCK_CYCLES` uses `EventCode` `0x44` and counts starts of IDI lock or split-lock sequences.
- `UNC_U_PHOLD_CYCLES.ASSERT_TO_ACK` uses `EventCode` `0x45`, `UMask` `0x1`.
- `UNC_U_RACU_DRNG.*` uses `EventCode` `0x4C` with masks for `RDRAND`, `RDSEED`, and `PFTCH_BUF_EMPTY`.
- `UNC_U_RACU_REQUESTS` uses `EventCode` `0x46` and counts outstanding register requests within the message-channel tracker.

These records are the package-control tail of the interconnect file. The final `]` at line 13859 closes the entire JSON array, so syntax errors in this range invalidate the whole Cascade Lake X interconnect event topic.

## Control Flow and Integration

This chunk has no executable control flow. The practical control flow is supplied by perf's data pipeline:

1. The x86 PMU event build selects the `arch/x86/cascadelakex` model directory for matching Cascade Lake X CPU models.
2. `jevents.py` reads topic files such as `uncore-interconnect.json` as JSON arrays.
3. Each object is converted into generated PMU event metadata. `EventCode` and `UMask` become raw event terms, `EventName` becomes the alias, descriptions become help text, `Unit` selects the uncore PMU family, `PerPkg` marks package scope, and `Deprecated`/`Experimental` become generated metadata flags.
4. The generated event tables are compiled into perf.
5. Runtime perf lookup APIs and user commands resolve names such as `UNC_UPI_RxL_FLITS.ALL_DATA` or `UNC_U_CLOCKTICKS` against the generated Cascade Lake X table.

The file integrates with kernel uncore PMU drivers indirectly: perf can only schedule these aliases if the running kernel exposes compatible uncore PMUs and if the event's counter restrictions match the hardware PMU layout.

## State and Persistence

There is no mutable software state in this chunk. Its persistent state is the source-controlled mapping from symbolic event names to uncore PMU encodings and descriptions.

The main persistence contracts are:

- `EventName` stability matters because users, scripts, documentation, and metric expressions may reference aliases by name.
- `EventCode` and `UMask` correctness determines which hardware signal perf programs. A wrong value can produce plausible but incorrect performance data.
- `Unit` controls PMU routing. A typo can make an event appear under the wrong generated PMU or disappear from the expected uncore PMU.
- `Counter` constraints describe legal hardware counters and affect scheduling expectations.
- `Deprecated` entries preserve compatibility while guiding users toward newer names.
- `Experimental` metadata warns consumers that some entries may be less stable or less fully documented.
- The closing array bracket persists structural validity for the whole file.

Because this is a static event database, changes take effect only after regenerating or rebuilding perf's PMU event tables.

## Dependencies

This chunk depends on:

- Valid JSON syntax for the whole `uncore-interconnect.json` array.
- The perf PMU event JSON schema and field spellings recognized by `jevents.py`.
- The Cascade Lake X x86 model mapping that selects the `cascadelakex` directory.
- Generated PMU event table code and lookup helpers used by `perf list`, `perf stat`, and metric parsing.
- Kernel uncore PMU support for Cascade Lake X units corresponding to `M3UPI`, `M2M`, `UPI`, and `UBOX`.
- Hardware documentation matching the listed event selectors, masks, counter constraints, and package-scoped semantics.

There are no direct code imports, includes, or local helper functions in the JSON file. The important dependency is the schema-level contract between static data and perf's generator.

## Risks

- The chunk starts mid-object. A chunk-only reader could miss that the first visible fields belong to `UNC_M3UPI_VN0_CREDITS_USED.NCS`, not a standalone object.
- The range ends the top-level JSON array. Any missing comma, brace, or closing bracket here breaks parsing for the entire Cascade Lake X uncore interconnect topic.
- Many records are experimental and have terse descriptions. Users may need platform documentation to interpret low-level flow-control names such as `FLOWQ_AD_VNA_BTW_2_THRESH` or `GV_BLOCK`.
- Deprecated aliases must remain syntactically valid. Removing or renaming them can break older perf scripts even if newer aliases exist.
- Header-match families use closely related masks for class and opcode matching. Accidental mask changes can silently turn a class match into an opcode-filtered match or vice versa.
- Rx and Tx families are intentionally similar but use different event selectors (`RxL_BASIC_HDR_MATCH` uses `0x5`, `TxL_BASIC_HDR_MATCH` uses `0x4`; Rx FLITs use `0x3`, Tx FLITs use `0x2`). Copying between families is error-prone.
- Some descriptions have legacy or inconsistent wording, such as QPI references inside UPI VN1 descriptions and brief-description mismatches around NCB/NCS/WB. Those strings may confuse users even when raw encodings are correct.
- Occupancy-style events are accumulated over cycles, not simple transaction counts. Tooling or documentation that treats them as raw event counts can produce misleading conclusions.
- `Counter` differs by unit: M3UPI uses three counters, UPI uses four, UBOX mostly uses two, and `UNC_U_CLOCKTICKS` is fixed. Incorrect scheduling assumptions can produce event-open failures or bad multiplexing behavior.

## Test and Validation Signals

Useful validation signals for this chunk include:

- Parse the full source file with a strict JSON parser, for example `python3 -m json.tool sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-interconnect.json`.
- Regenerate or build perf PMU event tables and confirm the Cascade Lake X table contains representative aliases from each unit: `UNC_M3UPI_VN1_NO_CREDITS.REQ`, `UNC_NoUnit_TxC_BL.DRS_UPI`, `UNC_UPI_CLOCKTICKS`, `UNC_UPI_RxL_FLITS.ALL_DATA`, `UNC_UPI_TxL_FLITS.ALL_DATA`, and `UNC_U_CLOCKTICKS`.
- Check sample generated encodings: `UNC_UPI_RxL_BASIC_HDR_MATCH.REQ_OPC` should carry `event=0x5,umask=0x108`; `UNC_UPI_TxL_BASIC_HDR_MATCH.REQ_OPC` should carry `event=0x4,umask=0x108`; `UNC_U_EVENT_MSG.MSI_RCVD` should carry `event=0x42,umask=0x2`.
- Run perf PMU event table tests, especially generated event lookup tests under `tools/perf/tests/pmu-events.c` in a full perf tree.
- Inspect `perf list --details` output for deprecated aliases and ensure replacement text is visible where present.
- On Cascade Lake X hardware with compatible kernel uncore PMUs, run low-impact `perf stat -a -e` checks for representative UPI and UBOX aliases and confirm event resolution, counter scheduling, and package-level aggregation.
- For behavioral validation, compare bypass, insert, and occupancy families under workloads that vary UPI traffic and link power state; bypass should represent the fast path, while insert/occupancy should rise when queues are used.
