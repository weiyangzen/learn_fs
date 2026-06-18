# Research: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-interconnect.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006635`: lines 1-3888, `Docs/researches/chunks/subset-b-006635_research.md`
- `subset-b-006636`: lines 3889-4452, `Docs/researches/chunks/subset-b-006636_research.md`

## Chunk Research

### subset-b-006635: lines 1-3888

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-interconnect.json lines 1-3888

## Scope

This chunk covers the first 3,888 lines of the Broadwell-EP/EX x86 uncore interconnect PMU event table used by Linux `perf` tooling. The source file is a JSON array of event descriptors, not executable code. In this range there are 395 event objects: 55 for `IRP`, 149 for `QPI`, 150 for `R3QPI`, and the first 41 `SBOX` entries. The source file continues past this chunk, and the final entries visible here are in the middle of the `UNC_S_RxR_BYPASS` / SBOX ingress-family section.

## Purpose

The chunk defines named BroadwellX uncore interconnect hardware events that `perf list`, `perf stat`, and related PMU-event lookup code can expose on matching x86 systems. Each object maps a human-facing `EventName` such as `UNC_Q_RxL_FLITS_G1.DRS_DATA` to the hardware selection fields needed by the uncore PMU driver: `Unit`, `Counter`, `EventCode`, optional `UMask`, and package scope. The descriptions document how to interpret counts for interconnect traffic, credits, stalls, occupancy accumulators, link power states, and ring utilization.

The dominant measurement areas are:

- IRP request flow between PCIe/R2PCIe and the uncore: transaction counts, snoop responses, queue occupancy, coherent operations, and Tx/Rx credit stalls.
- QPI link-layer receive/transmit behavior: flits, virtual-network credits, retry/CRC stalls, power states, RxQ/TxQ occupancy, and R3 egress credits.
- R3QPI ring stop behavior: CBox/QPI/HA/R2 credit empties, ring usage, ingress occupancy/allocations, VNA/VN0/VN1 credit usage or rejection, SBo credit pressure, and NACKs.
- SBOX switch-box ring usage and ingress pressure: ring usage for AD/AK/BL/IV, bounce/sink starvation, and the start of bypass/starvation counters.

## Data Model And Important Fields

Each array entry is a perf PMU event descriptor with a stable schema:

- `EventName`: perf-visible symbolic name. Names are hierarchical and encode unit and subevent family, for example `UNC_R3_VN1_CREDITS_REJECT.NCB`.
- `Unit`: the uncore PMU block that owns the event. This chunk uses `IRP`, `QPI`, `R3QPI`, and `SBOX`.
- `Counter`: comma-separated counter IDs on which the event can be scheduled. Most IRP entries use `0,1`; QPI uses `0,1,2,3`; R3QPI has mixed `0,1,2`, `0,1`, and counter-0-only occupancy events; SBOX uses `0,1,2,3`.
- `EventCode`: hardware event select value. A few clock/flit events omit it in this range, relying on perf's parser and PMU-specific defaults or aliases.
- `UMask`: subevent mask when a single event code is split by message class, direction, virtual network, polarity, or queue. Some aggregate events have no `UMask`.
- `PerPkg`: set to `1` throughout this chunk, meaning the event is package-scoped rather than per-core.
- `BriefDescription` and `PublicDescription`: user-facing text consumed by `perf list --details` and documentation generation. `PublicDescription` often contains the measurement equation or caveat needed to interpret counts.

There are no functions, classes, or APIs in this JSON itself. Its effective API is the perf PMU event-table contract: the field names and values must match the parser expectations in the surrounding `tools/perf/pmu-events` infrastructure.

## Event Families

### IRP

