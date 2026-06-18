# Research: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-interconnect.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006713`: lines 1-6508, `Docs/researches/chunks/subset-b-006713_research.md`
- `subset-b-006714`: lines 6509-7626, `Docs/researches/chunks/subset-b-006714_research.md`

## Chunk Research

### subset-b-006713: lines 1-6508

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-interconnect.json lines 1-6508

## Scope

This chunk covers the beginning of the Sapphire Rapids `uncore-interconnect.json` PMU event table through line 6508. The chunk starts at the JSON array opener and runs from `UNC_I_CACHE_TOTAL_OCCUPANCY.MEM` through the start of the next UPI receive-link event object. The last complete event in this chunk is `UNC_UPI_RxL_ANY_FLITS.SLOT2` at lines 6498-6505; line 6508 is inside the following `UNC_UPI_RxL_BASIC_HDR_MATCH.NCB` object, so that object must be completed by the next chunk before final per-file synthesis.

## Purpose

The file is declarative perf metadata, not executable Ceph client logic. It contributes Sapphire Rapids uncore interconnect event definitions consumed by Linux perf's PMU event table generation and lookup code under `tools/perf/pmu-events`. Each object maps a public perf event name to the hardware event selector fields needed to program an uncore PMU counter.

Within this chunk, the table describes five uncore units:

- `IRP`: 54 events covering inbound/outbound IIO request path occupancy, snoop responses, fast-path/secondary-cache behavior, Tx credit stalls, and Tx queue inserts.
- `M2M`: 186 events covering mesh-to-memory direct-to-core/direct-to-UPI behavior, directory hit/miss/update states, iMC reads/writes by channel and target media, prefetch CAM behavior, trackers, write queues, and near-memory tag hits.
- `M3UPI`: 324 events covering the mesh-to-UPI bridge, including CHA/M2/UPI peer credit empties, VN0/VN1 arbitration, ingress and egress flow queues, flit generation, header/data flit stalls, remote VNA credits, writeback pending/occupancy comparisons, and XPT prefetch flow.
- `MDF`: 14 events covering CRS transmit-ring inserts, vertical-ring bounce cycles, and fast/distress signal assertion at the SBO ingress.
- `UPI`: 42 complete events covering UPI clockticks, direct packet attempts, flow queue/VNA credit shortage, M3 bypass/RXQ block reasons, link power modes, L1 request ack/nack, M3 slot2 requests, Rx L0/L0p/L1 cycles, and Rx link any-flit categories.

## Data Model And Important Fields

