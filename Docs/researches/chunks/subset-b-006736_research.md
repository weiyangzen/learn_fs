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