The IRP block starts the file and tracks interconnect request pipeline activity. It includes cache total occupancy with `ANY` and `SOURCE` variants, where `SOURCE` depends on `IRP_PmonFilter.OrderingQ` and can monitor only one selected source queue at a time. It defines `UNC_I_CLOCKTICKS`, coherent operation types (`CLFLUSH`, `CRD`, `DRD`, `PCIDCAHINT`, `PCIRDCUR`, `PCITOM`, `RFO`, `WBMTOI`), miscellaneous fast-path/secondary-cache/prefetch events, and MESI-related slow-transfer events.

IRP RxR/TxR entries track inbound queues from R2PCIe and outbound requests toward devices: AK inserts, BL DRS/NCB/NCS inserts, occupancy, full cycles, outbound data inserts, request occupancy, and AD/BL egress credit stalls. `UNC_I_TRANSACTIONS.*` splits inbound transaction counts across reads, writes, prefetches, atomics, and other request types. `UNC_I_SNOOP_RESP.*` splits responses by miss, hit states, and snoop response types.

### QPI

The QPI section is the largest in this chunk. It begins with `UNC_Q_CLOCKTICKS`, CTO count, Direct2Core success/failure modes, link power states (`L0`, `L0p`, `L1`), Rx link bypass, and CRC error states.

Receive-side QPI events measure:

- VN0/VN1/VNA credits consumed by message class (`DRS`, `HOM`, `NCB`, `NCS`, `NDR`, `SNP`).
- RxQ not-empty cycles, inserts, and occupancy, split by message class and VN0/VN1 where supported.
- Flits by group: idle/null, DRS/HOM/SNP, and NCB/NCS/NDR, with data versus non-data breakdowns.
- Stalls sending to R3QPI on VN0/VN1 due to BGF, egress credits, or GV transition.

Transmit-side QPI events mirror much of the Rx link: Tx power states, TxQ bypass, LLR credit stalls, TxQ not-empty cycles, transmitted flit groups, inserts, and occupancy. `UNC_Q_TxR_*_CREDIT_ACQUIRED` and `*_CREDIT_OCCUPANCY` describe R3 egress credit state by AD/AK/BL ring, message class, and virtual network. `UNC_Q_VNA_CREDIT_RETURNS` and `UNC_Q_VNA_CREDIT_RETURN_OCCUPANCY` cover pending VNA credit returns.

Several descriptions include measurement guidance: QPI flits are 80 bits; full-width L0 data bandwidth can be estimated with data flits times 8 bytes over time, while L0p halves effective bytes per fit. The descriptions also warn that data bandwidth differs from total flit bandwidth because protocol/header flits are included in some counters.

### R3QPI

R3QPI events begin with `UNC_R3_CLOCKTICKS`, then focus on ring stop pressure and credits. The CBox credit-empty sets are split into high CBoxes (`CBO8` through grouped `CBO14_16` and `CBO_15_17`) and low CBoxes (`CBO0` through `CBO7`). HA/R2 BL credit empty entries cover `HA0`, `HA1`, `R2_NCB`, and `R2_NCS`.

QPI0/QPI1 AD and BL credit-empty groups distinguish VNA and VN0/VN1 message classes. Ring usage events (`UNC_R3_RING_AD_USED`, `AK_USED`, `BL_USED`, `IV_USED`) distinguish all, clockwise/counterclockwise, and even/odd polarities, with counters indicating cycles where packets pass by or sink at the ring stop. Ingress events provide not-empty cycles, inserts, and VN1 occupancy accumulators for HOM/SNP/NDR plus DRS/NCB/NCS variants where applicable.

Credit-flow events cover SBo0/SBo1 acquired/occupancy and stalls on missing SBo credits. TxR NACK entries split up/down and AD/AK/BL queues. VN0, VN1, and VNA credit groups report used, rejected, or acquired credits by message class. These descriptions are especially important because they explain the two-pool credit behavior: requests try VNA first and fall back to reserved VN0/VN1 pools to avoid deadlock; reject counters should normally be rare.

### SBOX

