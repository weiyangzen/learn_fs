# Research: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006681`: lines 1-6626, `Docs/researches/chunks/subset-b-006681_research.md`
- `subset-b-006682`: lines 6627-11744, `Docs/researches/chunks/subset-b-006682_research.md`
- `subset-b-006683`: lines 11745-16792, `Docs/researches/chunks/subset-b-006683_research.md`
- `subset-b-006684`: lines 16793-17915, `Docs/researches/chunks/subset-b-006684_research.md`

## Chunk Research

### subset-b-006681: lines 1-6626

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json lines 1-6626

## Scope

This chunk covers the first 6,626 lines of the Ice Lake Xeon uncore interconnect PMU event JSON table. The full file is a JSON array; this range contains 643 complete event objects and ends in the middle of the `UNC_M2M_TxR_HORZ_*` event families. The covered records are data definitions, not executable code.

## Purpose

The file provides perf's Ice Lake Xeon uncore interconnect event metadata. These records are consumed by the perf PMU event generation flow (`tools/perf/pmu-events/jevents.py`) and compiled into generated `pmu-events.c` tables that runtime perf code queries through `pmu_events_table` helpers. Users see the resulting aliases through commands such as `perf list` and use them as event names in perf stat/record workflows on matching x86 platforms.

In this chunk the event set starts with IRP unit events and then transitions into M2M/Common Mesh Stop events:

- `IRP` events: 73 records for IO coherency tracker activity, inbound/outbound IRP inserts, reads, writes, snoops, request queues, peer-to-peer, fast/slow-path and timeout/misc counters.
- `M2M` events: 570 records for mesh-to-memory/common mesh stop behavior, including clocks, directory lookups/hits/misses, iMC read/write classification, Near Memory tag hits, prefetch CAM behavior, tracker occupancy/full/not-empty, credit acquisition/occupancy, receiver/transgress queue occupancy/inserts/bypass/starvation, stalls, ring usage/bounces, distress, and the beginning of horizontal egress insert/NACK/occupancy families.

## Data Shape

Each event object uses the standard perf PMU event schema fields:

- `EventName`: canonical alias, for example `UNC_I_CLOCKTICKS`, `UNC_I_TRANSACTIONS.READS`, or `UNC_M2M_IMC_WRITES.PMM_NM_MISS`.
- `EventCode`: low-level event selector, represented as a hex string. Casing is inconsistent (`0x0F` and `0x0f` both appear), so consumers must treat it semantically as a number/string accepted by jevents rather than as a normalized display token.
- `UMask`: optional unit mask. Some events, especially broad clock or whole-event records, omit it.
- `Counter`: allowed counter indexes. IRP events in this chunk normally use `0,1`; M2M events normally use `0,1,2,3`.
- `Unit`: PMU unit name. This chunk has only `IRP` and `M2M`.
- `PerPkg`: almost every record is package-scoped with `"1"`, matching uncore PMU behavior.
- `BriefDescription` and sometimes `PublicDescription`: user-facing descriptions for event listing and help output.
- `Experimental`: many records are marked experimental, which should be preserved by generation and listing tools.

The JSON array ordering is significant for human maintainability and generated table stability, but the runtime lookup key is the event alias plus PMU matching logic rather than source line number.

## Important Event Families

The IRP section includes:

- Cache/read/write occupancy and request counts: `UNC_I_CACHE_TOTAL_OCCUPANCY.*`, `UNC_I_READS.*`, `UNC_I_WRITES.*`, `UNC_I_TRANSACTIONS.*`.
- Coherency operations: `UNC_I_COHERENT_OPS.*`, including CLFLUSH, PCITOM, RFO, and WBMTOI.
- FAF and IRP queue flow: `UNC_I_FAF_*`, `UNC_I_IRP_ALL.*`, `UNC_I_IRP_OCCUPANCY.*`, `UNC_I_IRP_PORT0/1.*`.
- Miscellaneous fast-path, slow-path, timeout, interrupt, retry, and source classifications: `UNC_I_MISC0.*`, `UNC_I_MISC1.*`, `UNC_I_REQUESTS.*`, `UNC_I_SNOOP_RESP.*`, `UNC_I_SNOOPS.*`, `UNC_I_P2P_TRANSACTIONS.*`.

The M2M section includes:

- Common activity and clocks: `UNC_M2M_CLOCKTICKS`, `UNC_M2M_CORE_SNOOP`, `UNC_M2M_RFO_*`.
- Directory and tag behavior: `UNC_M2M_DIRECTORY_LOOKUP.*`, `UNC_M2M_DIRECTORY_HIT.*`, `UNC_M2M_DIRECTORY_MISS.*`, `UNC_M2M_TAG_HIT.*`.
- iMC read/write routing and memory type breakdowns: `UNC_M2M_IMC_READS.*` and `UNC_M2M_IMC_WRITES.*`, with many combinations for all/partial/full writes, PMM/DRAM, Near Memory hit/miss, bypass, and directory state.
- Prefetch CAM behavior: `UNC_M2M_PREFCAM_*`, including occupancy, full/not-empty cycles, inserts, deallocations, demand drops, merge/no-merge, response misses, and per-channel drop reasons.
- Tracker and request queue pressure: `UNC_M2M_TRACKER_*`, `UNC_M2M_RPQ_*`, `UNC_M2M_RxR_*`, `UNC_M2M_TxC_*`, and `UNC_M2M_TxR_*`.
- Mesh/ring and stall signals: `UNC_M2M_HORZ_RING_*`, `UNC_M2M_RING_*`, `UNC_M2M_STALL*`, and `UNC_M2M_DISTRESS_ASSERTED.*`.
- Agent credit accounting: `UNC_M2M_AG0_*` and `UNC_M2M_AG1_*`, with AD/BL credit acquired and occupancy counters split across transgress lanes.

