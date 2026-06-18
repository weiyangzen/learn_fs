# subset-b-006718 Research

Grouped research for Linux perf PMU event-map JSON files under the Ceph client copy of `tools/perf/pmu-events/arch/x86`. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/uncore-io.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/uncore-io.json

## Purpose
Defines the Sierra Forest uncore I/O PMU event catalog for Linux perf. The file is a 168-entry JSON array of `UNC_IIO_*` events consumed by the perf PMU events table generator and runtime event resolver so users can select named Integrated I/O events instead of programming raw event selectors manually.

## Important APIs, Types, And Event Groups
The data contract is the perf PMU event JSON object schema. Every entry carries `EventName`, `EventCode`, `BriefDescription`, `Counter`, `PerPkg`, `PortMask`, and `Unit`; most entries also carry `UMask`, `FCMask`, and optional `Experimental` or `Deprecated` flags. `Unit` is consistently `IIO`, which routes aliases to the uncore IIO PMU rather than core PMU counters. `PerPkg: "1"` identifies package-scoped counting. `Counter` lists allowed programmable counter slots, generally `0,1,2,3`.

The event surface covers IIO clockticks, completion-buffer inserts and occupancy, data and transaction requests by CPU and of CPU, IOMMU activity for multiple IOMMU blocks, outstanding request counters, target-split request counts, and posted-write-table occupancy. The file uses repeated event-name suffixes such as `.PART0` through `.PART7`, `.ALL_PARTS`, `.READ`, `.WRITE`, `.ALLOC`, `.DEALLOC`, `.ATS_*`, and target classes to expose hardware filters as separate perf aliases.

## Control Flow
There is no executable control flow in the file. At build time, perf tooling parses the JSON array, validates known fields, and emits event table data. At runtime, perf resolves an alias such as `UNC_IIO_COMP_BUF_INSERTS.CMPD.PART3` into the encoded selector fields: event code, umask/filter fields, port mask, counter mask, and the `IIO` PMU unit. The user's measurement flow is therefore declarative: select alias, perf maps it to the matching uncore PMU, and the kernel driver programs hardware counters with the encoded fields.

## State And Persistence
The file persists static hardware event metadata in the repository. It does not read or write runtime state. When compiled into perf, the aliases become part of perf's generated PMU event tables; live counter values are held only by kernel perf events and hardware PMU registers during a measurement session. The `Deprecated` marker on the misspelled `UNC_IIO_NUM_OUSTANDING_REQ_FROM_CPU` entry preserves compatibility while steering users toward the correctly spelled alias.

## Dependencies And Integration Points
The file depends on perf's JSON PMU schema and on Sierra Forest uncore IIO PMU support in the Linux kernel. It integrates with sibling Sierra Forest event files through the architecture/mapfile selection mechanism, where CPU identification chooses this directory's catalogs. The `PortMask` and `FCMask` fields are especially important integration points because they exercise uncore-specific encodings not present in simple core event files.

## Risks
Encoding drift is the main risk: a wrong `EventCode`, `UMask`, `PortMask`, or `FCMask` silently produces misleading performance data. Repeated partition aliases increase copy/paste risk, especially where `.ALL_PARTS` uses a broad mask and individual parts use single-bit masks. `Experimental` events may reflect less stable hardware documentation. Alias spelling compatibility is another risk because changing or removing the deprecated misspelled event could break existing perf scripts.

## Test Signals
Useful tests include `jq empty` JSON validation, perf PMU event table generation, and `perf list` checks on a Sierra Forest-capable build to confirm aliases appear under the IIO unit. Runtime smoke tests should try representative clocktick, completion-buffer, data-request, IOMMU, outstanding-request, and occupancy aliases and verify that perf can open the event on supported hardware without raw encoding errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/uncore-io.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/uncore-memory.json

## Purpose
Defines the Sierra Forest integrated memory controller PMU event catalog for perf. The 90-entry JSON array describes `UNC_M_*` aliases for DRAM command activity, memory queue inserts and occupancy, read/write CAS counts by subchannel, self-refresh, power-down, MR4 thermal refresh behavior, and memory throttling.

