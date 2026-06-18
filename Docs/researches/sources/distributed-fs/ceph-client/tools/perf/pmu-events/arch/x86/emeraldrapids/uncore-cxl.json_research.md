# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-cxl.json

## Purpose

This file is a Linux `perf` PMU event table for Emerald Rapids x86 uncore CXL monitoring. It contributes named event aliases for CXL cache/memory and data-path units under `tools/perf/pmu-events/arch/x86/emeraldrapids/`, allowing perf's generated PMU event database to expose symbolic event names instead of requiring users to type raw event codes and unit masks.

The table contains 56 event descriptors. Forty-nine target the `CXLCM` unit and seven target the `CXLDP` unit. The two clocktick events are stable entries without `Experimental`; the remaining 54 entries are marked `"Experimental": "1"`, so consumers and tests should treat their names and descriptions as less stable than established architectural events.

## Data Model And Important Fields

Each array element is a perf PMU event descriptor object. There are no functions or executable APIs in this JSON file; the relevant "interfaces" are the schema keys consumed by perf's PMU event tooling:

- `EventName`: symbolic alias shown to users and referenced by `perf list` / `perf stat` style workflows, such as `UNC_CXLCM_RxC_FLITS.VALID` or `UNC_CXLDP_TxC_AGF_INSERTS.U2C_REQ`.
- `EventCode`: raw hardware event selector, represented as a hex string. The file uses `0x01`, `0x02`, `0x05`, `0x40`, `0x41`, `0x42`, `0x43`, `0x4b`, and `0x52`.
- `UMask`: hardware unit mask selecting the specific sub-event within an event code.
- `Unit`: PMU unit name. This file uses `CXLCM` and `CXLDP`, which must line up with the Emerald Rapids uncore units known to perf and with `counter.json`.
- `Counter`: allowed counter indices. `CXLCM_CLOCKTICKS` can use `0,1,2,3,4,5,6,7`; receive-side `CXLCM` events use `4,5,6,7`; transmit-side `CXLCM` and all `CXLDP` entries use `0,1,2,3`.
- `PerPkg`: set to `"1"` for every event, indicating package-scoped uncore counting.
- `BriefDescription`: human-facing summary used by event listings and documentation.
- `Experimental`: present on all non-clocktick entries to mark events as experimental.

The adjacent Emerald Rapids `counter.json` declares `CXLCM` with eight generic counters and `CXLDP` with four generic counters, so this file's counter availability is consistent with the broader platform metadata.

## Event Families

The `CXLCM` section covers the CXL cache/memory side:

- `UNC_CXLCM_CLOCKTICKS` counts low-frequency clock ticks and is the only `CXLCM` event available on all eight counters.
- `UNC_CXLCM_RxC_AGF_INSERTS.*` uses event code `0x43` to count receive-side allocations into AGF paths for cache request/response/data and memory request/data categories.
- `UNC_CXLCM_RxC_FLITS.*` uses event code `0x4b` to count received flits by header or message class: valid flits, protocol flits, control flits, headerless flits, AK/BE/SZ header markers, and valid messages.
- `UNC_CXLCM_RxC_MISC.*` uses event code `0x40` for receive-side link/protocol conditions such as LLCRD, retry, init flits, and CRC errors.
- `UNC_CXLCM_RxC_PACK_BUF_FULL.*`, `UNC_CXLCM_RxC_PACK_BUF_INSERTS.*`, and `UNC_CXLCM_RxC_PACK_BUF_NE.*` use event codes `0x52`, `0x41`, and `0x42` to report packing buffer pressure, insertions, and not-empty cycles for cache and memory traffic classes.
- `UNC_CXLCM_TxC_FLITS.*` uses event code `0x05` to count transmitted or packed flits by message/header class.
- `UNC_CXLCM_TxC_PACK_BUF_INSERTS.*` uses event code `0x02` to count transmit-side packing buffer allocations for cache and memory request/response/data classes.

The `CXLDP` section covers the CXL data-path side:

- `UNC_CXLDP_CLOCKTICKS` counts unit clock ticks.
- `UNC_CXLDP_TxC_AGF_INSERTS.*` uses event code `0x02` for transmit-side AGF allocation counts across U2C request/response/data and M2S request/data categories.

## Control Flow And Integration

