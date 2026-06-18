# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-interconnect.json lines 1-6247

## Scope

This chunk covers the first 6,247 lines of the Snow Ridge X uncore interconnect PMU event table. The file is a JSON array consumed by Linux `perf` PMU event tooling; this chunk includes 598 complete event objects plus the opening of one partial event object at the chunk boundary. Covered complete events are package-scoped uncore events for `IRP` and `M2M`; `UBOX` begins later in the file and is outside this chunk.

The chunk boundary cuts through `UNC_M2M_TxR_VERT_INSERTS0.BL_AG0`: lines 6242-6247 expose its description, counter set, event code, name, `Experimental`, and `PerPkg`, while `PublicDescription`, `UMask`, `Unit`, object close, and following sibling events are in the next chunk. The merge lane must avoid treating this partial object as complete until subsequent chunk data is available.

## Purpose

The table describes Intel Snow Ridge X uncore interconnect performance events for perf's JSON event database. Each object maps a human event name such as `UNC_I_SNOOP_RESP.ALL_HIT` or `UNC_M2M_IMC_WRITES.CH0_FULL` to the low-level selector fields perf needs to program an uncore PMU counter: `EventCode`, optional `UMask`, allowed `Counter` list, `Unit`, package scope, and optional descriptive metadata.

The early `IRP` section instruments IO coherency tracker behavior: cache occupancy, coherent operations, Fire-and-Forget queue pressure, P2P traffic, snoop responses, inbound transactions, egress queue occupancy, and credit stalls. The large `M2M` section instruments mesh-to-memory and Common Mesh Stop traffic: agent credits, memory-controller reads/writes, prefetch CAM behavior, horizontal and vertical ring use, ingress/egress queues, anti-deadlock slot use, bypass paths, starvation, NACKs, credit stalls, and transgress credit accounting.

## Data Model And Important Fields

Each complete item is a JSON object in a top-level array. There are no functions or classes in this file; the effective API is the perf PMU event schema.

Important fields visible in this chunk:

- `EventName`: required symbolic event name. Complete events in this chunk all have it.
- `EventCode`: hardware event selector. Present on 597 of the 598 complete visible events; `UNC_M2M_CLOCKTICKS` has no explicit code in this chunk.
- `UMask`: qualifier/mask bits. Present on 529 complete events; queue-wide or clock events often omit it.
- `Counter`: permitted hardware counters. `IRP` events use `0,1`; `M2M` events use `0,1,2,3`.
- `Unit`: PMU unit identifier. Complete events in this chunk are split into 73 `IRP` events and 524 `M2M` events, plus the partial boundary object whose `Unit` is not visible.
- `PerPkg`: every complete visible event is package scoped with `"1"`.
- `Experimental`: present on most events, but not all; users and tests should not assume every event has this flag.
- `BriefDescription` and `PublicDescription`: operator-facing explanations. `BriefDescription` is present throughout; `PublicDescription` is present for 352 complete visible events and is absent for many terse experimental events.

## Event Families

The `IRP` portion covers:

- `UNC_I_CACHE_TOTAL_OCCUPANCY`, `UNC_I_CLOCKTICKS`, `UNC_I_COHERENT_OPS`, `UNC_I_FAF_*`, and `UNC_I_IRP_ALL` for IRP occupancy and queue insertion behavior.
- `UNC_I_MISC0` and `UNC_I_MISC1` for fast-path, slow-path, secondary-transfer, and MESI-state edge cases.
- `UNC_I_P2P_*` for peer-to-peer inserts, occupancy, reads, writes, completions, locality, and target matches.
- `UNC_I_SNOOP_RESP` for snoop hit/miss and snoop type responses, including aggregate masks such as `ALL_HIT` and `ALL_MISS`.
- `UNC_I_TRANSACTIONS` for inbound atomic, write, fast-path write-prefetch, and other transaction classes.
- `UNC_I_TxC_*`, `UNC_I_TxR2_*`, and `UNC_I_TxS_*` for egress inserts, occupancy, full cycles, and credit stalls toward switch or PCIe-facing paths.

The `M2M` portion is much larger and highly patterned:

- Agent credit families `UNC_M2M_AG{0,1}_{AD,BL}_CRD_{ACQUIRED,OCCUPANCY}{0,1}.TGR*` enumerate transgress-specific credit activity for agents 0 and 1, AD/BL rings, and transgress IDs 0-10 split across `0` and `1` selector groups.
- `UNC_M2M_BYPASS_M2M_*`, `DIRECT2CORE_*`, and `DISTRESS_ASSERTED.*` describe bypass/direct-to-core behavior and throttling or distress signals.
- `UNC_M2M_HORZ_RING_*_IN_USE` and later vertical ring families describe ring utilization by direction/side/parity and ring type (`AD`, `AK`, `AKC`, `BL`, `IV`).
- `UNC_M2M_IMC_READS` and `UNC_M2M_IMC_WRITES` break memory-controller requests down by channel, normal versus isochronous traffic, full/partial writes, non-inclusive misses, and transgress-originated requests.
- `UNC_M2M_PREFCAM_*` covers prefetch CAM occupancy, full/not-empty cycles, inserts, dealloc reasons, demand merge/no-merge/drop behavior, per-channel drop reasons, and RxC side activity.
- `UNC_M2M_RING_BOUNCES_*`, `RING_SINK_STARVED_*`, and `RING_SRC_THRTL` count ring backpressure, bounces, sink starvation, and source throttling.
- `UNC_M2M_RPQ_NO_*_CRD`, `RxC_*`, `RxR_*`, `TGR_*`, `TRACKER_*`, and `TxC_*` cover ingress/egress queues, credits, full/not-empty/occupancy/inserts, bypass, starvation, and tracker pressure.
- `UNC_M2M_TxR_HORZ_*` and `UNC_M2M_TxR_VERT_*` cover horizontal and vertical Common Mesh Stop egress behavior, including ADS use, bypass, full/not-empty cycles, inserts, NACKs, occupancy, starvation, and no-credit stalls.