## Important APIs, Types, And Event Groups
The public contract is perf's PMU event JSON schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, `PerPkg`, and `Unit`. `Unit` is consistently `IMC`, routing events to integrated memory controller uncore PMUs, and `Counter` generally allows counters `0,1,2,3`. `PublicDescription` appears on selected entries where extra user-facing explanation is needed. Roughly half the entries are marked `Experimental`.

Major groups include `UNC_M_ACT_COUNT` for activate commands, `UNC_M_CAS_COUNT_SCH0` and `UNC_M_CAS_COUNT_SCH1` for read/write CAS operations per subchannel, `UNC_M_PRE_COUNT` for precharge operations, `UNC_M_RPQ/WPQ/RDB_INSERTS` and occupancy events for request/write/read-data buffers, `UNC_M_POWERDOWN_CYCLES`, `UNC_M_SELF_REFRESH`, `UNC_M_MR4_2XREF_CYCLES`, `UNC_M_PDC_MR4ACTIVE_CYCLES`, and throttle-level counters such as low/mid/high/critical cycles.

## Control Flow
The file has declarative parse-time flow only. Perf's build pipeline reads the array, turns each object into an event table row, and preserves event names as aliases. During a measurement, perf maps an alias to the IMC PMU and passes event code and mask fields to kernel perf. Subchannel and command-class distinctions are encoded as separate aliases rather than runtime branches.

## State And Persistence
The persistent state is static event metadata. The file does not store measurement results. At runtime, state lives in per-PMU kernel event descriptors and hardware IMC counters. Package and channel topology determine how many IMC PMU instances can be opened by perf; this JSON only supplies alias metadata.

## Dependencies And Integration Points
This catalog depends on Sierra Forest IMC PMU kernel support and perf's generated event table infrastructure. It integrates with platform topology because `IMC` events are uncore and package/channel scoped, not thread scoped. It also integrates with perf expression and listing paths through descriptive fields, letting users discover memory-controller aliases by category and event name.

## Risks
The biggest correctness risk is mismatching command class masks, especially in dense CAS subchannel families where read, write, underfill, auto-precharge, and regular variants differ only by `UMask`. Experimental thermal, throttling, and queue occupancy events may have caveats or changing documentation. Users can misinterpret occupancy events as transaction counts; reports should distinguish count events from cycle/occupancy events.

## Test Signals
Validate JSON syntax with `jq empty` and generated perf table builds. On supported hardware, `perf list` should expose `UNC_M_*` aliases under IMC. Runtime checks should open representative activate, CAS read/write, queue insert, queue occupancy, self-refresh, and throttle events. Cross-checking read/write CAS counters against memory bandwidth workloads is a practical semantic signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/uncore-power.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/uncore-power.json

## Purpose
Defines Sierra Forest package control unit power-management PMU events for perf. The 11-entry JSON array exposes `UNC_P_*` aliases for PCU clockticks, thermal/power frequency limits, frequency transition cycles, package C-state residency, core C-state occupancy, and PROCHOT throttling sources.

## Important APIs, Types, And Event Groups
Each object follows the perf PMU event schema with `EventName`, `EventCode`, `BriefDescription`, `PublicDescription`, `Counter`, `PerPkg`, and `Unit`. `Unit` is `PCU`, `Counter` allows slots `0,1,2,3`, and `PerPkg: "1"` marks package scope. Several entries carry `Experimental: "1"`, including thermal/power limit and package C-state residency events.

Important aliases include `UNC_P_CLOCKTICKS` as a fixed-rate PCU time base, `UNC_P_FREQ_MAX_LIMIT_THERMAL_CYCLES`, `UNC_P_FREQ_MAX_POWER_CYCLES`, `UNC_P_FREQ_TRANS_CYCLES`, `UNC_P_PKG_RESIDENCY_C2E_CYCLES`, `UNC_P_PKG_RESIDENCY_C6_CYCLES`, `UNC_P_POWER_STATE_OCCUPANCY_CORES_C0/C3/C6`, and internal/external PROCHOT cycle counters.

## Control Flow
The file is data-only. Perf's event-table generator parses it into aliases; perf runtime resolves a selected alias to a PCU uncore event selector. The descriptions encode intended analysis flow: use clockticks as a constant-rate denominator, compare frequency limit or PROCHOT cycles against elapsed PCU cycles, and combine occupancy/residency events with thresholding or edge detect where supported.