At build time, perf's PMU event generation tooling reads architecture-specific JSON event files under `tools/perf/pmu-events/arch/x86/`. `mapfile.csv` maps Emerald Rapids CPU model `GenuineIntel-6-CF` to the `emeraldrapids` directory, so this file is part of the event set selected for that platform. The generated event tables are then compiled into perf and surfaced through commands such as `perf list`, `perf stat`, and tooling that resolves event aliases into raw PMU encodings.

Runtime control flow is data-driven:

1. perf identifies the current CPU/platform and selects the Emerald Rapids event map.
2. Event aliases from this JSON are available when the corresponding PMU unit is present.
3. A user or higher-level tool requests an event by `EventName`.
4. perf resolves the alias to the `Unit`, `EventCode`, `UMask`, package scope, and allowed counter constraints.
5. The kernel/perf event opening path programs the uncore PMU with the selected encoding if the hardware and counter scheduling allow it.

There is no local branching, mutation, or function call graph in this file. The correctness path depends on schema validity, hardware metadata consistency, and perf's generator/alias resolver consuming every descriptor as intended.

## State And Persistence Behavior

This file is static source data. It does not persist runtime measurements or maintain in-process state. Its persistent behavior is indirect: once compiled or packaged into perf's PMU event database, the event names and raw encodings become part of the user-visible Emerald Rapids profiling interface. Changes to an `EventName`, `EventCode`, `UMask`, `Unit`, or `Counter` field can therefore alter user scripts, dashboards, or benchmark tooling that depend on these aliases.

The `PerPkg` setting means measurements are modeled as package-level uncore counters rather than per-core counters. This matters for aggregation and for interpreting values on multi-socket systems.

## Dependencies And Integration Points

Primary dependencies are perf's PMU JSON schema and the surrounding Emerald Rapids event metadata:

- `arch/x86/mapfile.csv` selects the `emeraldrapids` directory for `GenuineIntel-6-CF`.
- `arch/x86/emeraldrapids/counter.json` declares available generic counters for `CXLCM` and `CXLDP`.
- Other Emerald Rapids files in the same directory provide core, memory, interconnect, I/O, cache, and power events that are combined into the platform event database.
- perf's PMU event generator expects valid JSON arrays of event objects and known schema keys such as `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `BriefDescription`, `PerPkg`, and `Experimental`.

This file also has a conceptual dependency on the Emerald Rapids CXL uncore hardware programming reference. The JSON alone cannot prove that every event code and unit mask is semantically correct; it only declares the mapping perf will use.

## Risks And Edge Cases

- Several descriptions appear mismatched with their event suffixes. For example, some `RxC_AGF_INSERTS` cache and memory suffixes have descriptions that mention different traffic classes, and some `TxC_PACK_BUF_INSERTS` cache request/response suffixes describe the opposite class. These may be harmless wording defects, but they can mislead users reading `perf list`.
- Most events are experimental, so downstream scripts should avoid treating these names as a stable long-term ABI.
- Counter constraints are asymmetric: receive-side `CXLCM` events are limited to counters `4,5,6,7`, while transmit-side `CXLCM` and `CXLDP` events use `0,1,2,3`. If the constraints are wrong, perf may fail to schedule valid groups or may allow invalid counter placement.
- All events are package-scoped. Users comparing values to per-core work must normalize by package/socket topology and sampling interval.
- The table contains raw hardware encodings without derivation or comments. Reviewers need external hardware documentation or cross-platform comparison to validate `EventCode` and `UMask` semantics.
- JSON schema accepts strings for numeric fields; malformed hex strings or duplicate `EventName` values would not be caught by plain text review unless generator tests or validation scripts run.

## Test Signals

Useful validation signals for this file are:

- `python3 -m json.tool sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-cxl.json` succeeds, confirming syntactic JSON validity.
- Event-name uniqueness checks report no duplicate `EventName` values among the 56 descriptors.
- Schema checks confirm every object has `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, `UMask`, and `Unit`, with `Experimental` intentionally absent only from the two clocktick events.
- Cross-file checks confirm `CXLCM` and `CXLDP` are present in Emerald Rapids `counter.json`, and that the referenced counter ranges do not exceed the declared generic counter counts.
- A perf build or PMU event generation test should include this file without generator warnings.
- On Emerald Rapids hardware with CXL PMUs exposed, `perf list` should show the `UNC_CXLCM_*` and `UNC_CXLDP_*` aliases, and simple `perf stat` probes for clockticks and selected flit/packing-buffer events should either count successfully or fail only when the unit is absent.