## Control Flow and Runtime Integration

There is no in-file control flow. The effective flow is build-time and data-driven:

1. Perf's PMU event build scans architecture map files and JSON event files under `tools/perf/pmu-events/arch`.
2. `jevents.py` parses the JSON records, validates expected keys, and emits compact C tables.
3. The perf build links those generated tables through `libpmu-events.a`.
4. Runtime PMU code, including helpers referenced from `util/pmu.c` and `util/pmus.c`, finds the model's PMU table and exposes aliases to `perf list` and event parsing.
5. When a user selects one of these aliases, perf maps the alias metadata into event code, unit mask, counter constraints, unit/PMU matching, descriptions, and package-scoped semantics.

The `Unit` field is the key integration point for uncore PMU matching. If an event is assigned to the wrong unit, generated aliases may be hidden, listed under the wrong PMU, or parsed against the wrong sysfs event format.

## State and Persistence

This JSON file is persistent source metadata. It does not maintain runtime state, but it determines generated build artifacts and user-visible perf aliases. The persistent state boundary is:

- source JSON in the repository,
- generated `pmu-events.c` and object/archive outputs during the perf build,
- runtime PMU alias tables loaded from the generated data.

Counter values themselves come from hardware PMUs at runtime and are not stored here. The descriptions and event encodings in this file are the durable contract that connects Intel uncore documentation to perf's generated event tables.

## Dependencies

This chunk depends on the perf PMU events infrastructure accepting the schema used here. Important dependencies and assumptions include:

- Valid JSON array syntax across the whole source file. This chunk starts at the array opener but the full file must close later.
- `jevents.py` support for fields such as `BriefDescription`, `PublicDescription`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `Experimental`.
- x86 architecture mapping that selects the `icelakex` event directory for the matching CPU model.
- Runtime PMU unit names compatible with Linux perf uncore PMU names for Ice Lake Xeon.
- Consumer support for uncore package-scoped events and counter restrictions.

## Risks and Edge Cases

- The chunk boundary cuts after line 6,626 inside the larger file, so this report cannot describe the later continuation of `UNC_M2M_TxR_HORZ_OCCUPANCY` or later event units/families.
- Many records are mechanical variants over lanes, channels, agents, and masks. Copy/paste mistakes in `EventName`, `EventCode`, `UMask`, or description text can silently create misleading aliases even when the JSON remains syntactically valid.
- Hex string casing is mixed. Any tests or comparison tools that do textual normalization poorly may report false diffs or miss duplicate encodings.
- Some records omit `UMask`; this is valid for certain whole events but should be deliberate. Missing masks in variant families can be suspicious.
- `Experimental` is common in this range. Downstream UI or scripts may filter or annotate these events differently.
- Because the records are uncore events with `PerPkg`, users can misinterpret counts if they expect per-core semantics or if socket/package aggregation is not considered.
- The M2M records encode detailed platform-specific behavior, including PMM/Near Memory classifications. On systems without the corresponding hardware mode, aliases may be present but not meaningful or may depend on model matching.

## Test Signals

Useful validation signals for this chunk include:

- `jq` can parse the complete `uncore-interconnect.json` file and report the expected array length.
- Generated PMU event build succeeds with `NO_JEVENTS` disabled, proving `jevents.py` accepts all records.
- `perf list` on matching Ice Lake Xeon hardware exposes representative aliases from this chunk, such as `UNC_I_CLOCKTICKS`, `UNC_I_TRANSACTIONS.READS`, `UNC_M2M_CLOCKTICKS`, `UNC_M2M_IMC_READS.ALL`, and `UNC_M2M_PREFCAM_DEMAND_DROPS.UPI_ALLCH`.
- Event parsing accepts aliases with their unit constraints and maps to the expected event code and unit mask.
- Schema linting checks for duplicate `EventName` values, malformed hex fields, missing required descriptions, and suspicious absent `UMask` values in otherwise mask-split families.
- Regression checks compare generated `pmu-events.c` before and after changes to ensure intended changes are limited to affected aliases.

## Chunk Notes for Merge

The final per-file research should merge this with later chunks to cover the rest of the JSON array. For this chunk, the source path is `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json`, and the covered line range is 1-6626. The most important merge detail is that this range begins the file, establishes the JSON schema, fully covers the IRP unit section, and covers the early-to-middle M2M section through horizontal transgress egress NACK and the first occupancy record.

### subset-b-006682: lines 6627-11744

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json lines 6627-11744

## Scope

This chunk covers the middle of the Ice Lake Xeon uncore interconnect PMU event table used by `tools/perf/pmu-events`. The requested range starts inside the `UNC_M2M_TxR_HORZ_NACK.BL_UNCRD` object and ends inside the `UNC_M3UPI_RxC_OCCUPANCY_VN1.AD_RSP` object, so the first and last descriptors are partial at the chunk boundaries. Within the span, there are 472 `EventName` entries and 471 complete object starts visible in the raw line range. The complete source file parses as a JSON array with 1,689 event descriptors.

The chunk is data-only JSON. It declares hardware performance event metadata; it does not define executable functions, C types, mutable runtime state, or local control flow.

## Purpose

The file supplies Intel Ice Lake Xeon uncore interconnect event descriptions for Linux perf's PMU event database. `jevents.py` and related `pmu-events` build code consume this JSON and generate static event tables, which perf later uses to resolve symbolic event names, event codes, unit masks, descriptions, package scope, and counter eligibility.

This chunk is focused on interconnect traffic between common mesh stop, M2M, iMC, and UPI-facing units. It describes:

- `M2M` egress, vertical/horizontal ring, write-pending-queue, and write-tracker events.
- `M3UPI` mesh-to-UPI credit, ring, ingress arbitration, flit-generation, and receive-side queue events.