The SBOX portion starts near the end of this chunk. It defines `UNC_S_BOUNCE_CONTROL`, `UNC_S_CLOCKTICKS`, `UNC_S_FAST_ASSERTED`, and ring usage for AD, AK, and BL across all/up/down/even/odd masks. IV ring usage is present for up/down masks. Bounce and sink-starved counters distinguish AD cache, AK core acknowledgements, BL core data responses, and IV core snoops. The visible `RxR` entries cover busy-starved ingress cases for AD/BL bounces and credits plus the first bypass entries (`AD_BNC`, `AD_CRD`, `AK` visible in the field summary, with `BL_BNC`, `BL_CRD`, `IV`, and following credit-starved entries crossing the chunk boundary).

SBOX descriptions document Broadwell ring topology: up/down does not map to a single physical clockwise/counterclockwise ring across all CBoxes because CBoxes on different sides of the ring reverse the relationship.

## Control Flow And Loading Behavior

There is no runtime control flow in the file. At build or install time, perf's PMU-event tooling treats this JSON as declarative input for the BroadwellX architecture map. At runtime, perf resolves user event names against generated or parsed event tables, selects the matching PMU `Unit`, encodes `EventCode` and `UMask` into the uncore PMU event config, and schedules the event on an allowed `Counter`.

The only sequencing inside the JSON is organizational: events are grouped by PMU unit and then by related hardware family. The ordering matters mainly for readability and generated listing order; event lookup should use names and unit/event fields rather than array position.

## State And Persistence

The file is persistent source data checked into the perf source tree. It does not store runtime state, counters, or collected measurements. Actual state exists in hardware PMU counters while perf sessions run. The JSON expresses constraints that influence runtime scheduling, especially `Counter` availability and package scope. Occupancy events are accumulators over cycles; users derive averages by combining them with not-empty, insertion, or clock events, as described in several `PublicDescription` values.

## Dependencies And Integration Points

This file depends on the perf PMU-events schema shared under `tools/perf/pmu-events`. Integration points include:

- Architecture/model dispatch for x86 BroadwellX PMU event tables.
- Perf JSON validation and generated C table creation used by `perf list` and event lookup.
- The kernel uncore PMU driver support for PMU units named `IRP`, `QPI`, `R3QPI`, and `SBOX`, including the counter masks and event encodings used here.
- User workflows that compose related events into latency, occupancy, bandwidth, and credit-pressure calculations.

Because this file sits under `sources/distributed-fs/ceph-client/...`, it appears to be vendored kernel/perf source inside the Ceph client tree. Changes here should stay compatible with the upstream Linux perf event-table format.

## Risks And Edge Cases

- Schema mistakes are high-impact: misspelled field names, malformed JSON, duplicate/conflicting event names, or invalid hex strings can break perf event generation or hide events.
- Some entries omit `EventCode`, including `UNC_I_CLOCKTICKS`, `UNC_S_CLOCKTICKS`, and several QPI Tx flit group entries. This may be intentional for PMU-specific defaults, but it is a validation point if downstream tooling assumes every event has `EventCode`.
- Several descriptions show copy/paste or wording inconsistencies. Examples include QPI VN0 stall entries whose `EventName` suffix and brief message class labels appear swapped, R3 TxR NACK descriptions that do not align cleanly with `UP_*` names, and BroadwellX SBOX text that sometimes says `HSX`. These mostly affect user interpretation, not event encoding.
- Some descriptions contain typos or placeholders, such as `waitng`, `bypasssed`, `PCIDCAHin5t`, and `NCS is commonly used for ?`. Documentation consumers may surface these directly.
- Counter constraints differ by family. Occupancy events such as `UNC_R3_RxR_OCCUPANCY_VN1.*` and SBo credit occupancy are counter-0-only, so perf scheduling can fail or multiplex differently if users request incompatible events together.
- The chunk ends mid-SBOX family. Any final per-file report must reconcile this chunk with later chunks before describing complete SBOX coverage.

## Test Signals

Useful validation signals for this chunk are:

