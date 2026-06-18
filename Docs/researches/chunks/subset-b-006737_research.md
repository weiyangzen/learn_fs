# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-io.json lines 5318-10586

## Scope

This chunk covers lines 5318-10586 of `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-io.json`, a Linux `perf` PMU event JSON table for Intel Snow Ridge uncore I/O. The range is not standalone JSON: line 5318 starts inside the tail of a prior `UNC_M2P_AG0_AD_CRD_ACQUIRED1.TGR9` object, and line 10586 cuts into the `UNC_M2P_VERT_RING_BL_IN_USE.UP_EVEN` object that continues after the chunk. The final per-file reconciliation must merge this with adjacent chunks before doing full JSON validation.

The visible range contributes 488 complete `EventName` records, all for `Unit: "M2PCIe"`. Almost all are package-scoped and experimental: the span contains 488 visible `M2PCIe` unit entries, 486 explicit `Experimental: "1"` markers, and 489 visible `PerPkg: "1"` lines because the opening partial object contributes metadata without its `EventName` in this chunk.

## Purpose

This file is declarative hardware event metadata, not executable code. Each JSON object maps a public perf event name such as `UNC_M2P_RxR_OCCUPANCY.AD_ALL` or `UNC_M2P_TxR_VERT_STARVED0.AD_AG0` to the selector fields and descriptive metadata needed for Snow Ridge M2PCIe uncore PMU programming and listing.

The chunk focuses on the `UNC_M2P_*` M2PCIe fabric bridge between mesh/CMS and PCIe/IIO paths. It describes counters for CMS ingress/egress buffers, M2PCIe-to-IIO credits, local and remote peer-to-peer credit flow, horizontal and vertical ring usage, and starvation or backpressure conditions. These events support diagnosis of uncore I/O congestion: credit exhaustion, queue occupancy, bypasses, NACKs, ring utilization, and stalls waiting for transgress credits.

## Event Families

The first major section is CMS agent credit accounting. It defines agent 0 and agent 1 AD/BL credit acquired and occupancy families, split across `*0.TGR0` through `*0.TGR7` and `*1.TGR8` through `*1.TGR10` records. The selector pattern is consistent: paired event codes distinguish the lower and upper transgress-number groups, while `UMask` values select individual transgress lanes. These families include `UNC_M2P_AG0_AD_CRD_OCCUPANCY*`, `UNC_M2P_AG0_BL_CRD_ACQUIRED*`, `UNC_M2P_AG0_BL_CRD_OCCUPANCY*`, and the corresponding `AG1` versions.

The middle of the chunk covers M2PCIe/IIO and peer-to-peer credit movement. `UNC_M2P_IIO_CREDITS_USED`, `UNC_M2P_IIO_CREDITS_ACQUIRED`, and `UNC_M2P_IIO_CREDITS_REJECT` use message classes such as `DRS`, `NCB`, and `NCS` and CMS port suffixes to show when BL-ring traffic can or cannot acquire credits into the IIO agent. Local and remote P2P families then track dedicated/shared credit taken, returned, received, occupancy, and wait states across M2IOSF instances and agents.

The `RxC` and `TxC` sections describe CMS-to-ring or ring-to-CMS channel behavior. They include cycles full, cycles not empty, inserts, and occupancy for AD, AK, BL, and IV traffic classes. These are queue-state counters rather than packet payload counters, so they are useful as pressure and utilization signals.

The `RxR` section tracks transgress ingress behavior. `UNC_M2P_RxR_OCCUPANCY`, `UNC_M2P_RxR_INSERTS`, and `UNC_M2P_RxR_BYPASS` count ingress buffer state, allocations, and bypasses by credited/uncredited AD and BL traffic plus AK, AKC, and IV classes. `UNC_M2P_RxR_CRD_STARVED`, `UNC_M2P_RxR_BUSY_STARVED`, and the aggregate `UNC_M2P_RxR_CRD_STARVED_1` represent starvation caused by lack of egress credit or other queue priority.

