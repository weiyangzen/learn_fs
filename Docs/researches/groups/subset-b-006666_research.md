# Research: subset-b-006666

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/other.json

## Purpose

`other.json` is a Granite Rapids x86 perf PMU event topic file for miscellaneous core events that do not fit the larger pipeline/cache/memory topic files. It is a JSON array of seven event-definition objects consumed by perf's `pmu-events` build pipeline. The entries describe hardware assists, hardware interrupts, streaming write occupancy filtering, and request queue full cycles for the Granite Rapids CPU model directory selected by `arch/x86/mapfile.csv`.

The file does not implement executable logic. Its behavioral role is declarative: each object becomes metadata for a perf event alias, including the event select code, unit mask, usable counters, sample period, descriptions, and optional model-specific MSR filters.

## Important APIs, Types, And Event Fields

Perf's `jevents.py` treats each object as a `JsonEvent`-compatible record. The important fields present here are:

- `EventName`: user-facing symbolic alias, such as `ASSISTS.HARDWARE`, `ASSISTS.PAGE_FAULT`, `HW_INTERRUPTS.RECEIVED`, `OCR.STREAMING_WR.ANY_RESPONSE`, and `XQ.FULL_CYCLES`.
- `EventCode` and `UMask`: raw PMU select and unit mask values translated into perf event configuration.
- `Counter`: allowed programmable counter list. Most entries allow counters `0,1,2,3,4,5,6,7`; `OCR.STREAMING_WR.ANY_RESPONSE` and `XQ.FULL_CYCLES` are constrained to `0,1,2,3`.
- `CounterMask`: only used by `XQ.FULL_CYCLES` to count cycles satisfying a minimum threshold.
- `MSRIndex` and `MSRValue`: used by `OCR.STREAMING_WR.ANY_RESPONSE` to program offcore response filtering through MSRs `0x1a6,0x1a7` with value `0x10800`.
- `SampleAfterValue`: default period hints for sampling.
- `BriefDescription` and `PublicDescription`: short and long descriptions surfaced by perf tooling.

The file's event families are compact: two `ASSISTS.*` records share event code `0xc1`, three `HW_INTERRUPTS.*` records share `0xcb`, the offcore response record uses `0x2A,0x2B`, and `XQ.FULL_CYCLES` uses `0x2d`.

## Control Flow

At build time, `tools/perf/pmu-events/Build` includes JSON and CSV files under `pmu-events/arch`, copies them into the output tree if needed, and runs `pmu-events/jevents.py`. `jevents.py` walks the architecture tree, parses JSON records, lowers event names, converts fields such as `CounterMask` to perf encodings such as `cmask=`, converts `MSRIndex` through its MSR lookup path, and emits `pmu-events.c` tables. The generated object is linked into perf.

At runtime, perf matches the local CPU against `arch/x86/mapfile.csv`; Granite Rapids maps `GenuineIntel-6-A[DE]` to the `graniterapids` directory. Perf then exposes these rows as aliases that users can pass to commands such as `perf stat -e assists.hardware` or equivalent normalized names.

## State And Persistence Behavior

This file is persistent static metadata. It has no runtime mutable state, local cache, or side effects by itself. The only persistence it influences is generated build output (`pmu-events.c` and `pmu-events.o`) and perf's runtime alias table compiled from those generated artifacts. Changes to event encodings or names alter the ABI-like alias surface seen by perf users on Granite Rapids systems.

## Dependencies And Integration Points

The direct dependencies are the perf PMU event schema expected by `jevents.py`, Granite Rapids selection in `arch/x86/mapfile.csv`, and Linux perf code that consumes generated `struct pmu_event` tables. The `OCR.STREAMING_WR.ANY_RESPONSE` record also depends on correct offcore response MSR handling: both the comma-separated event code and the comma-separated MSR index must be understood by the generator and runtime PMU programming path.

The file sits beside topic siblings such as `pipeline.json`, `cache.json`, `memory.json`, and uncore event files. Together they form the complete Granite Rapids event table.

## Risks And Edge Cases

