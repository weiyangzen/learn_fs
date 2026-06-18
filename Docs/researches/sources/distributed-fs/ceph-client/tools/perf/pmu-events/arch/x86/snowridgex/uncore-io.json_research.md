# Research: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-io.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006736`: lines 1-5317, `Docs/researches/chunks/subset-b-006736_research.md`
- `subset-b-006737`: lines 5318-10586, `Docs/researches/chunks/subset-b-006737_research.md`
- `subset-b-006738`: lines 10587-10668, `Docs/researches/chunks/subset-b-006738_research.md`

## Chunk Research

### subset-b-006736: lines 1-5317

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-io.json lines 1-5317

## Scope

This chunk covers lines 1-5317 of `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-io.json`, the first chunk of the Snow Ridge uncore I/O PMU event table. The source is a static JSON array consumed by Linux `perf` pmu-events tooling. It is not Ceph runtime code; it is vendored kernel/perf metadata inside the Ceph client source tree.

The visible range starts at the top-level `[` and contains 429 visible `EventName` entries. Of those, 428 event objects close within this chunk. The last visible entry, `UNC_M2P_AG0_AD_CRD_ACQUIRED1.TGR9`, starts before line 5317 but continues in chunk `subset-b-006737`; this chunk alone is therefore not standalone valid JSON.

At a high level, the chunk contains:

- 409 completed `Unit: "IIO"` records for Snow Ridge Integrated I/O traffic-controller events.
- 9 completed `Unit: "iio_free_running"` records for free-running IIO bandwidth and clock counters.
- 10 completed `Unit: "M2PCIe"` records plus one partial M2PCIe record at the boundary.
- 326 visible records marked `Experimental: "1"`.
- 2 metric wrapper records with `MetricName`, `MetricExpr`, `Filter`, and `ScaleUnit`.

## Purpose

The file maps public perf event names to the hardware selector fields and metadata needed to program Snow Ridge uncore I/O counters. Each object is an event descriptor, not executable logic. The descriptors let perf expose names such as `UNC_IIO_DATA_REQ_OF_CPU.MEM_READ.PART0` or `UNC_IIO_TXN_REQ_BY_CPU.MEM_WRITE.PART4` instead of requiring users to remember raw event codes, masks, port masks, and counter constraints.

The chunk's practical purpose is I/O-path observability:

- PCIe read/write bandwidth metrics and derived LLC miss aliases at the start of the file.
- Free-running bandwidth-in and clocktick counters.
- PCIe completion buffer insert/occupancy counters.
- Data-volume and transaction-count counters for CPU-to-device and device-to-CPU request classes.
- Inbound arbitration, outstanding request, completion, target-match, and outbound issue counters.
- IOMMU/IOTLB/page-walk/cache-invalidation counters.
- Debug-bus mask/match helper events.
- The start of CMS/M2PCIe transgress credit-acquire counters.

The events are package-scoped through `PerPkg: "1"` and are intended for uncore PMU programming rather than per-thread or per-core counting.

## Data Contract And Important Fields

There are no functions, classes, or C APIs in this chunk. The effective API is the JSON schema expected by perf's pmu-events parser. The important fields are:

- `EventName`: public symbolic name shown by `perf list` and accepted by perf event selection.
- `EventCode`: hardware event selector. Repeated selector values form families; for example `0xC0`/`0xc0` covers data requested by CPU, `0x83` covers data requested of CPU, `0x84` covers transaction requests of CPU, and `0xC1`/`0xc1` covers transaction requests by CPU.
- `UMask`: selector submask. It distinguishes request classes such as config read, memory write, completion with data, message, peer read, peer write, and transgress index bits.
- `Counter`: allowed counter slots. IIO records commonly use `0,1,2,3`, CPU data-volume records split between `0,1` and `2,3`, free-running records bind to fixed free-running counter numbers, and M2PCIe records use `0,1,2,3`.
- `Unit`: PMU unit name. This chunk uses `IIO`, `iio_free_running`, and `M2PCIe`.
- `PerPkg`: package-scope marker. All visible complete records use `PerPkg: "1"`.
- `PortMask`: IIO port or lane-group selector. Common values are `0x01` through `0x80` for parts 0-7, `0xFF`/`0xff` for all parts, and `0x100`/`0x200` for IOMMU type 0/1 variants.
- `FCMask`: flow-control or functional-class mask. Many IIO traffic records use `0x07`; completion-data buffer events use `0x04`.
- `BriefDescription` and `PublicDescription`: user-facing help text. They often encode physical slot/lane interpretation, such as x16, x8, and x4 card placements.
- `Experimental`: stability/documentation signal. Most detailed IIO and M2PCIe records are experimental.
- `MetricExpr`, `MetricName`, `Filter`, and `ScaleUnit`: present only on the two leading `LLC_MISSES.PCIE_READ` and `LLC_MISSES.PCIE_WRITE` metric aliases. They aggregate four part-specific IIO data request events and scale data in 4-byte doublewords.