Every complete event object in this chunk has `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, and `Unit`. Most events include `UMask`; events without `UMask` are base events whose event code alone identifies the signal. Many entries also include `PublicDescription`, which perf can expose in richer event descriptions.

The parsed complete portion through `UNC_UPI_RxL_ANY_FLITS.SLOT2` contains 620 complete event objects. All 620 are package-scoped with `"PerPkg": "1"`. 597 are marked `"Experimental": "1"`, so tools and users should treat much of this table as potentially less stable than architected events. 354 have `PublicDescription`. Optional filter fields appear on a small subset: `FCMask` and `PortMask` each occur 15 times, mostly on M2M iMC read/write aggregate/channel entries and one M3UPI flow queue bypass entry.

`Counter` constrains which programmable counters may count the event. In this chunk the values are:

- `"0,1"` for all 54 IRP events.
- `"0,1,2,3"` for 311 events, mostly M2M, MDF, and many M3UPI/UPI events.
- `"0"` for 231 M3UPI events whose arbitration, occupancy, or credit signals are limited to counter 0.
- `"0,1,2"` for 24 M3UPI bypass/held events.

`EventName` is the integration key exposed to perf users and follows the normal uncore naming style: a base event family plus a dot-qualified subevent such as `UNC_M2M_DIRECTORY_UPDATE.I_TO_S_HIT_NON_PMM` or `UNC_M3UPI_RxC_ARB_LOST_VN0.BL_WB`. Repeated `EventCode` values with different `UMask` values define the subevents under one hardware event selector.

## Event Families

The IRP section defines IIO request processing events. It starts with total inbound coherent-memory occupancy and clockticks, then groups FAF full/insert/occupancy/transaction signals, aggregate IRP inbound/outbound insert masks, fast-path and secondary-cache miscellaneous events, MESI-sensitive snoop responses, a write-prefetch transaction event, TxC BL/AK egress queue inserts/full/occupancy events, TxR2 AD/BL credit stalls, and TxS outbound data/request occupancy. Several events explicitly recommend deriving average latency from paired insert and occupancy accumulators.

The M2M section is broad and memory-system oriented. It records direct-to-core and direct-to-UPI taken/not-taken/override cases, directory hit/miss/update states for clean/dirty and I/S/A/P states, egress ordering stalls, iMC read/write traffic by channel, target, isoch/full/partial type, PMM/DDR-as-cache/DDR-as-memory distinctions, prefetch CAM inserts/drops/merges/occupancy/response misses, RxC AD ingress inserts/occupancy, near-memory tag hits and misses, tracker insert/occupancy, WPQ flush/no-credit conditions, and posted/nonposted write tracker occupancy/inserts. This section is important for NUMA, PMM, near-memory cache, and multi-socket directory analysis.

The M3UPI section describes the bridge between mesh and UPI link-layer behavior. It includes high-level clockticks and direct packet sends, CBox/M2/UPI peer credit-empty events, multi-slot receive flits, detailed VN0/VN1 arbitration lost/no-credit/no-request events across AD and BL message classes, ingress bypass and credit occupancy, cycles-not-empty and occupancy accumulators for VN queues, header/data flit generation and not-sent causes, remote VNA credit thresholds and allocation choices, TxC AD/BL/AK flow queue cycles/inserts/occupancy/arbitration failures, VN credit used/no-credit signals, writeback pending/occupancy comparisons, and XPT prefetch arrival/bypass/arbitration/drop states. Many families mirror one pattern across VN0/VN1 and message classes (`REQ`, `SNP`, `RSP`, `WB`, `NCB`, `NCS`), which is useful but also makes naming consistency critical.

The MDF section is small and focuses on tile/ring fabric signals: CRS TxR inserts by message kind (`AD_BNC`, `AD_CRD`, `BL_BNC`, `BL_CRD`, `AK`, `AKC`, `IV`), vertical ring bounce cycles by message kind, and fast/asserted distress cycles for AD bounceable and BL credited paths.

The UPI section begins the physical/link-layer UPI unit definitions. Complete entries in this chunk include clockticks, direct attempts (`D2C`, `D2K`), flow queue no-VNA-credit thresholds, M3 bypass/RXQ blocked reasons, PHY init cycles, L1 request ack/nack, Rx/TX direction-sensitive power states, and receive-link any-flit filters for `DATA`, `LLCRD`, `LLCTRL`, `NULL`, `PROTHDR`, and slots 0-2. The chunk stops immediately after these `UNC_UPI_RxL_ANY_FLITS.*` events.

## Control Flow And Runtime Integration

There is no in-file control flow. Runtime behavior is supplied by perf's PMU event tooling: build-time scripts parse this JSON, validate the event schema, generate compact C tables, and runtime perf commands use the generated tables to resolve event aliases for CPUs matching Sapphire Rapids. The practical flow is:

1. Select Sapphire Rapids event JSONs under `arch/x86/sapphirerapids`.
2. Parse each event object and retain fields such as name, event code, unit mask, counter mask, unit, package scope, and descriptions.
3. Generate/lookup aliases so users can request events by `EventName`.
4. Program the corresponding uncore PMU instance using `EventCode`, `UMask`, optional filter masks, and counter constraints.

Because the file is table data, ordering is mostly for maintainability and generated output stability. The event groups are arranged by `Unit` and then by hardware block/family, which helps reviewers spot missing masks or inconsistent subevent naming.

## State And Persistence

The JSON file itself is the persistent source of truth for these uncore event aliases. It does not mutate state and has no runtime persistence behavior. Its data is persisted into perf-generated event tables during the perf build. The `"PerPkg": "1"` field on all complete events in this chunk indicates package-level uncore scoping, so collection and aggregation semantics differ from per-core PMU events.

The chunk contains multiple occupancy and cycles-not-empty accumulator events. These do not store state in the JSON, but their semantics depend on hardware accumulating cycles or queue depth over the enabled interval. Several descriptions imply users should pair insert/allocation events with occupancy events to compute latency or average occupancy.

## Dependencies And Integration Points

This file depends on perf's PMU event JSON schema and the Sapphire Rapids x86 model selection path. The important integration contracts are field names, string encodings, and hardware selector values:

- `EventName` must remain unique enough for perf alias resolution within the PMU unit namespace.
- `Unit` must match perf's uncore PMU naming for Sapphire Rapids (`IRP`, `M2M`, `M3UPI`, `MDF`, `UPI` in this chunk).
- `EventCode`, `UMask`, `FCMask`, and `PortMask` must be valid strings accepted by perf's event parser and must match the hardware programming model.
- `Counter` restricts scheduling; wrong counter masks can cause perf to accept an event that cannot actually be scheduled, or reject one that should be valid.
- `Experimental` affects how downstream documentation and users interpret stability.

The table also integrates conceptually with adjacent JSON files in the same architecture directory. A final per-file report should compare naming, unit coverage, and schema conventions across sibling Sapphire Rapids event files if the merge lane needs whole-directory consistency.

## Risks And Edge Cases

The line-range boundary cuts through `UNC_UPI_RxL_BASIC_HDR_MATCH.NCB`. This chunk report intentionally treats only events through `UNC_UPI_RxL_ANY_FLITS.SLOT2` as complete. The final merge must incorporate the next chunk before making whole-file claims about UPI or UBOX coverage.

There are many mechanically patterned event families, so copy/paste drift is a real risk. In this chunk, examples to review carefully during final reconciliation include M3UPI BL flow queue insert/occupancy descriptions whose `BriefDescription` text can appear swapped relative to event suffixes, upper/lowercase variation in `EventCode` strings (`0x1C` versus `0x1c`, `0x5E` versus `0x5e`), and mixed suffix spelling such as `CHN0`/`CH0` or `TO_NMCache`/`TO_NMCACHE`. Perf generally parses hex case-insensitively, but inconsistent names and descriptions affect user-facing documentation and searchability.

Most events are marked experimental, which creates compatibility risk for scripts that depend on stable event availability. Users measuring production systems should confirm event behavior on the target stepping and kernel/perf version.

Several events have aggregate masks (`ANY`, `ALL`, all-channel, all-slot, or multi-bit UMask values) alongside finer-grained subevents. Consumers must avoid double-counting when combining aggregate and component events in derived metrics.

Counter constraints are uneven. M3UPI has many counter-0-only events and some counter-0-through-2 events; scheduling groups that assume four generic counters may fail or multiplex unexpectedly.

## Test Signals

Useful validation for this chunk is schema-focused rather than unit-test driven:

- `jq` successfully parses the full JSON file, and the complete portion through line 6505 contains 620 complete events.
- A schema check should require every object to have `EventName`, `EventCode`, `BriefDescription`, `Counter`, `Unit`, and `PerPkg`.
- Generated perf tables should include aliases for representative events from each complete unit in this chunk, for example `UNC_I_CLOCKTICKS`, `UNC_M2M_DIRECTORY_UPDATE.ANY`, `UNC_M3UPI_RxC_HDR_FLIT_NOT_SENT.NO_TXQ_CRD`, `UNC_MDF_CRS_TxR_INSERTS.AD_BNC`, and `UNC_UPI_RxL_ANY_FLITS.SLOT2`.
- Runtime smoke tests on Sapphire Rapids hardware can use `perf list` to confirm alias visibility and `perf stat -e` with low-risk clocktick or flit events to confirm scheduling. Counter-constrained M3UPI events should be tested both alone and in groups to catch bad `Counter` masks.
- Documentation checks should compare `BriefDescription` and `PublicDescription` against event suffixes for patterned VN0/VN1 and NCB/NCS families, because many entries are user-facing and highly repetitive.

### subset-b-006714: lines 6509-7626

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-interconnect.json lines 6509-7626

## Scope

This chunk covers the tail of the Sapphire Rapids x86 uncore interconnect PMU event JSON file. The requested line range starts inside the first listed event object at `UNC_UPI_RxL_BASIC_HDR_MATCH.NCB` and continues through the final closing bracket of the file. The complete first object begins just before the chunk boundary, so this document treats that receive-header-match event as part of the chunk because its `EventCode`, `EventName`, descriptions, `UMask`, and `Unit` fields are in range.

The covered event families are:

- UPI receive-link header matching, flit counting, RxQ bypass/allocation/occupancy, CRC/LLR, virtual-network credit consumption, and slot-bypass events.
- UPI transmit-link L0/L0p power-state, clock-active, arbitrary flit, basic header match, flit count, TxQ bypass/allocation/occupancy, and VNA credit-return events.
- UBOX message, M2U channel, PHOLD, RACU DRNG, and RACU request events.

This is data, not executable code. It is a JSON array of perf PMU event descriptions consumed by the `tools/perf/pmu-events` generator for the `sapphirerapids` model selected in `arch/x86/mapfile.csv`.

## Purpose

The chunk provides event metadata that lets perf expose named Sapphire Rapids uncore events for inter-socket and uncore-fabric analysis. Each object maps a human-readable event name to hardware selector fields such as `EventCode`, `UMask`, `Counter`, `Unit`, and package scope. Perf turns this JSON into generated `struct pmu_event` tables so users can run commands such as `perf list`, `perf stat -e <event>`, or scripts using event aliases instead of raw uncore encodings.

The UPI entries diagnose link traffic and link health: valid flits, data versus non-data flits, protocol headers, null/idles, LLCRD/LLCTRL traffic, receive and transmit buffer pressure, credit consumption, CRC errors, link-layer retry requests, and link power states. The UBOX entries diagnose socket-level uncore message paths, message classes, credit overflow or empty/full cycles, processor-hold timing, and random-number request activity.

## Important Data Fields

Each event object uses the standard perf PMU JSON schema:

- `EventName` is the alias exposed to perf, for example `UNC_UPI_RxL_FLITS.DATA`, `UNC_UPI_TxL_POWER_CYCLES`, or `UNC_U_EVENT_MSG.MSI_RCVD`.
- `EventCode` is the hexadecimal hardware event selector. Related event variants share a selector and differ by `UMask`.
- `UMask` selects subevents such as slots, flit kinds, message classes, or queue states. Some base events do not have a `UMask`.
- `Counter` declares usable counter indices. UPI events generally use counters `0,1,2,3`; UBOX message events use `0,1`; many UBOX miscellaneous events are restricted to counter `0`.
- `Unit` identifies the PMU unit. This chunk uses `UPI` for Ultra Path Interconnect link events and `UBOX` for socket/global uncore box events.
- `PerPkg` marks the events as package-scoped.
- `Experimental` marks many aliases as less stable or less validated than ordinary public event names.
- `PublicDescription` provides longer user-facing guidance. Several sparse aliases have only `BriefDescription`, so generated perf help may be less explanatory for those events.
- `FCMask` and `PortMask` appear on `UNC_UPI_RxL_CREDITS_CONSUMED_VNA`, both set to zero, which is a special-case filter encoding included in the source event table.

There are no functions, types, classes, or runtime APIs in this JSON file. The important API surface is the schema contract consumed by `pmu-events/jevents.py` and exposed through generated `pmu-events.c`, `pmu-events.h`, and perf’s PMU event lookup helpers.

## Event Families

### UPI Receive Link

The receive-link section starts with `UNC_UPI_RxL_BASIC_HDR_MATCH.*` entries for Non-Coherent Bypass (`NCB`) and Non-Coherent Standard (`NCS`) traffic, with opcode-matching variants. These use `EventCode` `0x05` and `UMask` values `0xe`, `0x10e`, `0xf`, and `0x10f`. Their descriptions document a packed `UMask` interpretation for message class, opcode, local/remote direction, data/non-data header selection, dual/single-slot selection, and opcode/message-class enable bits. Link-layer control traffic is explicitly excluded from those header matches.

`UNC_UPI_RxL_BYPASSED.SLOT0..SLOT2`, `UNC_UPI_RxL_INSERTS.SLOT0..SLOT2`, and `UNC_UPI_RxL_OCCUPANCY.SLOT0..SLOT2` describe receive flit-buffer behavior. Bypass counts are expected to be common when incoming flits can pass directly to the egress/ring path. Inserts and occupancy indicate buffering and can be paired to estimate average RxQ lifetime or queue pressure.

`UNC_UPI_RxL_CRC_ERRORS` and `UNC_UPI_RxL_CRC_LLR_REQ_TRANSMIT` provide link reliability signals. CRC errors count received flits whose CRC detected corruption. LLR request transmission counts link-layer retry requests and should generally be less than or equal to CRC errors because repeated errors can be coalesced while an acknowledgement is pending.

`UNC_UPI_RxL_CREDITS_CONSUMED_VN0`, `VN1`, and `VNA` track receive-buffer credit consumption for UPI virtual networks. The VNA entry includes explicit zero `FCMask` and `PortMask` fields, unlike the VN0/VN1 entries.

`UNC_UPI_RxL_FLITS.*` provides typed receive flit accounting using `EventCode` `0x03`. The aliases distinguish all data, all null, data, idle, LLCRD, LLCTRL, non-data, null, protocol header, and slot 0/1/2 components. The descriptions explain that these show legal flit time, hiding L0p/L0c impact, and that data flits consume all slots while slot masks determine whether they count as 0 through 3 increments.

`UNC_UPI_RxL_SLOT_BYPASS.*` provides lower-level slot-to-RxQ bypass combinations such as `S0_RXQ1`, `S1_RXQ2`, and `S2_RXQ1`. These aliases have minimal descriptions, so consumers must rely on Intel uncore documentation for exact slot/RxQ routing semantics.

### UPI Transmit Link

`UNC_UPI_TxL0P_CLK_ACTIVE.*` uses `EventCode` `0x2a` and `UMask` values for configuration/control, RxQ, RxQ bypass, RxQ credit, TxQ, retry, DFX, and spare internal clock-active reasons while the transmit direction is in or around L0p behavior.

`UNC_UPI_TxL0P_POWER_CYCLES`, `UNC_UPI_TxL0P_POWER_CYCLES_LL_ENTER`, `UNC_UPI_TxL0P_POWER_CYCLES_M3_EXIT`, and `UNC_UPI_TxL0_POWER_CYCLES` track transmit-direction link power states. The L0p description is explicit that L0p disables half the UPI lanes to save power, reducing bandwidth and increasing snoop/data latency. The L0 event is the full-performance link-layer state; edge detection can count state entries, and Tx/Rx directions can be in different power states.

`UNC_UPI_TxL_ANY_FLITS.*` uses `EventCode` `0x4A` for broad transmit flit classification by data, LLCRD, LLCTRL, null, protocol header, and slots 0 through 2. These aliases are mostly brief-name-only entries and complement the more descriptive `UNC_UPI_TxL_FLITS.*` family.

`UNC_UPI_TxL_BASIC_HDR_MATCH.*` mirrors the receive header-match family on the transmit path, using `EventCode` `0x04` and the same NCB/NCS and opcode-match `UMask` pattern. The same warning applies: message-class and opcode enable bits must be configured consistently, and link-layer controls are excluded.

`UNC_UPI_TxL_BYPASSED`, `UNC_UPI_TxL_INSERTS`, and `UNC_UPI_TxL_OCCUPANCY` describe Tx flit-buffer behavior. The descriptions tie TxQ use to L0p and LLR retry behavior; bypass means a flit could pass directly out the UPI link, while inserts and occupancy indicate buffering and latency.

`UNC_UPI_TxL_FLITS.*` uses `EventCode` `0x02` for valid transmit flits: all data, all LLCRD, all LLCTRL, all null, all protocol headers, data, idle, LLCRD, LLCTRL, non-data, null, protocol header, and slots 0 through 2. The masks are parallel to the receive flit masks (`0xf`, `0x27`, `0x8`, `0x47`, `0x10`, `0x40`, `0x97`, `0x20`, `0x80`, and slot masks `0x1`, `0x2`, `0x4`). Some text has apparent source typos such as `ProtDDR` in the all-protocol-header description, so documentation consumers should not treat descriptions as normative encodings.

`UNC_UPI_VNA_CREDIT_RETURN_BLOCKED_VN01` and `UNC_UPI_VNA_CREDIT_RETURN_OCCUPANCY` expose VNA credit-return pressure. The occupancy description counts VNA credits on the receive side waiting to be returned across the link.

### UBOX

`UNC_U_EVENT_MSG.*` uses `EventCode` `0x42` and counts received uncore message classes: virtual logical wire, MSI, IPI, doorbell, and interrupt-priority messages. These are package-level UBOX events with counters `0,1`.

`UNC_U_M2U_MISC1.*`, `UNC_U_M2U_MISC2.*`, and `UNC_U_M2U_MISC3.*` are counter-0-only miscellaneous channel-pressure events. They cover receive cycles not empty for CBO/UPI NCB/NCS paths, transmit credit-overflow cycles for CBO/UPI and VN0 NCB/NCS paths, empty/full BL cycles, empty AK/AKC/BL cycles, and full AK/AKC/BL cycles.

`UNC_U_PHOLD_CYCLES.ASSERT_TO_ACK` counts PHOLD assert-to-ack cycles on UBOX counters `0,1`.

`UNC_U_RACU_DRNG.*` exposes DRNG-related RACU activity for `RDRAND`, `RDSEED`, and prefetch-buffer-empty states, all restricted to counter `0`. `UNC_U_RACU_REQUESTS` counts outstanding RACU register requests within the message channel tracker.

## Control Flow

This chunk has no runtime control flow. Build-time control flow is provided by perf’s PMU event generator:

1. `tools/perf/pmu-events/Build` includes PMU JSON and CSV inputs.
2. `pmu-events/jevents.py` reads JSON files such as this one, converts each object into an internal `JsonEvent`, compresses event strings, and emits generated C tables.
3. `arch/x86/mapfile.csv` maps `GenuineIntel-6-8F` to the `sapphirerapids` model directory, making this file part of the event table selected for Sapphire Rapids systems.
4. Runtime perf lookup helpers find the generated event table for the current CPU or PMU and expose the aliases through list, stat, and Python interfaces.

Within the data itself, related event objects are grouped by naming convention and by shared `EventCode`. Perf does not execute these objects in order, but ordering affects generated table layout and human review of event families.

## State and Persistence

The JSON file stores static source-tree metadata. It does not persist runtime state, allocate memory, or change hardware by itself.

The hardware state represented by these entries is transient PMU counter state and event-select programming in Sapphire Rapids uncore boxes. When a user selects one of these aliases, perf programs the appropriate UPI or UBOX uncore PMU counter with the event code, umask, package scope, and any applicable counter constraints. The counts then reflect hardware behavior during the measurement interval, such as flits observed, queue occupancy accumulated over cycles, CRC errors, retry requests, credit-return occupancy, power-state cycles, or UBOX message/channel state.

Many events are accumulation counters rather than simple transaction counts. Occupancy events accumulate queue depth over cycles; power-cycle events count cycles in a state; PHOLD and M2U full/empty events count cycles; flit and message events count occurrences. Downstream analysis must divide by an appropriate duration, clock, flit count, or companion event when computing rates, average queue occupancy, or average lifetime.

## Dependencies and Integration Points

This chunk depends on the perf PMU event schema and generator:

- `tools/perf/pmu-events/jevents.py` defines supported event attributes, reads JSON, and generates C event tables.
- `tools/perf/pmu-events/pmu-events.h` defines the generated `struct pmu_event` interface used by perf.
- `tools/perf/pmu-events/Build` wires JSON and CSV files into the perf build.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` associates Sapphire Rapids family/model `GenuineIntel-6-8F` with this model directory.
- `tools/perf/builtin-list.c`, `tools/perf/util/python.c`, and `tools/perf/python/ilist.py` consume generated names and descriptions for CLI and Python-visible event listings.