- Parse the whole JSON file with a strict JSON parser and confirm the array remains valid despite this chunk ending mid-object family.
- Run perf PMU-events validation or generation for the BroadwellX architecture and ensure all 395 events in lines 1-3888 are accepted with expected `Unit` values.
- Check that every `EventName` in this range is unique within the complete file and resolves to the intended `Unit`, `EventCode`, `UMask`, and `Counter` set.
- Exercise `perf list` on a BroadwellX-capable build or generated event database and verify representative names appear: `UNC_I_TRANSACTIONS.READS`, `UNC_Q_RxL_FLITS_G1.DRS_DATA`, `UNC_Q_TxR_BL_DRS_CREDIT_OCCUPANCY.VN_SHR`, `UNC_R3_VN1_CREDITS_REJECT.SNP`, and `UNC_S_RING_BL_USED.UP_ODD`.
- For hardware-level sanity, compare related event ratios on a matching machine: QPI clockticks versus link power-state cycles, flit totals versus data/non-data submasks, occupancy accumulators versus not-empty cycles, and credit reject counts versus used/acquired counts.

### subset-b-006636: lines 3889-4452

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-interconnect.json lines 3889-4452

## Scope

This chunk covers the final 564 lines of the BroadwellX `uncore-interconnect.json` PMU event table. The range starts at the `UNC_S_RxR_BYPASS.BL_BNC` SBOX entry and runs through the closing `]` of the JSON array. It contains only static event records; there are no functions, conditionals, or local runtime state in this source file.

The chunk is source-tree-aligned with perf's PMU event database under `tools/perf/pmu-events/arch/x86/broadwellx`. These records become BroadwellX uncore aliases in generated `pmu-events.c` output, where perf can expose symbolic event names instead of requiring users to spell raw event and umask values.

## Purpose

The purpose of this tail chunk is to describe SBOX and UBOX interconnect monitoring events for Intel BroadwellX-class systems. These are package-scoped uncore events (`"PerPkg": "1"`) that perf can map onto uncore PMUs:

- `Unit: "SBOX"` maps to the generated PMU name `uncore_sbox`.
- `Unit: "UBOX"` maps to the generated PMU name `uncore_ubox`.

The covered SBOX entries describe ring ingress and egress behavior:

- SBOX ingress bypass tracking via `UNC_S_RxR_BYPASS.*` for BL bounce, BL credit, and IV traffic.
- SBOX ingress credit starvation via `UNC_S_RxR_CRD_STARVED.*` for AD bounce, AD credit, AK, BL bounce, BL credit, IFV, and IV traffic.
- SBOX ingress allocation counts via `UNC_S_RxR_INSERTS.*` for AD, AK, BL, and IV classes.
- SBOX ingress occupancy via `UNC_S_RxR_OCCUPANCY.*` for the same traffic classes.
- SBOX Tx ring address-slot usage via `UNC_S_TxR_ADS_USED.AD`, `.AK`, and `.BL`.
- SBOX egress allocations and occupancy via `UNC_S_TxR_INSERTS.*` and `UNC_S_TxR_OCCUPANCY.*`.
- SBOX egress starvation onto the AD, AK, BL, and IV rings via `UNC_S_TxR_STARVED.*`.

The covered UBOX entries describe package-level uncore box behavior:

- Fixed UBOX clockticks via `UNC_U_CLOCKTICKS`.
- Event-message receipt via `UNC_U_EVENT_MSG.DOORBELL_RCVD`.
- Thread-filter match events via `UNC_U_FILTER_MATCH.*`.
- PHOLD cycles via `UNC_U_PHOLD_CYCLES.ASSERT_TO_ACK`.
- Outstanding RACU register requests via `UNC_U_RACU_REQUESTS`.
- UBOX-to-core monitor and error delivery via `UNC_U_U2C_EVENTS.*`.

## Data Model and Important Fields

Each item is a JSON object in the schema consumed by `tools/perf/pmu-events/jevents.py`. Important fields in this chunk are:

- `EventName`: Symbolic perf alias source. `jevents.py` lowercases this value, so `UNC_S_RxR_BYPASS.BL_BNC` becomes a generated event name like `unc_s_rxr_bypass.bl_bnc`.
- `EventCode`: Raw PMU event selector. SBOX entries in this chunk use selectors including `0x1`, `0x2`, `0x3`, `0x4`, `0x11`, `0x12`, `0x13`, and `0x14`; UBOX entries use `0x41`, `0x42`, `0x43`, `0x45`, `0x46`, and fixed `0xff`.
- `UMask`: Unit mask appended to the generated event string when present and non-zero. It differentiates the AD/AK/BL/IV traffic classes and UBOX subevents under a shared event selector.
- `Counter`: Legal counter set. SBOX events use counters `0,1,2,3`; most UBOX programmable events use `0,1`; `UNC_U_CLOCKTICKS` uses `FIXED`.
- `Unit`: Uncore block name used by `jevents.py` to derive the perf PMU name. Unknown/non-special units become `uncore_<unit-lowercase>`.
- `PerPkg`: Marks the event as package-scoped in generated `struct pmu_event.perpkg`.
- `BriefDescription`: Short description used as `struct pmu_event.desc`.
- `PublicDescription`: Longer help text used as `struct pmu_event.long_desc`. Some entries, such as `UNC_S_TxR_ADS_USED.*` and `UNC_U_CLOCKTICKS`, omit `PublicDescription`, making the brief description the main user-facing text.

No entry in this chunk defines metrics, formulas, PEBS precision, MSR filters, port masks, counter masks, or architecture-standard indirection. The generated event string is therefore mostly `event=<EventCode>,umask=<UMask>` plus PMU routing metadata.

## Event Families

### SBOX RxR Bypass and Starvation

Lines 3889-3917 finish the `UNC_S_RxR_BYPASS.*` family. The earlier AD and AK entries are owned by the previous chunk, while this chunk contributes BL bounce (`umask=0x8`), BL credit (`umask=0x4`), and IV (`umask=0x20`). These all share `EventCode 0x12` and describe traffic that bypasses the SBOX ingress queue.

Lines 3918-3987 define `UNC_S_RxR_CRD_STARVED.*`, all with `EventCode 0x14`. These count ingress starvation when an ingress entry cannot forward toward egress because credits are unavailable. The masks split the condition by ring/message class:

- AD credit: `0x1`.
- AD bounce: `0x2`.
- BL credit: `0x4`.
- BL bounce: `0x8`.
- AK: `0x10`.
- IV: `0x20`.
- IFV: `0x40`.

These events are useful when diagnosing ring pressure where ingress work is present but cannot make progress because the downstream path lacks credit.

### SBOX RxR Inserts and Occupancy

Lines 3988-4047 define `UNC_S_RxR_INSERTS.*` with `EventCode 0x13`. The family counts allocations into the SBOX ingress, which queues requests received from the ring. The covered masks are AD credit, AD bounce, AK, BL credit, BL bounce, and IV.

Lines 4048-4107 define `UNC_S_RxR_OCCUPANCY.*` with `EventCode 0x11`. These occupancy events accumulate how occupied the same ingress buffers are for each traffic class. The distinction between inserts and occupancy matters: inserts are event counts, while occupancy-style events are cycle-accumulated queue-depth signals and need interpretation against elapsed cycles or a clock event.

### SBOX TxR Address Use, Inserts, Occupancy, and Starvation

Lines 4108-4134 define `UNC_S_TxR_ADS_USED.AD`, `.AK`, and `.BL` with `EventCode 0x4` and masks `0x1`, `0x2`, and `0x4`. These records lack long descriptions, so downstream help output has less context than the surrounding SBOX families. Based on the names and placement, they monitor address-slot usage on Tx ring classes.

Lines 4135-4194 define `UNC_S_TxR_INSERTS.*` with `EventCode 0x2`. These count allocations into SBOX egress queues for requests destined for the ring.

