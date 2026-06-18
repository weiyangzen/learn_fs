# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/cache.json

## Purpose

`cache.json` is a Knights Landing x86 perf PMU event definition file for cache, L2, memory-uop, and offcore-response cache-hit analysis. It is data consumed by the Linux `perf` PMU event-table tooling, not executable code. Its records let users name KNL events such as `MEM_UOPS_RETIRED.L2_MISS_LOADS` or `OFFCORE_RESPONSE.ANY_READ.L2_HIT_FAR_TILE` instead of hand-programming event codes, umasks, and offcore response MSRs.

The file contains 213 event records. Most of the file is a generated-looking matrix of `OFFCORE_RESPONSE` aliases: 200 entries combine request classes with response classes for KNL tile-local, near-tile, far-tile, miss, outstanding, and any-response cases. The remaining records cover core/L2 queue rejection, icache fill stalls, L2 prefetch allocation, L2 request reference/miss counts, L2 request rejection, and retired memory uops by load/store and L1/L2/TLB/HITM categories.

## Important APIs, Types, and Schema

The effective API is the perf JSON event schema. Important fields are:

- `EventName`: canonical perf event alias, grouped by dotted family names such as `OFFCORE_RESPONSE`, `MEM_UOPS_RETIRED`, and `L2_REQUESTS`.
- `EventCode`: programmable raw event selector, commonly `0xB7` for offcore response and `0xD0` for retired memory uops.
- `UMask`: unit mask when the event needs one; many offcore rows share `0x1`.
- `Counter`: KNL programmable counter constraint. Every entry in this file uses `0,1`.
- `MSRIndex` and `MSRValue`: extra selector state for offcore-response events. Values target `0x1a6`, `0x1a7`, or both, with some partial-write and outstanding forms constrained to one MSR/counter path.
- `PEBS` and `Data_LA`: present on selected precise retired-memory-uop events, marking precise-event and data linear-address capability.
- `SampleAfterValue`, `BriefDescription`, and occasional `PublicDescription`: sampling defaults and user-facing metadata.

There are no functions or classes in this source. Downstream parsers treat the top-level JSON array as an ordered list of event descriptors.

## Control Flow and Data Flow

At build or install time, perf's PMU event tooling parses this JSON with the other KNL files, validates required fields, and converts records into event tables. At runtime, a perf command that names one of these aliases looks up the `EventName`, configures the core PMU with `EventCode`/`UMask`, applies `Counter` constraints, and writes `MSRIndex`/`MSRValue` for offcore-response filters when present.

The offcore rows encode a two-axis flow: request type first, response type second. Request classes include any code/data/read/request/RFO, bus locks, demand code/data/RFO, full or partial streaming stores, partial reads/writes, L1/L2 hardware prefetches, software prefetches, and UC code reads. Response classes include any response, tile-local cache states (`E`, `F`, `M`, `S`), near/far tile hits, L2 miss, and outstanding weighted-cycle forms.

## State and Persistence Behavior

This file is static source data. It persists PMU programming constants in the repository and has no runtime mutable state. Runtime state is external: perf may program core counters and offcore MSRs based on these records, but the JSON itself is not modified.

The ordering of the array is part of the practical maintenance surface because generated C tables and diagnostics often preserve input order. Consumers should not depend on unique prefixes alone; full `EventName` values are the stable keys.

## Dependencies and Integration Points

The file integrates with:

- Linux perf's `pmu-events` parser/generator under `tools/perf/pmu-events`.
- KNL architecture selection logic that loads `arch/x86/knightslanding` event tables for matching CPU IDs.
- The sibling `counter.json`, which declares that the KNL core PMU has two generic counters plus fixed counters; the `Counter: "0,1"` constraints in this file rely on that model.
- Offcore response MSRs `0x1a6` and `0x1a7`, which must be programmed consistently with the selected event and available counter.

## Risks and Edge Cases

The main correctness risk is selector drift: an incorrect `MSRValue` can produce a valid perf event that measures the wrong request/response combination. The offcore matrix is repetitive, so copy/paste mistakes are plausible and hard to spot by syntax alone.

Several rows have hardware-specific counter/MSR restrictions. For example, outstanding-response and partial-write style events may only be valid through a particular offcore MSR or counter path even though the visible `Counter` field still says `0,1`. Tooling that ignores `MSRIndex` or mishandles comma-separated MSR indices will silently misprogram these aliases.

Descriptions mention speculative-path inclusion and weighted-cycle semantics for some events. Users can misinterpret these as exact retired-request counts when they are not. PEBS/data-address metadata must also stay paired with only the precise events that support it.

## Test Signals

Useful validation signals are: `jq empty cache.json` succeeds; every record has an `EventName`, `EventCode` or fixed/raw equivalent, and `BriefDescription`; `EventName` values are unique; all offcore records with request/response filters carry the expected `MSRIndex` and `MSRValue`; `perf list` on a KNL-capable table shows these aliases; and raw `perf stat -e` smoke tests can open representative events from L2, memory-uop, and offcore families without parser errors.
