# subset-b-006655 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/metricgroups.json

## Purpose

`metricgroups.json` is a static perf PMU metadata file for the x86 Emerald Rapids CPU model. It maps metric group names to human-readable descriptions so perf's generated event tables can present and filter related metrics by category. The file is not executable Ceph code; it is part of the vendored Linux `tools/perf` event database under the Ceph client source tree.

The file contains 143 JSON object entries. Most legacy-style group names, such as `Backend`, `Frontend`, `Pipeline`, `MemoryBound`, `Branches`, `PortsUtil`, `HPC`, and `Summary`, use the shared description `Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet`. Top-down groups `TopdownL1` through `TopdownL6` and `tma_L1_group` through `tma_L6_group` describe the hierarchy levels used by Intel Top-down Microarchitecture Analysis. The remaining `tma_*_group` keys describe contributors to specific TMA categories, such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, `tma_ports_utilization_group`, and `tma_retiring_group`.

## Important APIs, Types, and Data

The schema is a flat JSON object: each property key is a metric group identifier and each value is a display description string. There are no functions, classes, or runtime APIs in this file. The important contract is the key namespace consumed by perf's PMU event tooling and by metric definitions elsewhere in the same Emerald Rapids directory.

The group names act as references for metric categorization. Camel-case names preserve older or user-facing groups, while lowercase `tma_*` names align with generated top-down metric identifiers and issue categories. The descriptions are intentionally short because detailed formulas and event encodings live in the metric and event JSON files rather than in this group index.

## Control Flow

There is no local control flow. At build or runtime, perf's PMU event parser loads architecture/model JSON data, associates metrics with group names, and uses this file to resolve group descriptions for listing, filtering, and display. If a metric references one of these groups, this object supplies the group label text shown to users and tools.

## State and Persistence Behavior

The file is immutable source metadata. It does not persist runtime state, counters, or measurements. Its contents are compiled into or loaded by perf tooling as part of the CPU PMU event database. Any stateful behavior happens in perf's event parser and generated tables, not in this JSON file.

## Dependencies and Integration Points

This file depends on perf's PMU JSON schema and the Emerald Rapids event/metric set around it. It integrates with Linux `tools/perf/pmu-events` generators, the x86 CPU model mapping logic, `perf list`, `perf stat -M`, metric grouping, and top-down metric presentation. It also indirectly integrates with Intel's Top-down Microarchitecture Analysis taxonomy, since most group descriptions and names mirror that spreadsheet-driven hierarchy.

## Risks and Edge Cases

The file is schema-light, so typos are the primary risk. A misspelled group key can silently break grouping for metrics that expect the canonical name, or create duplicate-looking categories. Duplicate semantic names are also possible: for example, both `MachineClears` and `Machine_Clears` exist, as do `MemoryBW` and `Memory_BW`, so downstream consumers must treat keys as exact identifiers rather than normalized labels.

Because the descriptions are generic, they do not validate whether all referenced TMA groups actually have corresponding metrics. Drift between this file and metric definition files can leave stale groups in `perf list` or omit descriptions for new metrics. JSON object ordering may be preserved for readability in source, but consumers should not depend on it.

## Test Signals

Useful validation signals include `python3 -m json.tool` or an equivalent JSON parser, perf PMU event generation tests, `perf list --details` on Emerald Rapids mappings, and metric-group filtering checks that ensure each metric group referenced by metric definitions has a description here. Diffing this file against the upstream Linux perf Emerald Rapids copy is also a strong drift signal for this vendored source tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/other.json

## Purpose

`other.json` defines miscellaneous Emerald Rapids core PMU events that do not fit the more specific perf event category files. It contributes six event records to the Linux perf PMU event database: page-fault assists, hardware interrupt states, streaming-store offcore response counting, and uncore request queue full cycles.

This is declarative hardware counter metadata. It gives perf enough information to program counters and MSR filters for named events; it does not collect samples or implement counter logic itself.

## Important APIs, Types, and Data