## Data Schema And API Surface

Each descriptor follows the perf PMU event JSON schema used throughout `tools/perf/pmu-events`:

- `EventName` is the stable symbolic user-facing name, for example `UNC_M2M_TxR_HORZ_OCCUPANCY.AD_ALL` or `UNC_M3UPI_RxC_INSERTS_VN0.BL_WB`.
- `EventCode` is the raw hardware event selector value.
- `UMask` selects a sub-event or traffic class within the event code.
- `Counter` lists allowed hardware counter indexes, usually `0,1,2,3` in this chunk.
- `Unit` binds the event to the uncore PMU block, mainly `M2M` or `M3UPI`.
- `PerPkg` marks package-scoped uncore measurement.
- `BriefDescription` and `PublicDescription` provide display text for `perf list` and event documentation.
- `Experimental: "1"` appears on most descriptors, signaling events that perf should expose but treat as experimental metadata.

The important compatibility contract is the string identity and field spelling. Perf's generator expects valid JSON objects with these known keys, and users/scripts depend on `EventName` strings remaining stable.

## Event Families Covered

### M2M Common Mesh Stop And Ring Events

The first 151 unit entries in the range are `M2M`. They cover Common Mesh Stop transgress/egress behavior:

- Horizontal egress NACK, occupancy, and starvation events for AD, AK, AKC, BL, and IV traffic classes.
- Vertical egress anti-deadlock slot use, bypass, fullness, not-empty cycles, inserts, NACKs, occupancy, and starvation. These are split across `*0` and `*1` event groups where the first group covers AD/AK/BL/IV agent variants and the second covers AKC/TGC-style variants.
- Vertical ring in-use counters for AD, AK, AKC, BL, IV, and TGC rings, with up/down and even/odd direction variants.

The M2M portion also tracks memory-side queues:

- `UNC_M2M_WPQ_FLUSH.*` and `UNC_M2M_WPQ_NO_*_CRD.*` describe write pending queue flushes and cycles lacking regular, PMM, or special credits for channels 0-2.
- `UNC_M2M_WR_TRACKER_*` describes write tracker fullness, inserts, not-empty cycles, occupancy, and posted/non-posted variants for memory channels and mirror paths.

These events are useful for diagnosing mesh pressure, ring utilization, anti-deadlock behavior, write queue backpressure, and memory-channel write tracking.

### M3UPI Credits, Rings, And Distress Signals

The remaining visible entries are `M3UPI`. The first large group measures Common Mesh Stop agent credits for AD and BL traffic:

- `UNC_M3UPI_AG0_*` and `UNC_M3UPI_AG1_*` split acquired and occupancy counters by agent, traffic class, and transgress target.
- The target indexes are represented as `TGR0` through `TGR10`, split across `*0` and `*1` groups because the hardware encodes them under adjacent event codes.

The chunk then describes M3UPI high-level state:

- `UNC_M3UPI_CHA_AD_CREDITS_EMPTY` for CBox request/snoop/VNA/writeback credit exhaustion.
- `UNC_M3UPI_CLOCKTICKS` and `UNC_M3UPI_CMS_CLOCKTICKS`.
- `UNC_M3UPI_D2C_SENT` and `UNC_M3UPI_D2U_SENT`.
- `UNC_M3UPI_DISTRESS_ASSERTED` for local/remote DPT and PMM, horizontal, vertical, IV-stalled, and no-credit distress conditions.
- Horizontal and vertical ring in-use, bounce, sink-starvation, and source-throttle events.
- `UNC_M3UPI_M2_BL_CREDITS_EMPTY` and `UNC_M3UPI_MISC_EXTERNAL` for M2 BL credit starvation and external MS2IDI-related signals.

These entries are integration points for users investigating socket fabric, UPI congestion, ring routing, and credit starvation.

### M3UPI Receive-Side Arbitration And Flit Generation

The final part of the chunk focuses on `RxC`, the receive/control path from CMS into UPI-facing queues:

- `UNC_M3UPI_RxC_ARB_LOST_VN0/VN1`, `ARB_NOCRD`, and `ARB_NOREQ` break arbitration failure reasons down by virtual network, AD request/response/snoop traffic, and BL NCB/NCS/RSP/WB traffic.
- `UNC_M3UPI_RxC_ARB_MISC` records parallel arbitration wins and no-progress cases for AD/BL and VN0/VN1.
- `UNC_M3UPI_RxC_BYPASSED`, `CRD_MISC`, and `CRD_OCC` describe bypass paths, background FIFO/path credits, D2K credits, transmit queue credits, flits in FIFO/path, and VNA usage.
- `UNC_M3UPI_RxC_CYCLES_NE_VN0/VN1`, `INSERTS_VN0/VN1`, and `OCCUPANCY_VN0` plus the start of `OCCUPANCY_VN1` provide the three related signals needed to reason about queue activity and latency: cycles not empty, allocations, and occupancy accumulation.
- Data/header flit families (`DATA_FLITS_NOT_SENT`, `FLITS_GEN_BL`, `FLITS_SLOT_BL`, `FLIT_GEN_HDR1`, `FLIT_GEN_HDR2`, `HDR_FLITS_SENT`, `HDR_FLIT_NOT_SENT`) expose why flits were or were not sent, pump wait states, slot occupancy, run-ahead behavior, rate-matching stalls, and message packing efficiency.
- `UNC_M3UPI_RxC_HELD` records messages held because AD/BL traffic could not be slotted or because VN0/VN1 state prevents immediate flit assembly.

The chunk ends before the full `UNC_M3UPI_RxC_OCCUPANCY_VN1` family completes; subsequent lines continue that family.

## Control Flow And State

There is no runtime control flow in this chunk. Its effective flow is build-time:

