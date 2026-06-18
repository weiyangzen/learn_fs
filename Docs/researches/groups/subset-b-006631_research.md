# subset-b-006631 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/uncore-io.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/uncore-io.json

## Purpose

`uncore-io.json` is a Broadwell-DE perf PMU event table for the R2PCIe uncore block. It contributes Intel model-specific aliases that let users refer to R2PCIe ring, IIO-credit, queue, and stall counters by symbolic names such as `UNC_R2_RING_AD_USED.ALL` rather than by raw uncore event encodings. The file is data, not executable code, but it is part of perf's build-time event database and therefore participates in the generated `pmu-events.c` tables used by `perf list`, event parsing, Python export, and PMU alias lookup.

The table contains 62 JSON objects, all scoped to `Unit: "R2PCIe"` and `PerPkg: "1"`. Every entry has an `EventCode`; all but `UNC_R2_CLOCKTICKS` also carry a `UMask`. The counters are package-level uncore counters, so they describe socket/package R2PCIe behavior rather than per-task or per-core attribution.

## Important APIs, Types, and Data Shape

Each object uses the perf PMU JSON schema fields consumed by `tools/perf/pmu-events/jevents.py`: `EventName`, `EventCode`, optional `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and often `PublicDescription`. During the perf build, `jevents.py` converts these records into generated C data in `pmu-events/pmu-events.c`, represented at runtime through the `pmu-events.h` event-table structures. `util/pmu.c` then exposes the generated entries as PMU aliases, and `builtin-list.c` prints their descriptions and encodings.

The important semantic API here is the stable event naming convention:

- `UNC_R2_CLOCKTICKS` is the baseline uncore clock-domain counter.
- `UNC_R2_IIO_CREDIT.*`, `UNC_R2_IIO_CREDITS_ACQUIRED.*`, and `UNC_R2_IIO_CREDITS_USED.*` describe IIO credit availability, acquisition, and in-use cycles for QPI and message classes.
- `UNC_R2_RING_{AD,AK,BL,IV}_USED.*` describe ring traffic occupancy by ring, direction, and polarity.
- `UNC_R2_RING_AK_BOUNCES.*` tracks AK ingress bounce events.
- `UNC_R2_RxR_*` and `UNC_R2_TxR_*` cover receive/transmit ring occupancy, non-empty/full cycles, inserts, and clockwise NACKs.
- `UNC_R2_SBO0_*` and `UNC_R2_STALL_NO_SBO_CREDIT.*` cover SBO credit acquisition, occupancy, and stalls.

Counters are declared as string lists such as `0,1` or `0,1,2,3`, which the generated alias metadata passes through to perf's PMU constraint logic. The unit string is the binding point to the kernel's R2PCIe uncore PMU name matching; if the running kernel does not expose a matching PMU, the aliases remain unavailable or unresolvable.

## Control Flow

There is no runtime control flow in the JSON itself. The effective control flow is:

1. The x86 `mapfile.csv` maps Broadwell-DE CPUs (`GenuineIntel-6-56`) to the `broadwellde` event directory.
2. The perf build copies or reads `pmu-events/arch/x86/broadwellde/uncore-io.json` through `pmu-events/Build`.
3. `jevents.py` parses the array, normalizes field names, and emits C table rows with event name, unit, event code, mask, counter constraints, package scope, and descriptions.
4. At runtime, perf chooses the generated table matching the host CPU model, looks up events for discovered PMUs, and exposes the aliases in `perf list` and event parsing.
5. When a user records or stats one of these aliases, perf resolves the alias to the raw R2PCIe uncore event selector and opens the corresponding perf event on the package PMU.

The file's order is also user-visible in generated event listings, so broad family grouping and stable ordering matter for review diffs and list output.

## State and Persistence Behavior

The source file is static repository data. Build products persist a transformed copy in generated `pmu-events.c` and `libpmu-events.a`; runtime state is limited to perf's in-memory PMU alias tables and opened perf-event file descriptors. The events themselves count hardware state in the R2PCIe unit while counters are enabled. `PerPkg: "1"` means results should be interpreted as package-level measurements, not process-local state.

No state is written back to this JSON. Changing an event name, code, mask, unit, or description affects all later perf builds and can break scripts that rely on alias strings.

## Dependencies and Integration Points

The file depends on the x86 PMU-event generator, the Broadwell-DE mapfile row, the kernel exposing compatible Intel uncore R2PCIe PMUs, and perf's PMU alias machinery. It integrates with `perf list` default and JSON output, `perf stat -e <alias>`, `perf record` where uncore sampling is supported, and Python dictionary export of PMU events. It is adjacent to other `broadwellde` core and uncore JSON files, which together form the model's complete event database.

The descriptions rely on Intel Broadwell-DE uncore event semantics. They distinguish cycles-in-use counters from discrete insert/acquire/bounce/NACK counters, which is important because users may combine them into ratios such as occupancy per clocktick or stalls per transfer.

## Risks and Edge Cases

The largest correctness risk is metadata drift from Intel's event specification: a wrong `EventCode`, `UMask`, or `Unit` silently produces wrong measurements or an alias that cannot be programmed. `UNC_R2_CLOCKTICKS` intentionally lacks `UMask`; validation should treat this as a clock event rather than a malformed entry. Ring-use masks combine direction and even/odd polarity, so copy/paste errors among `CW`, `CCW`, `*_EVEN`, and `*_ODD` entries are easy to miss in plain JSON review.

The file uses only R2PCIe package events, so applying these aliases on non-Broadwell-DE hardware or kernels without matching uncore PMUs should fail gracefully. Public descriptions contain nuanced wording about what is included and excluded, such as packets passing by versus sent from the ring stop; losing those descriptions would make derived analysis easier to misinterpret.

## Test Signals

Useful checks include `jq` parsing, schema checks for required fields, duplicate `EventName` detection, verification that every non-clock event has an `UMask`, and comparison against Intel Broadwell-DE uncore tables. Build-level validation should regenerate `pmu-events.c` without generator warnings and run perf's PMU-event tests. Runtime signals include `perf list --unit R2PCIe`, `perf list --json` showing the R2PCIe aliases, and `perf stat -e UNC_R2_CLOCKTICKS,UNC_R2_RING_AD_USED.ALL` on Broadwell-DE hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/uncore-io.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/uncore-memory.json

## Purpose

`uncore-memory.json` is the Broadwell-DE integrated memory-controller PMU event table for perf. It defines symbolic aliases for DRAM command counts, controller modes, queue occupancy, refresh/ECC/power behavior, priority classes, VMSE write behavior, and per-rank/per-bank read and write CAS counters. These aliases allow tools and users to measure memory-controller behavior through names such as `UNC_M_CAS_COUNT.RD`, `UNC_M_MAJOR_MODES.WRITE`, and `UNC_M_RD_CAS_RANK0.BANK0`.

The file contains 322 event records, all with `Unit: "iMC"` and `PerPkg: "1"`. It is the largest of this subset because it expands rank/bank matrices into individual aliases: read CAS counters for ranks 0, 1, 2, 4, 5, 6, and 7, and write CAS counters for ranks 0, 1, 4, 5, 6, and 7. The data is package-scoped uncore metadata, not executable logic.

## Important APIs, Types, and Data Shape

The records use perf's PMU event JSON schema: `EventName`, `EventCode`, optional `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and usually `PublicDescription`. `jevents.py` consumes these fields at build time and emits C event-table rows in generated `pmu-events.c`; `util/pmu.c`, `builtin-list.c`, metric code, and Python PMU export consume the generated tables.

