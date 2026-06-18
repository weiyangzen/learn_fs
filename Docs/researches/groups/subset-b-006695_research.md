# Research: subset-b-006695

Grouped research for the Jaketown perf PMU event JSON files under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown`. These files are declarative event-table inputs for the Linux `perf` PMU event tooling, not executable modules.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-interconnect.json

## Purpose

`uncore-interconnect.json` defines 207 Jaketown uncore interconnect PMU events consumed by perf's JSON event-table generation path. The file covers socket/package interconnect and system-agent style units rather than core pipeline events. Its records describe event aliases, event select codes, unit masks, allowed counter sets, package scope, and user-facing descriptions for the IRP, QPI, R3QPI, and UBOX units.

This file is data, but it behaves like an API contract for perf users and for the generated event tables. Names such as `UNC_Q_RxL_FLITS_G1.HOM_REQ` or `UNC_R3_RING_AD_USED.CW_EVEN` become stable event identifiers that can be requested through `perf stat`/`perf list` on matching Sandy Bridge-EP/Jaketown systems.

## Important API Surface and Data Shape

Each entry is a JSON object with common keys:

- `EventName`: public perf event alias. All 207 names are unique.
- `EventCode`: hardware event select value where required. Some clock or special QPI transfer entries omit this field.
- `UMask`: unit-mask selector where required. Some clock/simple events omit it.
- `Unit`: uncore PMU unit selector. This file uses `IRP`, `QPI`, `R3QPI`, and `UBOX`.
- `Counter`: comma-separated list of compatible hardware counter indexes.
- `PerPkg`: package-level scoping flag, consistently present for these uncore records.
- `BriefDescription` and usually `PublicDescription`: short and expanded event help text.

The main event families are:

- `IRP` (36 events): address-match stalls/merges, outstanding read/write/cache occupancy, IRP clockticks, receive ring insert/occupancy/full cycles, tickle events, transaction reads/writes/prefetches, transmit request/data insertions, and write-ordering stall cycles. IRP records use counters `0,1`.
- `QPI` (84 events): QPI clockticks, Direct2Core success/failure, link power cycles, receive/transmit link bypass, CRC/no-credit conditions, VN0/VNA credits, cycles-not-empty, flit classification for G0/G1/G2, link insert/occupancy, and stall reasons. QPI records generally allow counters `0,1,2,3`.
- `R3QPI` (63 events): ring and QPI interface bridge events including IIO credits acquired/used/rejected, AD/AK/BL ring used by direction and parity, IV usage, receive ring bypass/cycles/inserts/occupancy, VN0/VNA credit usage/rejects, and VNA credit cycles. Counter constraints vary more here, including single-counter records and combinations such as `0,1,2`.
- `UBOX` (24 events): UBOX clockticks, event-message classes, filter-match variants, lock cycles, message channel size, PHOLD cycles, RACU request count, and U2C monitor/error/trap message classes.

## Control Flow

There is no runtime control flow inside the file. The effective flow is external:

1. perf's PMU event-table generator reads architecture/model JSON files from `tools/perf/pmu-events/arch/x86/jaketown`.
2. Each JSON object is validated and converted into generated C table entries.
3. At runtime, perf matches the CPU model to the Jaketown table and exposes these aliases through `perf list`.
4. A user-selected alias is resolved into the encoded uncore PMU config using `EventCode`, `UMask`, `Unit`, and any filter fields.
5. The kernel/perf uncore driver programs the selected uncore PMU counter if the `Unit` and `Counter` constraints match available hardware.

Ordering in the file is meaningful for maintainability and generated help output: related umask variants are grouped together under a shared event prefix.

## State and Persistence Behavior

The file has no mutable state. Its persistent state is the checked-in JSON array. The hardware counters it describes are volatile PMU registers, but this file only maps symbolic names to encodings. Changes to event names, unit masks, or counter lists persist into generated perf event tables and can alter user-facing CLI compatibility.

All records are package-scoped through `PerPkg: "1"`, which matters for multi-socket aggregation: users should expect counts to represent uncore/package domains, not per-thread or per-core execution.

## Dependencies and Integration Points

Dependencies are structural rather than imported:

- The JSON schema expected by perf's `pmu-events` generator.
- Jaketown uncore PMU naming and encoding conventions.
- Matching uncore PMU unit names (`IRP`, `QPI`, `R3QPI`, `UBOX`) understood by perf's generated tables and runtime PMU discovery.
- Adjacent Jaketown files such as `uncore-io.json`, `uncore-memory.json`, and `uncore-power.json`, which complete the platform event catalog.

Integration risks are highest at the boundary where JSON strings become generated C constants. `Counter` is encoded as a string list, not a structured array, so formatting must remain compatible with the parser. Missing `EventCode` or `UMask` values are expected for some records, but consumers must distinguish intentional omissions from malformed event definitions.

## Risks and Edge Cases

- The file has 12 records without `EventCode` and 55 without `UMask`; this is valid for some event classes but should be covered by generator validation so absent fields are not silently mis-encoded.
- `UNC_U_CLOCKTICKS` lacks both `EventCode` and public/brief description content beyond its name, making generated help weaker than neighboring records.
- Some QPI flit transfer records omit `EventCode` while related receive-side records include codes; regressions in parser defaults could break only these aliases.
- `R3QPI` counter lists are less uniform than the QPI records. A mistaken broadening to `0,1,2,3` could allow invalid scheduling on hardware.
- Description text uses hardware abbreviations (`DRS`, `HOM`, `NCB`, `NCS`, `NDR`, `SNP`, `VNA`) without local glossary. That is acceptable for perf PMU tables but increases user interpretation risk.
- Because event names are public aliases, renaming or re-casing any name is a compatibility break for scripts that call `perf stat -e`.

## Test Signals

Useful validation signals include:

- `jq` parse succeeds and the root is an array of 207 objects.
- `EventName` uniqueness holds across all 207 entries.
- Required schema fields are present where expected: `EventName`, `Unit`, `Counter`, `BriefDescription`, and `PerPkg` for every entry.
- All `Unit` values are in the expected set: `IRP`, `QPI`, `R3QPI`, `UBOX`.
- Generated perf event tables build without pmu-events warnings.
- `perf list` on a supported Jaketown system shows representative aliases from each unit family.
- Hardware smoke tests can attempt `perf stat -e` for `UNC_I_CLOCKTICKS`, one QPI flit event, one R3QPI ring event, and one UBOX message event, verifying that counter constraints are accepted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-io.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-io.json

## Purpose

`uncore-io.json` defines 36 Jaketown uncore IO PMU events for the `R2PCIe` unit. These events expose PCIe/ring bridge behavior: IIO credit accounting, ring channel usage, receive ring pressure, egress fullness/not-empty cycles, and NACKs. The file complements `uncore-interconnect.json`, which contains the analogous `R3QPI` bridge events for QPI-facing traffic.

The public API is the set of `UNC_R2_*` event aliases. They let perf users diagnose IO-facing interconnect pressure, PCIe credit starvation, and ring AD/AK/BL traffic directionality.

## Important API Surface and Data Shape

The file is a JSON array of 36 unique event objects with these keys: `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, `PublicDescription`, `UMask`, and `Unit`.

