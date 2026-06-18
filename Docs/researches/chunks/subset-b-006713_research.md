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