## State And Persistence
No local runtime state is persisted by this JSON. The repository persists hardware metadata. Measurement state is maintained by perf event file descriptors, the kernel PCU PMU driver, and hardware counters while a profiling session is active. PCU clockticks are described as a fixed 1 GHz pclk counter, making them useful for wall-time normalization.

## Dependencies And Integration Points
The file depends on Sierra Forest PCU uncore PMU support and perf's architecture-specific map selection. It integrates with power and thermal analysis workflows where perf counters are correlated with workload phases, C-state residency, and throttling behavior. It also complements IMC and IIO uncore files by covering package-management state rather than traffic counts.

## Risks
These counters are easy to misread as per-core metrics even though they are package-scoped. Residency events exclude transition times, and occupancy events measure number of cores in a state over time rather than entry counts unless threshold or edge features are applied externally. Experimental flags mean the exact semantics may need hardware-documentation confirmation.

## Test Signals
JSON validation and perf event-table generation are basic tests. On Sierra Forest systems, `perf list` should show PCU aliases and `perf stat` should open `UNC_P_CLOCKTICKS` plus at least one residency, occupancy, frequency-limit, and PROCHOT event. Sanity checks include nonzero clockticks during measurement and plausible increases in throttling counters only under induced thermal or power pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/uncore-power.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/virtual-memory.json

## Purpose
Defines Sierra Forest core virtual-memory PMU aliases for perf. The 17-entry JSON array covers demand-load, store, and instruction-side TLB misses, second-level TLB hits, page-walk completion by page size, pending page-walk cycles, and a retirement stall event tied to DTLB misses.

