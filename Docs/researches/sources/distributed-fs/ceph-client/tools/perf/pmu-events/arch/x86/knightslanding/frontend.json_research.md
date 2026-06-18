# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/frontend.json

## Purpose

`frontend.json` defines Knights Landing perf aliases for front-end branch resteers, instruction-cache activity, and micro-sequencer decode entry. It contains seven core event records focused on instruction fetch and front-end redirection behavior.

The file supports analysis of instruction-cache hit/miss behavior, branch handling overhead before retirement, and flows decoded from MSROM.

## Important APIs, Types, and Schema

The event records are:

- `BACLEARS.ALL`, `BACLEARS.COND`, and `BACLEARS.RETURN`, all using `EventCode: "0xE6"` with different umasks for front-end resteers caused by branch handling.
- `ICACHE.ACCESSES`, `ICACHE.HIT`, and `ICACHE.MISSES`, all using `EventCode: "0x80"` with umasks for all fetches, cache hits, and misses that produce memory requests.
- `MS_DECODED.MS_ENTRY`, using `EventCode: "0xE7"` and `UMask: "0x1"` for micro-sequencer flow starts.

Every row uses `Counter: "0,1"` and has a `SampleAfterValue` default. This file uses only the compact schema fields `BriefDescription`, `Counter`, `EventCode`, `EventName`, `SampleAfterValue`, and `UMask`; there are no PEBS, data address, or offcore MSR fields.

## Control Flow and Data Flow

Perf reads this JSON into the KNL event alias table. At runtime, a named front-end event configures a generic core PMU counter with its event code and umask. Counts can then be compared against cycles, instructions, branch-retired, and branch-mispredicted events from `pipeline.json`.

The intended analysis flow is usually ratio-based: icache misses versus accesses, BACLEARS categories versus retired branches, or micro-sequencer entries versus total retired uops. The file itself only provides raw event selectors.

## State and Persistence Behavior

The file is immutable source metadata with no runtime state. It persists KNL-specific front-end selector values. Any runtime PMU state is created by perf when opening events and is discarded when the perf session ends.

## Dependencies and Integration Points

The file integrates with the KNL core PMU and the sibling `counter.json` capacity declaration. It also complements `pipeline.json`: `BACLEARS` are pre-retirement/front-end signals, while `BR_INST_RETIRED` and `BR_MISP_RETIRED` in `pipeline.json` provide retired branch denominators.

Instruction-cache events are front-end fetch metrics rather than offcore memory-source breakdowns. For miss-source investigation, users would combine them with offcore events from `cache.json` and `memory.json`.

## Risks and Edge Cases

`ICACHE.MISSES` counts an instruction fetch miss once, not once per outstanding cycle, so it should not be used as a direct stall-cycle metric. `BACLEARS` describe front-end resteers, not necessarily retired mispredictions, and may not line up one-for-one with branch-retired events.

All rows are constrained to only two programmable counters, so event groups that request many KNL core events can fail scheduling. The file also lacks `PublicDescription`, so user-facing interpretation depends heavily on the short `BriefDescription` text.

## Test Signals

Tests should parse the JSON array, confirm the seven expected `EventName` values, verify unique names and valid hex umasks, and confirm all rows are constrained to `0,1`. Integration smoke tests should check that `perf list` shows the `BACLEARS`, `ICACHE`, and `MS_DECODED` aliases and that representative events can be opened on KNL-compatible PMU tables.