All records use `Unit: "R2PCIe"` and `PerPkg: "1"`. Event families are:

- `UNC_R2_CLOCKTICKS`: uncore clock cycles for the R2PCIe domain, using counters `0,1,2,3`.
- `UNC_R2_IIO_CREDITS_ACQUIRED`, `UNC_R2_IIO_CREDITS_REJECT`, and `UNC_R2_IIO_CREDITS_USED`: DRS, NCB, and NCS credit accounting using event codes `0x33`, `0x34`, and `0x32`.
- `UNC_R2_RING_AD_USED`, `UNC_R2_RING_AK_USED`, and `UNC_R2_RING_BL_USED`: clockwise/counter-clockwise and even/odd ring channel usage variants using event codes `0x7`, `0x8`, and `0x9`.
- `UNC_R2_RING_IV_USED.ANY`: IV ring usage.
- `UNC_R2_RxR_AK_BOUNCES` and `UNC_R2_RxR_CYCLES_NE` variants for receive-ring activity.
- `UNC_R2_TxR_CYCLES_FULL`, `UNC_R2_TxR_CYCLES_NE`, and `UNC_R2_TxR_NACKS`: AD/AK/BL egress pressure and NACK indicators.

Most events allow counters `0,1`; ring usage and clock events generally allow `0,1,2,3`; the TxR cycle events are restricted to counter `0`.

