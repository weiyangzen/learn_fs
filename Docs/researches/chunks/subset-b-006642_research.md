# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/memory.json lines 1-6433

## Scope

This chunk covers the first 6,433 lines of the Cascade Lake Xeon `memory.json` PMU event table used by Linux `perf` PMU event generation. The physical file contains 743 JSON objects, but this chunk contains 618 complete event objects; line 6433 is the opening brace for the next object, so the last complete event in scope is `OFFCORE_RESPONSE.PF_L1D_AND_SW.L3_MISS_REMOTE_HOP1_DRAM.HITM_OTHER_CORE`.

## Purpose

The file is static event metadata, not executable Ceph client logic. Its purpose is to describe Cascade Lake X memory-related hardware performance events in the schema consumed by `tools/perf/pmu-events`: event aliases, encodings, counters, optional model-specific register setup, sampling defaults, PEBS/data-source capabilities, deprecation state, and short descriptions.

In a built perf tree, these records become part of the generated PMU event tables. Users can then select aliases such as `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128`, `OCR.DEMAND_DATA_RD.L3_MISS.REMOTE_HITM`, or deprecated compatibility names under `OFFCORE_RESPONSE.*` instead of spelling raw event/umask/MSR encodings by hand.

## Data Shape And Event Schema

Each complete in-scope object has:

- `EventName`: the perf alias exposed to users and metric authors.
- `EventCode` and `UMask`: the architectural event selector fields programmed into the core PMU.
- `Counter`: allowed programmable counters, consistently `0,1,2,3` for this chunk.
- `SampleAfterValue`: default sampling period used when sampling the event.
- `BriefDescription`: short human-readable help text.

Optional fields in this chunk include:

- `MSRIndex` and `MSRValue`: present on 603 of 618 records, mostly offcore response/request aliases that need offcore response filter MSRs `0x1a6`/`0x1a7` or load-latency threshold MSR `0x3f6`.
- `Deprecated`: present on 245 records, marking old `OFFCORE_RESPONSE.*` aliases that point users to newer `OCR.*` names.
- `CounterMask`: present on cycle/activity and offcore outstanding events that need a minimum number of cycles or outstanding requests.
- `PEBS`: marks precise-event support on HLE and load-latency records.
- `Data_LA`: marks load-latency events that support data linear address capture.
- `PublicDescription`: longer help text for selected events.
- `Errata`: `MACHINE_CLEARS.MEMORY_ORDERING` carries erratum `SKL089`.

## In-Scope Event Families

The chunk starts with scalar memory and transactional-memory events:

- `CYCLE_ACTIVITY.*`: cycle and stall accounting while L3 miss demand loads are outstanding.
- `HLE_RETIRED.*`: Hardware Lock Elision start, commit, and abort categories.
- `MACHINE_CLEARS.MEMORY_ORDERING`: machine clears caused by memory ordering conflicts.
- `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`: PEBS-capable sampled load-latency thresholds from 4 through 512 cycles, using `MSRIndex` `0x3F6` and threshold-specific `MSRValue`.

The dominant portion is offcore L3-miss response accounting:

- `OCR.*`: current aliases for offcore response classes. This chunk includes 14 request classes with 25 variants each: `ALL_DATA_RD`, `ALL_PF_DATA_RD`, `ALL_PF_RFO`, `ALL_READS`, `ALL_RFO`, `DEMAND_CODE_RD`, `DEMAND_DATA_RD`, `DEMAND_RFO`, `OTHER`, `PF_L1D_AND_SW`, `PF_L2_DATA_RD`, `PF_L2_RFO`, `PF_L3_DATA_RD`, and `PF_L3_RFO`.
- `OFFCORE_RESPONSE.*`: deprecated aliases mapping to the same offcore encodings as `OCR.*`. This chunk includes full 25-event groups for `ALL_DATA_RD`, `ALL_PF_DATA_RD`, `ALL_PF_RFO`, `ALL_READS`, `ALL_RFO`, `DEMAND_CODE_RD`, `DEMAND_DATA_RD`, `DEMAND_RFO`, and `OTHER`, plus the first 20 events of `PF_L1D_AND_SW`.
- `OFFCORE_REQUESTS.*` and `OFFCORE_REQUESTS_OUTSTANDING.*`: direct request and outstanding-demand-data-read aliases for L3-miss demand data reads.

The repeated 25-event offcore pattern combines a request type with response/locality/snoop filters:

