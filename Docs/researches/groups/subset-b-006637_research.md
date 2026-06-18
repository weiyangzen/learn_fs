# subset-b-006637 research

Grouped research report for BroadwellX perf PMU event JSON files. Each section is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-io.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-io.json

## Purpose

This file is a declarative Linux `perf` PMU event catalog for BroadwellX R2PCIe uncore I/O fabric events. It contains 62 JSON event records, all with `Unit: "R2PCIe"` and `PerPkg: "1"`. The records expose package-level aliases for R2PCIe clock ticks, IIO credit use, ring use, ring bounces, RxR and TxR queue pressure, SBO credit acquisition/occupancy, credit stalls, and clockwise TxR NACK causes.

The file is not executable code. Its source-level role is to feed `tools/perf/pmu-events/jevents.py`, which converts each JSON object into generated `pmu-events.c` metadata. `jevents.py` maps the `R2PCIe` unit through its generic `unit_to_pmu()` fallback to the runtime PMU name `uncore_r2pcie`, so the aliases are matched to Linux uncore R2PCIe PMU instances.

## Schema And Public API

Each JSON object is a public perf event alias. The important fields are `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and usually `PublicDescription`. `EventName` is lowercased by `jevents.py` for alias lookup; `EventCode` becomes `event=<hex>`; non-zero `UMask` becomes `umask=<hex>`; `Unit` selects the PMU; `PerPkg` records package aggregation semantics; descriptions are surfaced through `perf list`, JSON list output, and perf Python helpers.

The event families are:

- `UNC_R2_CLOCKTICKS`: R2PCIe uclk-domain cycles on counters 0-3.
- `UNC_R2_IIO_CREDIT.*`, `UNC_R2_IIO_CREDITS_ACQUIRED.*`, and `UNC_R2_IIO_CREDITS_USED.*`: QPI/IIO credit availability, acquisitions, and cycles with DRS, NCB, or NCS credits in use.
- `UNC_R2_RING_AD_USED.*`, `UNC_R2_RING_AK_USED.*`, `UNC_R2_RING_BL_USED.*`, and `UNC_R2_RING_IV_USED.*`: ring use split by all, clockwise, counterclockwise, even, and odd polarity where applicable.
- `UNC_R2_RING_AK_BOUNCES.*`: AK ingress bounce direction.
- `UNC_R2_RxR_*`, `UNC_R2_TxR_*`: receive/transmit ring queue cycles, inserts, occupancy, fullness, and NACKs by channel or direction.
- `UNC_R2_SBO0_*` and `UNC_R2_STALL_NO_SBO_CREDIT.*`: SBO0 AD/BL credit acquisition, occupancy, and stalls caused by missing SBO0/SBO1 credits.

## Control Flow And Integration

Build-time control flow is data-driven. The perf PMU build traverses `tools/perf/pmu-events/arch`, and `jevents.py` loads this file with `json.load(..., object_hook=JsonEvent)`. For each object, `JsonEvent.__init__` captures the name, descriptions, PMU unit, package flag, and encoding terms. The generated event string is built from `EventCode` plus supported fields such as `UMask`; this file does not use `Filter`, `ScaleUnit`, `Errata`, or metric expression fields.

At runtime, perf selects the BroadwellX table through the x86 mapfile entry for family/model `GenuineIntel-6-4F`. PMU matching code can ignore uncore instance suffixes and wildcard PMU names, allowing one generated `uncore_r2pcie` table to attach to the concrete R2PCIe PMU devices exposed under sysfs. User commands such as `perf list`, `perf stat -e unc_r2_ring_ad_used.all`, and JSON listing paths consume these aliases.

## State And Persistence

The JSON has no mutable runtime state and performs no I/O by itself. Its persistent effect is the generated perf event table compiled into the perf binary. Edits to event names, selectors, unit masks, counter constraints, units, or descriptions change the public alias API and the raw hardware event programming emitted by perf.

All records are package scoped through `PerPkg: "1"`, so they describe socket/package uncore activity rather than per-thread core activity. Counter availability is declarative: most ring-use events allow counters 0-3, while credit and queue families often use only counters 0-1 or a narrower subset. Actual scheduling and conflicts are enforced by perf and the kernel PMU format.

## Dependencies

The file depends on the PMU JSON schema accepted by `jevents.py`, the x86 BroadwellX mapfile selection, and kernel/sysfs support for Intel BroadwellX R2PCIe uncore PMUs. Hardware interpretation depends on BroadwellX ring topology, R2PCIe uclk timing, IIO message classes, QPI links, NCB/NCS/DRS credit behavior, SBO credit paths, and TxR/RxR queue semantics.

## Risks

The highest-risk fields are `Unit`, `EventCode`, `UMask`, and `Counter`. A `Unit` typo changes PMU routing or hides events. A wrong mask can silently count a different ring direction, queue class, or credit type. Counter restrictions matter because uncore PMUs have limited counters and some events only list counters 0-1.

Several aliases are intentionally derived from the same event code with different masks. Duplicate event codes are normal; duplicate `EventName` values would be a regression. The descriptions carry important semantic context, especially for R2PCIe clock divergence, IIO credit classes, ring stop accounting, and NACK direction. Removing or truncating them would not break generation but would degrade the public analysis API.

## Test Signals

Useful checks are `jq empty` for syntax, `jq 'length'` returning 62, and a key-set check limited to `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, `PublicDescription`, `UMask`, and `Unit`. Generator tests should ensure `jevents.py` emits `uncore_r2pcie` entries without duplicate aliases. Runtime smoke tests on BroadwellX hardware should verify representative aliases such as `UNC_R2_CLOCKTICKS`, `UNC_R2_IIO_CREDITS_USED.NCB`, `UNC_R2_RING_AD_USED.ALL`, `UNC_R2_STALL_NO_SBO_CREDIT.SBO0_AD`, and `UNC_R2_TxR_NACK_CW.UP_BL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-io.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-memory.json

## Purpose

This file is the BroadwellX integrated memory controller PMU event catalog for Linux `perf`. It contains 326 event records, all routed to `Unit: "iMC"` and marked `PerPkg: "1"`. `jevents.py` maps `iMC` to generated PMU name `uncore_imc`, making these aliases available for BroadwellX memory-controller PMU instances.

The table describes DRAM command traffic, CAS reads and writes, activates, precharges, refreshes, ECC corrections, major-mode residency, queue occupancy/inserts, memory-controller power states, throttling, partial-write underfills, VMSE write push behavior, and detailed read/write CAS breakdowns by rank, bank, and bank group. The first two aliases, `LLC_MISSES.MEM_READ` and `LLC_MISSES.MEM_WRITE`, are derived convenience aliases over memory-controller CAS events with `ScaleUnit: "64Bytes"`.

## Schema And Public API

Each object is a perf alias record. The common fields are `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and `PublicDescription`. The file also uses `ScaleUnit` for the two LLC miss memory-traffic aliases and `Deprecated: "1"` for `UNC_M_DCLOCKTICKS`.

