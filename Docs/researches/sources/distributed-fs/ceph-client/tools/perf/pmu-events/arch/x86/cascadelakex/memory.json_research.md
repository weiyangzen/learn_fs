# Research: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/memory.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006642`: lines 1-6433, `Docs/researches/chunks/subset-b-006642_research.md`
- `subset-b-006643`: lines 6434-7766, `Docs/researches/chunks/subset-b-006643_research.md`

## Chunk Research

### subset-b-006642: lines 1-6433

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

### subset-b-006643: lines 6434-7766

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/memory.json lines 6434-7766

## Scope

This chunk covers the final 1,333 lines of the Cascadelake-X `memory.json` PMU event table used by the vendored Linux `tools/perf` event-list machinery. The range starts immediately after the opening brace for a deprecated `OFFCORE_RESPONSE.PF_L1D_AND_SW...HIT_OTHER_CORE_FWD` event and runs through the closing `]` of the JSON array.

The chunk contains 125 event objects by name. The first 105 are deprecated `OFFCORE_RESPONSE.*` aliases for offcore response filters, each pointing users to a replacement `OCR.*` event name in `BriefDescription`. The last 20 entries are non-deprecated transactional memory events for RTM, TSX execution conditions, and TSX/HLE memory-abort reasons.

## Purpose

The file is declarative metadata rather than executable Ceph logic. Perf consumes this JSON to expose architecture-specific event names, event select values, unit masks, offcore MSR filters, sampling defaults, PEBS attributes, and deprecation hints for Intel Cascadelake-X CPUs.

Within this chunk, the deprecated offcore aliases preserve compatibility for older event names while steering users and tooling toward newer `OCR.*` names. The aliases still carry complete programming information: `EventCode` is `0xB7, 0xBB`, `UMask` is `0x1`, `Counter` is `0,1,2,3`, `MSRIndex` is `0x1a6,0x1a7`, and `MSRValue` encodes the offcore request, locality, cache-state, and snoop-response filter bits.

The transactional-memory tail provides direct event definitions for Intel TSX profiling. `RTM_RETIRED.*` counts RTM start, commit, and abort categories; `TX_EXEC.*` counts instructions or conditions that may cause transactional aborts; `TX_MEM.*` counts capacity, conflict, HLE lock-buffer, and elided-lock abort reasons.

## Important Data and Event Families