Consumers must tolerate optional fields. Some events omit `UMask`, `PublicDescription`, `PortMask`, or `FCMask`; free-running records use a separate unit; the boundary record lacks closing fields within this chunk.

## Event Families In This Chunk

The first two records define public metric aliases:

- `LLC_MISSES.PCIE_READ` derives from `UNC_IIO_DATA_REQ_OF_CPU.MEM_READ.PART0` through `.PART3`.
- `LLC_MISSES.PCIE_WRITE` derives from `UNC_IIO_DATA_REQ_OF_CPU.MEM_WRITE.PART0` through `.PART3`.

Both use `EventCode: "0x83"`, `FCMask: "0x07"`, `Filter: "ch_mask=0x1f"`, `PortMask: "0x01"`, `ScaleUnit: "4Bytes"`, and `Unit: "IIO"`. These are higher-level convenience metrics for PCIe bandwidth, not independent low-level counters.

The `iio_free_running` records cover:

- `UNC_IIO_BANDWIDTH_IN.PART0_FREERUN` through `.PART7_FREERUN`, one counter per part, all `EventCode: "0xff"` with `UMask` values `0x20` through `0x27`.
- `UNC_IIO_CLOCKTICKS_FREERUN`, `Counter: "0"`, `UMask: "0x10"`.

The regular `IIO` event families cover:

- `UNC_IIO_CLOCKTICKS`: integrated I/O traffic-controller clock ticks.
- `UNC_IIO_COMP_BUF_INSERTS.CMPD.*` and `UNC_IIO_COMP_BUF_OCCUPANCY.CMPD.*`: completion-buffer insert and occupancy counters for completions with data. These expose aggregate/all-parts and per-part variants.
- `UNC_IIO_DATA_REQ_BY_CPU.*`: data volume requested by the CPU/main die, including config read/write, I/O read/write, memory read/write, peer read/write, each with IOMMU0/IOMMU1 and part 0-7 variants.
- `UNC_IIO_DATA_REQ_OF_CPU.*`: data volume requested of the CPU by cards/devices, including atomic, completion-data, memory read/write, messages, peer read/write, again using IOMMU and part variants.
- `UNC_IIO_INBOUND_ARB_REQ.*` and `UNC_IIO_INBOUND_ARB_WON.*`: inbound arbitration request and grant stages for data, final read/write, IOMMU hit/request, request ownership, and write-line states.
- `UNC_IIO_IOMMU0.*`, `UNC_IIO_IOMMU1.*`, and `UNC_IIO_IOMMU3.*`: IOTLB lookup/hit/miss, page-walk cache, PWT/PWC, interrupt-entry cache, context-cache invalidation, and IOTLB invalidation counters.
- `UNC_IIO_MASK_MATCH_AND.*` and `UNC_IIO_MASK_MATCH_OR.*`: debug-bus mask/match events for non-PCIe and PCIe bus combinations.
- `UNC_IIO_NOTHING`: explicit counting-disabled/no-op event.
- `UNC_IIO_NUM_OUSTANDING_REQ_FROM_CPU.TO_IO`: outbound request queue occupancy. The event name preserves the source spelling `OUSTANDING`.
- `UNC_IIO_NUM_OUTSTANDING_REQ_OF_CPU.*`: outstanding request-of-CPU stages.
- `UNC_IIO_NUM_REQ_FROM_CPU.*`, `UNC_IIO_NUM_REQ_OF_CPU.*`, and `UNC_IIO_NUM_REQ_OF_CPU_BY_TGT.*`: request counts by origin, commit/all state, and target category such as abort, confined/local/remote peer-to-peer, multicast, memory, message-B, and UBOX.
- `UNC_IIO_NUM_TGT_MATCHED_REQ_OF_CPU`: ITC address-map match count.
- `UNC_IIO_OUTBOUND_CL_REQS_ISSUED.TO_IO` and `UNC_IIO_OUTBOUND_TLP_REQS_ISSUED.TO_IO`: outbound cacheline/TLP request issue counters.
- `UNC_IIO_PWT_OCCUPANCY`: page-walk table occupancy.
- `UNC_IIO_REQ_FROM_PCIE_CL_CMPL.*`, `UNC_IIO_REQ_FROM_PCIE_CMPL.*`, and `UNC_IIO_REQ_FROM_PCIE_PASS_CMPL.*`: completion/passed-completion pipeline-state counters.
- `UNC_IIO_SYMBOL_TIMES`: PCIe symbol-time measurement.
- `UNC_IIO_TXN_REQ_BY_CPU.*`: transaction counts requested by CPU/main die, mirroring the data-volume request classes where this chunk includes config, I/O, memory, peer read, and peer write variants.
- `UNC_IIO_TXN_REQ_OF_CPU.*`: transaction counts requested of CPU by devices/cards, covering atomic, completion-data, memory read/write, message, peer read, and peer write variants.