The file is a JSON array of event objects following the perf PMU event schema. Common fields include `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. `XQ.FULL_CYCLES` also uses `CounterMask`; `OCR.STREAMING_WR.ANY_RESPONSE` uses `MSRIndex` and `MSRValue` to configure offcore response filtering.

The event families are:

- `ASSISTS.PAGE_FAULT`, event code `0xc1`, umask `0x8`, counting page-fault assists on programmable counters 0 through 7.
- `HW_INTERRUPTS.MASKED`, `HW_INTERRUPTS.PENDING_AND_MASKED`, and `HW_INTERRUPTS.RECEIVED`, event code `0xcb`, distinguishing masked, pending-and-masked, and received hardware interrupts.
- `OCR.STREAMING_WR.ANY_RESPONSE`, event codes `0x2A,0x2B`, MSRs `0x1a6,0x1a7`, and MSR value `0x10800`, counting streaming stores with any response on counters 0 through 3.
- `XQ.FULL_CYCLES`, event code `0x2d`, umask `0x1`, counter mask `1`, counting cycles where the uncore cannot accept further core requests.

## Control Flow

There is no internal control flow. Perf's event loader reads the array, indexes entries by `EventName`, and uses the encoding fields when users request an event by name. For plain programmable events, perf programs the selected counter with `EventCode`, `UMask`, and any qualifier fields such as `CounterMask`. For the OCR event, perf must also program the listed model-specific register filter values before counting the offcore response event.

## State and Persistence Behavior

The JSON file is persistent source metadata. Runtime state consists of hardware counter values, overflow periods derived from `SampleAfterValue`, and MSR programming performed by perf or the kernel PMU driver. None of that state is stored in this file. The `Counter` field constrains where perf may schedule each event, and the MSR fields create a temporary hardware configuration while the event is active.

## Dependencies and Integration Points

The file depends on Linux perf's PMU event JSON parser, the x86 Emerald Rapids model mapping, and kernel PMU support for the encoded core events and offcore response MSRs. It integrates with `perf list`, `perf stat`, `perf record`, event alias resolution, counter scheduling, PEBS or sampling period setup where applicable, and tests that compare event encodings against upstream Linux or Intel PMU data.

The interrupt and assist counters are useful integration points for OS and low-level runtime diagnosis. The OCR streaming store event bridges core PMU event selection with MSR-filtered offcore response counting. `XQ.FULL_CYCLES` ties core pipeline observation to pressure at the core-to-uncore request interface.

## Risks and Edge Cases

MSR-backed events are higher risk than simple events. If `MSRIndex`, `MSRValue`, or allowed counters are wrong, perf may program an invalid offcore response filter, count a different transaction class, or fail to schedule the event. The two event codes for `OCR.STREAMING_WR.ANY_RESPONSE` imply paired offcore response facilities; tooling must support the comma-separated encoding form.

Counter constraints matter. The OCR and XQ events are limited to counters 0 through 3, while assists and interrupts can use counters 0 through 7. Ignoring those constraints can cause schedule failures or inaccurate multiplexing assumptions.

Several events have terse `BriefDescription` values without a richer `PublicDescription`. Users and tests may need external PMU documentation to distinguish exact semantics. Interrupt counts are sensitive to privilege, masking behavior, virtualization, and kernel configuration, so observed values may be workload and environment dependent.

## Test Signals

Validation should include JSON parsing, perf PMU table generation, `perf list` visibility for all six event aliases, and event encoding checks for `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, and `MSRValue`. Practical smoke tests include `perf stat -e ASSISTS.PAGE_FAULT`, `perf stat -e HW_INTERRUPTS.RECEIVED`, and scheduling checks for `OCR.STREAMING_WR.ANY_RESPONSE` on Emerald Rapids hardware or a perf event parser test fixture. Drift checks against upstream Linux perf PMU data are important for this vendored copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/pipeline.json

## Purpose