Important event families include:

- `UNC_M_ACT_COUNT.*`, `UNC_M_PRE_COUNT.*`, `UNC_M_DRAM_PRE_ALL`, and `UNC_M_DRAM_REFRESH.*` for DRAM row activate, precharge, and refresh activity.
- `UNC_M_CAS_COUNT.*` for aggregate read/write CAS counts, including RMM/WMM split and underfill reads.
- `UNC_M_RD_CAS_RANK*.*` and `UNC_M_WR_CAS_RANK*.*` for rank/bank-specific read and write CAS attribution.
- `UNC_M_MAJOR_MODES.*`, `UNC_M_WMM_TO_RMM.*`, and `UNC_M_WRONG_MM` for memory-controller scheduling mode behavior.
- `UNC_M_RPQ_*`, `UNC_M_WPQ_*`, `UNC_M_WPQ_READ_HIT`, and `UNC_M_WPQ_WRITE_HIT` for read/write pending queue behavior.
- `UNC_M_POWER_*` for channel, rank, self-refresh, PCU throttling, critical throttling, and CKE/power-throttle cycles.
- `UNC_M_ECC_CORRECTABLE_ERRORS` for corrected ECC events.
- `UNC_M_VMSE_*` for VMSE write occupancy and push behavior.

The schema count shows one event without `EventCode` (`UNC_M_DCLOCKTICKS`) and 29 events without `UMask`, mostly clock or unfiltered single-selector events. The remaining records use masks to distinguish mode, rank, bank, priority, and command-type subevents.