The main risks are data-quality risks. Incorrect `EventCode`, `UMask`, `Counter`, `MSRIndex`, or `MSRValue` values would silently expose misleading aliases. The offcore response entry is higher risk because it uses paired event codes and paired MSRs; a parser or schema regression around comma-separated values could break only this style of event. `ASSISTS.HARDWARE` has a broad public description and overlaps conceptually with more specific assist events in other topic files, so users may misinterpret it as an exhaustive architectural assist counter.

Counter constraints are also important: if `Counter` is widened incorrectly for PDIST/offcore-style events, perf may schedule an event on a counter that cannot support the filter. If narrowed incorrectly, perf may reject valid groups or multiplex more than necessary.

## Test Signals

Useful validation signals are: all JSON parses cleanly with `jq`; `jevents.py` generation succeeds for x86; generated `pmu-events.c` contains aliases for all seven `EventName` values; `perf list` on Granite Rapids includes these names; and a Granite Rapids `perf stat` smoke test can schedule representative events from each family, especially `OCR.STREAMING_WR.ANY_RESPONSE` and `XQ.FULL_CYCLES`. Diffing generated encodings before and after edits is a strong regression check because this file is pure declarative input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/pipeline.json

## Purpose

`pipeline.json` is the Granite Rapids core pipeline PMU topic file. It contains 125 event-definition objects covering execution, retirement, branch behavior, speculative recovery, top-down slots, stalls, vector instruction retirement, dispatch ports, uop issue/execution/retirement, and cycle activity. The file gives perf human-readable aliases for raw Intel core PMU encodings on Granite Rapids.

This is not executable source. Its purpose is to be compiled by perf's PMU event generator into alias metadata so users can select events by stable names instead of raw event selectors and masks.

## Important APIs, Types, And Event Fields

Each array element matches the perf PMU JSON event schema used by `jevents.py`'s `JsonEvent` model. Important fields in this file include:

- `EventName`: alias names grouped by prefix. The file has families such as `ARITH`, `ASSISTS`, `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `EXE_ACTIVITY`, `INST_RETIRED`, `INT_MISC`, `INT_VEC_RETIRED`, `LD_BLOCKS`, `LSD`, `MACHINE_CLEARS`, `RESOURCE_STALLS`, `RS`, `TOPDOWN`, `UOPS_DISPATCHED`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`.
- `EventCode` and `UMask`: raw event selector and mask. Many related aliases share an event code and differ by unit mask, for example `BR_INST_RETIRED.*` on `0xc4`, `BR_MISP_RETIRED.*` on `0xc5`, `CYCLE_ACTIVITY.*` on `0xa3`, `EXE_ACTIVITY.*` on `0xa6`, `UOPS_EXECUTED.*` on `0xb1`, and `UOPS_DISPATCHED.*` on `0xb2`.
- `Counter`: programmable counter constraints. Most events allow counters `0,1,2,3,4,5,6,7`, while some cycle activity and dispatch/offcore-style events are limited to subsets such as `0,1,2,3`.
- `CounterMask`, `Invert`, and `EdgeDetect`: event modifiers used for cycle threshold, inverted-cycle, and edge-counting semantics. Examples include `ARITH.DIV_ACTIVE`, `CPU_CLK_UNHALTED.PAUSE_INST`, `CYCLE_ACTIVITY.*`, `INT_MISC.CLEARS_COUNT`, `MACHINE_CLEARS.COUNT`, `RS.EMPTY_COUNT`, and several `UOPS_EXECUTED` and `UOPS_RETIRED` cycle events.
- `MSRIndex` and `MSRValue`: extra MSR filtering for records such as `INT_MISC.UNKNOWN_BRANCH_CYCLES` and `UOPS_RETIRED.MS`, both using MSR `0x3F7` with distinct values.
- `RetirementLatencyMin`, `RetirementLatencyMean`, and `RetirementLatencyMax`: PEBS retirement-latency metadata on branch misprediction cost events such as `BR_MISP_RETIRED.COND_TAKEN_COST`, `BR_MISP_RETIRED.INDIRECT_COST`, and `BR_MISP_RETIRED.RET_COST`.
- `SampleAfterValue`: default sample period. The file uses different defaults for high- and low-frequency events, such as larger values for clock/uop-cycle events and lower values for branch cost or clear events.

