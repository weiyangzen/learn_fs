# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/pipeline.json

## Purpose

This file is the Broadwell Xeon PMU event table for core pipeline-related events in Linux `perf`. It is declarative JSON, not executable code: each array entry names a hardware event alias and describes the raw event selector, unit mask, counter constraints, sampling period, precision support, and user-facing help text that `perf list`, `perf stat`, and `perf record` expose after the `pmu-events` generator embeds the table into perf.

The file contains 137 event records. They cover branch execution and retirement, branch misprediction, unhalted cycles, cycle activity and memory-pending stall cycles, instruction retirement, RAT/allocator recovery, load blocking, loop stream detector activity, machine clears, move elimination, resource stalls, reservation-station empty periods, execution/dispatch port utilization, issued uops, and retired uops. The x86 PMU map connects this BroadwellX directory to `GenuineIntel-6-4F` systems through `tools/perf/pmu-events/arch/x86/mapfile.csv`.

## Important Schema Fields

The records use the event half of the perf PMU JSON schema parsed by `tools/perf/pmu-events/jevents.py`.

- `EventName`: public alias, such as `BR_INST_RETIRED.ALL_BRANCHES_PEBS`, `CYCLE_ACTIVITY.STALLS_L2_PENDING`, or `UOPS_EXECUTED_PORT.PORT_0_CORE`. `jevents.py` lowercases names when creating generated aliases.
- `EventCode`: raw architectural or model-specific event select value for programmable counters. Four fixed-counter events omit `EventCode` and are identified by `Counter`.
- `UMask`: unit mask bits that select the subevent. Some architectural aliases, such as `BR_INST_RETIRED.ALL_BRANCHES`, `BR_MISP_RETIRED.ALL_BRANCHES`, `CPU_CLK_UNHALTED.THREAD_P`, and `INST_RETIRED.ANY_P`, intentionally omit `UMask`.
- `Counter`: counter placement constraint. Most events allow programmable counters `0,1,2,3`; exceptions include fixed counters 0, 1, and 2, `INST_RETIRED.PREC_DIST` restricted to counter 1, and L1D cycle-activity events restricted to counter 2.
- `CounterMask`, `Invert`, and `EdgeDetect`: additional raw config attributes emitted by `jevents.py` as `cmask=`, `inv=`, and `edge=`. This file has 32 counter-mask records, 6 inverted records, and 2 edge-detect records.
- `AnyThread`: marks events counted at physical-core scope rather than only the current logical thread. There are 13 records, including clock aliases, allocator recovery, and the `_CORE` execution-port aliases.
- `PEBS`: marks precise events. Thirteen records support PEBS, including precise retired branch/mispredict aliases, `INST_RETIRED.PREC_DIST`, `UOPS_RETIRED.ALL`, and `UOPS_RETIRED.RETIRE_SLOTS`.
- `Errata`: carries processor-specification-update caveats. This file cites `BDW98`, `BDM61`, `BDM11`, and `BDM55`.
- `BriefDescription` and `PublicDescription`: text surfaced by listing APIs and JSON output. Several entries have only brief descriptions, so consumers must tolerate missing long descriptions.
- `SampleAfterValue`: default sample period used for event-based sampling. Values vary by event family, commonly `100003`, `200003`, `400009`, `1000003`, or `2000003`.

## Event Families

The largest families are branch and uop pipeline events. `BR_INST_EXEC.*` and `BR_MISP_EXEC.*` count speculative plus retired branch behavior at execution time, split by conditional, direct jump, direct call, indirect jump, indirect call, return, taken, and not-taken forms. `BR_INST_RETIRED.*` and `BR_MISP_RETIRED.*` provide retired-only branch and misprediction aliases, with several PEBS-capable variants.

Clock and retirement aliases establish denominators for many perf workflows. `CPU_CLK_UNHALTED.*` includes fixed-counter thread/reference-cycle aliases and programmable equivalents with thread and any-thread variants. `INST_RETIRED.*` includes fixed `INST_RETIRED.ANY`, programmable `ANY_P`, precise distribution, and x87 retirement.

Backend and memory-stall records include `CYCLE_ACTIVITY.*`, `LD_BLOCKS.*`, `LD_BLOCKS_PARTIAL.ADDRESS_ALIAS`, `RESOURCE_STALLS.*`, `RS_EVENTS.*`, and `MACHINE_CLEARS.*`. The cycle-activity records combine event `0xA3`, unit masks, and counter masks to distinguish cycles or stalls while L1D, L2, or broader memory demand-load conditions are pending.

Uop throughput records include `UOPS_DISPATCHED_PORT.PORT_0` through `PORT_7`, `UOPS_EXECUTED.*`, `UOPS_EXECUTED_PORT.*`, `UOPS_ISSUED.*`, and `UOPS_RETIRED.*`. These are used to reason about port pressure, execution width, issue stalls, retirement slots, and cycles with no executed or retired uops. The `_CORE` port aliases set `AnyThread=1`; the non-core port aliases are per-thread.

## Control Flow

The JSON file itself has no runtime control flow. The relevant flow is data ingestion and lookup.

At build time, `tools/perf/pmu-events/Build` includes all JSON and CSV files under `pmu-events/arch`. It runs `pmu-events/jevents.py`, which traverses architecture directories, reads each JSON file, converts records into `JsonEvent` objects, canonicalizes numeric fields, maps schema keys such as `AnyThread`, `CounterMask`, `EdgeDetect`, `Invert`, and `UMask` into perf event encoding strings, and emits generated `pmu-events.c`. `print_mapping_table()` then binds generated event tables to CPU IDs from `arch/x86/mapfile.csv`; BroadwellX is selected for `GenuineIntel-6-4F`.