## Important APIs, Types, And Event Groups
Objects use the core perf PMU event schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and optional `SampleAfterValue`. Unlike the uncore Sierra Forest files, there is no `Unit` because these are core PMU events. Event groups include `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, `ITLB_MISSES.*`, and `LD_HEAD.DTLB_MISS_AT_RET`.

The aliases distinguish STLB hits from page walks, aggregate walk-completed masks from page-size-specific masks, and pending-walk cycle events from completed-walk counts. Load and store families use different event codes (`0x08` and `0x49`), while instruction-side events use `0x85`.

## Control Flow
Perf consumes the file declaratively. During build, entries are transformed into alias table rows. During runtime, selecting a virtual-memory alias programs a core PMU counter with the event code and umask. Analysis control flow is left to the user: compare STLB-hit counts with page-walk counts, split load/store/instruction behavior, and use pending-cycle events to estimate walk pressure.

## State And Persistence
The JSON persists static alias definitions only. Runtime state is per-process, per-CPU, or system-wide depending on the perf command used. Hardware counters hold counts during an active session; perf stores results in command output or `perf.data`, not in this file.

## Dependencies And Integration Points
The file depends on Sierra Forest core PMU support and perf's x86 PMU event-map mechanism. It integrates with broader perf workflows for page-size tuning, TLB pressure analysis, and front-end versus data-side stall attribution. It complements cache and memory-controller event files by explaining address-translation costs before memory/cache access.

## Risks
Some brief descriptions are terse and one entry says `DTLB_STORE_MISSES.WALK_COMPLETED` counts misses to a 1G page despite its aggregate `0xe` mask, so documentation review is needed before relying on that wording. Pending-walk events count outstanding walks per cycle, not completed walks. Aggregated aliases can double count if summed with page-size-specific aliases from the same event group.

## Test Signals
Tests include `jq empty`, perf table generation, and `perf list` visibility for each alias. Runtime smoke tests can run TLB-stressing workloads with small and huge pages and verify that 4K versus 2M/4M walk aliases move in expected directions. Sampling tests should verify `SampleAfterValue` handling where present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/cache.json

## Purpose
Defines Silvermont cache, memory-uop, offcore-response, queue-rejection, and related core PMU aliases for perf. The 77-entry JSON array gives users named events for L1/L2 behavior, load/store retirement, cross-core HITM, instruction-cache fill stalls, offcore response filters, and REHABQ activity.

## Important APIs, Types, And Event Groups
The file uses perf's event JSON schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and optional `PEBS`, `MSRIndex`, and `MSRValue`. It does not specify `Unit`, so aliases target the Silvermont core PMU. `SampleAfterValue` is present on all entries, and `PEBS` appears on memory-uop events that support precise sampling.

Major groups are `LONGEST_LAT_CACHE.*`, `MEM_UOPS_RETIRED.*`, `FETCH_STALL.ICACHE_FILL_PENDING_CYCLES`, `CORE_REJECT_L2Q.ALL`, `L2_REJECT_XQ.ALL`, `REHABQ.*`, and a large `OFFCORE_RESPONSE.*` family. Offcore-response aliases share event code `0xB7` and umask `0x1` but use `MSRIndex` and `MSRValue` to program the dedicated offcore response MSR with request and response filters.

## Control Flow
Control flow is declarative but has an important offcore programming path. Perf parses each JSON object into an alias; for normal aliases it programs event select and umask fields. For offcore aliases, perf must also write the encoded `MSRValue` to the specified `MSRIndex` so the hardware filters request type and response class correctly. Runtime measurement flow depends on whether the selected alias is simple, PEBS-capable, or offcore-MSR-backed.

## State And Persistence
The file persists static alias metadata. Runtime state includes programmed core PMU counters and, for offcore events, dedicated MSR filter state associated with the event. PEBS-capable aliases may produce precise sample records in perf sampling mode. No results are written back to the JSON.

## Dependencies And Integration Points
This catalog depends on Silvermont core PMU support, perf's PMU alias parser, and perf/kernel support for offcore response MSR programming. It integrates with the `counter.json` file because Silvermont has only two generic counters, making scheduling conflicts likely when many cache/offcore events are requested together. It also interacts with PEBS sampling paths for precise retired memory-uop events.

## Risks
The dense offcore family is high risk because many aliases differ only by `MSRValue`; a single wrong bit changes the request or response filter while leaving the alias syntactically valid. Offcore events also need compatible counter/MSR handling, so multiplexing and unsupported combinations can surprise users. PEBS flags need to match hardware capability. Count semantics vary: references, misses, retired uops, queue rejects, and cycles should not be combined without normalization.

## Test Signals
Use `jq empty` and perf table-generation tests for syntax/schema coverage. `perf list` should show the aliases, including offcore variants. Runtime smoke tests should open a simple cache event, a PEBS memory-uop event, and an offcore response event; offcore tests should confirm that perf accepts the MSR-backed alias and does not fall back to an unfiltered raw event. Workloads with cache misses and cross-core sharing can validate directional behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/counter.json

## Purpose
Declares the Silvermont PMU counter inventory for perf. The one-object JSON array states that the `core` PMU has four fixed counters and two generic programmable counters.

## Important APIs, Types, And Event Groups
The schema is the perf counter-description JSON object: `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. `Unit: "core"` binds the declaration to the core PMU. `CountersNumFixed: "4"` and `CountersNumGeneric: "2"` inform perf tooling and generated metadata about the hardware counter capacity available for Silvermont events.

## Control Flow
The file contains no branches or executable logic. Perf tooling parses it as metadata alongside the event catalogs. Runtime scheduling decisions happen in perf and the kernel, where the number of fixed and generic counters constrains how many events can be programmed without multiplexing.

## State And Persistence
The persistent state is static hardware-capacity metadata. It does not change at runtime and does not store counter values. Live event scheduling state belongs to perf event descriptors and kernel PMU context management.

## Dependencies And Integration Points
This file integrates with all Silvermont event catalog files in the same directory. It is especially relevant for events in `cache.json`, `pipeline.json`, and virtual-memory files because only two generic counters mean many user-selected combinations will require multiplexing unless fixed counters can be used.

## Risks
If the fixed or generic counter counts are wrong, perf may present misleading scheduling expectations or generate incorrect metadata. The small generic-counter count is also an operational risk for analysis: users comparing many aliases at once may see multiplexed scaled counts rather than simultaneously measured counters.

## Test Signals
Validate JSON syntax and generated perf metadata. On Silvermont hardware or emulation with matching PMU support, `perf stat` with more than two generic events should reveal multiplexing behavior, while fixed events such as retired instructions and unhalted cycles should use fixed counter paths where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/floating-point.json