There are no `MetricGroup` fields in this file; metrics are defined elsewhere, while this file only defines raw event aliases.

## Control Flow

Build control flow starts in `tools/perf/pmu-events/Build`, which selects JSON and CSV inputs and invokes `pmu-events/jevents.py` unless `NO_JEVENTS=1` is set. `jevents.py` parses each JSON object, normalizes the event name, maps schema keys to perf config terms, and emits generated C tables. Field conversion includes `CounterMask` to `cmask=`, `EdgeDetect` to edge detection, `Invert` to inverted counting, `MSRIndex`/`MSRValue` to model-specific extra register programming, and `Unit` to PMU names when present. Because this file is core-only, its records do not use `Unit`; they bind to the core PMU table selected for Granite Rapids.

Runtime flow is CPU selection followed by alias lookup. `arch/x86/mapfile.csv` maps `GenuineIntel-6-A[DE]` to the `graniterapids` directory, so a Granite Rapids perf build can expose these event aliases through `perf list` and resolve user event names to raw PMU config at `perf stat` or `perf record` time.

## State And Persistence Behavior

The file has no mutable runtime state. It is persistent source metadata that becomes generated C data during the perf build. Any modification persists into the perf binary after regeneration and changes alias availability, descriptions, default sample periods, or raw event programming. Runtime event counts are read from hardware PMU counters; this JSON only determines how perf programs and names those counters.

## Dependencies And Integration Points

Primary dependencies are the Intel Granite Rapids PMU specification, the perf PMU JSON schema, `jevents.py`, `pmu-events/Build`, and the x86 mapfile entry for Granite Rapids. It integrates with top-down analysis through `TOPDOWN.*` slot events and with PEBS cost analysis through `BR_MISP_RETIRED.*_COST` retirement-latency records. It also interacts with perf's event scheduler through `Counter` constraints and with the MSR programming path for MSR-filtered aliases.

The event families are designed to complement sibling topic files. For example, cache miss cycle events in this file are core pipeline stall signals, while uncore cache request and occupancy events live in `uncore-cache.json`; assists specific to miscellaneous traps are split between `pipeline.json` and `other.json`.

## Risks And Edge Cases

The highest risk is incorrect hardware encoding. A wrong `UMask`, `CounterMask`, `Invert`, or `EdgeDetect` can produce plausible but wrong counts. Events that share the same `EventCode` are particularly sensitive because a one-bit mask error changes the semantic within the same family. PEBS branch cost events are also sensitive: their descriptions state that they fire on the instruction immediately following the mispredicted branch and use the PEBS `Retire_Latency` field, so consumers must not treat them as ordinary branch retired events without understanding the cost sampling semantics.

MSR-filtered events are another edge case. `INT_MISC.UNKNOWN_BRANCH_CYCLES` and `UOPS_RETIRED.MS` depend on MSR `0x3F7` programming; if the generator's MSR lookup or runtime support changes, these aliases may fail while ordinary event-code aliases still work. Counter constraints can affect grouping: events limited to counters `0,1,2,3` may fail to schedule in groups that would otherwise appear valid.

Some events intentionally use inverted cycle semantics (`Invert`) or edge counting (`EdgeDetect`). These are easy to regress in schema translation tests because the event name may still appear even when the generated config modifier is wrong.

## Test Signals

Baseline tests are JSON parsing and x86 `jevents.py` generation. Stronger checks include verifying generated aliases and encodings in `pmu-events.c`, running perf's PMU event/metric tests where available, and checking `perf list` on Granite Rapids for representative families: `br_inst_retired.*`, `br_misp_retired.*_cost`, `cycle_activity.*`, `topdown.*`, `uops_dispatched.port_*`, and `uops_retired.*`. Hardware smoke tests should try grouped scheduling of counter-constrained events and a PEBS-capable sampling command for a branch cost event to confirm retirement-latency metadata remains usable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-cache.json -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-cxl.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-cxl.json