1. The JSON file is read by perf's PMU event generation scripts.
2. Event objects are transformed into generated C event tables.
3. Perf runtime code exposes the generated events through `perf list`, event parsing, metric resolution, and PMU selection.

There is no persistence behavior beyond the checked-in JSON data and generated build artifacts. Runtime counter values are provided by CPU uncore PMU hardware, not stored by this file.

## Dependencies And Integration Points

This chunk depends on:

- The `tools/perf/pmu-events` JSON schema and `jevents.py` generator behavior.
- The x86 Ice Lake Xeon model mapping that selects this architecture directory.
- Kernel/perf uncore PMU names matching `Unit` values such as `M2M` and `M3UPI`.
- Intel uncore event encoding correctness for `EventCode`, `UMask`, and counter constraints.

Integration points include:

- `tools/perf/util/pmu.c` and related PMU parsing code, which use generated event tables.
- `tools/perf/tests/pmu-events.c` and parser tests that validate generated event metadata.
- User workflows such as `perf list`, `perf stat -e <event>`, and scripts that reference symbolic `EventName` strings.

## Risks And Edge Cases

- The assigned chunk boundaries split JSON objects. Any merge or reconciliation step must use the complete source file or neighboring chunks to avoid treating the line range alone as standalone JSON.
- Many event families are repetitive and hardware-encoded by masks. Copy/paste errors in `UMask`, `EventCode`, or suffixes such as `AG0/AG1`, `TGR8/TGR9/TGR10`, `VN0/VN1`, and `CH0/CH1/CH2` would silently map a symbolic event to the wrong counter.
- Several descriptions appear mechanically duplicated or inconsistent. For example, some "Cycles CMS Vertical Egress Queue Is Full" descriptions mention "Not Full", and some `VN0` occupancy descriptions mention `VN1`. These may be inherited vendor text, but they are user-visible through perf.
- `Experimental: "1"` on most entries limits the confidence users should place in exact semantics and may affect downstream filtering or documentation expectations.
- Case varies in event codes, including lowercase `0xae` near otherwise uppercase codes. JSON parsing accepts it as a string, but style-sensitive validation or generated diffs could flag it.
- The range contains event-code reuse across different units and subfamilies. This is expected for PMU event tables, but consumers must always combine `Unit`, `EventCode`, and `UMask`.

## Test Signals

Useful validation signals for this chunk are:

- `jq length sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json` succeeds and returns the full descriptor count.
- `jq -r '.[].EventName' ...` succeeds without null or duplicate surprises for the full file.
- Perf's PMU event generation step rebuilds generated `pmu-events.c` without schema errors.
- `tools/perf` PMU event tests, especially tests including `pmu-events/pmu-events.h`, pass after generation.
- Manual `perf list` on an Ice Lake Xeon-capable build shows the expected `UNC_M2M_*` and `UNC_M3UPI_*` event names and descriptions.

### subset-b-006683: lines 11745-16792

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json lines 11745-16792

## Chunk Scope

This chunk covers lines 11745-16792 of the Ice Lake Xeon `uncore-interconnect.json` PMU event catalog. It is a data-only slice of a larger JSON array, not executable code. The slice contains 466 event objects: 418 for the `M3UPI` unit and 49 for the `UPI` unit, with one event object beginning before this chunk boundary. Most entries are marked `"Experimental": "1"` and `"PerPkg": "1"`, meaning the generated perf events are model-specific uncore package events rather than per-core counters.

## Purpose

The chunk describes hardware event encodings for Ice Lake server uncore interconnect monitoring. These rows let perf expose named events for UPI/M3UPI traffic, queueing, arbitration, credit pressure, ring activity, writeback routing, and link power states. Users consume the names through `perf list`, `perf stat -e <event>`, JSON output from `perf list --details`, and generated PMU lookup tables.

The data is intended to preserve Intel PMU semantics in a machine-readable form:

- `EventName` gives the stable perf-visible symbolic name, often with a suffix variant such as `.AD_REQ`, `.BL_WB`, `.TGR0`, or `.UP_EVEN`.
- `EventCode` and `UMask` encode the raw PMU selector bits.
- `Counter` constrains which programmable counters can count the event.
- `Unit` maps the event to the uncore PMU block, mainly `M3UPI` in this range and then `UPI` near the end.
- `BriefDescription` and `PublicDescription` provide short and long user-facing text for generated event tables.

## Data Model and Important Fields

Every event object in this chunk follows the perf PMU JSON schema consumed by `tools/perf/pmu-events/jevents.py`. There are no local functions, classes, or runtime state in this file; the important "APIs" are the JSON keys that the generator recognizes.

Key fields visible here:

- `EventName`: required for named hardware events. `jevents.py` lowercases this name when building generated tables, so case and uniqueness still matter for source review.
- `EventCode`: hexadecimal hardware event selector. Several families share one selector and vary by `UMask`.
- `UMask`: hexadecimal sub-selector, commonly one bit per channel/message-class variant. A missing `UMask` is valid for some base events such as clockticks and power-state cycle counters.
- `Counter`: comma-separated allowed counter indexes. Most `M3UPI` entries use `0,1,2,3`, but some packing events use `0,1,2` and earlier chunk context shows other units may use narrower masks.
- `Unit`: uncore PMU namespace. The generator uses this to associate events with PMU names and runtime PMU matching.
- `BriefDescription` and `PublicDescription`: copied into generated descriptions. `PublicDescription` is absent for some terse events, in which case perf tests and generated output rely on the brief text.
- `Experimental` and `PerPkg`: metadata flags affecting presentation and interpretation; `PerPkg` tells users these events are package scoped.

## Event Families in This Chunk