The event objects all use perf PMU JSON schema keys, primarily `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and sometimes `PublicDescription`, `Deprecated`, `MSRIndex`, `MSRValue`, and `PEBS`.

The deprecated offcore events in this range are all `OFFCORE_RESPONSE.*` names. They are compatibility aliases for `OCR.*` replacements and all set `"Deprecated": "1"`. Their `BriefDescription` has a uniform migration message naming the replacement event. These entries program the offcore response events through event codes `0xB7, 0xBB`, allowing perf to choose either offcore response MSR slot `0x1a6` or `0x1a7`.

The visible offcore request classes are prefetch-oriented. The range begins at the tail of `PF_L1D_AND_SW` remote-hop1-DRAM response variants, then covers `PF_L2_DATA_RD`, `PF_L2_RFO`, `PF_L3_DATA_RD`, and `PF_L3_RFO` groups. These distinguish prefetch levels and request intent: data read versus read-for-ownership.

The offcore response dimensions are repeated across request classes. Generic `L3_MISS` entries include `ANY_SNOOP`, `HITM_OTHER_CORE`, `HIT_OTHER_CORE_FWD`, `HIT_OTHER_CORE_NO_FWD`, `NO_SNOOP_NEEDED`, `REMOTE_HITM`, `REMOTE_HIT_FORWARD`, `SNOOP_MISS`, and `SNOOP_NONE`. Local-DRAM entries add `L3_MISS_LOCAL_DRAM.*`, including `SNOOP_MISS_OR_NO_FWD`. Remote memory entries include `L3_MISS_REMOTE_DRAM.SNOOP_MISS_OR_NO_FWD` and the fuller `L3_MISS_REMOTE_HOP1_DRAM.*` response matrix.

`RTM_RETIRED.*` entries use event code `0xC9`. `RTM_RETIRED.START` counts non-nested RTM region entry, `COMMIT` counts successful commits, and `ABORTED`/`ABORTED_*` categorize aborts by memory events, incompatible memory type, uncommon/timer conditions, unfriendly instructions, and residual event causes. `RTM_RETIRED.ABORTED` has `PEBS: "2"`.

`TX_EXEC.*` entries use event code `0x5d` and unit masks `0x1` through `0x10`. They count execution of instruction classes or transactional nesting/mixing conditions that may abort a transaction, including `vzeroupper`, excessive nesting, XBEGIN inside HLE, and HLE XACQUIRE inside RTM.

`TX_MEM.*` entries use event code `0x54`. The memory abort categories include `ABORT_CONFLICT`, `ABORT_CAPACITY`, `ABORT_HLE_STORE_TO_ELIDED_LOCK`, `ABORT_HLE_ELISION_BUFFER_NOT_EMPTY`, `ABORT_HLE_ELISION_BUFFER_MISMATCH`, `ABORT_HLE_ELISION_BUFFER_UNSUPPORTED_ALIGNMENT`, and `HLE_ELISION_BUFFER_FULL`.

## Control Flow

There is no in-file control flow. Runtime behavior is driven by perf's event lookup and PMU programming flow:

1. Perf maps a user-visible event string such as an `OFFCORE_RESPONSE.*`, `RTM_RETIRED.*`, `TX_EXEC.*`, or `TX_MEM.*` name to the matching JSON object for the detected Cascadelake-X CPU.
2. Perf validates counter constraints and deprecation metadata. Deprecated aliases remain usable but can produce guidance toward the `OCR.*` replacement names.
3. For offcore response aliases, perf programs event select `0xB7` or `0xBB` with `UMask 0x1` and writes the filter value to one of the offcore response MSRs listed by `MSRIndex`.
4. For TSX events, perf programs the direct event code and unit mask, and may use PEBS for `RTM_RETIRED.ABORTED` according to the `PEBS` metadata.
5. Sampling defaults come from `SampleAfterValue`: the deprecated offcore aliases use `100003`, while the TSX events use `2000003`.

The repeated `MSRValue` patterns are the most important implicit flow for the offcore events. The request class contributes low request bits, locality contributes memory-source bits, and response/snoop state contributes upper filter bits. Perf does not derive these values from the event name in this file; it consumes the explicit `MSRValue`.

## State and Persistence Behavior

The JSON itself has no mutable runtime state. Its contents persist as static tool metadata in the repository and in built perf installations.

At runtime, perf translates selected entries into kernel perf event attributes and, for offcore response events, model-specific register configuration. Those programmed counter/MSR states live only for the lifetime of the perf event or measurement session.

The deprecation state is declarative and persistent. Removing these aliases would break users, scripts, dashboards, or tests that still request the old `OFFCORE_RESPONSE.*` names. Keeping `Deprecated: "1"` while retaining the programming fields supports compatibility without making the aliases the preferred interface.

The TSX counters measure dynamic CPU state: RTM/HLE starts, commits, abort causes, instruction classes, capacity pressure, conflicts, and elision-buffer conditions. The metadata does not store measurements; it only defines how perf should configure hardware to collect them.

## Dependencies and Integration Points

This file integrates with the Linux perf PMU event-table parser under `tools/perf`, with generated event lists for x86 CPU models, and with Intel Cascadelake-X core PMU semantics. It is vendored under `sources/distributed-fs/ceph-client`, so its main dependency is the imported Linux toolchain data rather than Ceph application code.

The offcore entries depend on Intel offcore response MSRs `0x1a6` and `0x1a7` and the event encodings for `OFFCORE_RESPONSE` event selects `0xB7` and `0xBB`. Correct behavior also depends on the perf core knowing that `MSRValue` belongs in the matching offcore response MSR slot.

The replacement names referenced in `BriefDescription` depend on corresponding `OCR.*` event definitions elsewhere in this JSON file or adjacent PMU event data. The merge lane should confirm those replacement events are present in earlier chunks before treating the deprecation guidance as fully resolvable.

The TSX events depend on Cascadelake-X support for RTM/HLE-related PMU events and on runtime CPU/firmware policy. Systems with TSX disabled, restricted, or affected by microcode behavior can expose event names while producing unavailable, zero, or misleading measurements depending on perf/kernel handling.

## Risks and Edge Cases

JSON validity is a high-level risk because this chunk closes the array. The first line of this chunk is inside an object whose opening brace is in the preceding chunk, while the final line is the file's closing bracket. Chunk-local review must not assume the range is independently parseable JSON.

Offcore alias drift is the main semantic risk. Each deprecated `OFFCORE_RESPONSE.*` entry must continue to match the hardware filter implied by its name and by the referenced `OCR.*` replacement. A wrong `MSRValue`, `MSRIndex`, request-class bit, locality bit, or snoop-response bit can silently count the wrong memory behavior.

The duplicate event-code form `0xB7, 0xBB` requires parser support for events that can use either offcore response slot. Tools that expect a single numeric event code could mishandle these aliases.

Deprecation must remain non-destructive. If `Deprecated` entries are hidden too aggressively, old user workflows break; if they are not clearly marked, users may keep building new tooling on names that the file itself says should migrate to `OCR.*`.

The offcore response names are long and highly patterned, so copy/paste errors are plausible. Important pairings include local versus remote DRAM, remote hop1 versus generic remote, data-read versus RFO, L2 versus L3 prefetch source, and `HIT_OTHER_CORE_FWD` versus `HIT_OTHER_CORE_NO_FWD`.

TSX metrics are sensitive to platform configuration and microcode. Counting RTM/HLE events without checking TSX availability can lead to confusing diagnostics. Some abort categories overlap conceptually, and `RTM_RETIRED.ABORTED` explicitly notes that multiple categories may count as one abort.

Sampling defaults differ between the two families. Applying the offcore sample-after value to TSX events, or vice versa, would change profiling overhead and sample density.

## Test Signals

Useful validation for this chunk includes parsing the complete `memory.json` with a strict JSON parser and verifying that all 125 event objects in this line range are reachable through perf's generated event tables.

Schema validation should confirm required keys for each family: deprecated offcore aliases need `Deprecated`, `EventCode`, `UMask`, `MSRIndex`, `MSRValue`, `Counter`, `SampleAfterValue`, and a replacement-bearing `BriefDescription`; TSX events need direct `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and useful descriptions.