## Purpose

`uncore-cxl.json` is the Granite Rapids uncore CXL PMU topic file. It defines three package-scoped events for CXL-related uncore units: B2CXL clockticks, CXLCM receive-side memory data packing buffer inserts, and CXLDP transmit-side M2S data AGF inserts. These records give perf symbolic aliases for low-level CXL fabric/data-path counters.

The file is a small declarative JSON input to perf's PMU event generation. It contains no functions or executable control flow.

## Important APIs, Types, And Event Fields

The three records follow the perf PMU JSON event schema:

- `UNC_B2CXL_CLOCKTICKS`: uses `Unit` `B2CXL`, `EventCode` `0x01`, counters `0,1,2,3`, `PortMask` `0x000`, and `PerPkg` `1`.
- `UNC_CXLCM_RxC_PACK_BUF_INSERTS.MEM_DATA`: uses `Unit` `CXLCM`, `EventCode` `0x41`, `UMask` `0x10`, counters `4,5,6,7`, and `PerPkg` `1`.
- `UNC_CXLDP_TxC_AGF_INSERTS.M2S_DATA`: uses `Unit` `CXLDP`, `EventCode` `0x02`, `UMask` `0x20`, counters `0,1,2,3`, and `PerPkg` `1`.

Schema fields of note are `Unit`, which binds each alias to a specific uncore PMU type; `PerPkg`, which marks package-level scope; `Counter`, which differs between the CXLCM record and the other two records; and `PortMask`, which is present only on the B2CXL clocktick event and is translated by `jevents.py` to a channel-mask config term.

## Control Flow

The build path is the standard perf PMU event path. `pmu-events/Build` collects JSON inputs under `pmu-events/arch/x86`, then `jevents.py` parses this file, converts `Unit` names to Linux PMU identifiers, maps fields such as `PortMask`, `EventCode`, and `UMask` into generated event strings, and emits C table entries. The Granite Rapids mapfile row selects this directory for CPU IDs matching `GenuineIntel-6-A[DE]`.

At runtime, perf resolves these generated aliases against available uncore PMU instances. Users can request the aliases by name instead of configuring B2CXL, CXLCM, or CXLDP event selectors manually.

## State And Persistence Behavior

The JSON is static source metadata. It does not store runtime samples or maintain mutable state. Once generated into perf, it persists as alias definitions in the binary. Runtime behavior depends on the kernel exposing the relevant uncore CXL PMU devices and on the package topology present on the system.

## Dependencies And Integration Points

This file depends on Granite Rapids CXL uncore PMU support and perf's event-generation schema. It integrates with `uncore-cache.json` because CHA TOR records include CXL-hit/miss and `CXL_ACC` traffic views, while this file provides counters from dedicated CXL units. It also integrates with any memory/CXL performance workflows that correlate CXL data path activity with core stalls, LLC/TOR traffic, or memory-controller activity from sibling topic files.

## Risks And Edge Cases

The small number of records makes schema drift easy to spot, but each event is unit-specific. A wrong `Unit` value would bind an alias to the wrong PMU or make it disappear. The `Counter` split is important: `UNC_CXLCM_RxC_PACK_BUF_INSERTS.MEM_DATA` is restricted to counters `4,5,6,7`, unlike the B2CXL and CXLDP entries. If perf scheduling or documentation assumes all uncore CXL events use counters `0,1,2,3`, this record may fail to schedule in groups.

Another edge case is platform availability. A Granite Rapids CPU may match the event table while a given machine configuration lacks exposed CXL devices or PMU instances. In that case the alias can exist in generated metadata but not be schedulable on a specific host.

## Test Signals

Validation should include JSON parsing, x86 `jevents.py` generation, and checking generated aliases for all three event names. On suitable Granite Rapids hardware, `perf list` should expose B2CXL, CXLCM, and CXLDP aliases when the kernel exposes those PMUs. Runtime smoke tests should schedule `UNC_B2CXL_CLOCKTICKS` and one data-path insert event, with a separate group test for the CXLCM counter range constraint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-cxl.json -->