The hardware integration point is the Linux perf uncore PMU support for Intel UPI and UBOX units. The `Unit` strings must match PMU naming expected by perf’s uncore discovery and event lookup machinery. Counter constraints in `Counter` must also match what the underlying PMU driver can program.

## Risks

- Event encodings are hardware ABI. A wrong `EventCode`, `UMask`, `Counter`, `Unit`, `FCMask`, or `PortMask` can silently collect the wrong signal or fail to program on real Sapphire Rapids systems.
- Many entries are marked `Experimental`. Users and tests should expect possible naming, documentation, or validation gaps compared with stable public events.
- Header-match events have packed, multi-field `UMask` semantics. Combining message-class disable with opcode enable is specifically warned against in the descriptions; tools that synthesize masks must preserve those constraints.
- Flit-count events combine slot masks and type masks. Data flits consume all slots, and counts can vary from zero to three depending on enabled slot bits, so naive event comparisons can misinterpret bandwidth.
- Occupancy and cycle events are not raw transaction counts. Treating accumulated occupancy or full/empty cycles as inserts can produce invalid latency or pressure conclusions.
- Several aliases have sparse descriptions, especially slot-bypass, TxL0P internal clock-active, M2U miscellaneous, and RACU DRNG events. External hardware documentation is needed for precise interpretation.
- Text quality issues exist in source descriptions, including typos such as `waitng`, `bypasssed`, and `ProtDDR`. These are documentation risks, not necessarily encoding risks, but they propagate into generated perf help.
- The range begins inside an event object, and the file ends at the JSON array close. Chunk-level reporting must be reconciled with the previous chunk for the full context around `UNC_UPI_RxL_BASIC_HDR_MATCH.NCB`.

