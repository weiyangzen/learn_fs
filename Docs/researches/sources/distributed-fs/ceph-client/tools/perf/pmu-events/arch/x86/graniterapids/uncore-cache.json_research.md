# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-cache.json

## Purpose

`uncore-cache.json` is the Granite Rapids uncore cache and home-agent PMU topic file. It contains 368 event-definition objects for CHA and CHACMS units, covering CHA clockticks, distress signals, directory lookup/update behavior, LLC lookup and victim filters, remote snoop filter behavior, request classes, ring/source throttling, TOR inserts, and TOR occupancy. These aliases let perf users observe package-level cache/coherency traffic that is outside the core pipeline counters.

The file is declarative PMU metadata, not executable code. It is compiled by perf's event generator into uncore PMU alias tables.

## Important APIs, Types, And Event Fields

The records use the same perf PMU JSON schema as core events but add uncore-specific binding fields:

- `EventName`: aliases are primarily under `UNC_CHA_*` and `UNC_CHACMS_*`. Major families include `UNC_CHA_LLC_LOOKUP` with 27 records, `UNC_CHA_LLC_VICTIMS` with 15, `UNC_CHA_REMOTE_SF` with 12, `UNC_CHA_REQUESTS` with 9, `UNC_CHA_TOR_INSERTS` with 142, and `UNC_CHA_TOR_OCCUPANCY` with 137.
- `Unit`: maps events to uncore PMUs. Most records use `CHA`; three records use `CHACMS`.
- `PerPkg`: every observed record sets package-level scope with `"1"`, meaning these aliases are modeled as package uncore counters rather than per-thread core counters.
- `Counter`: CHA and CHACMS clock/distress/simple events generally allow counters `0,1,2,3`; TOR occupancy events use counter `0` only, which is a key scheduling constraint.
- `EventCode` and `UMask`: raw uncore event selectors and filters. `UNC_CHA_TOR_INSERTS.*` concentrates on event code `0x35`, while `UNC_CHA_TOR_OCCUPANCY.*` concentrates on `0x36`; LLC lookup uses `0x34`; LLC victims use `0x37`; requests use `0x50`; remote snoop filter uses `0x69`.
- `PortMask`: present on CHACMS records as `0x000`, exposed by `jevents.py` as `ch_mask=`.
- `Experimental`: many uncore filters are marked experimental, notably directory, LLC lookup/victim, remote SF, aggregate TOR, and several PMM/local/remote variants. This is part of the event metadata consumers may display or filter.
- `BriefDescription` and `PublicDescription`: semantic descriptions of filters such as local vs remote homing, IA vs IO source, hit vs miss, DDR vs PMM vs CXL accelerator target, and request opcode class.

The high-cardinality event families encode a matrix of filters in the alias name and `UMask`: source (`IA`, `IO`, `CXL`, remote snoops), request type (`CRD`, `DRD`, `RFO`, `ITOM`, `WCIL`, `WCILF`, `WIL`, `PCIRDCUR`, `CLFLUSH`), hit/miss state, homing (`LOCAL`, `REMOTE`), and target (`DDR`, `PMM`, `CXL_ACC`).

## Control Flow

During the perf build, `pmu-events/Build` includes this JSON under the x86 architecture input set and invokes `jevents.py`. `jevents.py` parses each record, converts `Unit` values to Linux uncore PMU names, maps `PortMask` to channel-mask configuration, lowers event names, and emits generated uncore `pmu_event` table data. The Granite Rapids x86 mapfile entry selects the `graniterapids` directory for `GenuineIntel-6-A[DE]`.

At runtime, perf enumerates matching uncore PMUs and resolves aliases against the generated table. Users can select package uncore events such as CHA clockticks, LLC lookups, TOR inserts, or TOR occupancy without hand-writing raw uncore event codes and masks. For occupancy events restricted to counter `0`, perf's scheduler must honor the counter field when building event groups.

## State And Persistence Behavior

This file has no mutable state or persistence logic. It persists as source metadata and is transformed into generated C tables. Runtime state lives in hardware uncore counters and in perf's event session, not in the JSON. Because uncore counters are package scoped, the counts reflect package/CHA activity rather than task-local state; interpreting results requires awareness of system-wide traffic and PMU instance aggregation.

## Dependencies And Integration Points

The file depends on Granite Rapids uncore PMU definitions, perf's JSON schema, `jevents.py` field mapping, and the kernel/perf runtime support for CHA and CHACMS PMU units. It integrates with CXL and memory-analysis topic files through shared traffic categories: this file contains CXL-hit/miss TOR filters and CXL accelerator target variants, while `uncore-cxl.json` defines dedicated B2CXL/CXLCM/CXLDP counters.

It also integrates with top-down and core analysis indirectly. Core pipeline stall or memory-bound signals from `pipeline.json` can be correlated with package-level LLC lookups, TOR occupancy, and remote/local coherency traffic from this file.

## Risks And Edge Cases

The largest risk is the dense filter matrix. Many records differ only by a few bits in a long `UMask` or by a short name segment such as `LOCAL`, `REMOTE`, `DDR`, `PMM`, `HIT`, or `MISS`; copy/paste or spec transcription errors could create aliases that look correct but count a neighboring condition. `UNC_CHA_LLC_LOOKUP.*` descriptions note non-standard filtering semantics and require selecting state bits; an incorrect mask can count nothing or count multiple cache lookups per request.

`UNC_CHA_TOR_OCCUPANCY.*` events are counter-0-only. If tooling ignores `Counter`, users may see scheduling failures or incorrect multiplexing. `Experimental` records should be treated cautiously in documentation and tests because they may represent less stable hardware semantics. Package-scoped uncore events are also sensitive to multi-socket and PMU-instance aggregation; users can misread them as per-core or per-process metrics.

The CXL-related TOR events create an integration edge with dedicated CXL uncore PMUs. Names such as `*_CXL_ACC` in this file are CHA observations of traffic targeting CXL accelerators, not the same PMU unit as `B2CXL`, `CXLCM`, or `CXLDP` in `uncore-cxl.json`.

## Test Signals

Validation should start with `jq` JSON parsing and successful `jevents.py` generation. Generated C output should contain CHA and CHACMS PMU names and aliases for all 368 records. Runtime checks on Granite Rapids should verify `perf list` shows representative aliases from `UNC_CHA_LLC_LOOKUP`, `UNC_CHA_TOR_INSERTS`, `UNC_CHA_TOR_OCCUPANCY`, and `UNC_CHACMS_*`; scheduling tests should include both ordinary CHA counter events and a counter-0-only occupancy event. Regression checks should diff generated encodings for high-cardinality families, because semantic errors are most likely to appear as small `UMask` changes.
