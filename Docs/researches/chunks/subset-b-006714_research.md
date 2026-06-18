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
