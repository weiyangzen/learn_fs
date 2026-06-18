# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json lines 1-6626

## Scope

This chunk covers the first 6,626 lines of the Ice Lake Xeon uncore interconnect PMU event JSON table. The full file is a JSON array; this range contains 643 complete event objects and ends in the middle of the `UNC_M2M_TxR_HORZ_*` event families. The covered records are data definitions, not executable code.

## Purpose

The file provides perf's Ice Lake Xeon uncore interconnect event metadata. These records are consumed by the perf PMU event generation flow (`tools/perf/pmu-events/jevents.py`) and compiled into generated `pmu-events.c` tables that runtime perf code queries through `pmu_events_table` helpers. Users see the resulting aliases through commands such as `perf list` and use them as event names in perf stat/record workflows on matching x86 platforms.

In this chunk the event set starts with IRP unit events and then transitions into M2M/Common Mesh Stop events:

- `IRP` events: 73 records for IO coherency tracker activity, inbound/outbound IRP inserts, reads, writes, snoops, request queues, peer-to-peer, fast/slow-path and timeout/misc counters.
- `M2M` events: 570 records for mesh-to-memory/common mesh stop behavior, including clocks, directory lookups/hits/misses, iMC read/write classification, Near Memory tag hits, prefetch CAM behavior, tracker occupancy/full/not-empty, credit acquisition/occupancy, receiver/transgress queue occupancy/inserts/bypass/starvation, stalls, ring usage/bounces, distress, and the beginning of horizontal egress insert/NACK/occupancy families.

## Data Shape

Each event object uses the standard perf PMU event schema fields:

- `EventName`: canonical alias, for example `UNC_I_CLOCKTICKS`, `UNC_I_TRANSACTIONS.READS`, or `UNC_M2M_IMC_WRITES.PMM_NM_MISS`.
- `EventCode`: low-level event selector, represented as a hex string. Casing is inconsistent (`0x0F` and `0x0f` both appear), so consumers must treat it semantically as a number/string accepted by jevents rather than as a normalized display token.
- `UMask`: optional unit mask. Some events, especially broad clock or whole-event records, omit it.
- `Counter`: allowed counter indexes. IRP events in this chunk normally use `0,1`; M2M events normally use `0,1,2,3`.
- `Unit`: PMU unit name. This chunk has only `IRP` and `M2M`.
- `PerPkg`: almost every record is package-scoped with `"1"`, matching uncore PMU behavior.
- `BriefDescription` and sometimes `PublicDescription`: user-facing descriptions for event listing and help output.
- `Experimental`: many records are marked experimental, which should be preserved by generation and listing tools.

The JSON array ordering is significant for human maintainability and generated table stability, but the runtime lookup key is the event alias plus PMU matching logic rather than source line number.

## Important Event Families

The IRP section includes:

- Cache/read/write occupancy and request counts: `UNC_I_CACHE_TOTAL_OCCUPANCY.*`, `UNC_I_READS.*`, `UNC_I_WRITES.*`, `UNC_I_TRANSACTIONS.*`.
- Coherency operations: `UNC_I_COHERENT_OPS.*`, including CLFLUSH, PCITOM, RFO, and WBMTOI.
- FAF and IRP queue flow: `UNC_I_FAF_*`, `UNC_I_IRP_ALL.*`, `UNC_I_IRP_OCCUPANCY.*`, `UNC_I_IRP_PORT0/1.*`.
- Miscellaneous fast-path, slow-path, timeout, interrupt, retry, and source classifications: `UNC_I_MISC0.*`, `UNC_I_MISC1.*`, `UNC_I_REQUESTS.*`, `UNC_I_SNOOP_RESP.*`, `UNC_I_SNOOPS.*`, `UNC_I_P2P_TRANSACTIONS.*`.

The M2M section includes:

- Common activity and clocks: `UNC_M2M_CLOCKTICKS`, `UNC_M2M_CORE_SNOOP`, `UNC_M2M_RFO_*`.
- Directory and tag behavior: `UNC_M2M_DIRECTORY_LOOKUP.*`, `UNC_M2M_DIRECTORY_HIT.*`, `UNC_M2M_DIRECTORY_MISS.*`, `UNC_M2M_TAG_HIT.*`.
- iMC read/write routing and memory type breakdowns: `UNC_M2M_IMC_READS.*` and `UNC_M2M_IMC_WRITES.*`, with many combinations for all/partial/full writes, PMM/DRAM, Near Memory hit/miss, bypass, and directory state.
- Prefetch CAM behavior: `UNC_M2M_PREFCAM_*`, including occupancy, full/not-empty cycles, inserts, deallocations, demand drops, merge/no-merge, response misses, and per-channel drop reasons.
- Tracker and request queue pressure: `UNC_M2M_TRACKER_*`, `UNC_M2M_RPQ_*`, `UNC_M2M_RxR_*`, `UNC_M2M_TxC_*`, and `UNC_M2M_TxR_*`.
- Mesh/ring and stall signals: `UNC_M2M_HORZ_RING_*`, `UNC_M2M_RING_*`, `UNC_M2M_STALL*`, and `UNC_M2M_DISTRESS_ASSERTED.*`.
- Agent credit accounting: `UNC_M2M_AG0_*` and `UNC_M2M_AG1_*`, with AD/BL credit acquired and occupancy counters split across transgress lanes.