Important event families include:

- `LLC_MISSES.MEM_READ` and `LLC_MISSES.MEM_WRITE`: scaled 64-byte traffic aliases derived from `UNC_M_CAS_COUNT.RD` and `.WR`.
- `UNC_M_ACT_COUNT.*`, `UNC_M_PRE_COUNT.*`, `UNC_M_BYP_CMDS.*`, `UNC_M_DRAM_PRE_ALL`, and `UNC_M_DRAM_REFRESH.*`: DRAM activate, precharge, bypass, precharge-all, and refresh commands.
- `UNC_M_CAS_COUNT.*`: read and write CAS totals, regular reads, underfills, and read/write major-mode splits.
- `UNC_M_CLOCKTICKS`, `UNC_M_CLOCKTICKS_P`, and deprecated `UNC_M_DCLOCKTICKS`: fixed and programmable clock aliases. `UNC_M_CLOCKTICKS_P` and `UNC_M_DCLOCKTICKS` omit `EventCode`, which `jevents.py` encodes as event zero.
- `UNC_M_MAJOR_MODES.*`, `UNC_M_WMM_TO_RMM.*`, and `UNC_M_WRONG_MM`: memory-controller read, write, partial, and isoch major-mode behavior.
- `UNC_M_POWER_*`: channel DLL off, precharge power-down, CKE cycles by rank, self-refresh, PCU throttling, critical throttling, and per-rank throttle cycles.
- `UNC_M_RPQ_*`, `UNC_M_WPQ_*`, `UNC_M_PREEMPTION.*`, `UNC_M_RD_CAS_PRIO.*`, and `UNC_M_VMSE_*`: queue pressure, read/write priority, preemption, and VMSE write push behavior.
- `UNC_M_RD_CAS_RANK*.*` and `UNC_M_WR_CAS_RANK*.*`: the largest portion of the file, expanding CAS read/write accounting by rank 0, 1, 4, 5, 6, and 7 across all banks, banks 0-15, and bank groups 0-3. `UNC_M_RD_CAS_RANK2.BANK0` is a lone rank-2 read entry.

