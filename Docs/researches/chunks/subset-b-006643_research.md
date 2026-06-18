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