The final section starts the `M2PCIe` unit:

- `UNC_M2P_AG0_AD_CRD_ACQUIRED0.TGR0` through `.TGR7` are complete in this chunk and use `EventCode: "0x80"` with one-hot `UMask` bits `0x1` through `0x80`.
- `UNC_M2P_AG0_AD_CRD_ACQUIRED1.TGR10` and `.TGR8` are complete with `EventCode: "0x81"`.
- `UNC_M2P_AG0_AD_CRD_ACQUIRED1.TGR9` is only partially visible by line 5317 and continues in the next chunk.

## Control Flow And Integration

Runtime control flow belongs to perf's pmu-events infrastructure. The expected integration path is:

1. Build or runtime tooling parses `arch/x86/snowridgex/uncore-io.json` as one complete JSON array.
2. Each descriptor is validated against the pmu-events schema and emitted into generated event tables or loaded event maps.
3. `perf list` and related help paths expose `EventName`, descriptions, `Experimental`, metric names, and scale units.
4. When a user selects an event, perf resolves `Unit`, `EventCode`, `UMask`, `Counter`, `PortMask`, `FCMask`, and optional filters into the appropriate uncore PMU programming attributes.
5. The kernel/perf uncore PMU drivers program the hardware counters and report package-scoped counts.

This chunk depends on the rest of the same JSON file for syntactic validity and for the rest of the M2PCIe event family. It also integrates with sibling files under `tools/perf/pmu-events/arch/x86/`, which follow the same schema for other Intel platforms. Exact spelling is part of the public interface: shell scripts and dashboards may reference event names literally.

## State And Persistence Behavior

The chunk is persisted static metadata. It has no mutable program state, no I/O side effects, no allocation behavior, and no direct interaction with Ceph data structures. Runtime state exists only after perf uses these descriptors to program hardware counters.

State semantics are encoded declaratively:

- `PerPkg: "1"` means counts are package-level uncore observations.
- `Counter` restricts where an event may be scheduled.
- `PortMask` selects PCIe part/slot/IOMMU scope.
- `FCMask` and `UMask` select internal IIO pipeline and request-class states.
- `Experimental: "1"` persists stability risk in the source table.
- Metric aliases persist derived formulas through `MetricExpr`; changing the underlying event names would break those formulas.

Because this file is checked into the source tree, the main persistence risk is accidental metadata drift: typo changes, inconsistent masks, or renamed events can persist into generated perf tables and user-facing documentation.

## Dependencies

Direct dependencies are schema-level rather than link-time:

- perf pmu-events JSON parser and table generator.
- Intel Snow Ridge uncore PMU definitions for IIO, IIO free-running counters, and M2PCIe.
- perf uncore PMU support that understands units, selectors, masks, port filters, free-running counters, and package-level aggregation.
- JSON tooling in build/test paths.

The metadata also depends on Intel's terminology for PCIe lane parts, IOMMU types, transaction-layer packet stages, completion buffers, page-walk/IOTLB caches, and CMS/M2PCIe transgress credits. Consumers should not infer all `UNC_` names share the same PMU unit; `Unit` is authoritative.

## Risks And Edge Cases