## Control Flow And Integration

The file is parsed at build time by `jevents.py`. Each JSON object is converted into a `JsonEvent`; `EventName` becomes the alias name, `BriefDescription` and `PublicDescription` become short and long descriptions, `Unit: "iMC"` becomes `uncore_imc`, `ScaleUnit` becomes the generated unit string, `Deprecated` is preserved, and `EventCode`/`UMask` are canonicalized into perf event terms.

At runtime, perf selects the BroadwellX PMU table through the x86 CPU map, then attaches the generated `uncore_imc` aliases to matching uncore memory-controller PMUs. User-facing integration points include `perf list`, `perf stat`, JSON event listing, metric expressions that reference memory bandwidth aliases, and Python helpers that expose PMU metadata. The table works with sysfs PMU `format` files that define how `event`, `umask`, and any unit-specific terms map to config bits.

## State And Persistence

The file has no runtime state. Its persistent behavior is generated metadata compiled into perf. Changing an alias name is an API change for scripts and metrics; changing event encodings changes which hardware condition is measured; changing `ScaleUnit` alters bandwidth-style presentation for the derived memory-read/write aliases.

All records are package-level uncore events. Hardware counter values are ephemeral, but the generated alias table persists until perf is rebuilt. `Deprecated: "1"` on `UNC_M_DCLOCKTICKS` is a compatibility state signal: consumers should prefer `UNC_M_CLOCKTICKS_P` while old scripts may still resolve the deprecated alias.

## Dependencies

The table depends on BroadwellX iMC PMU support in the kernel, the perf PMU-events generator, the BroadwellX x86 mapfile, and sysfs PMU format definitions for memory-controller event and mask fields. Hardware meaning depends on DRAM channel/rank/bank topology, read-major/write-major mode behavior, ECC support, power-management states, and BroadwellX-specific queue and VMSE mechanisms.

The many rank and bank aliases depend on correct generated-data preservation. Their names encode topology selections that are not validated by JSON syntax alone.

## Risks

The main risks are silent semantic drift and large generated-family maintenance errors. The rank/bank sections repeat similar encodings hundreds of times; a single wrong `UMask`, rank number, or event name can produce a plausible but incorrect alias. The lone `UNC_M_RD_CAS_RANK2.BANK0` should be treated as intentional only if it matches hardware documentation; it is structurally unusual compared with the complete rank 0/1/4/5/6/7 families.

Missing `EventCode` on `UNC_M_CLOCKTICKS_P` and deprecated `UNC_M_DCLOCKTICKS` is accepted by the current generator but should be guarded if schema validation tightens. `ScaleUnit: "64Bytes"` on the two derived LLC miss aliases is user-visible and important for bandwidth calculations. The deprecated alias should remain present unless a compatibility break is intended.

## Test Signals

Useful validation signals are `jq empty`, `jq 'length'` returning 326, no duplicate `EventName` values, and a key-set check covering `BriefDescription`, `Counter`, `Deprecated`, `EventCode`, `EventName`, `PerPkg`, `PublicDescription`, `ScaleUnit`, `UMask`, and `Unit`. Generation should produce `uncore_imc` entries and preserve `ScaleUnit` and `Deprecated`. Runtime smoke tests on BroadwellX hardware should cover `LLC_MISSES.MEM_READ`, `UNC_M_CAS_COUNT.RD`, `UNC_M_CAS_COUNT.WR`, `UNC_M_ECC_CORRECTABLE_ERRORS`, `UNC_M_MAJOR_MODES.READ`, `UNC_M_POWER_CKE_CYCLES.RANK0`, `UNC_M_RPQ_INSERTS`, and one read/write CAS rank-bank alias.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-power.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-power.json

## Purpose

This file is the BroadwellX package-control-unit power and residency PMU event table for Linux `perf`. It contains 57 event records, all with `Unit: "PCU"` and `PerPkg: "1"`. `jevents.py` maps the unit to generated PMU name `uncore_pcu`, exposing package-level PCU aliases for power-management analysis.

The events cover PCU clock ticks, per-core C-state transition cycles, per-core C-state demotions, frequency-limit cycles, frequency-transition cycles, memory phase shedding, package C-state residency, power-state occupancy filters, PROCHOT and VR hot cycles, total transition cycles, and ring global-voltage/frequency transitions.

## Schema And Public API