## Purpose
Defines the Silvermont floating-point assist event exposed to perf. The one-entry JSON array maps `MACHINE_CLEARS.FP_ASSIST` to the PMU encoding used to count stalls due to floating-point assists.

## Important APIs, Types, And Event Groups
The object uses perf's core event schema: `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. The event is encoded as event code `0xC3` with umask `0x4`, sharing the broader machine-clear event family with memory-ordering, self-modifying-code, and all-clears entries in sibling files.

## Control Flow
Perf parses the single alias at build time and resolves it at runtime to a core PMU event. There is no in-file execution. In analysis, users select the alias to attribute stall or clear activity to FP assists rather than to other machine-clear causes.

## State And Persistence
The file persists only the alias metadata. Runtime counts are maintained by hardware and perf event state during measurement. Sampling behavior is controlled by `SampleAfterValue` and perf command options, not by any mutable state in this file.

## Dependencies And Integration Points
It depends on Silvermont core PMU support and perf's event-table infrastructure. It integrates with `pipeline.json` because that file defines other `MACHINE_CLEARS.*` aliases using the same event code, and with floating-point performance investigations where FP assist counts are correlated with instruction mixes and exception/denormal behavior.

## Risks
The main risk is semantic isolation: counting FP assists as machine clears may be confused with all machine clears if users also select aggregate events. Because this is a single specialized event, an incorrect umask would remove most of the file's value while remaining syntactically valid.

## Test Signals
Use JSON validation and perf list generation. Runtime validation requires a Silvermont target and a workload likely to trigger FP assists, such as denormal or exceptional floating-point operations, then checking that this alias moves independently from aggregate machine-clear counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/frontend.json

## Purpose
Defines Silvermont front-end PMU aliases for perf. The eight-entry JSON array covers branch-address clears, decode restriction due to wrong predecode length prediction, instruction-cache accesses/hits/misses, and microcode-sequencer entry from the front-end complex.

## Important APIs, Types, And Event Groups
The file uses perf's core PMU schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. Event groups are `BACLEARS.*`, `DECODE_RESTRICTION.PREDECODE_WRONG`, `ICACHE.*`, and `MS_DECODED.MS_ENTRY`. The branch-address-clear aliases share event code `0xE6` with different masks for all, conditional, and return-related clears.

## Control Flow
There is no executable flow. Perf table generation converts entries into named aliases. Runtime perf selection programs the core PMU with the relevant event code and umask. User analysis flow is usually hierarchical: start with aggregate front-end stalls or instruction-cache misses, then narrow to BACLEARS, wrong predecode, or microcode flow entries.

## State And Persistence
This JSON stores static event definitions only. Runtime count and sampling state belongs to perf and hardware counters. Instruction-cache hit/miss/access counts persist only in perf output or recorded perf data when explicitly collected.

## Dependencies And Integration Points
The file depends on Silvermont core PMU support and integrates with `other.json`, which includes fetch stall aliases for all reasons and ITLB pending cycles, and with `cache.json`, which has `FETCH_STALL.ICACHE_FILL_PENDING_CYCLES`. Together these files let users distinguish front-end redirection, decode, icache, and ITLB-related pressure.

## Risks
The branch-address-clear events are speculative or front-end oriented and should not be treated as retired branch counts. Instruction-cache access/hit/miss masks are simple but easy to double count if users add aggregate and component aliases. Microcode entry counts can include fault or assist-inserted flows, so interpretation requires workload context.

## Test Signals
Run JSON validation and perf table-generation checks. On Silvermont, `perf list` should expose all eight aliases. Runtime smoke tests can use branch-heavy code, instruction-cache-sensitive loops, and code paths that trigger microcode assists to verify that related aliases respond in expected directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/memory.json

## Purpose
Defines a Silvermont memory-ordering machine-clear alias for perf. The one-entry JSON array maps `MACHINE_CLEARS.MEMORY_ORDERING` to the PMU encoding for stalls due to memory ordering.

## Important APIs, Types, And Event Groups
The object follows perf's core event schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. It uses event code `0xC3` and umask `0x2`, placing it in the same machine-clear family as FP assist and self-modifying-code/all-clears events from sibling Silvermont files.