The first part continues `UNC_M3UPI_RxC_OCCUPANCY_VN1`, covering VN1 ingress occupancy variants by AD/BL message class. The chunk then describes receive credit and packing behavior:

- `UNC_M3UPI_RxC_PACKING_MISS_VN0` and `UNC_M3UPI_RxC_PACKING_MISS_VN1` count cases where ingress had packets available but failed to pack them into a flit slot.
- `UNC_M3UPI_RxC_VNA_CRD` and `UNC_M3UPI_RxC_VNA_CRD_MISC` expose remote VNA credit levels, corrected credits, and allocation restrictions across VN0/VN1 and AD/BL.
- `UNC_M3UPI_RxR_OCCUPANCY`, `UNC_M3UPI_RxR_INSERTS`, `UNC_M3UPI_RxR_BYPASS`, `UNC_M3UPI_RxR_CRD_STARVED`, and `UNC_M3UPI_RxR_BUSY_STARVED` describe transgress ingress queues, allocations, bypasses, and starvation on AD, AK, AKC, BL, IFV, and IV classes.

The middle of the slice is dominated by M3UPI transmit/ring pressure:

- `UNC_M3UPI_STALL0_NO_TxR_HORZ_CRD_*` and `UNC_M3UPI_STALL1_NO_TxR_HORZ_CRD_*` count stalls from missing horizontal transgress credits for AD/BL, agent 0/1, and transgress indexes.
- `UNC_M3UPI_TxC_AD_*`, `UNC_M3UPI_TxC_AK_*`, `UNC_M3UPI_TxC_BL_*`, and `UNC_M3UPI_TxC_BL_WB_FLQ_OCCUPANCY` cover flit queue bypass, not-empty cycles, inserts, occupancy, and arbitration failures on AD/AK/BL egress paths.
- `UNC_M3UPI_TxR_HORZ_*` covers horizontal transgress ADS usage, bypass, full/not-empty cycles, inserts, NACKs, occupancy, and starvation.
- `UNC_M3UPI_TxR_VERT_*` mirrors much of the same behavior for vertical rings, split into numbered ring groups and variants such as AD, AK, AKC, BL, IV, IFV, and TGC.
- `UNC_M3UPI_VERT_RING_*_IN_USE` gives direct in-use counters for AD, AKC, AK, BL, IV, and TGC vertical ring directions/parities.

The later M3UPI entries track peer credits and writeback routing:

- `UNC_M3UPI_UPI_PEER_AD_CREDITS_EMPTY` and `UNC_M3UPI_UPI_PEER_BL_CREDITS_EMPTY` identify when peer credits are empty for request/response/snoop/non-coherent/writeback classes.
- `UNC_M3UPI_VN0_CREDITS_USED`, `UNC_M3UPI_VN1_CREDITS_USED`, `UNC_M3UPI_VN0_NO_CREDITS`, and `UNC_M3UPI_VN1_NO_CREDITS` expose VN-level credit usage and no-credit conditions by traffic type.
- `UNC_M3UPI_WB_PENDING` and `UNC_M3UPI_WB_OCC_COMPARE` describe writeback pending state and local-destination versus route-through occupancy comparisons for VN0/VN1.
- `UNC_M3UPI_XPT_PFTCH` and `UNC_M3UPI_UPI_PREFETCH_SPAWN` expose prefetch-related arbitration, arrival, bypass, flitting, and loss conditions.

The final section starts the `UPI` unit:

- `UNC_UPI_CLOCKTICKS` gives the UPI clock baseline.
- `UNC_UPI_DIRECT_ATTEMPTS` counts direct packet attempts for D2C and D2K.
- `UNC_UPI_FLOWQ_NO_VNA_CRD`, `UNC_UPI_M3_BYP_BLOCKED`, `UNC_UPI_M3_RXQ_BLOCKED`, and `UNC_UPI_M3_CRD_RETURN_BLOCKED` expose flow queue, bypass, receive queue, and credit-return blocking causes.
- `UNC_UPI_L1_POWER_CYCLES`, `UNC_UPI_PHY_INIT_CYCLES`, `UNC_UPI_POWER_L1_REQ`, `UNC_UPI_POWER_L1_NACK`, `UNC_UPI_RxL0_POWER_CYCLES`, and `UNC_UPI_RxL0P_POWER_CYCLES` describe link-layer/PHY power-state residency and transitions.
- `UNC_UPI_REQ_SLOT2_FROM_M3` counts request slot-2 classes arriving from M3.
- `UNC_UPI_RxL_BASIC_HDR_MATCH` starts a header match family for received UPI packets, with class and opcode-match variants for NCB, NCS, request, response, snoop, and writeback traffic. The family continues after this chunk.

## Control Flow and Integration

There is no direct control flow in this JSON file. The effective flow is build-time:

1. `tools/perf/pmu-events/Build` includes the architecture JSON tree in the generated PMU event build.
2. `tools/perf/pmu-events/jevents.py` reads event JSON objects, normalizes descriptions and event names, and emits generated C tables in `pmu-events.c`.
3. The generated tables are included by perf PMU lookup code through `pmu-events/pmu-events.h`.
4. Runtime consumers such as `perf list`, `perf stat`, `util/pmu.c`, `builtin-list.c`, and Python bindings surface the generated names, encodings, and descriptions.
5. Tests under `tools/perf/tests/pmu-events.c` compare generated table entries against expected JSON-derived fields.

Because this is a chunk of one large array, the chunk boundaries do not align with semantic families. The opening event is a continuation of an object/family started before line 11745, and the final `UNC_UPI_RxL_BASIC_HDR_MATCH` family continues after line 16792.

## State and Persistence

The persistent state is the checked-in JSON event catalog. At build time, the catalog is transformed into generated C data. At runtime, perf does not mutate this file; it reads generated event tables and programs hardware PMU selectors based on `EventCode`, `UMask`, PMU unit, counter constraints, and other generated metadata.