## Test and Validation Signals

Useful validation for this chunk includes:

- JSON syntax validation with `jq` or Python `json.load` for the full `uncore-interconnect.json` file.
- A perf build that regenerates `pmu-events.c` through `pmu-events/jevents.py`; this catches unsupported attributes, malformed objects, and generator regressions.
- `perf list` on a Sapphire Rapids host should expose representative aliases from this chunk, including `UNC_UPI_RxL_FLITS.DATA`, `UNC_UPI_TxL_FLITS.DATA`, `UNC_UPI_TxL_BYPASSED`, `UNC_UPI_TxL0P_POWER_CYCLES`, and `UNC_U_EVENT_MSG.MSI_RCVD`.
- `perf stat` smoke tests should verify that UPI events can program counters `0,1,2,3` and UBOX counter-limited events honor their `Counter` restrictions.
- Link-traffic tests should compare Tx and Rx flit families under local-only workloads, NUMA remote-memory workloads, and inter-socket traffic generators.
- Link-health tests should monitor CRC and LLR request events; CRC errors should normally remain near zero on healthy links.
- Queue-pressure tests should correlate bypass, inserts, occupancy, and not-empty/full cycle events under high UPI bandwidth or L0p-heavy workloads.
- Power-management tests should compare L0 and L0p cycle events with platform link-power policy changes.
- UBOX message tests should observe MSI/IPI/doorbell/VLW event movement under interrupt-heavy, IPI-heavy, and device-interrupt workloads.