- Chunk boundary: line 5317 cuts through `UNC_M2P_AG0_AD_CRD_ACQUIRED1.TGR9`. The complete source file must be parsed for syntax validation; this chunk cannot be validated as standalone JSON.
- Case variations: selector values use mixed-case hex spellings such as `0xC0` and `0xc0`, `0xC1` and `0xc1`, `0xC2` and `0xc2`. Tooling should parse them numerically rather than string-normalizing in ways that affect diffs or generated output.
- Optional fields: not every event has `PublicDescription`, `UMask`, `PortMask`, `FCMask`, metric fields, or `Experimental`. Parsers and research merge tooling must not assume uniform object shape.
- Event-name spelling is public API. For example `UNC_IIO_NUM_OUSTANDING_REQ_FROM_CPU.TO_IO` appears misspelled in the source; changing it would likely break existing perf usage even if it improves spelling.
- Description mismatch risk: some per-part descriptions embed lane/slot explanations and repeated text. The selector fields and event names should be treated as more authoritative than prose if there is a conflict.
- Part masks encode topology. `PART0` through `PART7` use `PortMask` bit values, while IOMMU variants use `0x100` and `0x200`; merging or aggregating these without preserving scope can double-count or hide topology.
- The two `LLC_MISSES.PCIE_*` records are derived metric aliases. They rely on the continued availability and spelling of the `UNC_IIO_DATA_REQ_OF_CPU.MEM_*` part events named in `MetricExpr`.
- Most detailed records are experimental, so downstream documentation and tests should allow for vendor-table churn while still catching structural regressions.

## Test Signals

Useful validation signals for this chunk and the eventual merged per-file report:

- The full `uncore-io.json` file should parse as JSON; the isolated line range should not be expected to parse because of the split object at line 5317.
- `perf list` generation for Snow Ridge should include the leading aliases `LLC_MISSES.PCIE_READ` and `LLC_MISSES.PCIE_WRITE` with their metric expressions intact.
- Schema checks should verify required fields for completed records: at minimum `EventName`, `EventCode`, `BriefDescription`, and `Unit` for event descriptors, with optional handling for masks/descriptions.
- Event-name uniqueness should be checked across the complete file, especially across chunk boundaries.
- Unit distribution in this chunk should remain consistent with expectations: regular IIO records dominate, free-running records use `iio_free_running`, and M2PCIe starts near the end.
- Selector-family tests should preserve repeated family patterns: per-part records should carry the correct `PortMask`, IOMMU records should use `0x100`/`0x200`, and transgress credit records should use one-hot `UMask` bits.
- Metric-expression validation should confirm referenced `UNC_IIO_DATA_REQ_OF_CPU.MEM_READ.PART0-3` and `MEM_WRITE.PART0-3` events exist in the same full file.

### subset-b-006737: lines 5318-10586

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-io.json lines 5318-10586

## Scope

This chunk covers lines 5318-10586 of `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-io.json`, a Linux `perf` PMU event JSON table for Intel Snow Ridge uncore I/O. The range is not standalone JSON: line 5318 starts inside the tail of a prior `UNC_M2P_AG0_AD_CRD_ACQUIRED1.TGR9` object, and line 10586 cuts into the `UNC_M2P_VERT_RING_BL_IN_USE.UP_EVEN` object that continues after the chunk. The final per-file reconciliation must merge this with adjacent chunks before doing full JSON validation.

The visible range contributes 488 complete `EventName` records, all for `Unit: "M2PCIe"`. Almost all are package-scoped and experimental: the span contains 488 visible `M2PCIe` unit entries, 486 explicit `Experimental: "1"` markers, and 489 visible `PerPkg: "1"` lines because the opening partial object contributes metadata without its `EventName` in this chunk.

## Purpose

This file is declarative hardware event metadata, not executable code. Each JSON object maps a public perf event name such as `UNC_M2P_RxR_OCCUPANCY.AD_ALL` or `UNC_M2P_TxR_VERT_STARVED0.AD_AG0` to the selector fields and descriptive metadata needed for Snow Ridge M2PCIe uncore PMU programming and listing.

The chunk focuses on the `UNC_M2P_*` M2PCIe fabric bridge between mesh/CMS and PCIe/IIO paths. It describes counters for CMS ingress/egress buffers, M2PCIe-to-IIO credits, local and remote peer-to-peer credit flow, horizontal and vertical ring usage, and starvation or backpressure conditions. These events support diagnosis of uncore I/O congestion: credit exhaustion, queue occupancy, bypasses, NACKs, ring utilization, and stalls waiting for transgress credits.

## Event Families

The first major section is CMS agent credit accounting. It defines agent 0 and agent 1 AD/BL credit acquired and occupancy families, split across `*0.TGR0` through `*0.TGR7` and `*1.TGR8` through `*1.TGR10` records. The selector pattern is consistent: paired event codes distinguish the lower and upper transgress-number groups, while `UMask` values select individual transgress lanes. These families include `UNC_M2P_AG0_AD_CRD_OCCUPANCY*`, `UNC_M2P_AG0_BL_CRD_ACQUIRED*`, `UNC_M2P_AG0_BL_CRD_OCCUPANCY*`, and the corresponding `AG1` versions.