## Control Flow

The JSON has no branches or functions, but it participates in perf's deterministic PMU-event generation flow:

1. `pmu-events/arch/x86/mapfile.csv` maps Broadwell-DE model 6-56 to the `broadwellde` directory.
2. `pmu-events/Build` feeds the architecture directory to `jevents.py`.
3. `jevents.py` parses this file, converts each memory-controller alias into generated C data, and preserves event encodings, counter constraints, descriptions, unit, and package scope.
4. Runtime PMU discovery matches generated `Unit: "iMC"` aliases against kernel iMC uncore PMUs.
5. `perf list`, `perf stat`, metrics, and user event parsing resolve symbolic names into raw uncore iMC events.

The rank/bank sections are effectively a generated-looking cross product encoded as literal JSON. That makes ordering important: list output and review diffs depend on stable grouping by rank and bank.

## State and Persistence Behavior

The file persists only static event metadata. Generated build artifacts persist a compiled representation until the next perf rebuild. Runtime state exists in perf's alias tables and in hardware iMC counters opened for a measurement interval. Because all records are package-scoped uncore events, measurements are shared by workloads on the package and cannot be attributed directly to a single process without additional experimental control.

There is no writeback path. Any change to event names can break user scripts, dashboards, or metric expressions that name these aliases. Any change to encodings changes hardware programming and therefore the meaning of collected data.

## Dependencies and Integration Points

This file depends on perf's x86 PMU-event generation, the Broadwell-DE CPU map, the Intel uncore iMC kernel PMU driver, and user-space PMU alias support. It integrates with `perf list --unit iMC`, `perf stat -e` on iMC aliases, JSON event listing, generated metric parsing where metrics refer to memory aliases, and perf tests that compare generated event tables with expected PMU-event rows.

It also has conceptual dependencies on memory-controller behavior: open-page versus closed-page policy, read major mode, write major mode, partial/underfill handling, rank CKE states, throttling, and ECC support. Some events are useful only on systems with matching DRAM configuration, ECC enabled, or ranks/banks that physically exist.

## Risks and Edge Cases

The large rank/bank matrix is vulnerable to copy/paste errors in event names, masks, and descriptions. `UNC_M_RD_CAS_RANK2.BANK0` is the only rank-2 read entry in this file, while rank 3 is absent and ranks 4-7 are populated; that asymmetry may reflect the Broadwell-DE source table but should be treated as a high-value regression check. Write CAS entries omit ranks 2 and 3 entirely. If those omissions are accidental, users lose aliases; if they are intentional, tests should not auto-generate nonexistent aliases.

`UNC_M_DCLOCKTICKS` lacks an `EventCode`, and many power or single-selector events lack `UMask`; generator validation must allow these forms when the upstream schema permits them. Some descriptions include known spelling/wording issues from source material. Correcting text is low risk, but changing encoded fields is high risk because the generator does not know the hardware truth.

Interpretation risks are also significant: CAS counts are per channel/controller, power states may count cycles when all ranks are in a state, and rank filters can count only configured ranks. Users can easily derive misleading bandwidth or page-hit metrics if they ignore clock domains, channel count, package scope, or unavailable rank/bank topology.

## Test Signals