## Control Flow

The file has no executable control flow. Its external flow is:

1. The perf pmu-events generation tooling reads the Jaketown JSON catalog.
2. The R2PCIe records are emitted into generated event tables with event code, umask, unit, and counter metadata.
3. Runtime perf CPU-model matching selects the Jaketown table.
4. `perf list` exposes `UNC_R2_*` names, and `perf stat -e` resolves a selected name to an R2PCIe uncore PMU configuration.
5. The uncore PMU driver enforces availability and counter restrictions on the target hardware.

The records are ordered by hardware topic: clock, credits, ring channel usage, receive-ring state, then transmit-ring pressure.

## State and Persistence Behavior

The only persistent state is the checked-in JSON event mapping. It defines stable perf aliases and hardware encodings. There is no local mutation, caching, or generated output in this source file.

All events are package scoped (`PerPkg: "1"`), so measurements represent package-level uncore IO domains. This is important for interpretation on multi-socket systems and for tools that aggregate counts.

## Dependencies and Integration Points

This file depends on:

- perf's expected PMU JSON schema and generated table pipeline.
- Jaketown R2PCIe hardware event encodings.
- The runtime uncore PMU implementation that recognizes R2PCIe units.
- Related R3QPI and QPI definitions in `uncore-interconnect.json`, because cross-unit diagnostics often compare IO-facing and QPI-facing ring pressure.

Its most important integration point is the `Unit` string. If `R2PCIe` does not match the generated/runtime PMU naming convention, all aliases in this file become undiscoverable or unprogrammable even if the event codes are correct.

## Risks and Edge Cases

- Two records omit `UMask` (`UNC_R2_CLOCKTICKS` and possibly another simple selector), so schema validation must allow intentional mask absence.
- TxR full/not-empty records use only counter `0`; scheduling them like the broader ring events would be incorrect.
- The credit events distinguish DRS, NCB, and NCS by unit mask. Copy/paste mistakes in those masks would produce plausible but wrong measurements.
- `PerPkg` package scope can surprise users expecting per-core IO attribution.
- Names are public perf aliases. Renaming `UNC_R2_*` entries breaks user scripts and dashboards.

## Test Signals

- `jq` should parse the file as 36 objects with 36 unique `EventName` values.
- Every record should have `Unit == "R2PCIe"` and `PerPkg == "1"`.
- Counter lists should be checked by family: clock/ring events permit `0,1,2,3`, credit and NACK events mostly `0,1`, and TxR cycle pressure events `0`.
- Generated pmu-events tables should build without warnings.
- On supported hardware, `perf list` should show `UNC_R2_CLOCKTICKS`, a credit event, a ring event, and a TxR pressure event.
- A runtime smoke test can use `perf stat -e UNC_R2_CLOCKTICKS` plus one restricted counter event to catch parser or unit-name regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-io.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-memory.json

## Purpose

`uncore-memory.json` defines 51 Jaketown integrated memory controller (`iMC`) uncore PMU events. These records let perf users observe DRAM command traffic, memory-controller modes, power states, throttling, refresh behavior, ECC correctable errors, read/write pending queue pressure, precharge behavior, and queue hit activity.

The file is the memory-controller event catalog for the Jaketown platform. It is declarative, but it forms the stable event alias and encoding API used by perf.

## Important API Surface and Data Shape