`pipeline.json` defines Emerald Rapids pipeline, retirement, branch, top-down, and execution-port PMU events for Linux perf. It contains 124 event objects covering arithmetic divider use, assists, branch retirement and misprediction, unhalted clocks, memory-stall cycle activity, execution activity, retired instructions and uops, integer vector operations, load blocking, loop stream detector activity, machine clears, resource stalls, reservation-station state, top-down slots, dispatched execution ports, and issued/executed/retired uops.

The file is declarative PMU metadata. Its purpose is to let perf name, encode, schedule, sample, and display these microarchitectural events for the Emerald Rapids CPU model. It does not implement the counters; it describes how perf should program CPU PMU hardware.

## Important APIs, Types, and Data

The schema is a JSON array of event objects. Common fields are `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. Qualifier fields include `CounterMask`, `EdgeDetect`, `Invert`, `Deprecated`, `MSRIndex`, and `MSRValue`. Some architectural events use fixed counters and omit `EventCode`, such as `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, `CPU_CLK_UNHALTED.REF_TSC`, and `TOPDOWN.SLOTS`.

The file's event families include:

- `ARITH`: divider-active events, including deprecated aliases for older names and replacements such as `ARITH.DIV_ACTIVE` and `ARITH.IDIV_ACTIVE`.
- `ASSISTS`: `ASSISTS.ANY` for hardware microcode assists.
- `BR_INST_RETIRED` and `BR_MISP_RETIRED`: retired branch and mispredicted branch categories including conditional, taken, far, indirect, call, return, and near-taken variants.
- `CPU_CLK_UNHALTED`: thread, reference, distributed, one-thread-active, C0 wait, pause, and fixed-counter clock events.
- `CYCLE_ACTIVITY`: cycles and stalls while L1D, L2, or broader memory-subsystem load misses are outstanding.
- `EXE`, `EXE_ACTIVITY`, `UOPS_DISPATCHED`, and `UOPS_EXECUTED`: AMX activity, port utilization, load/store/execution bound cycles, dispatch-port counts, uop execution counts, and stall cycles.
- `INST_DECODED`, `INST_RETIRED`, `UOPS_ISSUED`, and `UOPS_RETIRED`: decoder use, retired instruction/uop accounting, macro-fusion, NOPs, precise distribution, repeat-string iterations, issue cycles, and retirement stalls.
- `INT_MISC`, `MACHINE_CLEARS`, `RS`, `RS_EMPTY`, and `RESOURCE_STALLS`: recovery after clears, unknown branch cycles, uop dropping, machine clears, reservation-station emptiness, store-buffer stalls, and serializing-operation stalls.
- `INT_VEC_RETIRED`: 128-bit and 256-bit integer vector add, multiply, shuffle, and VNNI instruction retirement.
- `LD_BLOCKS`, `LOAD_HIT_PREFETCH`, and `LSD`: load blocking causes, software-prefetch fill-buffer hits, and loop stream detector cycles/uops.
- `TOPDOWN`: backend-bound, bad-speculation, branch-mispredict, memory-bound, and slot denominator events for Top-down Microarchitecture Analysis.

Seven entries are marked deprecated and intentionally remain as compatibility aliases: `ARITH.DIVIDER_ACTIVE`, `ARITH.FP_DIVIDER_ACTIVE`, `ARITH.INT_DIVIDER_ACTIVE`, `RS_EMPTY.COUNT`, `RS_EMPTY.CYCLES`, `UOPS_EXECUTED.STALL_CYCLES`, and `UOPS_RETIRED.STALL_CYCLES`.

## Control Flow

There is no executable control flow in the file. Perf control flow is data driven: the PMU event generator or runtime loader parses the JSON, selects records matching Emerald Rapids, and registers event aliases. When a user requests an event, perf resolves the alias, validates counter constraints, programs fixed or programmable counters using the event encoding fields, applies qualifiers such as edge detection, inversion, counter masks, and MSR filters, and then reads or samples the resulting hardware counts.

Top-down analysis adds a higher-level flow. `TOPDOWN.SLOTS` or `TOPDOWN.SLOTS_P` supplies the denominator, and the bound/speculation slot events supply components that perf metrics can combine into percentages. Fixed-counter events leave programmable counters available for other events, while `_P` variants expose programmable-counter alternatives when needed by grouping or sampling.