At runtime, perf identifies the running CPU, selects the generated BroadwellX event table, and resolves a user alias such as `uops_retired.retire_slots` or `br_misp_retired.all_branches_pebs` to the encoded PMU event string. Listing paths, including JSON output in `builtin-list.c`, expose the generated `EventName`, descriptions, PMU unit, topic, and encoding. Counting and sampling commands then rely on kernel perf_event scheduling to program the requested raw event, unit mask, fixed counter, PEBS mode, and counter modifiers.

## State and Persistence

This file is persistent source data. It does not maintain runtime state, mutate counters, or write files on its own. Its stateful effect is indirect: when perf is built, the event definitions are embedded into generated `pmu-events.c` and compiled into the perf binary or library. Runtime counts are ephemeral hardware counter readings, while the aliases, descriptions, sample periods, and constraints remain stable until this JSON source changes and perf is rebuilt.

Because event names are public aliases, changes to `EventName`, encodings, PEBS flags, counter constraints, or descriptions are user-visible API changes. Scripts can depend on these aliases through `perf stat -e`, `perf record -e`, `perf list`, perf JSON output, or Python bindings that expose PMU event metadata.

## Dependencies and Integration Points

Primary integration points are:

- `tools/perf/pmu-events/jevents.py`, which parses this JSON, constructs event encodings, stores descriptions, appends errata notes, and emits compact generated C tables.
- `tools/perf/pmu-events/Build` and `tools/perf/Makefile.perf`, which decide when PMU JSON needs regeneration and compilation.
- `tools/perf/pmu-events/arch/x86/mapfile.csv`, which maps BroadwellX CPUID pattern `GenuineIntel-6-4F` to this directory.
- `tools/perf/pmu-events/pmu-events.h`, which defines the generated event and metric table interfaces consumed by perf.
- `tools/perf/builtin-list.c`, which prints generated event metadata, including JSON fields like `EventName`, `BriefDescription`, `PublicDescription`, and encoding.
- Neighboring BroadwellX JSON files, especially `frontend.json`, `memory.json`, `cache.json`, `floating-point.json`, `virtual-memory.json`, and `bdx-metrics.json`, which together provide a full event/metric vocabulary for the same CPU model.
- Kernel perf_event x86 PMU support, fixed counters, PEBS support, last-branch-record support for `ROB_MISC_EVENTS.LBR_INSERTS`, and any-thread/event-constraint handling.

## Risks and Edge Cases

Several aliases share the same event code and differ only by unit mask, counter mask, inversion, or any-thread semantics. A small encoding mistake can silently turn a high-level alias into a different hardware measurement. This is especially important for `CYCLE_ACTIVITY.*`, `UOPS_EXECUTED.*`, `UOPS_RETIRED.*`, and branch subevents.

Counter constraints are part of correctness. `CYCLE_ACTIVITY.CYCLES_L1D_MISS` and `STALLS_L1D_MISS` require counter 2, `INST_RETIRED.PREC_DIST` requires counter 1, and fixed-counter aliases must not be treated as programmable events. Grouped perf commands can fail or multiplex if these constraints collide with other events.

PEBS and errata fields need preservation. Precise aliases such as `BR_INST_RETIRED.ALL_BRANCHES_PEBS`, `BR_MISP_RETIRED.ALL_BRANCHES_PEBS`, `INST_RETIRED.PREC_DIST`, and `UOPS_RETIRED.*` have different sampling semantics from non-precise aliases. Errata notes warn that values may be affected by known Broadwell issues.

Any-thread aliases can surprise users on SMT systems because they count physical-core activity rather than only one logical CPU thread. The `_CORE` execution-port aliases and several clock aliases should not be compared directly to per-thread aliases without accounting for this scope.

Documentation quality varies. Some entries lack `PublicDescription`, have duplicate concepts under legacy and newer names, or expose terse names such as `THREAD_P`. Test expectations should check encodings and availability, not only prose text.

## Test Signals

Useful validation signals for this file are:

- JSON syntax: `jq empty sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/pipeline.json`.
- Record count: `jq 'length' .../pipeline.json` should report 137 records.
- Schema coverage: all records should have `EventName`, `BriefDescription`, `Counter`, and `SampleAfterValue`; programmable events should have valid numeric `EventCode` unless they are fixed-counter aliases.
- Generator smoke test: running the perf `pmu-events` build or invoking `jevents.py` for x86 should parse this file and regenerate `pmu-events.c` without exceptions.
- Mapping check: `arch/x86/mapfile.csv` should continue mapping `GenuineIntel-6-4F` to `broadwellx`, so these aliases are selected on Broadwell Xeon.
- Listing check on a generated perf: `perf list --json` or `perf list pipeline` should expose representative aliases such as `br_inst_retired.all_branches`, `cycle_activity.stalls_l2_pending`, and `uops_retired.retire_slots` with expected descriptions and encodings.
- Encoding spot checks: branch aliases should preserve event `0x88`, `0x89`, `0xC4`, and `0xC5` unit-mask splits; port aliases should preserve event `0xA1` with masks `0x1` through `0x80`; inverted stall aliases should retain `inv=1` and their `cmask` values.
- Runtime smoke tests on BroadwellX hardware: `perf stat -e cycles,instructions,br_inst_retired.all_branches,uops_retired.retire_slots -- sleep 1` should resolve aliases and count without unsupported-event errors.
- PEBS smoke test on suitable hardware and permissions: precise aliases such as `inst_retired.prec_dist` or `br_misp_retired.all_branches_pebs` should be accepted for sampling where PEBS is available.