The middle of the chunk covers M2PCIe/IIO and peer-to-peer credit movement. `UNC_M2P_IIO_CREDITS_USED`, `UNC_M2P_IIO_CREDITS_ACQUIRED`, and `UNC_M2P_IIO_CREDITS_REJECT` use message classes such as `DRS`, `NCB`, and `NCS` and CMS port suffixes to show when BL-ring traffic can or cannot acquire credits into the IIO agent. Local and remote P2P families then track dedicated/shared credit taken, returned, received, occupancy, and wait states across M2IOSF instances and agents.

The `RxC` and `TxC` sections describe CMS-to-ring or ring-to-CMS channel behavior. They include cycles full, cycles not empty, inserts, and occupancy for AD, AK, BL, and IV traffic classes. These are queue-state counters rather than packet payload counters, so they are useful as pressure and utilization signals.

The `RxR` section tracks transgress ingress behavior. `UNC_M2P_RxR_OCCUPANCY`, `UNC_M2P_RxR_INSERTS`, and `UNC_M2P_RxR_BYPASS` count ingress buffer state, allocations, and bypasses by credited/uncredited AD and BL traffic plus AK, AKC, and IV classes. `UNC_M2P_RxR_CRD_STARVED`, `UNC_M2P_RxR_BUSY_STARVED`, and the aggregate `UNC_M2P_RxR_CRD_STARVED_1` represent starvation caused by lack of egress credit or other queue priority.

The `STALL0` and `STALL1` families record egress-buffer stall cycles waiting for transgress credits. They are split by AD/BL, agent 0/1, and transgress number. `STALL0` covers TGR0-TGR7 and `STALL1` covers TGR8-TGR10. These are high-signal events for diagnosing a specific transgress endpoint causing head-of-line blocking.

The largest visible group is `TxR` egress behavior. Horizontal egress events include bypass, full/not-empty cycles, inserts, NACKs, occupancy, ADS used, and starvation. Vertical egress mirrors much of that surface through `UNC_M2P_TxR_VERT_*` families. The chunk ends in ring-in-use events for horizontal and vertical AD/AK/AKC/BL/IV/TGC rings, where `UMask` distinguishes directions or side/parity such as `UP_EVEN`, `DN_ODD`, `LEFT_EVEN`, and `RIGHT_ODD`.

Smaller families include `UNC_M2P_CLOCKTICKS`, CMS state/distress assertions, ring bounces/starvation, and miscellaneous egress/ingress classification events. They provide context counters that can be correlated with the more granular credit and queue events.

## Important APIs, Types, And Data Contract

There are no functions or classes in this JSON file itself, but the fields are consumed as a structured API by perf's pmu-events tooling:

- `EventName` is the public symbolic name shown by `perf list` and accepted by perf event parsing. The generator lowercases it in `JsonEvent.name`.
- `EventCode` becomes the base `event=...` selector in generated event strings.
- `UMask` becomes `umask=...` when present and non-zero. Many families share one `EventCode` and rely entirely on `UMask` to select the subcondition.
- `Counter` constrains which hardware counter slots can program the event; most visible M2PCIe records use `0,1,2,3`.
- `Unit: "M2PCIe"` is converted by `jevents.py` into PMU name `uncore_m2pcie`, because unknown unit strings are mapped to `uncore_` plus the lowercased unit.
- `PerPkg: "1"` becomes the `pmu_event.perpkg` boolean and later `perf_pmu_alias.per_pkg`, indicating package-level aggregation semantics.
- `BriefDescription` maps to the short description; `PublicDescription` maps to the long description when it is not identical.
- `Experimental: "1"` is present on most records in this chunk. In the generator, this field primarily affects metric dependency analysis; event objects still compile into the PMU event table.

The generated C-side public type is `struct pmu_event` in `tools/perf/pmu-events/pmu-events.h`, with fields for `name`, `event`, `desc`, `topic`, `long_desc`, `pmu`, `unit`, `perpkg`, and `deprecated`. Runtime alias creation in `tools/perf/util/pmu.c` copies these values into `struct perf_pmu_alias` through `pmu_add_cpu_aliases_table()` and `perf_pmu__new_alias()`.

## Control Flow And Integration