## Control Flow And Runtime Behavior

There is no executable control flow in this JSON file. Runtime control flow is external:

1. Perf's PMU event generator/parser loads architecture-specific JSON files under `tools/perf/pmu-events/arch/x86`.
2. It validates the JSON array and indexes each object by `EventName`, `Unit`, event selector fields, and optional descriptions.
3. At perf runtime, user-facing event aliases are resolved to the matching PMU unit and encoded hardware selector. For this file, that means package-scoped uncore units such as `IRP` and `M2M`.
4. Counter restrictions guide scheduling: `IRP` aliases are limited to counters `0,1`, while `M2M` aliases are limited to counters `0,1,2,3`.

The repeated families rely on perf's schema preserving hexadecimal strings exactly enough for later conversion. Event-code casing is inconsistent (`0x0F`, `0x0f`, `0xae`, etc.), so consumers must parse case-insensitively.

## State And Persistence

The file is static metadata tracked in the source tree. It does not persist runtime measurements, allocate state, or mutate counters by itself. Its durable state is the event catalog: event names, encodings, masks, and descriptions. Once built into perf's pmu-events tables, changes to this file alter user-visible event aliases and the hardware encodings perf programs on Snow Ridge X systems.

`PerPkg` marks the events as package-scoped rather than per-core. This affects aggregation semantics and should be treated as part of the persisted event contract, not as incidental documentation.

## Dependencies And Integration Points

Primary dependencies are the perf PMU event JSON schema and the Snow Ridge X uncore PMU naming/encoding conventions. The file integrates with:

- perf's JSON parser and generated pmu-events tables;
- architecture selection under `arch/x86/snowridgex`;
- uncore PMU discovery for units named `IRP` and `M2M`;
- user-facing `perf list`, `perf stat -e <event>`, and generated event descriptions;
- any downstream tooling that scrapes `EventName`, `BriefDescription`, `PublicDescription`, or `Unit`.

The file is independent of Ceph client code despite living under `sources/distributed-fs/ceph-client`; it is vendored Linux perf tooling data.

## Risks And Edge Cases

- The chunk boundary is mid-object, so chunk-local JSON is not valid by itself. Validators must run on the full file or a line-range-aware reconstruction.
- Several families are generated-like and repetitive; copy/paste mistakes are plausible. One visible example is in `UNC_M2M_AG1_BL_CRD_ACQUIRED0.TGR6` and `.TGR7`, whose brief/public descriptions mention transgress 4/5 while the event names and `UMask` values indicate 6/7.
- Some aggregate masks intentionally combine bits, for example `UNC_I_SNOOP_RESP.ALL_HIT` and `UNC_M2M_IMC_WRITES.*`. Tests should distinguish valid aggregate masks from duplicate accidental masks.
- Missing optional fields are normal. `PublicDescription`, `UMask`, and `Experimental` cannot be assumed for every event.
- `EventCode` casing and even field presence vary. Parsers should not string-compare hexadecimal codes without normalization.
- Event names encode semantic dimensions (`CH0`, `CH1`, `ALLCH`, `TGR*`, `AG0`, `AG1`, `AD`, `AK`, `AKC`, `BL`, `IV`). Downstream scripts that infer groups from names need to handle the suffix patterns consistently.
- Many descriptions say "Cycles", "Occupancy", "Inserts", "Credits", or "Stalls"; misuse can lead to incorrect derived metrics if users divide occupancy by the wrong allocation event or mix per-cycle occupancy with event counts.

## Test Signals

Useful validation checks for this chunk and the eventual merged file:

- Full-file JSON parses as a top-level array; this chunk alone should not be expected to parse because line 6247 is mid-object.
- All complete events in lines 1-6247 have `EventName`, `Counter`, `PerPkg`, and `Unit`.
- Complete event unit counts before the boundary are 73 `IRP` and 524 `M2M`.
- `IRP` complete events use `Counter: "0,1"` and `M2M` complete events use `Counter: "0,1,2,3"`.
- `EventName` values are unique within the complete-event subset.
- Hex strings in `EventCode` and `UMask` parse case-insensitively.
- `perf list` on a build that includes this file should expose Snow Ridge X uncore aliases for representative events such as `UNC_I_CLOCKTICKS`, `UNC_I_SNOOP_RESP.ALL_HIT`, `UNC_M2M_CLOCKTICKS`, `UNC_M2M_IMC_READS.ALL`, and `UNC_M2M_TxR_HORZ_INSERTS.AD_ALL`.
- Description quality checks should flag mismatches where transgress IDs in descriptions disagree with `EventName` suffixes, without automatically blocking valid hardware encodings.