Lines 4195-4254 define `UNC_S_TxR_OCCUPANCY.*` with `EventCode 0x1`. These mirror the egress side of the ingress occupancy family and describe how occupied egress buffers are for AD, AK, BL, and IV traffic classes.

Lines 4255-4294 define `UNC_S_TxR_STARVED.*` with `EventCode 0x3`. They count egress injection starvation when egress cannot send a transaction onto the AD, AK, BL, or IV ring for a long time. These are a direct signal for ring-side backpressure at the point of injection.

### UBOX Clock, Filter, PHOLD, RACU, and U2C Events

Lines 4295-4302 define `UNC_U_CLOCKTICKS`, a fixed-counter UBOX clocktick event with `EventCode 0xff`. It is the natural denominator for UBOX rates and occupancy-like interpretations.

Lines 4303-4312 define `UNC_U_EVENT_MSG.DOORBELL_RCVD`, which counts received Virtual Logical Wire legacy messages. Its long description states that filtering uses `NCUPMONCTRLGLCTR.ThreadID`; this register-level filter is not encoded as a JSON `Filter` field, so consumers need platform knowledge or perf syntax support outside this record.

Lines 4313-4352 define `UNC_U_FILTER_MATCH.*` variants with `EventCode 0x41`: `ENABLE`, `DISABLE`, `U2C_ENABLE`, and `U2C_DISABLE`. They describe per-thread filter matches with or without filter enablement, again referring to `NCUPMONCTRLGLCTR.ThreadID`.

Lines 4353-4362 define `UNC_U_PHOLD_CYCLES.ASSERT_TO_ACK`, a PHOLD cycle counter with a source CoreID filter mentioned in text.

Lines 4363-4371 define `UNC_U_RACU_REQUESTS`, which counts outstanding register requests within the message-channel tracker.

Lines 4372-4451 define `UNC_U_U2C_EVENTS.*` with `EventCode 0x43`. The masks split monitor/error events delivered from uncore toward cores:

- `MONITOR_T0`: `0x1`.
- `MONITOR_T1`: `0x2`.
- `LIVELOCK`: `0x4`.
- `LTERROR`: `0x8`.
- `CMC`: `0x10`.
- `UMC`: `0x20`.
- `TRAP`: `0x40`.
- `OTHER`: `0x80`, described as PREQ, PSMI, P2U, Thermal, PCUSMI, and PMI.

## Control Flow and Integration

This JSON file has no direct control flow. Its integration path is build-time and runtime data plumbing:

1. `tools/perf/pmu-events/README` defines the PMU event database layout: architecture model directories contain topic JSON files, and `jevents` processes them before perf itself is built.
2. `tools/perf/pmu-events/jevents.py` reads JSON arrays with `json.load(..., object_hook=JsonEvent)`.
3. `JsonEvent.__init__()` maps fields from each object into generated event attributes. For this chunk, `EventName` becomes lowercase `name`, `BriefDescription` becomes `desc`, `PublicDescription` becomes `long_desc`, `Unit` becomes an uncore PMU name, `PerPkg` becomes package aggregation metadata, `EventCode` becomes `event=<value>`, and non-zero `UMask` becomes `umask=<value>`.
4. `JsonEvent.to_c_string()` serializes the parsed event into generated compact C string-table data for `pmu-events.c`.
5. At perf runtime, APIs declared in `tools/perf/pmu-events/pmu-events.h` expose the generated tables through `perf_pmu__find_events_table()`, `pmu_events_table__for_each_event()`, `pmu_events_table__find_event()`, and `pmu_events_table__num_events()`.
6. User commands such as `perf list` and `perf stat -e <event>` can then discover or resolve aliases for the matching BroadwellX uncore PMUs.

The mapfile for x86 selects model directories such as `broadwellx`; this file's events are part of that model's uncore interconnect topic rather than the core CPU event table.

## State and Persistence

There is no mutable software state in the chunk. The persistent contract is the static mapping from symbolic names to hardware PMU event selectors and masks.