The `STALL0` and `STALL1` families record egress-buffer stall cycles waiting for transgress credits. They are split by AD/BL, agent 0/1, and transgress number. `STALL0` covers TGR0-TGR7 and `STALL1` covers TGR8-TGR10. These are high-signal events for diagnosing a specific transgress endpoint causing head-of-line blocking.

The largest visible group is `TxR` egress behavior. Horizontal egress events include bypass, full/not-empty cycles, inserts, NACKs, occupancy, ADS used, and starvation. Vertical egress mirrors much of that surface through `UNC_M2P_TxR_VERT_*` families. The chunk ends in ring-in-use events for horizontal and vertical AD/AK/AKC/BL/IV/TGC rings, where `UMask` distinguishes directions or side/parity such as `UP_EVEN`, `DN_ODD`, `LEFT_EVEN`, and `RIGHT_ODD`.

Smaller families include `UNC_M2P_CLOCKTICKS`, CMS state/distress assertions, ring bounces/starvation, and miscellaneous egress/ingress classification events. They provide context counters that can be correlated with the more granular credit and queue events.

## Important APIs, Types, And Data Contract

There are no functions or classes in this JSON file itself, but the fields are consumed as a structured API by perf's pmu-events tooling:

- `EventName` is the public symbolic name shown by `perf list` and accepted by perf event parsing. The generator lowercases it in `JsonEvent.name`.
- `EventCode` becomes the base `event=...` selector in generated event strings.
- `UMask` becomes `umask=...` when present and non-zero. Many families share one `EventCode` and rely entirely on `UMask` to select the subcondition.
- `Counter` constrains which hardware counter slots can program the event; most visible M2PCIe records use `0,1,2,3`.
- `Unit: "M2PCIe"` is converted by `jevents.py` into PMU name `uncore_m2pcie`, because unknown unit strings are mapped to `uncore_` plus the lowercased unit.
- `PerPkg: "1"` becomes the `pmu_event.perpkg` boolean and later `perf_pmu_alias.per_pkg`, indicating package-level aggregation semantics.
- `BriefDescription` maps to the short description; `PublicDescription` maps to the long description when it is not identical.
- `Experimental: "1"` is present on most records in this chunk. In the generator, this field primarily affects metric dependency analysis; event objects still compile into the PMU event table.

The generated C-side public type is `struct pmu_event` in `tools/perf/pmu-events/pmu-events.h`, with fields for `name`, `event`, `desc`, `topic`, `long_desc`, `pmu`, `unit`, `perpkg`, and `deprecated`. Runtime alias creation in `tools/perf/util/pmu.c` copies these values into `struct perf_pmu_alias` through `pmu_add_cpu_aliases_table()` and `perf_pmu__new_alias()`.

## Control Flow And Integration

Build-time control flow starts in `tools/perf/pmu-events/jevents.py`. The script loads the full JSON array with `json.load(..., object_hook=JsonEvent)`, converts each object into a `JsonEvent`, builds canonical event selector strings, folds duplicated strings into a shared big C string, and emits generated `pmu-events.c` tables. `EventCode` and `UMask` from this chunk become event terms such as `event=0xe0,umask=0x11`; `Unit: "M2PCIe"` groups these records under the `uncore_m2pcie` PMU table.

Model integration is through `tools/perf/pmu-events/arch/x86/mapfile.csv`, which maps `GenuineIntel-6-86` to `snowridgex`. At runtime, perf uses CPU identification and PMU names to find the Snow Ridge table, then filters events by PMU wildcard matching. When an `uncore_m2pcie` PMU is present, `pmu_add_cpu_aliases_table()` iterates matching generated events and creates aliases so users can request these `UNC_M2P_*` names.

User-visible control flow is simple: `perf list` enumerates these records with descriptions and package-scope metadata; `perf stat -e <event>` resolves a name to its generated selector string; the PMU layer programs the relevant uncore M2PCIe event code and mask into an available counter slot. The JSON does not implement sampling or counting logic; it supplies the selector vocabulary for hardware that does.

## State And Persistence Behavior