- Generic `L3_MISS.*`: `ANY_SNOOP`, `HITM_OTHER_CORE`, `HIT_OTHER_CORE_FWD`, `HIT_OTHER_CORE_NO_FWD`, `NO_SNOOP_NEEDED`, `REMOTE_HITM`, `REMOTE_HIT_FORWARD`, `SNOOP_MISS`, and `SNOOP_NONE`.
- `L3_MISS_LOCAL_DRAM.*`: local DRAM variants, including `SNOOP_MISS_OR_NO_FWD`.
- `L3_MISS_REMOTE_DRAM.SNOOP_MISS_OR_NO_FWD`.
- `L3_MISS_REMOTE_HOP1_DRAM.*`: remote-hop DRAM variants for any snoop, hitm, forwarded hit, no-forward hit, no-snoop-needed, snoop miss, and snoop none.

## Control Flow And Integration

There is no runtime control flow inside this JSON file. The effective flow is external:

1. Perf build tooling discovers architecture/model JSON files under `tools/perf/pmu-events/arch/x86/cascadelakex/`.
2. The PMU event generator parses the JSON array and emits compiled event table data for Cascade Lake X.
3. Runtime perf commands match the host CPU model to this table and expose `EventName` aliases through `perf list`, `perf stat`, `perf record`, and metric resolution.
4. When a user selects an alias, perf programs the listed `EventCode`, `UMask`, counter constraints, optional `CounterMask`, and any `MSRIndex`/`MSRValue` offcore or latency filter setup.

The main integration point is therefore the perf PMU-events schema and x86 PMU programming path. The entries are architecture-specific and depend on Intel Cascade Lake X event semantics; incorrect values can lead to silently wrong measurements even if the JSON remains syntactically valid.

## State And Persistence

This chunk is persistent static metadata in source control. It does not maintain mutable state, write files, or depend on runtime storage. The closest stateful behavior appears when perf uses records with `MSRIndex`/`MSRValue`: those aliases require programming model-specific registers while a counting or sampling session is active. Deprecated aliases are also persistent compatibility state: they keep older perf event names resolvable while steering users toward `OCR.*`.

## Dependencies

The data depends on:

- The Linux perf PMU-events JSON schema, including accepted keys such as `EventName`, `EventCode`, `UMask`, `MSRIndex`, `MSRValue`, `PEBS`, `Deprecated`, and `SampleAfterValue`.
- x86 Cascade Lake X PMU event encodings and Intel offcore response MSR bit layouts.
- Perf's generated table builder and runtime alias resolver.
- Hardware support for PEBS/data-address capture on the marked load-latency and HLE records.

It has no direct dependency on Ceph client code. Its location under `sources/distributed-fs/ceph-client/tools/perf` indicates this repository vendors or mirrors perf tooling as part of the source corpus.

## Risks And Maintenance Notes

- Offcore aliases are highly repetitive and differ mainly by `MSRValue`; copy/paste mistakes can preserve valid JSON while changing the measured request type, locality, or snoop state.
- Deprecated `OFFCORE_RESPONSE.*` aliases must stay aligned with their `OCR.*` replacements. The deprecation descriptions are the visible migration path for users.
- Line 6433 starts an incomplete next object relative to this chunk boundary. Merge/reconciliation should avoid double-counting that following event when combining chunk reports.
- Several `BriefDescription` strings are mechanically repeated or terse. They are good enough for alias discovery but provide limited semantic detail without Intel PMU documentation.
- Events using `MSRIndex` `0x1a6,0x1a7` rely on offcore response filter programming. Any parser or runtime path that mishandles comma-separated event codes or MSR indexes will break a large majority of this chunk.
- `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` events have low sample periods and PEBS/data-address behavior; tests need hardware-aware validation because parser-only checks cannot prove data-source correctness.

## Test Signals

Useful validation signals for this chunk are:

- JSON parses as an array and the first 618 complete objects expose required core keys.
- `perf list` on a Cascade Lake X capable build shows representative aliases from each family, including `CYCLE_ACTIVITY.CYCLES_L3_MISS`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_64`, `OCR.ALL_READS.L3_MISS.REMOTE_HITM`, and deprecated `OFFCORE_RESPONSE.ALL_READS.L3_MISS.REMOTE_HITM`.
- Generated PMU table tests preserve `MSRIndex`/`MSRValue` for offcore aliases and `MSRIndex` `0x3F6` thresholds for load-latency aliases.
- Deprecated records remain visible with `Deprecated` metadata and point to the matching `OCR.*` replacement in `BriefDescription`.
- Hardware smoke tests with `perf stat -e <alias>` or `perf record -e <PEBS alias>` should fail clearly on unsupported hosts but resolve aliases correctly on matching Cascade Lake X systems.