The important persisted semantics are:

- The SBOX/UBOX hardware selector and mask values are treated as authoritative for BroadwellX uncore PMU programming.
- `PerPkg` tells perf these are package-level uncore events, which affects aggregation and alias display.
- `Counter` limits which hardware counters can count an event, but the JSON-to-`pmu_event` conversion primarily carries this as event metadata for the generated table and help text path rather than implementing scheduling logic in this file.
- Description strings persist into generated help output and into programmatic event listings.

Because this is source data, any incorrect event code, mask, unit, or name persists into all generated perf binaries built from this tree.

## Dependencies

The chunk depends on:

- The perf PMU event JSON schema recognized by `jevents.py`.
- Python JSON parsing during the `jevents` build step.
- The BroadwellX x86 mapfile entries that route this model to the `broadwellx` directory.
- Linux perf uncore PMU names matching generated unit names such as `uncore_sbox` and `uncore_ubox`.
- The kernel's uncore PMU drivers exposing compatible SBOX and UBOX PMUs and accepting the event/umask encodings listed here.
- Runtime lookup helpers declared in `pmu-events.h` and used by perf list/stat tooling.

There are no local includes or code-level APIs in the JSON itself, but the field names are an API between the static data and the generator.

## Risks

- The chunk begins in the middle of the complete `UNC_S_RxR_BYPASS.*` family. A whole-file report must reconcile the AD and AK bypass records from the previous chunk with the BL/IV records here.
- `EventCode`/`UMask` errors are hard failures in practice: perf may still create an alias, but it would program the wrong hardware counter and produce misleading performance data.
- `Unit` is semantically important. A typo would route an event to the wrong generated PMU name, likely making aliases invisible or unusable for the real BroadwellX uncore device.
- Several descriptions contain hardware-register filtering guidance, such as `NCUPMONCTRLGLCTR.ThreadID` and source CoreID filters, but the JSON records do not encode those filters in machine-readable `Filter` fields. Users may see the event but still need separate knowledge to apply thread/core filtering correctly.
- `UNC_S_TxR_ADS_USED.*` records have only terse brief descriptions and no `PublicDescription`, increasing the chance of user confusion and reducing generated documentation quality.
- Occupancy events and insertion events share similar traffic-class naming but have different interpretation. Treating occupancy as a simple transaction count can lead to wrong conclusions.
- Counter constraints differ between SBOX, UBOX programmable counters, and the UBOX fixed counter. Alias availability may depend on perf scheduling and the physical PMU counter layout.
- The final `]` closes the entire JSON array. Any edit near this chunk can break parsing for the whole BroadwellX interconnect topic.

## Test and Validation Signals

Useful validation signals for this chunk are:

- Run the perf PMU event generation path and ensure `jevents.py` parses `arch/x86/broadwellx/uncore-interconnect.json` without JSON exceptions.
- Validate the generated event strings for sample aliases. Examples should include `UNC_S_RxR_CRD_STARVED.IFV` producing `event=0x14,umask=0x40`, `UNC_S_TxR_STARVED.IV` producing `event=0x3,umask=0x8`, and `UNC_U_U2C_EVENTS.OTHER` producing `event=0x43,umask=0x80`.
- Build perf and run PMU event tests, especially the tests under `tools/perf/tests/pmu-events.c` that compare generated tables and event lookup behavior.
- Use `perf list` on a BroadwellX-capable environment, or with generated table inspection in a build tree, to confirm the SBOX and UBOX aliases appear under the expected uncore PMUs.
- On real hardware, run low-impact `perf stat -a -e` checks against representative aliases such as `unc_s_rxr_inserts.iv`, `unc_s_txr_starved.ad`, and `unc_u_clockticks` to verify event resolution and counter scheduling.
- For documentation quality, inspect `perf list --details` output for entries without `PublicDescription`, especially `UNC_S_TxR_ADS_USED.*`, to make sure terse descriptions are still acceptable.