## Control Flow and Runtime Integration

There is no in-file control flow. The effective flow is build-time and data-driven:

1. Perf's PMU event build scans architecture map files and JSON event files under `tools/perf/pmu-events/arch`.
2. `jevents.py` parses the JSON records, validates expected keys, and emits compact C tables.
3. The perf build links those generated tables through `libpmu-events.a`.
4. Runtime PMU code, including helpers referenced from `util/pmu.c` and `util/pmus.c`, finds the model's PMU table and exposes aliases to `perf list` and event parsing.
5. When a user selects one of these aliases, perf maps the alias metadata into event code, unit mask, counter constraints, unit/PMU matching, descriptions, and package-scoped semantics.

The `Unit` field is the key integration point for uncore PMU matching. If an event is assigned to the wrong unit, generated aliases may be hidden, listed under the wrong PMU, or parsed against the wrong sysfs event format.

## State and Persistence

This JSON file is persistent source metadata. It does not maintain runtime state, but it determines generated build artifacts and user-visible perf aliases. The persistent state boundary is:

- source JSON in the repository,
- generated `pmu-events.c` and object/archive outputs during the perf build,
- runtime PMU alias tables loaded from the generated data.

Counter values themselves come from hardware PMUs at runtime and are not stored here. The descriptions and event encodings in this file are the durable contract that connects Intel uncore documentation to perf's generated event tables.

## Dependencies

This chunk depends on the perf PMU events infrastructure accepting the schema used here. Important dependencies and assumptions include:

- Valid JSON array syntax across the whole source file. This chunk starts at the array opener but the full file must close later.
- `jevents.py` support for fields such as `BriefDescription`, `PublicDescription`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `Experimental`.
- x86 architecture mapping that selects the `icelakex` event directory for the matching CPU model.
- Runtime PMU unit names compatible with Linux perf uncore PMU names for Ice Lake Xeon.
- Consumer support for uncore package-scoped events and counter restrictions.

## Risks and Edge Cases

- The chunk boundary cuts after line 6,626 inside the larger file, so this report cannot describe the later continuation of `UNC_M2M_TxR_HORZ_OCCUPANCY` or later event units/families.
- Many records are mechanical variants over lanes, channels, agents, and masks. Copy/paste mistakes in `EventName`, `EventCode`, `UMask`, or description text can silently create misleading aliases even when the JSON remains syntactically valid.
- Hex string casing is mixed. Any tests or comparison tools that do textual normalization poorly may report false diffs or miss duplicate encodings.
- Some records omit `UMask`; this is valid for certain whole events but should be deliberate. Missing masks in variant families can be suspicious.
- `Experimental` is common in this range. Downstream UI or scripts may filter or annotate these events differently.
- Because the records are uncore events with `PerPkg`, users can misinterpret counts if they expect per-core semantics or if socket/package aggregation is not considered.
- The M2M records encode detailed platform-specific behavior, including PMM/Near Memory classifications. On systems without the corresponding hardware mode, aliases may be present but not meaningful or may depend on model matching.

## Test Signals

Useful validation signals for this chunk include:

- `jq` can parse the complete `uncore-interconnect.json` file and report the expected array length.
- Generated PMU event build succeeds with `NO_JEVENTS` disabled, proving `jevents.py` accepts all records.
- `perf list` on matching Ice Lake Xeon hardware exposes representative aliases from this chunk, such as `UNC_I_CLOCKTICKS`, `UNC_I_TRANSACTIONS.READS`, `UNC_M2M_CLOCKTICKS`, `UNC_M2M_IMC_READS.ALL`, and `UNC_M2M_PREFCAM_DEMAND_DROPS.UPI_ALLCH`.
- Event parsing accepts aliases with their unit constraints and maps to the expected event code and unit mask.
- Schema linting checks for duplicate `EventName` values, malformed hex fields, missing required descriptions, and suspicious absent `UMask` values in otherwise mask-split families.
- Regression checks compare generated `pmu-events.c` before and after changes to ensure intended changes are limited to affected aliases.

## Chunk Notes for Merge

The final per-file research should merge this with later chunks to cover the rest of the JSON array. For this chunk, the source path is `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-interconnect.json`, and the covered line range is 1-6626. The most important merge detail is that this range begins the file, establishes the JSON schema, fully covers the IRP unit section, and covers the early-to-middle M2M section through horizontal transgress egress NACK and the first occupancy record.