Build-time control flow starts in `tools/perf/pmu-events/jevents.py`. The script loads the full JSON array with `json.load(..., object_hook=JsonEvent)`, converts each object into a `JsonEvent`, builds canonical event selector strings, folds duplicated strings into a shared big C string, and emits generated `pmu-events.c` tables. `EventCode` and `UMask` from this chunk become event terms such as `event=0xe0,umask=0x11`; `Unit: "M2PCIe"` groups these records under the `uncore_m2pcie` PMU table.

Model integration is through `tools/perf/pmu-events/arch/x86/mapfile.csv`, which maps `GenuineIntel-6-86` to `snowridgex`. At runtime, perf uses CPU identification and PMU names to find the Snow Ridge table, then filters events by PMU wildcard matching. When an `uncore_m2pcie` PMU is present, `pmu_add_cpu_aliases_table()` iterates matching generated events and creates aliases so users can request these `UNC_M2P_*` names.

User-visible control flow is simple: `perf list` enumerates these records with descriptions and package-scope metadata; `perf stat -e <event>` resolves a name to its generated selector string; the PMU layer programs the relevant uncore M2PCIe event code and mask into an available counter slot. The JSON does not implement sampling or counting logic; it supplies the selector vocabulary for hardware that does.

## State And Persistence Behavior

The chunk is static persisted metadata in source control. It has no mutable runtime state and does not maintain counters directly. State appears only when perf programs the corresponding hardware counters and reads their values from the uncore PMU.

Package scope is persisted inline with `PerPkg: "1"` and should affect aggregation and display. Credit occupancy, queue fullness, and starvation events are semantically stateful hardware observations, but the JSON only names and encodes them. The distinction matters for interpretation: events like `*_OCCUPANCY` and `*_CYCLES_NE` generally count cycles in a state, while `*_INSERTS`, `*_ACQUIRED`, and `*_RETURNED` generally count occurrences.

The `Experimental` flag is also persisted as data. Downstream reports and tests should treat these M2PCIe names as lower-stability hardware definitions even though they are compiled into perf like other events.

## Dependencies

This chunk depends on the perf PMU event JSON schema and the `jevents.py` converter's field naming conventions. It also depends on Intel Snow Ridge uncore hardware definitions for M2PCIe, CMS agents, transgress IDs, AD/AK/AKC/BL/IV/TGC message classes, M2IOSF ports, NCB/NCS/DRS message classes, and horizontal/vertical ring topology.

The content has implicit dependencies on adjacent chunks. The opening partial record and closing partial record cannot be validated or summarized completely without the previous and next line ranges. The final file-level report should also reconcile this M2PCIe section with earlier `IIO` and `iio_free_running` records in the same `uncore-io.json` file because they describe adjacent parts of the Snow Ridge I/O path.

Runtime dependencies include the presence of an `uncore_m2pcie` PMU exposed by the kernel for Snow Ridge systems. If the PMU is absent, the generated entries can still exist in perf's tables but will not become useful programmable aliases for that host.

## Risks And Edge Cases

- The chunk boundaries split JSON objects. Standalone parsing of this line range should fail; only the full file or reconciled neighboring chunks should be parsed as JSON.
- The range contains repeated mechanical families, so copy/paste drift is a real risk. Visible examples include AG1 BL acquired descriptions for `TGR6` and `TGR7` that repeat "For Transgress 4/5" text while the `EventName` suffixes and masks identify TGR6/TGR7.
- Some descriptions contain stale or generic topology text such as references to "JKT" or missing spaces around sentences. Generated help text will preserve these wording issues.
- `UMask` is the primary differentiator for many records with identical `EventCode`; a wrong mask silently changes the measured condition.
- Several aggregate masks combine credited and uncredited classes, such as `AD_ALL` and `BL_ALL`. Consumers should avoid summing aggregates with their components unless deliberately double-counting.
- Unit conversion is implicit. Since `M2PCIe` is not in the special-case unit table in `jevents.py`, it becomes `uncore_m2pcie` by convention. Renaming the JSON unit would change runtime PMU matching.
- Nearly all records are experimental, so dashboards or tests should prefer representative smoke coverage over strict semantic assertions for every event.

## Test Signals

Useful validation signals for this chunk and the later merged file include:

- Full-file JSON parsing succeeds for `uncore-io.json`; this line range alone is expected to be incomplete.
- The range contributes 488 visible complete `EventName` records, all under `Unit: "M2PCIe"`.
- Generated event strings for representative records include the expected base selector and mask, for example `UNC_M2P_RxR_OCCUPANCY.AD_ALL` as `event=0xe0,umask=0x11` and `UNC_M2P_IIO_CREDITS_REJECT.NCS` as `event=0x34,umask=0x20`.
- `jevents.py` maps `Unit: "M2PCIe"` to PMU name `uncore_m2pcie`, and perf alias creation can list a sample of `UNC_M2P_*` events for that PMU.
- Counter-slot constraints are preserved as `0,1,2,3` for the visible M2PCIe event families.
- Package-scope metadata survives generation so aliases are marked per-package.
- Event-family coverage tests should sample credit acquired/occupancy, IIO credit reject, P2P credit wait, RxR occupancy/inserts/starvation, TxR horizontal/vertical queue state, STALL0/STALL1 transgress stalls, and ring-in-use events.

### subset-b-006738: lines 10587-10668

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-io.json lines 10587-10668

## Scope And Purpose

This chunk is the final tail of the Snow Ridge X `uncore-io.json` PMU event table used by Linux `perf` under `tools/perf/pmu-events/arch/x86`. The source file is a JSON array of declarative event descriptors, not executable code. These descriptors let perf expose named uncore IO events and translate each `EventName` into the raw unit, event selector, mask, package scope, and counter constraints needed to program Snow Ridge X uncore PMUs.

The requested line range begins inside the already-open `UNC_M2P_VERT_RING_BL_IN_USE.UP_EVEN` object, starting at its `PublicDescription`, and then continues through the closing `]` of the top-level JSON array. Interpreting by event objects that intersect this range, the chunk covers the last 8 `M2PCIe` vertical-ring utilization descriptors in the file: 2 BL, 2 IV, and 4 TGC events. Seven of those objects are complete within the selected range; the first object is completed here but starts on line 10580 in the previous chunk.

All visible descriptors are package-scoped (`PerPkg: "1"`), experimental (`Experimental: "1"`), use programmable counters `0,1,2,3`, and belong to `Unit: "M2PCIe"`. The full file parses as one top-level JSON array with 924 event objects and this chunk supplies the final entries before the array terminator.

## Data Contract And Important Fields

There are no local functions, classes, or methods. The effective API is the PMU event metadata schema consumed by perf's pmu-events tooling:

- `EventName` is the user-facing symbolic alias. In this chunk the names are `UNC_M2P_VERT_RING_*_IN_USE.*` variants for BL, IV, and TGC vertical ring activity.
- `Unit` is `M2PCIe`, selecting the mesh-to-PCIe uncore PMU block rather than a core PMU or another uncore unit.
- `EventCode` identifies the hardware event family. `0xb2` is used for BL ring use, `0xb3` for IV ring use, and `0xb5` for TGC ring use.
- `UMask` selects the direction/parity subtype. Up/even uses `0x1`, up/odd uses `0x2`, down/even uses `0x4`, and down/odd uses `0x8` where the family supports even/odd split.
- `Counter` constrains scheduling to counters `0,1,2,3` on the M2PCIe PMU.
- `PerPkg` marks these as package-level uncore events, so interpretation and aggregation should be socket/package scoped.
- `Experimental` flags the events as less stable or less formally guaranteed than non-experimental aliases.
- `BriefDescription` and `PublicDescription` are the help text shown by list/documentation paths and are important for users interpreting ring-direction semantics.

## Event Families In This Chunk

The BL entries describe vertical BL ring cycles in use at the ring stop. The selected range completes `UNC_M2P_VERT_RING_BL_IN_USE.UP_EVEN` and includes the full `UNC_M2P_VERT_RING_BL_IN_USE.UP_ODD` object. Both share `EventCode: "0xb2"` and differ only by mask: `0x1` for up/even and `0x2` for up/odd. The public text says the count includes cycles where packets pass by or are sunk at this ring stop, but excludes packets being sent from the ring stop.

The IV entries are `UNC_M2P_VERT_RING_IV_IN_USE.DN` and `UNC_M2P_VERT_RING_IV_IN_USE.UP`, both using `EventCode: "0xb3"`. Unlike BL and TGC, this family exposes only direction-level masks in the visible tail: down is `0x4` and up is `0x1`. The description notes there is only one IV ring, so consumers wanting even or odd monitoring must combine up and down selections according to the surrounding ring topology guidance.