Statefulness relevant to users is hardware-side:

- Occupancy events accumulate queue occupancy over cycles and require pairing with not-empty or allocation events to derive average occupancy or latency.
- Credit events represent instantaneous or per-cycle credit pressure conditions.
- Power events count cycles in, entering, or failing to enter UPI link power states.
- Per-package uncore events should be interpreted across sockets/packages and UPI links, not as thread-local measurements.

## Dependencies

This data depends on:

- The perf PMU JSON schema implemented by `pmu-events/jevents.py`.
- Ice Lake Xeon uncore PMU hardware definitions for `M3UPI` and `UPI`.
- The x86 model mapping that selects the `icelakex` event directory for the running CPU.
- Runtime sysfs PMU exposure for matching uncore PMU instances and supported counters.
- Description handling in `builtin-list.c`, `util/python.c`, and test code that expects `BriefDescription`/`PublicDescription` fields to be well-formed strings.

## Risks and Review Notes

- A malformed JSON object anywhere in the large source file can break PMU event generation for the whole model. This chunk begins and ends mid-array, so validation must be done on the complete file.
- Event-name uniqueness is critical. Families here reuse `EventCode` heavily and rely on distinct `UMask` and suffix names to remain distinguishable.
- Several entries have terse `BriefDescription` values that are just the event name, and some lack `PublicDescription`. That is valid but reduces `perf list` usability and can hide semantic mistakes.
- Many descriptions describe derived analysis relationships, such as occupancy plus not-empty or allocations. If companion events live in other chunks, merged documentation should preserve those cross-chunk links.
- The chunk shows one lowercase selector spelling, `0xe4`, while most event codes use uppercase hex digits. Numeric parsing should tolerate this, but reviewers should avoid accidental string-based normalization regressions.
- Some families have suffixes ending in `_1` or numbered ring groups, likely to avoid name collisions or represent hardware ring instances. These should not be "cleaned up" without checking Intel source data and generated table uniqueness.
- `Counter` constraints vary by family. Broadening them in JSON would make perf advertise invalid measurements; narrowing them would make valid events unavailable.
- Most rows are experimental, so user-facing output should make that status visible and tests should not assume stable behavior across CPU steppings without hardware confirmation.

## Test Signals

Useful validation signals for this chunk are:

- Parse the full `uncore-interconnect.json` with a strict JSON parser to catch commas, unterminated strings, and mid-array damage.
- Run the perf PMU event generation path for x86/icelakex and confirm `pmu-events.c` builds.
- Run `tools/perf/tests/pmu-events.c`-backed tests, which verify generated event fields against JSON-derived expectations.
- Use `perf list --details` on an Ice Lake Xeon system and spot-check representative names from this chunk, such as `UNC_M3UPI_RxC_VNA_CRD.LT10`, `UNC_M3UPI_TxR_HORZ_OCCUPANCY.AD_ALL`, `UNC_UPI_POWER_L1_REQ`, and `UNC_UPI_RxL_BASIC_HDR_MATCH.REQ_OPC`.
- For runtime confidence, compare raw event encodings emitted by perf for a few names against the JSON `EventCode` and `UMask` values.
- For semantic confidence, use paired measurements described in `PublicDescription`, such as occupancy with not-empty/allocation events, to check that derived averages are plausible under known UPI traffic.

## Unresolved Cross-Chunk References

The chunk references companion events outside this exact range:

- The first visible event belongs to the `UNC_M3UPI_RxC_OCCUPANCY_VN1` family that started before line 11745.
- Occupancy descriptions mention not-empty and allocation events that may appear in earlier chunks.
- The `UNC_UPI_RxL_BASIC_HDR_MATCH` family continues after line 16792 with additional receive-header variants.
- The final merged file report should reconcile these partial-family boundaries and summarize the whole `uncore-interconnect.json` source, not just this slice.

### subset-b-006684: lines 16793-17915

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json lines 16793-17915

## Scope

This chunk covers the final portion of the Ice Lake Xeon uncore interconnect PMU event JSON file. It starts inside the object for `UNC_UPI_RxL_BASIC_HDR_MATCH.WB_OPC` and then lists UPI receive-link, transmit-link, link-power, credit, and UBOX events through the closing `]` of the JSON array.