Validation should include JSON parsing, duplicate-name checks, required-field checks, generator rebuild, and perf PMU-event unit tests. Event-family tests should verify that aggregate CAS, major-mode, queue, power, and rank/bank aliases appear in `perf list --unit iMC`. Hardware smoke tests on Broadwell-DE should include `UNC_M_DCLOCKTICKS`, `UNC_M_CAS_COUNT.RD`, `UNC_M_CAS_COUNT.WR`, one rank/bank read CAS event, one write CAS event, and one power/throttle event. Review tests should flag unexpected changes to the rank/bank inventory, especially absent or newly added rank-2/rank-3 aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/uncore-power.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/uncore-power.json

## Purpose

`uncore-power.json` defines Broadwell-DE PCU uncore PMU aliases for package power, frequency-limit, C-state transition, residency, demotion, PROCHOT, VR-hot, and related power-controller behavior. It lets perf expose hardware counters with names such as `UNC_P_CLOCKTICKS`, `UNC_P_FREQ_MAX_POWER_CYCLES`, `UNC_P_PKG_RESIDENCY_C6_CYCLES`, and `UNC_P_DEMOTIONS_CORE0`.

The file contains 57 records, all scoped to `Unit: "PCU"` and `PerPkg: "1"`. The PCU clock event has no `EventCode`, and none of the events use `UMask`; instead, each selector is either a single code or, for `UNC_P_POWER_STATE_OCCUPANCY.*`, a shared event code with a `Filter` value that distinguishes core C-state occupancy classes.

## Important APIs, Types, and Data Shape

