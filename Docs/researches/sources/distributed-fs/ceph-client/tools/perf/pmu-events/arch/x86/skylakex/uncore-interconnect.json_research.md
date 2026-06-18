# Research: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-interconnect.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006726`: lines 1-6272, `Docs/researches/chunks/subset-b-006726_research.md`
- `subset-b-006727`: lines 6273-11875, `Docs/researches/chunks/subset-b-006727_research.md`
- `subset-b-006728`: lines 11876-13758, `Docs/researches/chunks/subset-b-006728_research.md`

## Chunk Research

### subset-b-006726: lines 1-6272

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-interconnect.json lines 1-6272

This chunk covers the opening 6,272 lines of the Skylake Xeon `uncore-interconnect.json` PMU event table. It starts at the JSON array opener and contains 597 complete visible event records through `UNC_M3UPI_RING_BOUNCES_HORZ.AD`. The final requested line, 6272, is inside the next event object after its `EventCode`; that object's `EventName` and remaining fields begin after this chunk. The full source file has 13,758 lines, so this is only the first portion of a larger uncore interconnect event table.

## Purpose

This file is static perf PMU metadata, not executable Ceph filesystem logic. Its purpose is to describe Intel Skylake X uncore interconnect hardware events so the Linux `perf` build can generate model-specific event lookup tables. The generated tables let users and metrics refer to symbolic event aliases such as `UNC_I_TRANSACTIONS.READS`, `UNC_M2M_IMC_READS.ALL`, and `UNC_M3UPI_CLOCKTICKS` instead of manually encoding raw event select, umask, counter, and unit values.

The chunk covers three uncore units:

- `IRP`: 76 complete events for inbound request port traffic, coherent operations, P2P traffic, snoop responses, FAF/P2P queue occupancy, and IRP egress stalls.
- `M2M`: 433 complete events for Mesh-to-Memory credit accounting, direct-to-core/direct-to-UPI paths, directory lookups/updates, iMC reads/writes, prefetch CAMs, trackers, CMS ingress/egress queues, transgress credits, ring usage, ring bounces, starvation, NACKs, bypasses, and anti-deadlock slot usage.
- `M3UPI`: 88 complete events for the beginning of the M3/UPI interconnect section, including CMS agent credits, CHA/M2 credit-empty conditions, clockticks, D2C/D2U sends, ordering stalls, FaST distress signals, horizontal ring use, M2 BL credit-empty masks, multi-slot flit receives, and the first horizontal ring-bounce event.

## Schema And API Surface

Each complete object follows the perf PMU event JSON schema consumed by `tools/perf/pmu-events/jevents.py`:

- `EventName`: stable user-facing alias. It encodes the hardware block and subtype, for example `UNC_M2M_TxR_VERT_OCCUPANCY.BL_AG1`.
- `EventCode`: raw event select value programmed for the unit's PMU. Some clock events, such as `UNC_M2M_CLOCKTICKS`, omit it when the event is special-cased by the PMU description.
- `UMask`: event subtype mask. Many event families share one `EventCode` and distinguish variants only by `UMask`.
- `Counter`: allowed hardware counter indexes. IRP events mostly use `0,1`; M2M mostly uses `0,1,2,3`; M3UPI mostly uses `0,1,2`, with narrower exceptions such as some AG1 BL occupancy entries using counter `0`.
- `Unit`: routes the event to the generated uncore PMU namespace. In this chunk the units are `IRP`, `M2M`, and `M3UPI`.
- `PerPkg`: all complete events in this chunk are package-scoped uncore events.
- `BriefDescription` and optional `PublicDescription`: user-visible `perf list` documentation.
- `Experimental` and `Deprecated`: metadata flags. Most low-level ring/credit events are marked experimental; the older `UNC_M2M_RPQ_CYCLES_NO_SPEC_CREDITS.CHN*` aliases are marked deprecated and point users toward `UNC_M2M_RPQ_CYCLES_SPEC_CREDITS.CHN*`.

The generated C API surface is defined by `tools/perf/pmu-events/pmu-events.h`, especially `struct pmu_event`, `struct pmu_events_table`, `pmu_events_table__for_each_event()`, `pmu_events_table__find_event()`, `perf_pmu__find_events_table()`, and `find_core_events_table()`. This JSON is an input to those generated tables rather than a runtime parser input.

## Event Families

The `IRP` section defines inbound request port measurements:

- Cache/queue occupancy and clocks: `UNC_I_CACHE_TOTAL_OCCUPANCY.*`, `UNC_I_CLOCKTICKS`, FAF/P2P inserts and occupancy, and outbound request occupancy.
- Coherency and transaction classification: `UNC_I_COHERENT_OPS.*` distinguishes CLFLUSH, CRd, DRd, PCIRdCur, PCITOM, RFO, WbMtoI, and related operations; `UNC_I_TRANSACTIONS.*` separates reads, write prefetches, read prefetches, writes, atomics, and other transactions.
- P2P, snoop, and misc diagnostics: `UNC_I_P2P_TRANSACTIONS.*`, `UNC_I_SNOOP_RESP.*`, `UNC_I_MISC0.*`, and `UNC_I_MISC1.*` expose local/remote matches, MESI response states, fast-path behavior, secondary-transfer state, and lost-forward conditions.
- IRP transmit-side queues and stalls: `UNC_I_TxC_*`, `UNC_I_TxR2_*`, and `UNC_I_TxS_*` cover BL/AK egress queues, credit stalls, and switch-bound request/data insertion.

The `M2M` section is the largest part of this chunk:

- Agent/transgress credit families repeat across Agent 0/1, AD/BL, acquired/occupancy, and transgress indexes 0-5.
- Directory and bypass events cover M2M-to-iMC bypass, direct-to-core/direct-to-UPI operation, directory hit/miss states, multi-socket directory lookup states, and directory state transitions such as `I2S`, `S2A`, and `A2I`.
- iMC, prefetch, and tracker events count reads/writes, priority classes, prefetch CAM inserts/promotions/occupancy/full cycles, RPQ credit cycles by channel, and tracker cycles/inserts/occupancy by channel.
- CMS receive/transmit queues are split into `RxC`, `RxR`, `TxC`, `TxR_HORZ`, and `TxR_VERT` families. They expose inserts, occupancy, full/not-empty cycles, bypass, starvation, credit-starved, no-credit, NACK, and anti-deadlock slot usage.
- Ring events classify AD/AK/BL/IV usage across vertical and horizontal directions, left/right sides, even/odd rings, source throttling, sink starvation, ring bounces, and FaST distress assertions.

The `M3UPI` section begins a similar matrix for M3/UPI-facing uncore traffic:

- CMS agent credit events mirror the M2M pattern for AD and BL credits, with counters adjusted for the M3UPI PMU.
- Credit-empty and direct-send families include `UNC_M3UPI_CHA_AD_CREDITS_EMPTY.*`, `UNC_M3UPI_M2_BL_CREDITS_EMPTY.*`, `UNC_M3UPI_D2C_SENT`, and `UNC_M3UPI_D2U_SENT`.
- The chunk includes horizontal ring-in-use events for AD, AK, BL, and IV rings, multi-slot flit receive masks, and starts the ring-bounce family at `UNC_M3UPI_RING_BOUNCES_HORZ.AD`.

## Control Flow

The effective control flow is data-driven:

1. `tools/perf/pmu-events/Build` includes PMU JSON files and invokes `pmu-events/jevents.py` to generate `$(OUTPUT)pmu-events/pmu-events.c`.
2. `jevents.py` traverses model directories such as `arch/x86/skylakex`, reads JSON event objects, normalizes fields, maps `Unit` values to PMU names, lowercases event aliases internally, and emits compact generated event tables.
3. `tools/perf/pmu-events/arch/x86/mapfile.csv` maps Intel family/model patterns to the `skylakex` model directory; in this tree `GenuineIntel-6-55-[01234]` selects `skylakex`.
4. Runtime perf code finds the host PMU event table through generated lookup functions and exposes aliases through `perf list`, `perf stat -e`, metric expansion, and JSON/list output.
5. When a user selects one of these aliases, perf resolves `EventName` plus optional unit context to the encoded `EventCode`, `UMask`, `Counter`, `Unit`, package-scope flag, and descriptions generated from this JSON.

There is no imperative control flow in the JSON itself. Ordering still matters for generated output stability, diff review, and chunk reconciliation.

## State And Persistence

This source file has no mutable runtime state and no direct persistence behavior. Its persistent contract is the checked-in mapping from symbolic event names to hardware encodings and descriptions. During a perf build, that metadata is transformed into generated `pmu-events.c`; after compilation it becomes read-only data linked into perf. Runtime counter state is owned by the kernel PMU drivers and active perf sessions, not by this JSON file.

Name, code, mask, unit, and deprecation changes are persistent compatibility changes. They can alter `perf list` output, break scripts that request specific event aliases, change metric formulas that reference those aliases, or program different uncore counters on Skylake X systems.