## Control Flow
The file is parsed by perf's event tooling and exposes one alias. At runtime, selecting the alias programs the core PMU with the machine-clear memory-ordering filter. Analysis flow is to correlate this event with memory-order-sensitive code patterns, store/load ordering, and aggregate machine-clear counts.

## State And Persistence
Only static alias metadata is persisted. Runtime counter state is held by hardware and perf event contexts. Results are external to the JSON file.

## Dependencies And Integration Points
It depends on Silvermont core PMU support and integrates with `pipeline.json` and `floating-point.json`, which define related machine-clear causes. It also complements cache and virtual-memory files because memory ordering stalls can be mistaken for memory hierarchy latency if measured without cause-specific clear events.

## Risks
The single-entry file is highly sensitive to umask correctness. Users may over-attribute performance loss to memory ordering without comparing against aggregate machine clears and other stall signals. Because it is a stall/clear cause rather than a memory transaction count, it should not be normalized as bandwidth.

## Test Signals
Basic tests are JSON validation and perf list visibility. Runtime checks need workloads with known memory-ordering pressure and comparison against `MACHINE_CLEARS.ALL` where available. The event should remain near zero for simple independent arithmetic workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/other.json

## Purpose
Defines two miscellaneous Silvermont front-end fetch stall aliases for perf. The events count cycles in which code fetch is stalled for any reason or due to an outstanding ITLB fill.

## Important APIs, Types, And Event Groups
Both objects use the core perf event schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. `FETCH_STALL.ALL` uses event code `0x86` and umask `0x3f` for all code-fetch stall reasons. `FETCH_STALL.ITLB_FILL_PENDING_CYCLES` uses the same event code with umask `0x2` for outstanding ITLB miss fill cycles.

## Control Flow
Perf consumes the file declaratively. The runtime path is a normal core PMU event selection, with no special MSR or uncore routing. Analysis typically starts from `FETCH_STALL.ALL` and compares it to more specific fetch-stall events in this file and sibling cache/frontend files.

## State And Persistence
The JSON persists static alias data only. Runtime counts are held by the PMU and perf event contexts. No local persistence occurs beyond generated perf tables and user-requested perf output.

## Dependencies And Integration Points
This file depends on Silvermont core PMU support. It integrates with `frontend.json` for branch/decode/icache activity, `cache.json` for `FETCH_STALL.ICACHE_FILL_PENDING_CYCLES`, and `virtual-memory.json` for page-walk and TLB events. Together they let users separate ITLB-related fetch stalls from icache fill and other front-end causes.

## Risks
`FETCH_STALL.ALL` is an aggregate event and can overlap conceptually with more specific aliases, so component counts should not be blindly summed with it. `ITLB_FILL_PENDING_CYCLES` counts cycles with outstanding ITLB fill, not completed walks. Interpretation needs correlation with page-walk and instruction-cache events.

## Test Signals
Use `jq empty`, perf table-generation tests, and `perf list` visibility. Runtime smoke tests can compare behavior on instruction-cache-friendly loops versus large-code-footprint or ITLB-stressing workloads; ITLB-specific cycles should rise with instruction-side translation pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/pipeline.json

## Purpose
Defines Silvermont pipeline, branch-retirement, clock, instruction-retirement, divider, machine-clear, allocation-stall, reservation-station-stall, and retired-uop aliases for perf. The 34-entry JSON array provides the core PMU vocabulary for high-level pipeline accounting and branch-misprediction analysis.

## Important APIs, Types, And Event Groups
The file uses perf's core event schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and optional `PEBS`. Some fixed-counter aliases omit `EventCode` and use `UMask` values that identify fixed counter slots, such as `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.CORE`, and `CPU_CLK_UNHALTED.REF_TSC`. Programmable aliases include branch retired/mispredicted families, divider busy cycles, machine clears, no-allocation cycles, reservation-station full stalls, and retired uops.

Important groups are `BR_INST_RETIRED.*`, `BR_MISP_RETIRED.*`, `CPU_CLK_UNHALTED.*`, `INST_RETIRED.*`, `CYCLES_DIV_BUSY.ALL`, `MACHINE_CLEARS.*`, `NO_ALLOC_CYCLES.*`, `RS_FULL_STALL.*`, and `UOPS_RETIRED.*`. Several retired branch and instruction events are marked `PEBS`, enabling precise sampling where supported.