The file is a JSON array of 51 unique objects. Common keys are `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, `Unit`, and often `UMask` and `PublicDescription`.

All records use `Unit: "iMC"` and `PerPkg: "1"`. All visible counter lists allow `0,1,2,3`.

Important event families:

- Command counters: `UNC_M_ACT_COUNT`, `UNC_M_CAS_COUNT.*`, `UNC_M_DRAM_PRE_ALL`, and `UNC_M_PRE_COUNT.*`.
- CAS breakdowns: `UNC_M_CAS_COUNT.RD`, `RD_REG`, `RD_UNDERFILL`, `WR`, `WR_RMM`, `WR_WMM`, and `ALL`, all sharing event code `0x4` with different masks.
- DRAM maintenance and reliability: `UNC_M_DRAM_REFRESH.HIGH`, `UNC_M_DRAM_REFRESH.PANIC`, and `UNC_M_ECC_CORRECTABLE_ERRORS`.
- Controller mode occupancy: `UNC_M_MAJOR_MODES.ISOCH`, `PARTIAL`, `READ`, and `WRITE`.
- Power behavior: channel DLL off, precharge power-down, CKE cycles per rank, critical throttle cycles, self refresh, and throttle cycles per rank.
- Queue pressure: read pending queue cycles full/not-empty, inserts, occupancy; write pending queue cycles full/not-empty, inserts, occupancy; WPQ read/write hit.
- Preemption events: read-preempt-read and read-preempt-write.

## Control Flow

There is no executable control flow. Externally:

1. perf's pmu-events generator reads the JSON array.
2. It converts each `UNC_M_*` object into generated event table rows.
3. Runtime CPU matching selects the Jaketown table.
4. perf exposes the aliases in `perf list`.
5. User-selected aliases are translated into iMC PMU event codes and masks, then programmed on available memory-controller counters.

The file groups related masks together, especially CAS and rank-specific power/throttle events, making manual review easier and reducing accidental cross-family drift.

## State and Persistence Behavior

The file persists static hardware metadata. It does not mutate state or hold runtime measurements. The actual PMU counts are hardware state outside the repository.

Package scoping through `PerPkg: "1"` means measurements are package/socket-level uncore observations. On platforms with multiple memory controllers or channels, users and tooling must account for aggregation semantics supplied by perf and the kernel uncore driver.

## Dependencies and Integration Points

This source depends on:

- perf's PMU event JSON schema.
- Jaketown iMC event encodings, masks, and rank semantics.
- Generated C event tables in the perf build.
- The kernel/perf uncore iMC PMU support for this CPU family.

It integrates with other Jaketown uncore files for whole-system bottleneck analysis. For example, `uncore-memory.json` queue occupancy and CAS counts can be interpreted alongside QPI/R2/R3 interconnect events from the adjacent JSON files.

## Risks and Edge Cases

- Seven CAS records lack `PublicDescription` and rely only on `BriefDescription`; generated help remains useful but less detailed.
- Eighteen records omit `UMask`; this is expected for simple selector events but should be schema-validated.
- `UNC_M_CLOCKTICKS` lacks `EventCode`, so parser defaults and clock-event handling must remain compatible.
- Rank-specific events (`RANK0` through `RANK7`) are repetitive. A copied event code or rank mapping error would be difficult to detect from syntax alone.
- Several power/throttle families use nearby event codes and identical counter lists; semantic regressions may only appear under hardware validation.
- `UNC_M_CAS_COUNT.ALL` has a brief description that mentions write CAS despite the name implying combined read/write CAS. This may be inherited vendor text, but it is a documentation ambiguity worth preserving or correcting only against authoritative hardware docs.

## Test Signals

- `jq` parse succeeds and reports 51 unique event names.
- Every record has `Unit == "iMC"` and `PerPkg == "1"`.
- CAS family masks should be checked for expected bit combinations: read regular/underfill and write read-major/write-major modes compose into broader read/write/all aliases.
- Rank families should contain exactly RANK0 through RANK7 for both CKE and throttle cycles.
- Generated pmu-events code should build without warnings.
- On supported hardware, representative smoke tests should include `UNC_M_ACT_COUNT`, `UNC_M_CAS_COUNT.RD`, `UNC_M_RPQ_OCCUPANCY`, and one rank-specific power event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-power.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-power.json

## Purpose

`uncore-power.json` defines 39 Jaketown package control unit (`PCU`) uncore PMU events. These events expose package power-management behavior: PCU clockticks, per-core C-state transition cycles, demotions, frequency band residency, frequency/voltage transition cycles, maximum-frequency limit reasons, memory phase shedding, core C-state occupancy, PROCHOT cycles, and VR-hot cycles.

The file supplies perf's public `UNC_P_*` event aliases for package power and thermal diagnostics on Jaketown systems.

## Important API Surface and Data Shape

The file is a JSON array of 39 unique objects. Common keys are `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, `PublicDescription`, and `Unit`. Unlike most neighboring files, none of these records use `UMask`; the core C-state occupancy records use a `Filter` field instead.