The TGC entries are a complete four-way direction/parity family under `EventCode: "0xb5"`: `DN_EVEN` (`0x4`), `DN_ODD` (`0x8`), `UP_EVEN` (`0x1`), and `UP_ODD` (`0x2`). Their descriptions follow the same vertical ring occupancy semantics as the BL events and explain the clockwise/counter-clockwise interpretation of up/down paths on the left and right sides of the ring.

## Control Flow And Integration

This JSON chunk has no direct runtime control flow. Its integration path is data-driven:

1. Perf's PMU event build tooling reads the Snow Ridge X JSON files and validates the top-level event array.
2. The generator converts each object into generated event tables or event-map data.
3. At runtime, perf selects the Snow Ridge X event map for matching hardware.
4. `perf list` and related help paths display the aliases and descriptions.
5. `perf stat` or similar commands resolve a selected alias to `Unit: M2PCIe`, the event code, the unit mask, package scope, and the allowed counter set before programming the uncore PMU.

The chunk is tightly coupled to earlier chunks because it is the tail of a single JSON array and begins mid-object. A processor must parse the full `uncore-io.json` file, or at least stitch adjacent chunks, rather than treating lines 10587-10668 as standalone JSON.

## State And Persistence Behavior

The file is static persisted metadata. It does not allocate memory, mutate state, or maintain counters itself. Runtime state lives in hardware counters after perf programs the selected uncore event.

The persistent state encoded here is semantic metadata: package scope through `PerPkg`, experimental status through `Experimental`, counter eligibility through `Counter`, and ring topology guidance through descriptions. Because the events are uncore and package-scoped, counts should not be interpreted as per-thread or per-core activity.

## Dependencies And External Contracts

The immediate dependency is perf's PMU event JSON schema, including support for string-encoded hexadecimal fields, comma-separated counter lists, optional descriptive fields, and package-level uncore metadata. The content depends on Intel Snow Ridge X M2PCIe uncore PMU definitions and on the kernel/perf uncore PMU naming that exposes a compatible `M2PCIe` unit.

The event aliases also depend on naming consistency with the rest of `uncore-io.json`. The dotted suffixes (`UP_EVEN`, `UP_ODD`, `DN_EVEN`, `DN_ODD`, `UP`, `DN`) are part of the public perf interface. Renaming them, changing masks, or moving them to another unit would be a user-visible behavioral change even though this is data-only source.

## Risks And Edge Cases

- The selected range starts at a `PublicDescription` line inside an object, so isolated JSON parsing of only these lines will fail. Full-file validation is the relevant test signal.
- Wrong `UMask` values are a high-risk metadata error: the file would remain syntactically valid but count the wrong ring direction or parity.
- The ring descriptions explain that up/down mapping reverses across ring sides and CBo halves. Documentation changes that simplify this text may make the counters easier to misuse.
- TGC public descriptions say "two rings in JKT" even though this file is for Snow Ridge X. This appears to be inherited vendor wording and should be checked against the source authority before changing.
- All entries are experimental, so downstream tests should verify parseability and event availability without assuming permanent semantic stability.
- Counter constraints are unit-specific. Ignoring `Counter: "0,1,2,3"` or `Unit: "M2PCIe"` could produce event scheduling failures or invalid PMU programming.

## Test Signals

Useful validation signals for this chunk and the final merged per-file report include:

- Parse the full `uncore-io.json` file as JSON and confirm it contains 924 top-level event objects and ends at line 10668.
- Confirm the final 8 objects are all `Unit: "M2PCIe"`, `PerPkg: "1"`, `Experimental: "1"`, and `Counter: "0,1,2,3"`.
- Verify the BL family uses `EventCode: "0xb2"` with `UP_EVEN` mask `0x1` and `UP_ODD` mask `0x2`.
- Verify the IV family uses `EventCode: "0xb3"` with `UP` mask `0x1` and `DN` mask `0x4`.
- Verify the TGC family uses `EventCode: "0xb5"` with masks `UP_EVEN=0x1`, `UP_ODD=0x2`, `DN_EVEN=0x4`, and `DN_ODD=0x8`.
- Run perf PMU event generation or schema checks to catch malformed JSON, missing required fields, duplicate aliases, or unsupported unit/counter metadata.
- On Snow Ridge X hardware with matching uncore PMUs, use `perf list` and short `perf stat` probes for representative aliases such as `UNC_M2P_VERT_RING_BL_IN_USE.UP_EVEN`, `UNC_M2P_VERT_RING_IV_IN_USE.DN`, and `UNC_M2P_VERT_RING_TGC_IN_USE.UP_ODD`.