Each object is a perf alias record. Common fields are `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and usually `PublicDescription`. Unlike most other BroadwellX PMU files, this file does not use `UMask`; instead, three `UNC_P_POWER_STATE_OCCUPANCY.*` entries use `Filter` values (`occ_sel=1`, `occ_sel=2`, `occ_sel=3`) that `jevents.py` appends verbatim to the generated event encoding.

Important families include:

- `UNC_P_CLOCKTICKS`: PCU 1 GHz pclk cycles. It omits `EventCode`, so the current generator emits event zero for it.
- `UNC_P_CORE{0..17}_TRANSITION_CYCLES`: one event per core, using event codes `0x60` through `0x71`.
- `UNC_P_DEMOTIONS_CORE{0..17}`: one event per core, using event codes `0x30` through `0x41`.
- `UNC_P_FREQ_MAX_LIMIT_THERMAL_CYCLES`, `UNC_P_FREQ_MAX_OS_CYCLES`, `UNC_P_FREQ_MAX_POWER_CYCLES`, and `UNC_P_FREQ_MIN_IO_P_CYCLES`: frequency limit residency by cause.
- `UNC_P_FREQ_TRANS_CYCLES`, `UNC_P_TOTAL_TRANSITION_CYCLES`, and `UNC_P_UFS_TRANSITIONS_RING_GV`: package/ring transition timing.
- `UNC_P_PKG_RESIDENCY_C0_CYCLES`, `C1E`, `C2E`, `C3`, `C6`, and `C7`: package C-state residency counters.
- `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`, `.CORES_C3`, and `.CORES_C6`: filtered occupancy events using the same base event with different `occ_sel` filters.
- `UNC_P_PROCHOT_EXTERNAL_CYCLES`, `UNC_P_PROCHOT_INTERNAL_CYCLES`, and `UNC_P_VR_HOT_CYCLES`: thermal or voltage-regulator hot condition cycles.

## Control Flow And Integration

At build time, the PMU-events generator loads the JSON array and constructs one `JsonEvent` per record. `Unit: "PCU"` becomes `uncore_pcu`; `Filter` terms are appended to the event string; descriptions are embedded in generated compact string storage; `PerPkg` is preserved. At runtime, perf maps the BroadwellX table to PCU uncore PMUs and resolves user aliases to the generated encodings.

The primary integration points are `jevents.py`, generated `pmu-events.c`, `pmu-events.h`, uncore PMU matching in `tools/perf/util/pmu.c`, `perf list`, `perf stat`, and any BroadwellX metric groups that use PCU power or residency denominators.

## State And Persistence

There is no mutable state inside this file. Its persistent effect is the compiled alias table in perf. The hardware state being observed is package and per-core power-management state, but the JSON only describes how to program counters for that state.

The per-core transition and demotion events are source-level expansions up to core 17. They encode a BroadwellX core-count assumption into public aliases. All records are package-level uncore aliases through `PerPkg: "1"`.

## Dependencies

The table depends on BroadwellX PCU uncore PMU support, sysfs PMU format support for event selectors and the `occ_sel` filter, the x86 BroadwellX mapfile, and the perf PMU-events generator. Correct interpretation also depends on processor power-management behavior, C-state availability, thermal throttling, OS power policy, and package/ring frequency transition mechanisms.

## Risks

The highest-risk field is `Filter` on `UNC_P_POWER_STATE_OCCUPANCY.*`, because it is appended verbatim by the generator and must match the kernel PMU format. `UNC_P_CLOCKTICKS` lacks an `EventCode`; this is accepted now but should be preserved intentionally. Per-core event names and codes are easy to misorder because lexical order places core 10 before core 1 in some listings, while the numeric event-code sequence is hardware-defined.

The file encodes aliases for cores 0-17. On systems with disabled or absent cores, runtime availability and counts may differ from alias presence. Users comparing package residency, core transition, and demotion events must account for package scope and power-management policy.

## Test Signals

Validation should include `jq empty`, `jq 'length'` returning 57, a key-set check covering `BriefDescription`, `Counter`, `EventCode`, `EventName`, `Filter`, `PerPkg`, `PublicDescription`, and `Unit`, and generation checks that the three occupancy events preserve `occ_sel`. Runtime smoke tests on BroadwellX hardware should cover `UNC_P_CLOCKTICKS`, `UNC_P_CORE0_TRANSITION_CYCLES`, `UNC_P_DEMOTIONS_CORE0`, `UNC_P_FREQ_MAX_POWER_CYCLES`, `UNC_P_PKG_RESIDENCY_C6_CYCLES`, `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`, and `UNC_P_PROCHOT_INTERNAL_CYCLES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-power.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/virtual-memory.json

## Purpose