## State and Persistence Behavior

The JSON file is static source metadata. Runtime state is held in CPU PMU counters, fixed counters, overflow status bits, and any MSR programming performed while an event is active. `SampleAfterValue` provides default sampling periods, but actual period state is managed by perf and the kernel.

Counter availability is part of the persistent metadata contract. Most events allow counters 0 through 7, but some are restricted to 0 through 3, some top-down bad-speculation events are counter 0 only, and fixed-counter events are bound to fixed counters 0 through 3. Qualifiers such as `CounterMask`, `EdgeDetect`, and `Invert` alter how the hardware increments during an active measurement but do not persist after the event is removed.

## Dependencies and Integration Points

The file depends on the Linux perf PMU event schema, x86 Emerald Rapids model detection, kernel PMU driver support for the listed event encodings, and Intel's architectural and model-specific PMU definitions. It integrates with `perf list`, `perf stat`, `perf record`, event grouping, top-down metrics, generated PMU tables, counter scheduling, fixed-counter handling, and tooling that validates vendored perf data against upstream Linux.

The events are also integration points for higher-level performance diagnosis. Branch events feed control-flow and bad-speculation metrics. `CPU_CLK_UNHALTED` and `INST_RETIRED` are denominator inputs for IPC and utilization metrics. `CYCLE_ACTIVITY`, `RESOURCE_STALLS`, `RS`, and `EXE_ACTIVITY` support front-end versus back-end stall attribution. `TOPDOWN` events anchor Intel TMA. `UOPS_DISPATCHED` and `UOPS_EXECUTED` expose execution-port pressure and throughput.

## Risks and Edge Cases

Encoding accuracy is the main risk. An incorrect `EventCode`, `UMask`, `CounterMask`, `Invert`, `EdgeDetect`, or fixed-counter assignment changes the measured hardware condition while still producing plausible-looking counts. Counter constraints are especially important for top-down events and events limited to counters 0 through 3.

Deprecated aliases must stay coherent with their replacement events. Removing them can break user scripts, while changing their encodings can make historical event names diverge from the intended replacement. Events with `_P` suffixes are programmable-counter alternatives to fixed architectural events and should not be treated as exact duplicates in all scheduling contexts.

Some descriptions are terse or use architecture-specific terms such as RS, RAT, LSD, PEBS, PDIR, PDIST, C0.1/C0.2, and AMX. Consumers should avoid deriving semantics from names alone. Clock events have caveats around halt states, hyper-thread distribution, throttling, pause/umwait/tpause behavior, and fixed-counter overflow status. MSR-filtered entries such as `INT_MISC.UNKNOWN_BRANCH_CYCLES` and `UOPS_RETIRED.MS` require correct MSR programming.

Hardware and virtualization can affect availability and counts. Fixed counter 3 top-down slots, PEBS precise distribution, AMX activity, and model-specific port mappings depend on Emerald Rapids PMU support. Multiplexing may make ratios misleading unless `enabled` and `running` time are considered by perf.

## Test Signals

Useful checks include JSON parser validation, perf PMU event generation, `perf list` coverage for all 124 aliases, and static validation of unique names, deprecated aliases, counter constraints, fixed-counter names, event codes, umasks, and qualifier fields. On capable hardware, smoke tests should schedule representative events from each family, including `TOPDOWN.SLOTS`, `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, branch retired and mispredicted events, `CYCLE_ACTIVITY.STALLS_TOTAL`, `UOPS_DISPATCHED.PORT_0`, and `UOPS_RETIRED.SLOTS`.

Metric-level tests should verify top-down formulas that use these events, especially denominator consistency and counter scheduling for grouped measurements. Regression checks should compare the file against the upstream Linux Emerald Rapids PMU database and run perf parser tests that exercise fixed counters, programmable alternatives, MSR-backed events, deprecated aliases, and counter-mask/invert/edge-detect qualifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/pipeline.json -->