The source is data consumed by Linux `perf`, not executable Ceph code. Each object describes a discoverable perf event with fields such as `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `Experimental`, `BriefDescription`, and sometimes `PublicDescription`. The records map human-readable event aliases to Ice Lake Xeon uncore PMU encodings.

## Purpose

The file gives perf's PMU event tooling enough metadata to expose architectural and model-specific uncore measurements by name. For this range, the focus is Intel UPI and UBOX telemetry:

- UPI receive-side packet/header matching, flit classification, RxQ bypass, RxQ allocation, RxQ occupancy, CRC/LLR retry handling, and credit consumption.
- UPI transmit-side link power state cycles, clock-active reasons during L0p, packet/header matching, flit classification, TxQ bypass, TxQ allocation, TxQ occupancy, and VNA credit return state.
- UBOX package-level events for uncore clockticks, received message categories, IDI lock/split-lock cycles, M2U queue/credit conditions, PHOLD timing, RACU DRNG activity, and RACU request occupancy.

The practical consumer is `perf stat`, `perf list`, and related pmu-events generation code. A user can request names such as `UNC_UPI_TxL_FLITS.ALL_DATA` instead of manually programming event select and unit-mask values.

## Important APIs, Types, and Data

There are no functions, structs, or classes in this chunk. The public surface is the JSON event schema used by perf's PMU event tables.

Important fields are:

- `EventName`: stable perf-facing event alias, using Intel uncore naming conventions such as `UNC_UPI_RxL_*`, `UNC_UPI_TxL_*`, and `UNC_U_*`.
- `EventCode`: event select value programmed into the target PMU unit.
- `UMask`: unit-mask bits for subevents. Some events omit `UMask` when the event select is sufficient.
- `Unit`: target uncore PMU block. This range uses `UPI` for Ultra Path Interconnect link counters and `UBOX` for package uncore box counters.
- `Counter`: legal counter slots. UPI events generally allow counters `0,1,2,3`; UBOX programmable events generally allow `0,1`; `UNC_U_CLOCKTICKS` uses the fixed counter.
- `PerPkg`: marks package-scoped uncore accounting.
- `Experimental`: marks many events as lower-stability or less-promoted metadata in perf's event list.
- `BriefDescription` and `PublicDescription`: user-visible text for `perf list` and generated documentation.

The UPI receive portion includes:

- `UNC_UPI_RxL_BASIC_HDR_MATCH.WB_OPC` with event code `0x05` and UMask `0x10d`, completing a receive-path basic-header match family that begins in the preceding chunk.
- `UNC_UPI_RxL_BYPASSED.SLOT0/1/2`, which count incoming flits that bypass the RxQ flit buffer and move directly across the BGF into egress.
- `UNC_UPI_RxL_CRC_ERRORS` and `UNC_UPI_RxL_CRC_LLR_REQ_TRANSMIT`, which expose CRC detection and link-level retry request behavior.
- `UNC_UPI_RxL_CREDITS_CONSUMED_VN0`, `VN1`, and `VNA`, which count consumed RxQ virtual-network credits.
- `UNC_UPI_RxL_FLITS.*`, which classify received legal flit time by data, non-data, NULL, LLCRD, LLCTRL, protocol-header, and slot-mask dimensions.
- `UNC_UPI_RxL_INSERTS.SLOT0/1/2` and `UNC_UPI_RxL_OCCUPANCY.SLOT0/1/2`, which support RxQ queueing and average lifetime/occupancy analysis.
- `UNC_UPI_RxL_SLOT_BYPASS.*`, which expose slot-to-RxQ bypass combinations with sparse descriptions.

The UPI transmit portion includes:

- `UNC_UPI_TxL0P_CLK_ACTIVE.*`, an L0p clock-active reason family for config/control, DFX, retry, RxQ, RxQ bypass, RxQ credit, TxQ, and spare causes.
- `UNC_UPI_TxL0P_POWER_CYCLES`, `UNC_UPI_TxL0P_POWER_CYCLES_LL_ENTER`, `UNC_UPI_TxL0P_POWER_CYCLES_M3_EXIT`, and `UNC_UPI_TxL0_POWER_CYCLES`, which measure link-layer power state residency and transitions.
- `UNC_UPI_TxL_BASIC_HDR_MATCH.*`, matching transmit headers by message class and optional opcode across non-coherent bypass, non-coherent standard, request, response conflict, invalid response, data response, no-data response, snoop, and writeback classes.
- `UNC_UPI_TxL_BYPASSED`, `UNC_UPI_TxL_INSERTS`, and `UNC_UPI_TxL_OCCUPANCY`, which characterize TxQ bypass, allocation, and occupancy.
- `UNC_UPI_TxL_FLITS.*`, the transmit counterpart to the receive flit classification family.
- `UNC_UPI_VNA_CREDIT_RETURN_BLOCKED_VN01` and `UNC_UPI_VNA_CREDIT_RETURN_OCCUPANCY`, which expose VNA credit return backpressure and pending-return occupancy.

The UBOX portion includes:

- `UNC_U_CLOCKTICKS`, the fixed 48-bit UBOX clock counter event.
- `UNC_U_EVENT_MSG.*` for doorbell, interrupt priority, IPI, MSI, and legacy virtual logical wire messages received by UBOX.
- `UNC_U_LOCK_CYCLES` for IDI lock/split-lock sequence starts.
- `UNC_U_M2U_MISC1`, `UNC_U_M2U_MISC2`, and `UNC_U_M2U_MISC3` subevents for CBO/UPI non-coherent queue non-empty cycles, transmit-credit overflow cycles, empty/full AK/AKC/BL queue states, and VN0 credit overflow.
- `UNC_U_PHOLD_CYCLES.ASSERT_TO_ACK` for PHOLD assert-to-ack timing.
- `UNC_U_RACU_DRNG.*` and `UNC_U_RACU_REQUESTS` for RDRAND/RDSEED/prefetch-buffer-empty and register access control unit request occupancy.

## Control Flow

The runtime control flow is outside this file. During the perf build or packaging process, pmu-events tooling parses this JSON, validates the schema, and compiles the event records into perf's event map data. At runtime, perf resolves a user-provided event name to the generated record, chooses the uncore PMU instance matching `Unit`, programs `EventCode` and `UMask` into an allowed `Counter`, and formats the description in list/help output.

Measurement flow for the UPI link families is hardware-driven. Rx flit events count receive-path slots and packet types; RxQ events separate fast-path bypass from buffer allocation and occupancy; CRC and LLR events identify physical/link reliability and replay behavior; credit events expose virtual-network flow-control pressure. Tx events mirror the transmit direction and add link-power state residency for L0 and L0p, including the cost of lower-power operation on bandwidth and latency.

The basic-header match families encode a configurable match model in the `UMask`: message class, optional opcode match enable, local/remote selection, data versus non-data header selection, dual-slot versus single-slot header selection, and exclusion of link-layer control/null/LLCRD traffic. These rows are predefined aliases for common classes rather than procedural match code.

UBOX event flow is package-level and message-channel oriented. Message events count received interrupt/message categories; M2U miscellaneous events expose queue occupancy and credit overflow conditions between mesh/UPI/CBO paths and UBOX; RACU events track register-access and DRNG-related request state.

## State and Persistence Behavior

This JSON file stores persistent event metadata in the source tree. It does not store measured counter values, maintain runtime state, or mutate hardware.

The state represented by these events lives in processor uncore PMU counters while a perf session is active. UPI counters are per package and per UPI PMU instance, with legal programmable counters listed as `0,1,2,3`. UBOX events are per package and generally use counters `0,1`, except `UNC_U_CLOCKTICKS`, which uses the fixed counter. Counter values are reset, enabled, read, multiplexed, and scaled by perf and the kernel PMU driver, not by this JSON table.

Several event families are intended to be combined analytically. For example, RxQ/TxQ allocation and occupancy events can estimate average queue lifetime or average occupancy; bypass events can be compared against flit counts to detect queueing; CRC errors can be compared with LLR requests; L0/L0p cycle counts can be related to flit throughput and latency-sensitive workloads.

## Dependencies and Integration Points

The file depends on perf's pmu-events JSON schema and on Intel Ice Lake Xeon uncore PMU naming and event encodings. The exact `EventCode`, `UMask`, counter-slot, and unit values must match the CPU model's PMU specification and Linux uncore PMU driver behavior.

Integration points include:

- `tools/perf/pmu-events` generation scripts, which parse this JSON and build perf's event tables.
- `perf list`, which surfaces `BriefDescription`, `PublicDescription`, `Unit`, and `Experimental` status.
- `perf stat` and related event selection paths, which resolve these aliases to hardware encodings.
- Linux x86 uncore PMU support for Ice Lake Xeon UPI and UBOX units, including sysfs PMU names, event format files, counter constraints, package scoping, and fixed-counter handling.
- Intel UPI and UBOX hardware semantics for flits, slots, virtual networks, link-layer retry, L0/L0p power states, non-coherent classes, message routing, and RACU/DRNG activity.

Although this source tree is under a Ceph client mirror, this path is part of the vendored Linux perf tooling. Ceph runtime code does not directly call into these records.

## Risks and Edge Cases

- The chunk begins mid-object for `UNC_UPI_RxL_BASIC_HDR_MATCH.WB_OPC`; the event name and trailing fields are present here, while the opening brace belongs to the preceding lines. Reconciliation should join adjacent chunks before producing a whole-file report.
- Event-code or UMask drift can silently make a named perf event count the wrong hardware condition. This is especially risky for dense match families where related names differ by only one bit or suffix.
- Many events are marked `Experimental`; downstream tests and documentation should avoid treating their descriptions as a stable architectural contract.
- Some records intentionally lack `PublicDescription`, leaving only the brief event name. Generated docs and user-facing help may be sparse for `SLOT_BYPASS`, `TxL0P_CLK_ACTIVE`, some UBOX miscellaneous subevents, and DRNG subevents.
- `PerPkg` accounting can be misread as per-core or per-process accounting. These uncore counters measure package/link-level activity and often reflect all traffic on the socket.
- UPI link power states are directional and per link. A Tx-side L0/L0p event does not necessarily describe Rx-side residency or another UPI link.
- Flit-count events use slot masks and type masks. Data flits consume all slots, but the counted amount can depend on which slot bits are enabled; naive ratios can be wrong if slot and type masks are mixed inconsistently.
- Queue occupancy events accumulate queue depth over cycles, not a simple packet count. They need a divisor such as cycles-not-empty, inserts, or clockticks depending on the intended average.
- CRC and LLR events are reliability indicators but are not one-to-one: multiple CRC detections can be coalesced before a request/ack sequence completes.
- The UBOX fixed counter event uses `Counter: FIXED`, unlike the programmable UBOX events. Tooling must preserve that distinction.

## Test Signals

Useful validation signals for this chunk include:

- JSON syntax validation for the full `uncore-interconnect.json` file after adjacent chunks are considered.
- pmu-events generation coverage that compiles this file into perf's event tables without schema errors.
- `perf list` checks on an Ice Lake Xeon-capable perf build showing representative aliases from this chunk, including `UNC_UPI_RxL_FLITS.ALL_DATA`, `UNC_UPI_TxL_BASIC_HDR_MATCH.REQ`, `UNC_UPI_TxL0P_POWER_CYCLES`, `UNC_UPI_TxL_OCCUPANCY`, `UNC_U_CLOCKTICKS`, and `UNC_U_EVENT_MSG.MSI_RCVD`.
- Event encoding checks that generated tables preserve each `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `Experimental` field.
- Hardware smoke tests on Ice Lake Xeon systems using UPI traffic or NUMA workloads to confirm nonzero UPI flit, bypass, insert, occupancy, and L0/L0p counters where expected.
- Error/retry-oriented validation, where available, for `UNC_UPI_RxL_CRC_ERRORS` and `UNC_UPI_RxL_CRC_LLR_REQ_TRANSMIT`, with the expected relationship that LLR request counts are generally less than or equal to CRC detections.
- Ratio sanity checks comparing Rx/Tx flit counts with bypass, insert, and occupancy events to catch swapped masks or unit misregistration.
- UBOX validation using interrupt-heavy workloads for MSI/IPI/message events and lock/split-lock tests for `UNC_U_LOCK_CYCLES`.
- Fixed-counter handling tests for `UNC_U_CLOCKTICKS`, ensuring perf selects the fixed UBOX counter rather than a programmable slot.

## Cross-Chunk Notes

The previous chunk is needed to reconstruct the beginning of the `UNC_UPI_RxL_BASIC_HDR_MATCH.WB_OPC` JSON object. The final line in this chunk closes the whole JSON array, so subsequent source lines are not part of this event table.

The merge lane should keep this document aligned to `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json` and merge it with other chunks for that exact source path before creating any final per-file report.