This file is the BroadwellX core PMU event table for virtual-memory and TLB behavior in Linux `perf`. It contains 38 event records and intentionally omits `Unit`, so `jevents.py` maps them to `default_core` rather than an uncore PMU. The aliases cover DTLB load misses, DTLB store misses, ITLB misses, EPT walk cycles, ITLB flushes, page-walker load sources, and TLB flushes.

The file is declarative input to the perf PMU-events generator. It supplies public aliases and sampling defaults for memory-translation analysis, including page-walk cause/completion/duration by access type and page size.

## Schema And Public API

Common fields are `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and sometimes `PublicDescription`. The file also uses `Errata` extensively. Twenty-five records cite errata: most cite `BDM69`, and some page-walker load records cite `BDM69, BDM98`. There is no `PerPkg` because these are core PMU events, not package uncore events.

Important families include:

- `DTLB_LOAD_MISSES.*`: load-side DTLB/STLB misses, STLB hits by 2M or 4K page size, page walks caused, walks completed by page size, and page-walk duration.
- `DTLB_STORE_MISSES.*`: store-side equivalents for misses, STLB hits, completed walks, and walk duration.
- `ITLB_MISSES.*` and `ITLB.ITLB_FLUSH`: instruction-side translation misses, STLB hits, completed walks, walk duration, and ITLB flushes.
- `EPT.WALK_CYCLES`: extended page-table walk cycles for virtualization workloads.
- `PAGE_WALKER_LOADS.*`: page-walker loads sourced from DTLB or ITLB L1, L2, L3, or memory.
- `TLB_FLUSH.DTLB_THREAD` and `TLB_FLUSH.STLB_ANY`: TLB flush events for thread DTLB and shared TLB.

## Control Flow And Integration

During perf build, `jevents.py` parses this JSON and turns each object into generated core-PMU aliases. `EventName` is lowercased, `EventCode` and `UMask` become event terms, `SampleAfterValue` becomes `period=<value>`, descriptions are embedded, and `Errata` text is appended to descriptions as specification-update notes.

At runtime, the BroadwellX CPU map selects this table for family/model `GenuineIntel-6-4F`. Since `Unit` is absent, PMU matching uses the default core PMU marker. Commands such as `perf list`, `perf stat -e dtlb_load_misses.walk_completed`, and `perf record -e itlb_misses.walk_duration` resolve through generated aliases to model-specific raw core events.

## State And Persistence

The file has no mutable state. Its persistent effect is the generated alias table and default sampling periods compiled into perf. Runtime counter readings and samples are transient hardware state. The public alias names, errata notes, and default periods are stable until the JSON changes and perf is regenerated.

Because many aliases share an event code and differ only by `UMask`, the state users observe depends heavily on correct mask selection. Page-size-specific aliases are particularly sensitive to mask correctness.

## Dependencies

The file depends on BroadwellX core PMU support, perf's JSON schema and generator, the BroadwellX mapfile, and kernel support for programming the listed model-specific event selectors. Correct interpretation depends on BroadwellX TLB hierarchy, page-walk hardware, STLB behavior, EPT support for virtualization, page sizes in use, and errata documented by Intel specification updates.

## Risks

Errata preservation is the main documentation risk. `jevents.py` appends errata strings to generated descriptions, so removing `Errata` fields would silently remove important correctness caveats from `perf list`. Some public descriptions appear copy-pasted across access types and mention stores in ITLB contexts; this is a documentation-quality risk even if encodings are correct.

The event families are highly mask-driven. `DTLB_LOAD_MISSES`, `DTLB_STORE_MISSES`, and `ITLB_MISSES` each use one base event code with masks for walk caused, STLB hit, completed walks by page size, and duration. A mask typo can produce a plausible alias that measures the wrong page-walk condition. `SampleAfterValue` values differ by family and affect profiling behavior, so they should not be normalized blindly.

## Test Signals

Validation should include `jq empty`, `jq 'length'` returning 38, and a key-set check covering `BriefDescription`, `Counter`, `Errata`, `EventCode`, `EventName`, `PublicDescription`, `SampleAfterValue`, and `UMask`. Generation should verify errata text is appended to descriptions and default-core PMU routing is used. Runtime smoke tests on BroadwellX should cover `DTLB_LOAD_MISSES.MISS_CAUSES_A_WALK`, `DTLB_LOAD_MISSES.WALK_COMPLETED_4K`, `DTLB_STORE_MISSES.WALK_DURATION`, `ITLB_MISSES.STLB_HIT`, `EPT.WALK_CYCLES`, `PAGE_WALKER_LOADS.DTLB_MEMORY`, and `TLB_FLUSH.STLB_ANY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/virtual-memory.json -->
