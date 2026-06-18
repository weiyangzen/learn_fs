# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-interconnect.json lines 11876-13758

## Scope

This chunk is the tail of the Skylake-X uncore interconnect PMU event JSON table used by Linux `perf`/pmu-events tooling. It covers lines 11876-13758 of `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-interconnect.json` and ends the top-level JSON array. The first line in this chunk is inside the prior `UNC_M3UPI_VN0_CREDITS_USED.WB` object, so that object must be merged with the previous chunk for a complete per-file report.

The visible chunk contains 180 event-name records: 18 `M3UPI`, 1 deprecated `M2M` alias, 149 `UPI`, and 12 `UBOX` records. Most records are marked `PerPkg: "1"`; 159 are marked `Experimental`, and 25 are marked `Deprecated`.

## Purpose

The file is declarative data for hardware performance events rather than executable code. Each object describes one named uncore performance event for Intel Skylake-X interconnect blocks, mapping a human-facing `EventName` to the event selector fields and metadata needed by perf:

- `EventCode` selects the hardware event.
- `UMask` refines the event to a channel, slot, message class, opcode mode, or subcondition.
- `Counter` lists usable counter slots, including `FIXED` for `UNC_U_CLOCKTICKS`.
- `Unit` binds the event to an uncore PMU unit such as `M3UPI`, `UPI`, `UBOX`, or the deprecated `M2M` alias.
- `BriefDescription` and `PublicDescription` provide CLI/help text and formula context for users interpreting counts.
- `Experimental`, `Deprecated`, and `PerPkg` communicate stability, replacement paths, and package-level scope to consumers.

## Event Groups In This Chunk

The chunk starts with M3UPI virtual-network credit pressure events. `UNC_M3UPI_VN0_NO_CREDITS.*`, `UNC_M3UPI_VN1_CREDITS_USED.*`, and `UNC_M3UPI_VN1_NO_CREDITS.*` all use counters `0,1,2` and describe credit consumption or stalls for message classes on AD/BL paths: request (`REQ`), snoop (`SNP`), response (`RSP`), writeback/data response (`WB`/`NCB` naming), and non-coherent standard/broadcast (`NCS`/`NCB`). These events are useful for diagnosing fallback from shared VNA credits to reserved VN0/VN1 credits and for identifying cycles where reserved credits are exhausted.

The single `UNC_NoUnit_TxC_BL.DRS_UPI` record is explicitly deprecated and points to `UNC_M2M_TxC_BL.DRS_UPI`. It remains in the table as a compatibility alias with `Unit: "M2M"`, `EventCode: "0x40"`, and `UMask: "0x4"`.

The central section defines the `UPI` unit. It includes baseline clocking (`UNC_UPI_CLOCKTICKS`), direct-attempt counters (`UNC_UPI_DIRECT_ATTEMPTS.D2C`, `.D2U`, with `.D2K` deprecated), flow-queue VNA-credit pressure events, M3 bypass/RxQ blocking events, credit-return blockage, and power-state counters for L1, L0, and L0p. It also includes Rx and Tx link-layer traffic classification through basic header match events, flit counters, bypass/insert/occupancy counters, CRC/link-layer-retry indicators, and VNA credit return occupancy.

The UPI Rx and Tx sections are roughly mirrored:

- `UNC_UPI_RxL_BASIC_HDR_MATCH.*` and `UNC_UPI_TxL_BASIC_HDR_MATCH.*` classify receive/transmit packets by message class, including `NCB`, `NCS`, `REQ`, `RSPCNFLT`, `RSPI`, `RSP_DATA`, `RSP_NODATA`, `SNP`, and `WB`, plus `_OPC` variants that use opcode bits in `UMask`.
- `UNC_UPI_RxL_FLITS.*` and `UNC_UPI_TxL_FLITS.*` count data, null, idle, protocol-header, link-layer credit/control, and per-slot flits.
- Deprecated `*_HDR_MATCH.*`, `*.NULL`, and `*.PROT_HDR` records preserve old names while pointing users to `*_BASIC_HDR_MATCH.*`, `*.ALL_NULL`, or `*.PROTHDR`.
- Rx-specific events include CRC errors, LLR requests, VN0/VN1/VNA credits consumed, RxQ inserts/occupancy by slot, and slot bypass combinations.
- Tx-specific events include TxL0p clock-active subdomains, Tx queue bypass, Tx flit-buffer inserts/occupancy, and VNA credit return events.

The final `UBOX` section covers uncore box-level events: fixed clockticks, virtual logical wire/event-message receipt variants (`DOORBELL_RCVD`, `INT_PRIO`, `IPI_RCVD`, `MSI_RCVD`, `VLW_RCVD`), lock/split-lock cycles, PHOLD assertion-to-ack cycles, RACU DRNG request variants (`RDRAND`, `RDSEED`, `PFTCH_BUF_EMPTY`), and outstanding RACU register requests.

## Effective API And Data Contract

The data contract is a JSON array of event descriptor objects. There are no functions or classes, but downstream code treats each object as a structured PMU API entry. The important fields are stable across this chunk:

- `EventName` is the public symbolic name users pass to perf, usually with a unit-family prefix such as `UNC_UPI_`.
- `EventCode` and `UMask` are encoded selector values; repeated `EventCode` values form families distinguished by `UMask`.
- `Counter` constrains where the event can be programmed. UPI records generally use `0,1,2,3`, M3UPI uses `0,1,2`, UBOX uses `0,1`, and `UNC_U_CLOCKTICKS` uses `FIXED`.
- `Unit` selects the uncore PMU implementation; consumers must not infer all `UNC_` events live on the same PMU.
- `Deprecated: "1"` means the event name should remain parseable but should not be recommended for new usage.
- `Experimental: "1"` indicates reduced stability or lower documentation confidence.

One important schema nuance is that `UMask` is optional. Several aggregate or fixed events in this chunk omit it, including clockticks, some power counters, occupancy/allocation counters, and RACU request events. Parsers must tolerate missing `PublicDescription` too; many experimental or deprecated records only provide `BriefDescription`.

## Control Flow And Integration

Runtime control flow is owned by perf's PMU event loader, not this JSON file. The expected flow is:

1. The pmu-events build tooling reads this JSON file for the `arch/x86/skylakex` CPU model.
2. It validates/parses each JSON object into generated C tables or runtime event maps.
3. At perf runtime, user-facing event names resolve to event selectors, masks, units, and counter constraints.
4. Help/listing paths display `BriefDescription`, `PublicDescription`, deprecation flags, and experimental metadata.
5. Hardware programming paths use `Unit`, `EventCode`, `UMask`, and `Counter` to program the appropriate uncore PMU.

This chunk integrates with the earlier chunks of the same file because the JSON array is a single ordered collection. It also depends on the broader perf pmu-events schema used by sibling files under `tools/perf/pmu-events/arch/x86/*`. Replacement references inside deprecated records create semantic dependencies on other event names, including names outside this chunk such as `UNC_M2M_TxC_BL.DRS_UPI`.

## State And Persistence Behavior

The chunk is static persisted metadata. It does not mutate state, allocate resources, or maintain runtime counters itself. State is represented indirectly by hardware counters when perf programs events described here. `PerPkg: "1"` tells consumers that these uncore events are package-scoped, so aggregation and display logic should account for package-level rather than per-core semantics.

Deprecation state is persisted inline through `Deprecated: "1"` plus replacement text in `BriefDescription`; experimental state is similarly persisted through `Experimental: "1"`. These flags are important because they affect how generated documentation and event-listing output should guide users without removing legacy names.

## Dependencies

The direct dependency is the perf PMU event JSON schema. The content also depends on Intel Skylake-X uncore PMU definitions for UPI, M3UPI, UBOX, message classes, virtual networks, link power states, and flit/slot terminology. Tooling must understand hexadecimal selector strings, comma-separated counter lists, fixed counter naming, and optional fields.

No source-level imports exist in this JSON, but practical integration depends on the pmu-events parser and any generated-table consumers preserving exact event-name spelling. Typos or naming mismatches in replacement descriptions can reduce discoverability even if the raw selector fields are still usable.

## Risks And Edge Cases

- The chunk boundary splits one M3UPI event object, so isolated validation of this line span as standalone JSON would fail. The full file must be parsed for syntax validation.
- Some names and descriptions are inconsistent: for example several `NCB`/`NCS` and `WB` records have brief descriptions that do not exactly match the suffix, and some text still says QPI while the event family is UPI. Consumers should treat selector fields as authoritative and descriptions as user guidance.
- Deprecated aliases remain selectable. Removing or renaming them could break scripts that rely on old perf event names.
- `_OPC` variants depend on opcode bits encoded in `UMask`; users and tooling need clear mask handling to avoid confusing a class match with an opcode-filtered match.
- Optional `UMask` and `PublicDescription` fields must be handled correctly by parsers and generated documentation paths.
- Most records are `Experimental`, so downstream tests should avoid assuming these names are as stable as non-experimental events.
- Counter availability differs by unit (`M3UPI` versus `UPI` versus `UBOX`), so merging unit definitions or ignoring `Counter` could cause invalid hardware programming.

## Test Signals

Useful validation signals for this chunk and the final merged file include:

- Full-file JSON parsing succeeds and returns one top-level array ending at line 13758.
- This chunk contributes 180 `EventName` records: 18 `M3UPI`, 1 `M2M`, 149 `UPI`, and 12 `UBOX`.
- Deprecated records remain present and their replacement references point to existing or intentionally external event names.
- Event families with shared `EventCode` use distinct `UMask` values, especially `UNC_UPI_RxL_BASIC_HDR_MATCH.*`, `UNC_UPI_TxL_BASIC_HDR_MATCH.*`, `UNC_UPI_RxL_FLITS.*`, and `UNC_UPI_TxL_FLITS.*`.
- Parser tests cover records with no `UMask`, no `PublicDescription`, `Counter: "FIXED"`, and multi-counter strings.
- Perf event-list output for Skylake-X includes representative names from this chunk, such as `UNC_UPI_CLOCKTICKS`, `UNC_UPI_RxL_CRC_ERRORS`, `UNC_UPI_TxL_FLITS.ALL_DATA`, and `UNC_U_CLOCKTICKS`.