## Control Flow
Perf parses the JSON into generated alias rows. At runtime, fixed-counter aliases route to fixed PMU counters while programmable aliases consume one of Silvermont's limited generic counters. PEBS-marked events may enter perf's precise sampling path. Analysis flow generally starts with cycles and instructions, then branches into branch mispredicts, allocation starvation, reservation-station fullness, divider pressure, machine clears, or uop retirement depending on bottleneck symptoms.

## State And Persistence
The JSON persists static event metadata. Runtime state is held by fixed counters, generic counters, PEBS buffers when sampling, and perf event contexts. Because `counter.json` declares only two generic counters, many combinations from this file cannot be measured simultaneously without multiplexing.

## Dependencies And Integration Points
This file depends on Silvermont core PMU support and integrates directly with `counter.json` for fixed/generic counter capacity. It also connects to `frontend.json` for branch-address and decode causes, `memory.json` and `floating-point.json` for machine-clear subcauses, and cache/virtual-memory files for memory-side bottleneck attribution.

## Risks
Fixed-counter aliases are structurally different from normal event-code aliases, so schema handling must preserve entries with missing `EventCode`. Aggregate and component relationships create double-counting hazards, such as all branches versus taken/JCC/call/return classes or all no-allocation cycles versus specific causes. Some descriptions are truncated or terse, so hardware documentation may be needed for exact semantics. PEBS flags must be accurate because false precision support can break sampling expectations.

## Test Signals
Tests include JSON validation, generated event table builds, and `perf list` inspection. Runtime smoke tests should open fixed counters, one branch retired event, one branch-mispredicted event, a no-allocation event, an RS-full event, and a PEBS-capable retired event. Multiplexing behavior should be checked when more than two programmable events are requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/virtual-memory.json

## Purpose
Defines Silvermont virtual-memory PMU aliases for perf. The seven-entry JSON array covers retired load uops that missed the DTLB and page-walk cycles/walk counts split between data side, instruction side, and aggregate I-side plus D-side behavior.

## Important APIs, Types, And Event Groups
The objects follow the core perf PMU schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, optional `PEBS`, and `Counter`. Event groups are `MEM_UOPS_RETIRED.DTLB_MISS_LOADS` and `PAGE_WALKS.*`. The page-walk aliases use event code `0x05` with masks `0x1`, `0x2`, and `0x3`; the same masks are exposed as both cycle-duration aliases and completed-walk aliases, relying on the event name and perf metadata to describe the intended interpretation.

## Control Flow
The file is declarative. Perf table generation creates aliases, and runtime selection programs normal Silvermont core PMU events. Analysis flow is to count load uops with DTLB misses, then compare page-walk cycles and walk counts by data side and instruction side. Aggregate `PAGE_WALKS.CYCLES`/`WALKS` should be used as totals rather than summed with their component aliases.

## State And Persistence
Static event metadata is persisted in the JSON. Runtime page-walk counts and cycle samples live only in perf event state and hardware counters. `PEBS` on `MEM_UOPS_RETIRED.DTLB_MISS_LOADS` means precise sampling may be available for identifying instructions causing DTLB-miss load uops.

## Dependencies And Integration Points
This file depends on Silvermont core PMU and PEBS support. It integrates with `other.json` through ITLB fetch-stall cycles, with `cache.json` through `MEM_UOPS_RETIRED.UTLB_MISS`, and with pipeline counters for cycles/instructions normalization. It is used in TLB and page-size tuning workflows.

## Risks
The page-walk aliases share event codes and masks between cycle and walk names, so consumers must verify that the underlying hardware and perf parser distinguish count modes as intended; otherwise the names may appear redundant. Aggregates overlap with I-side and D-side components. DTLB miss load events do not cover store or instruction-side misses, so broader virtual-memory analysis needs sibling events.

## Test Signals
Validate syntax and generated perf aliases. Runtime tests should run workloads with high data-side TLB pressure and instruction-side pressure separately, checking that D-side and I-side aliases respond differently. PEBS sampling on `MEM_UOPS_RETIRED.DTLB_MISS_LOADS` should produce precise attribution when the hardware and kernel support it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/virtual-memory.json -->