The table uses perf PMU event JSON fields `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, `PublicDescription`, and for three occupancy aliases `Filter`. `jevents.py` converts these records into generated C PMU-event rows, and perf's PMU alias layer later binds them to PCU uncore PMUs discovered from the kernel.

Important event groups include:

- `UNC_P_CLOCKTICKS`, the fixed 1 GHz PCU clock domain used as a wall-time-like baseline.
- `UNC_P_CORE{0..17}_TRANSITION_CYCLES`, per-core C-state transition-cycle counters.
- `UNC_P_DEMOTIONS_CORE{0..17}`, per-core C-state demotion counters.
- `UNC_P_FREQ_MAX_LIMIT_THERMAL_CYCLES`, `UNC_P_FREQ_MAX_POWER_CYCLES`, `UNC_P_FREQ_MAX_OS_CYCLES`, `UNC_P_FREQ_MIN_IO_P_CYCLES`, and `UNC_P_FREQ_TRANS_CYCLES`, which identify frequency-limit and transition causes.
- `UNC_P_PKG_RESIDENCY_C{0,1E,2E,3,6,7}_CYCLES` for package C-state residency.
- `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`, `.CORES_C3`, and `.CORES_C6`, all using event code `0x80` with different filters.
- `UNC_P_PROCHOT_INTERNAL_CYCLES`, `UNC_P_PROCHOT_EXTERNAL_CYCLES`, `UNC_P_VR_HOT_CYCLES`, `UNC_P_TOTAL_TRANSITION_CYCLES`, `UNC_P_MEMORY_PHASE_SHEDDING_CYCLES`, and `UNC_P_UFS_TRANSITIONS_RING_GV` for platform throttling and power-state transitions.

The lack of masks is meaningful: reviewers should not assume every PMU event row requires a `UMask`. For the filter-based occupancy rows, `Filter` is the field that selects the subcondition.

## Control Flow

Runtime behavior is produced by the standard PMU-event path:

1. Broadwell-DE CPU matching selects the `broadwellde` PMU-event directory.
2. The build reads this JSON through `jevents.py`.
3. The generator emits PCU aliases into generated `pmu-events.c`.
4. Perf discovers PCU uncore PMUs and matches `Unit: "PCU"` aliases to them.
5. `perf list` and event parsing expose the aliases; `perf stat` opens package PCU counters and reports counts for the enabled interval.

The core-indexed transition and demotion aliases are enumerated as individual records rather than being parameterized. That keeps runtime alias lookup simple, but means additions or corrections must update every affected literal row.

## State and Persistence Behavior

The file stores static metadata only. Generated build artifacts persist the compiled alias table. Runtime state is in hardware PCU counters and perf's opened file descriptors for the measurement interval. `PerPkg: "1"` makes these counters package-level; even per-core demotion and transition aliases are exposed through the package PCU uncore device rather than through ordinary per-core programmable counters.

No persistent measurements are stored by this file. Description and encoding changes affect future builds and may alter user-visible `perf list` output and scripted event names.

## Dependencies and Integration Points

This file depends on the Broadwell-DE CPU map, perf's PMU-event generator, the Intel PCU uncore kernel PMU, and perf alias matching. It integrates with power and frequency investigations in `perf stat`, `perf list --unit PCU`, JSON event output, and any higher-level metrics that use PCU clock or residency counters as denominators.

The event semantics depend on PCU firmware/hardware definitions: fixed 1 GHz PCU clocking, package C-state residency accounting, core C-state demotion rules, PROCHOT source accounting, and frequency limit causes. Correct interpretation may also depend on BIOS power settings and workload residency behavior.

## Risks and Edge Cases

The three `UNC_P_POWER_STATE_OCCUPANCY.*` rows share `EventCode: "0x80"` and differ by `Filter`; dropping or mishandling the `Filter` field would collapse distinct aliases into the same encoding. `UNC_P_CLOCKTICKS` has no `EventCode`, which must be accepted as a clock event. Because none of the rows uses `UMask`, schema validators that require masks for all non-clock events would reject valid PCU entries.

Core-numbered aliases cover cores 0 through 17. Broadwell-DE SKUs with fewer active cores may expose counters whose corresponding logical core is absent or inactive; users must interpret zero or unsupported counts in the context of the actual package. Package-level power counters are also workload-shared, so they are sensitive to background activity and platform firmware.

Descriptions are concise and repetitive for core transition/demotion rows. That is good for generated list readability but increases the chance that a single code change in the sequence goes unnoticed. Tests should verify monotonic code mapping for core indices rather than relying only on JSON syntax.

## Test Signals

Useful validation includes JSON parsing, duplicate-name detection, generator rebuild, and explicit checks that `Filter` survives generation for `UNC_P_POWER_STATE_OCCUPANCY.*`. Runtime smoke tests on Broadwell-DE should include `perf list --unit PCU`, `perf stat -e UNC_P_CLOCKTICKS`, one package residency alias, one frequency-limit alias, one PROCHOT/VR-hot alias, and one per-core transition or demotion alias. Review tests should compare the core-indexed `EventCode` sequences for cores 0-17 against the Intel table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/uncore-power.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/virtual-memory.json

## Purpose

`virtual-memory.json` defines Broadwell-DE core PMU aliases for TLB misses, page walks, EPT walks, page-walker memory-source attribution, and TLB flushes. It is the model-specific event table behind symbolic events such as `DTLB_LOAD_MISSES.WALK_COMPLETED_4K`, `ITLB_MISSES.STLB_HIT`, `PAGE_WALKER_LOADS.DTLB_MEMORY`, and `TLB_FLUSH.STLB_ANY`.

The file contains 38 records. Unlike the uncore files in this subset, these are core PMU events and therefore do not carry a `Unit` or `PerPkg` field. Every record has an `EventCode`, `UMask`, `Counter`, `BriefDescription`, and `SampleAfterValue`; 25 records include `Errata: "BDM69"`, warning that the affected Broadwell-DE event semantics have documented errata.

## Important APIs, Types, and Data Shape

The JSON schema fields are consumed by `jevents.py` and compiled into generated `pmu-events.c` rows. Runtime consumers include `perf list`, `perf record`, `perf stat`, `perf report` metadata, and Python PMU event export. The `SampleAfterValue` field is important for sampling defaults: it gives perf a suggested period for sampled use of these core events.

Important families include:

- `DTLB_LOAD_MISSES.*`: load-side DTLB misses, STLB hits, page-walk causes, completed walks by page size, and walk duration.
- `DTLB_STORE_MISSES.*`: store-side equivalents for STLB hits and page walks.
- `ITLB_MISSES.*`: instruction-side miss, STLB-hit, completed-walk, page-size, and walk-duration events.
- `ITLB.ITLB_FLUSH`: instruction TLB flush counts.
- `EPT.WALK_CYCLES`: cycles spent in extended page table walks for virtualization.
- `PAGE_WALKER_LOADS.*`: page-walker loads sourced from L1, L2, L3, or memory, split for DTLB and ITLB where applicable.
- `TLB_FLUSH.DTLB_THREAD` and `TLB_FLUSH.STLB_ANY`: data-thread and shared-TLB flush events.

The repeated `EventCode` values form families selected by masks: `0x08` for DTLB load misses, `0x49` for DTLB store misses, `0x85` for ITLB misses, `0xBC` for page-walker loads, and `0xBD` for TLB flushes. Subevent masks distinguish STLB hit page size, page-walk completion page size, walk duration, or flush target.

## Control Flow

The file has no executable control flow. Its build/runtime flow is:

1. Broadwell-DE CPU model matching selects the `broadwellde` JSON directory.
2. `jevents.py` parses `virtual-memory.json` and emits core PMU event aliases into generated `pmu-events.c`.
3. Perf's PMU alias layer associates these events with the default core PMU for matching Broadwell-DE systems.
4. `perf list` exposes the aliases and descriptions; `perf stat` and `perf record` resolve alias names to raw event selector, mask, counter, and sampling-period metadata.
5. Downstream reports interpret samples or counts as core-level virtual-memory behavior.

Because these are core PMU events, they interact with ordinary per-thread/per-CPU perf targeting, multiplexing, counter constraints, and sample period behavior rather than the package-level uncore matching used by the other three files.

## State and Persistence Behavior

The JSON persists static event metadata. Generated build artifacts persist C representations until rebuild. Runtime state is in perf's alias tables and in programmed core PMU counters or sample streams. `SampleAfterValue` influences the default sampling threshold when users record these events, but the JSON itself does not store collected samples or counts.

Errata metadata is persistent descriptive state: consumers and reviewers should preserve `BDM69` tags because they signal that counts may need caveats or may be unsuitable for some derived metrics.

## Dependencies and Integration Points

The file depends on perf's PMU-event build, the Broadwell-DE x86 mapfile entry, core PMU event parsing, and the kernel's core perf event support. It integrates with TLB and virtual-memory profiling workflows: `perf stat` for aggregate miss/walk/flush counts, `perf record` for sampling high-volume miss events, `perf report` for attributing samples, and `perf list --json` for tooling that discovers event metadata.

It also connects to virtualization analysis through `EPT.WALK_CYCLES`, and to memory hierarchy analysis through page-walker source events. These aliases are often combined with CPU cycles, instructions, cache misses, and memory events to estimate TLB pressure, page-walk cost, huge-page effectiveness, and flush overhead.

## Risks and Edge Cases

The `BDM69` errata tag appears on most walk-causing and walk-completed DTLB/ITLB events. Removing or ignoring those tags can lead users to over-trust affected measurements. Several public descriptions appear copied between load/store/instruction families and contain wording mismatches, such as ITLB descriptions referring to store or DTLB misses; textual cleanup should be careful not to alter encodings unless verified against Intel's table.

Subevent masks are dense and similar across families. A wrong mask can turn a page-size-specific event into a broader or different count while still parsing correctly. The `WALK_COMPLETED` aggregate masks (`0xe`) overlap the individual page-size masks (`0x2`, `0x4`, `0x8`), so tests should check intentional aggregation instead of flagging it as duplicate encoding.

Sampling defaults differ: most events use `100003`, while STLB load hits and some walk events use `2000003`. Changes to `SampleAfterValue` alter record overhead and sample density. As core events, these aliases are also subject to multiplexing and counter availability; `Counter: "0,1,2,3"` permits four generic counters but does not guarantee simultaneous measurement with arbitrary other events.

## Test Signals

Useful validation includes JSON parsing, duplicate-name checks, required `EventCode`/`UMask`/`SampleAfterValue` checks, errata tag preservation, and generator rebuild. Runtime checks should include `perf list DTLB_LOAD_MISSES`, `perf list ITLB_MISSES`, and `perf stat` on representative aliases such as `DTLB_LOAD_MISSES.WALK_DURATION`, `DTLB_STORE_MISSES.STLB_HIT_4K`, `ITLB.ITLB_FLUSH`, `PAGE_WALKER_LOADS.DTLB_MEMORY`, and `TLB_FLUSH.STLB_ANY`. Sampling tests should confirm that `perf record -e <alias>` accepts the generated alias and uses a sane sample period.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/virtual-memory.json -->