## Dependencies And Integration Points

- `sources/distributed-fs/ceph-client/tools/perf/pmu-events/Build` discovers PMU JSON inputs and runs `jevents.py`.
- `sources/distributed-fs/ceph-client/tools/perf/pmu-events/jevents.py` parses schema fields such as `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `BriefDescription`, `PublicDescription`, `PerPkg`, `Experimental`, and `Deprecated`.
- `sources/distributed-fs/ceph-client/tools/perf/pmu-events/pmu-events.h` defines generated table interfaces and `struct pmu_event`.
- `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/mapfile.csv` maps x86 CPUID patterns to the `skylakex` event directory.
- `sources/distributed-fs/ceph-client/tools/perf/tests/pmu-events.c` validates generated event tables and alias behavior.
- Perf PMU listing and event parsing code consumes the generated aliases, while metric code can depend on event-name stability even though this file itself defines events rather than formulas.

## Risks And Edge Cases

The chunk boundary is mid-object. Lines 6269-6272 begin the `UNC_M3UPI_RING_BOUNCES_HORZ.AK` object but stop before its `EventName`, `Experimental`, `PerPkg`, `PublicDescription`, `UMask`, `Unit`, and closing brace. This chunk is therefore not independently parseable as JSON; only the complete source file is.

The event matrix is highly repetitive, so copy/paste drift is a real maintenance risk. Similar names differ only by agent, direction, channel, ring type, or transgress bit, and a wrong `UMask` or `Counter` can silently produce a valid generated table with incorrect hardware behavior.

Description quality is uneven. Several descriptions contain typos or label drift, such as "PCIDCAHin5t", "prefect queue", `QPI` wording in a UPI-era file, and some `CYCLES_FULL` descriptions that say "Not Full" in nearby M2M vertical egress text. Consumers should treat `EventName`, `EventCode`, `UMask`, `Counter`, and Intel hardware documentation as the authoritative behavioral mapping when descriptions conflict.

Deprecated entries must remain usable until intentionally removed. The `UNC_M2M_RPQ_CYCLES_NO_SPEC_CREDITS.CHN*` records are marked deprecated but still carry encodings; removing or renaming them can break existing scripts.

Many entries are marked `Experimental`, especially deep ring, credit, and starvation diagnostics. Tooling should preserve that flag so users understand these aliases may be less stable or less validated than standard events.

## Test Signals

Useful validation signals for this chunk and its final merged file include:

- Strictly parse the complete file with a JSON parser, for example `python3 -m json.tool sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-interconnect.json`.
- Regenerate perf PMU events for x86/skylakex and confirm `pmu-events.c` generation completes without schema, numeric conversion, duplicate-name, or unit-mapping errors.
- Inspect generated entries for representative events from each covered unit: `UNC_I_TRANSACTIONS.READS`, `UNC_I_SNOOP_RESP.ALL_HIT`, `UNC_M2M_DIRECTORY_LOOKUP.STATE_A`, `UNC_M2M_IMC_WRITES.PARTIAL`, `UNC_M2M_TxR_VERT_OCCUPANCY.IV`, `UNC_M2M_VERT_RING_AD_IN_USE.UP_EVEN`, `UNC_M3UPI_CLOCKTICKS`, and `UNC_M3UPI_RING_BOUNCES_HORZ.AD`.
- Run perf PMU event tests under `tools/perf/tests/pmu-events.c` after generation to catch alias/table regressions.
- On a Skylake X host, `perf list` should expose representative `uncore_*` aliases with package-scope metadata, and `perf stat -e` should accept complete event names from the generated table.
- Chunk reconciliation should verify the next chunk completes the partial `UNC_M3UPI_RING_BOUNCES_HORZ.AK` object before producing the final per-file report.

### subset-b-006727: lines 6273-11875

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-interconnect.json lines 6273-11875

## Scope

This chunk is a middle slice of the Skylake X uncore interconnect PMU event JSON. It starts inside the `UNC_M3UPI_RING_BOUNCES_HORZ.AK` record and ends inside the `UNC_M3UPI_VN0_CREDITS_USED.WB` record, so both boundary events are partial records that must be reconciled with adjacent chunks during the final per-file merge. Within the requested line window there are 514 visible `EventName` fields, 513 complete `Unit: M3UPI` fields, and 513 complete `Experimental: 1` fields. The full source file parses as a valid JSON array with 1291 event objects.

## Purpose

The lines in this chunk define symbolic `perf` aliases for Skylake X `M3UPI` uncore interconnect counters. The events describe mesh-to-UPI traffic behavior: ring bounces and starvation, RxC receive-channel arbitration and credit pressure, RxR receive-ring queue behavior, TxC flow-queue/arbitration behavior, TxR horizontal and vertical egress behavior, UPI peer credit exhaustion, prefetch spawning, vertical ring utilization, and the beginning of VN0 credit-use/no-credit counters.

These entries let users and tooling request named events such as `unc_m3upi_rxc_arb_lost_vn0.ad_req` rather than hand-writing raw PMU config strings. The data is hardware-model metadata, not executable logic, but incorrect fields directly change generated `pmu-events.c` aliases and therefore user-visible `perf list`, `perf stat -e ...`, and Python perf-event metadata.

## Data Model And Important Fields

Each complete object in this chunk follows the perf PMU-events JSON schema consumed by `tools/perf/pmu-events/jevents.py`:

- `EventName` is the symbolic alias. `jevents.py` lowercases it for the generated PMU table.
- `EventCode` is the base hardware event selector. Repeated families use one `EventCode` with distinct `UMask` values.
- `UMask` selects message class, virtual network, agent, direction, or queue subcondition. Some aggregate events, such as `UNC_M3UPI_RING_SRC_THRTL` and `UNC_M3UPI_UPI_PREFETCH_SPAWN`, have no visible `UMask` in this chunk.
- `Counter: "0,1,2"` constrains these events to M3UPI counters 0 through 2.
- `Unit: "M3UPI"` maps through `unit_to_pmu()` into the uncore M3UPI PMU name used by generated aliases.
- `PerPkg: "1"` marks package-scoped counting.
- `Experimental: "1"` marks the events as experimental; metric tooling can detect references to experimental events.
- `BriefDescription` and optional `PublicDescription` are normalized by `fixdesc()` and propagated to perf list output and Python bindings.

The source uses suffixes as structured dimensions: channel suffixes such as `AD`, `AK`, `BL`, and `IV`; protocol/message suffixes such as `REQ`, `RSP`, `SNP`, `WB`, `NCB`, and `NCS`; virtual-network suffixes such as `VN0`, `VN1`, and `VNA`; direction suffixes such as `UP`, `DN`, `HORZ`, and `VERT`; and agent suffixes such as `AG0` and `AG1`.

## Event Families In This Chunk

The first visible families cover ring-level behavior: horizontal and vertical ring bounces, sink starvation, source throttling, and vertical ring in-use counters. These are cycle or activity counters for mesh/interconnect pressure by ring type or direction.

The `UNC_M3UPI_RxC_*` families dominate the first half of the chunk. They describe receive-channel arbitration outcomes (`ARB_LOST`, `ARB_NOAD_REQ`, `ARB_NOCRED`, `ARB_MISC`), bypasses, flit collisions, credit occupancy and miscellaneous credit states, queue non-empty cycles, flits generated/sent/not-sent, held messages, inserts, occupancy, packing misses, SMI3 prefetch classes, and VNA credit behavior. Most of these are repeated across VN0/VN1 and AD/BL message classes with predictable `UMask` assignments.

The `UNC_M3UPI_RxR_*` families cover receive-ring busy/starved states, bypass, credit starvation, insert counts, and occupancy. These events separate ring direction/agent/channel dimensions and provide diagnostics for ring-side pressure after traffic is received from UPI-facing paths.

The `UNC_M3UPI_STALL_NO_TxR_HORZ_CRD_*` families record stalls caused by missing horizontal TxR credits for AD or BL traffic and for agent 0/1 variants. They bridge receive-side pressure and transmit-ring credit availability.

The `UNC_M3UPI_TxC_*` families describe transmit-channel flow queue and arbitration behavior, including AD/BL arbitration failures, FLQ bypasses, non-empty cycles, inserts, occupancy, snoop-filter groups, and speculative arbitration credit/new-message/no-other-pending conditions. The `AK_FLQ_*` records are smaller one-event families.

The `UNC_M3UPI_TxR_HORZ_*` and `UNC_M3UPI_TxR_VERT_*` families cover horizontal and vertical egress queues: ADS used, bypass, cycles full, cycles non-empty, inserts, NACKs, occupancy, and injection starvation. The vertical variants generally include AD/AK/BL agent split plus IV entries; the horizontal variants are similar but have fewer IV-only cases.

The chunk ends with UPI peer AD/BL credit-empty counters, a UPI prefetch spawn counter, vertical AD/AK/BL/IV ring-in-use counters, and the beginning of `UNC_M3UPI_VN0_CREDITS_USED` plus the first partial `UNC_M3UPI_VN0_NO_CREDITS` record in adjacent lines.

## Control Flow And Generation Path

There is no runtime control flow in this JSON file. The relevant flow is build-time and lookup-time:

1. The perf build reads JSON files under `tools/perf/pmu-events/arch/...` according to the architecture mapfile.
2. `jevents.py` parses each object, converts `EventName` to lowercase, canonicalizes `EventCode` and `UMask`, converts `Unit` to a PMU name, and assembles an event string such as `event=0x4b,umask=0x1`.
3. `jevents.py` emits generated `pmu-events.c` tables.
4. The generated object is compiled into perf and exposed through PMU event lookup.
5. Runtime tools such as `perf list`, `perf stat`, and perf Python bindings display or select these aliases and descriptions.

Because the chunk is JSON data, control-flow risk is mostly transformation risk: malformed JSON, duplicate aliases, wrong selector fields, or description/schema fields that the generator silently normalizes into misleading user-visible aliases.

## State And Persistence Behavior

The persistent state is the checked-in event metadata. Generated `pmu-events.c` is a derived build artifact and should not be manually edited for these events. `PerPkg: "1"` means the resulting events aggregate at package scope, which matters when interpreting counts on multi-socket systems. Counter selection state is constrained by `Counter: "0,1,2"` and the M3UPI PMU availability exposed by the running kernel and hardware.

No mutable runtime state is stored in this source file. Counter values are produced by hardware during perf sessions; this JSON only persists the mapping from symbolic event names to hardware selectors and descriptions.

## Dependencies And Integration Points

This chunk depends on the PMU-events schema implemented by `tools/perf/pmu-events/jevents.py`, the x86 mapfile that maps Skylake X CPU IDs to the `skylakex` event directory, and perf's PMU alias machinery in `tools/perf/util/pmu.c` and `tools/perf/util/pmu.h`. It also feeds user-facing list output in `tools/perf/builtin-list.c` and Python metadata in `tools/perf/util/python.c`.

The semantic dependency is Intel Skylake X uncore M3UPI hardware: the event codes and masks are only meaningful when the kernel exposes matching uncore M3UPI PMUs. The repeated `Experimental: "1"` flags also integrate with PMU metric helpers that can mark formulas using experimental events.

## Risks And Edge Cases

The requested slice begins and ends mid-object. A final merged report must not treat the first and last visible records as independently complete without adjacent chunk context.

Several families reuse the same `EventCode` with different masks. A single wrong `UMask` can create a valid but semantically incorrect alias that build tests may not catch unless compared with Intel reference data or hardware behavior.

Some visible descriptions appear inconsistent with event suffixes near the boundary and credit families. For example, the visible tail maps `UNC_M3UPI_VN0_CREDITS_USED.WB` to a brief description saying `RSP on BL`, while earlier BL suffixes distinguish `WB` from `RSP`. Similar AD/BL credit-empty brief descriptions should be checked against the hardware specification before relying on the prose.

The chunk has many near-duplicate families, so copy/paste drift is a realistic risk: swapped `VN0`/`VN1`, `AG0`/`AG1`, `AD`/`BL`, `HORZ`/`VERT`, or direction masks would still parse and generate aliases.

All complete visible events are marked experimental. Downstream metric formulas or documentation should avoid presenting these counters as stable architectural events unless the experimental status is intentional.

## Test Signals

Useful validation starts with syntax: `jq empty sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-interconnect.json` succeeds for the full file. In this workspace, the full file contains 1291 JSON objects.

Build-time validation should include the perf PMU-events generation path, especially the `jevents.py` rule that emits `pmu-events.c`. The generated table should contain lowercase aliases for the M3UPI names in this chunk and event strings that combine the expected `event=...` and `umask=...` pairs.

Runtime smoke signals, on matching Skylake X hardware, are `perf list` showing M3UPI aliases from these families and `perf stat -e` accepting representative aliases from ring, RxC, RxR, TxC, TxR, and UPI peer credit families. Hardware-level semantic validation requires comparing counts against workloads that create UPI traffic, ring pressure, or credit starvation.

Chunk-local guard checks used for this research: the requested lines expose 514 `EventName` fields, 513 complete `Unit: "M3UPI"` fields, and 513 complete `Experimental: "1"` fields. The one-field difference is expected because the line range starts and ends inside event objects.

### subset-b-006728: lines 11876-13758

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