The chunk is static persisted metadata in source control. It has no mutable runtime state and does not maintain counters directly. State appears only when perf programs the corresponding hardware counters and reads their values from the uncore PMU.

Package scope is persisted inline with `PerPkg: "1"` and should affect aggregation and display. Credit occupancy, queue fullness, and starvation events are semantically stateful hardware observations, but the JSON only names and encodes them. The distinction matters for interpretation: events like `*_OCCUPANCY` and `*_CYCLES_NE` generally count cycles in a state, while `*_INSERTS`, `*_ACQUIRED`, and `*_RETURNED` generally count occurrences.

The `Experimental` flag is also persisted as data. Downstream reports and tests should treat these M2PCIe names as lower-stability hardware definitions even though they are compiled into perf like other events.

## Dependencies

This chunk depends on the perf PMU event JSON schema and the `jevents.py` converter's field naming conventions. It also depends on Intel Snow Ridge uncore hardware definitions for M2PCIe, CMS agents, transgress IDs, AD/AK/AKC/BL/IV/TGC message classes, M2IOSF ports, NCB/NCS/DRS message classes, and horizontal/vertical ring topology.

The content has implicit dependencies on adjacent chunks. The opening partial record and closing partial record cannot be validated or summarized completely without the previous and next line ranges. The final file-level report should also reconcile this M2PCIe section with earlier `IIO` and `iio_free_running` records in the same `uncore-io.json` file because they describe adjacent parts of the Snow Ridge I/O path.

Runtime dependencies include the presence of an `uncore_m2pcie` PMU exposed by the kernel for Snow Ridge systems. If the PMU is absent, the generated entries can still exist in perf's tables but will not become useful programmable aliases for that host.

## Risks And Edge Cases

- The chunk boundaries split JSON objects. Standalone parsing of this line range should fail; only the full file or reconciled neighboring chunks should be parsed as JSON.
- The range contains repeated mechanical families, so copy/paste drift is a real risk. Visible examples include AG1 BL acquired descriptions for `TGR6` and `TGR7` that repeat "For Transgress 4/5" text while the `EventName` suffixes and masks identify TGR6/TGR7.
- Some descriptions contain stale or generic topology text such as references to "JKT" or missing spaces around sentences. Generated help text will preserve these wording issues.
- `UMask` is the primary differentiator for many records with identical `EventCode`; a wrong mask silently changes the measured condition.
- Several aggregate masks combine credited and uncredited classes, such as `AD_ALL` and `BL_ALL`. Consumers should avoid summing aggregates with their components unless deliberately double-counting.
- Unit conversion is implicit. Since `M2PCIe` is not in the special-case unit table in `jevents.py`, it becomes `uncore_m2pcie` by convention. Renaming the JSON unit would change runtime PMU matching.
- Nearly all records are experimental, so dashboards or tests should prefer representative smoke coverage over strict semantic assertions for every event.

## Test Signals

Useful validation signals for this chunk and the later merged file include:

- Full-file JSON parsing succeeds for `uncore-io.json`; this line range alone is expected to be incomplete.
- The range contributes 488 visible complete `EventName` records, all under `Unit: "M2PCIe"`.
- Generated event strings for representative records include the expected base selector and mask, for example `UNC_M2P_RxR_OCCUPANCY.AD_ALL` as `event=0xe0,umask=0x11` and `UNC_M2P_IIO_CREDITS_REJECT.NCS` as `event=0x34,umask=0x20`.
- `jevents.py` maps `Unit: "M2PCIe"` to PMU name `uncore_m2pcie`, and perf alias creation can list a sample of `UNC_M2P_*` events for that PMU.
- Counter-slot constraints are preserved as `0,1,2,3` for the visible M2PCIe event families.
- Package-scope metadata survives generation so aliases are marked per-package.
- Event-family coverage tests should sample credit acquired/occupancy, IIO credit reject, P2P credit wait, RxR occupancy/inserts/starvation, TxR horizontal/vertical queue state, STALL0/STALL1 transgress stalls, and ring-in-use events.
