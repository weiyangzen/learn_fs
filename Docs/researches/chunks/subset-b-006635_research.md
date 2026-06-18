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