Deprecation tests should request representative old names such as `OFFCORE_RESPONSE.PF_L2_DATA_RD.L3_MISS.ANY_SNOOP`, `OFFCORE_RESPONSE.PF_L3_DATA_RD.L3_MISS_LOCAL_DRAM.SNOOP_NONE`, and `OFFCORE_RESPONSE.PF_L3_RFO.L3_MISS_REMOTE_HOP1_DRAM.SNOOP_MISS`, then verify that perf accepts them, marks or reports deprecation as expected, and points to the corresponding `OCR.*` event.

Offcore programming tests should check that selected aliases program event code `0xB7` or `0xBB`, unit mask `0x1`, the correct offcore response MSR, and the expected `MSRValue`. A useful cross-check is comparing each deprecated alias's value with its `OCR.*` replacement.

TSX tests should run on hardware/configurations where TSX is enabled and verify `RTM_RETIRED.START`, `RTM_RETIRED.COMMIT`, `RTM_RETIRED.ABORTED_MEM`, `TX_EXEC.MISC*`, `TX_MEM.ABORT_CONFLICT`, and `TX_MEM.ABORT_CAPACITY` against synthetic workloads that deliberately commit, conflict, exceed capacity, or execute abort-prone instructions.

Negative test signals include running the same TSX event requests on TSX-disabled systems and confirming perf/kernel behavior is explicit rather than silently misreported.

Regression tests should cover the tail-of-file structure: the object spanning the chunk boundary must remain comma-separated correctly from the preceding event, and the last `TX_MEM.HLE_ELISION_BUFFER_FULL` object must be followed only by the closing array bracket.

## Cross-Chunk Notes

This chunk is the terminal chunk for `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/memory.json`. The first event object begins one line before this chunk, so the merge lane should combine this report with the preceding chunk before producing the final per-file report.

Earlier chunks are needed to describe the complete memory event catalog and to verify that every `OCR.*` replacement referenced here exists with matching hardware encodings. This chunk alone establishes the compatibility-alias tail and the TSX transactional-memory tail of the file.