All records use `Unit: "PCU"` and `PerPkg: "1"`. Counter lists allow `0,1,2,3`.

Important event families:

- `UNC_P_CLOCKTICKS`: PCU pclk cycles.
- `UNC_P_CORE{0..7}_TRANSITION_CYCLES`: per-core C-state transition cycles.
- `UNC_P_DEMOTIONS_CORE{0..7}`: per-core demotion events.
- `UNC_P_FREQ_BAND{0..3}_CYCLES`: cycles spent in selected frequency bands.
- Max/min/frequency controls: `UNC_P_FREQ_MAX_CURRENT_CYCLES`, `MAX_LIMIT_THERMAL`, `MAX_OS`, `MAX_POWER`, `MIN_IO_P`, `MIN_PERF_P`, and `FREQ_TRANS_CYCLES`.
- Voltage controls: increase/decrease/change transition cycles.
- Package pressure indicators: memory phase shedding, internal/external PROCHOT, total transition cycles, and VR hot.
- `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`, `.CORES_C3`, and `.CORES_C6`: event code `0x80` differentiated by `Filter` values `occ_sel=1`, `occ_sel=2`, and `occ_sel=3`.

## Control Flow

No code executes inside the file. External control flow:

1. perf's pmu-events tooling parses the JSON.
2. Generated event tables include PCU event rows and filter metadata.
3. Runtime perf CPU matching selects the Jaketown table.
4. `perf list` exposes `UNC_P_*` aliases.
5. When a user selects an alias, perf encodes the event code and any filter into a PCU uncore PMU configuration.

The `Filter` field is the most notable control input. It changes the occupancy selector for the shared `0x80` event code, so generator/runtime support for filter strings is required.

## State and Persistence Behavior

The file persists static mappings from public names to PCU PMU encodings. It has no mutable state and no local persistence beyond source control.

All records are package scoped. Counts describe package/PCU power-management behavior and should not be interpreted as per-thread execution. Per-core event names identify core indexes as observed by the PCU, not local thread state.

## Dependencies and Integration Points

Dependencies include:

- perf pmu-events JSON parser support for uncore `Unit` and `Filter`.
- Jaketown PCU hardware event codes and occupancy selectors.
- Runtime uncore PCU PMU support in the kernel/perf stack.
- Adjacent memory and interconnect event catalogs for correlated power/performance analysis.

The `Filter` integration point is important: if filters are dropped during generation, all three `UNC_P_POWER_STATE_OCCUPANCY.*` aliases would collapse to the same event encoding.

## Risks and Edge Cases

- The file intentionally omits `UMask` on all 39 records. Consumers must not require `UMask` for PCU events.
- `UNC_P_CLOCKTICKS` and `UNC_P_FREQ_TRANS_CYCLES` omit `EventCode`, so defaults or special handling need validation.
- The three occupancy records share the same brief/public text saying "Number of cores in C0" even for `CORES_C3` and `CORES_C6`; the `Filter` distinguishes the actual selector, but generated help text is misleading.
- Core-indexed families must stay complete for cores 0 through 7. Missing one core or swapping event codes would skew diagnostics.
- Power/thermal events often depend on platform firmware behavior, so hardware smoke tests can be noisy or workload-dependent.

## Test Signals

- `jq` parse succeeds and reports 39 unique event names.
- Every record has `Unit == "PCU"` and `PerPkg == "1"`.
- No record requires `UMask`; tests should assert parser tolerance for PCU records without masks.
- The occupancy family should have exactly three aliases with `Filter` values `occ_sel=1`, `occ_sel=2`, and `occ_sel=3`.
- Generated pmu-events code should retain filter metadata.
- On supported hardware, `perf list` should show PCU aliases, and smoke tests should include `UNC_P_CLOCKTICKS`, a frequency-band event, and an occupancy event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-power.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/virtual-memory.json

## Purpose

`virtual-memory.json` defines 16 core PMU events for Jaketown virtual-memory and TLB behavior. Unlike the uncore files in this work item, these records describe core events: DTLB load/store misses, ITLB misses, EPT walk cycles, ITLB flushes, and TLB flush attempts.

The file supplies user-facing perf aliases for diagnosing page-walk cost, STLB hit behavior, instruction/data TLB pressure, virtualization EPT walks, and TLB flush activity.

## Important API Surface and Data Shape

The file is a JSON array of 16 unique event objects. Keys are:

- `EventName`: public alias such as `DTLB_LOAD_MISSES.WALK_DURATION`.
- `EventCode`: core PMU event select code.
- `UMask`: unit mask variant.
- `Counter`: allowed core counters, consistently `0,1,2,3`.
- `SampleAfterValue`: default sampling period hint, consistently `2000003`.
- `BriefDescription` and sometimes `PublicDescription`.

Unlike the uncore files, there is no `Unit` or `PerPkg` field. These are ordinary core PMU events selected by CPU model.

Event families:

- `DTLB_LOAD_MISSES.*`: load-side TLB miss page walks, completed walks, walk duration, and STLB hits.
- `DTLB_STORE_MISSES.*`: store-side equivalents.
- `ITLB_MISSES.*`: instruction TLB miss page walks, completed walks, walk duration, and STLB hits.
- `EPT.WALK_CYCLES`: extended page table walk cycles for virtualization.
- `ITLB.ITLB_FLUSH`: instruction TLB flushes.
- `TLB_FLUSH.DTLB_THREAD` and `TLB_FLUSH.STLB_ANY`: DTLB and STLB flush attempts.

## Control Flow

There is no executable control flow. External flow:

1. perf's pmu-events generator reads the Jaketown core event JSON files.
2. Event records become generated table entries keyed by CPU model.
3. Runtime perf exposes aliases via `perf list`.
4. `perf stat`/`perf record` resolves aliases into core PMU `EventCode` plus `UMask`.
5. For sampling, `SampleAfterValue` provides the default period hint used by generated event metadata.

The family grouping mirrors the way users reason about memory translation: data load/store TLB behavior first, then virtualization and instruction-side events, then flushes.

## State and Persistence Behavior

The file persists static core PMU alias metadata. It has no runtime state. Counts and samples are collected by hardware PMU counters during perf sessions and are not persisted by this JSON file.

The absence of `PerPkg` is meaningful: these are core PMU events, not package-level uncore events. Aggregation semantics depend on perf's selected CPU/thread scope.

## Dependencies and Integration Points

Dependencies include:

- perf's core PMU event JSON schema.
- Jaketown/Sandy Bridge core PMU event encodings for TLB and EPT events.
- Generated perf event tables and CPU-model matching.
- Runtime PMU programming support for counters `0,1,2,3`.

This file integrates with memory and uncore PMU files during performance diagnosis. For example, high `DTLB_*WALK_DURATION` can be correlated with memory-controller queue pressure from `uncore-memory.json`, but the event domains and aggregation scopes differ.

## Risks and Edge Cases

- Thirteen records omit `PublicDescription`, so generated long help relies heavily on brief text.
- All events have `SampleAfterValue`; a parser regression that treats this as mandatory elsewhere could affect files that do not provide it.
- Event code reuse is extensive: load DTLB variants share `0x08`, store DTLB variants share `0x49`, ITLB miss variants share `0x85`, and TLB flush variants share `0xBD`. Correct `UMask` preservation is critical.
- The `EPT.WALK_CYCLES` description is virtualization-specific; users may misinterpret it as ordinary page-walk duration.
- Because these are core events, adding uncore fields such as `Unit` or `PerPkg` would be wrong and could confuse generated table handling.

## Test Signals

- `jq` parse succeeds and reports 16 unique event names.
- Every object has `EventCode`, `UMask`, `Counter`, `EventName`, and `SampleAfterValue`.
- No object should have `Unit` or `PerPkg`.
- Family masks should remain distinct for walk-causing misses, completed walks, walk duration, and STLB hits.
- Generated pmu-events code should build without warnings.
- Runtime smoke tests on supported hardware can use `perf stat -e DTLB_LOAD_MISSES.WALK_DURATION,ITLB_MISSES.STLB_HIT,TLB_FLUSH.STLB_ANY` on a small workload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/virtual-memory.json -->
