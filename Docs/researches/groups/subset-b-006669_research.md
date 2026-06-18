# Research: subset-b-006669

This grouped report covers Haswell-EP/Haswell-X `perf` PMU event metadata under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx`. These files are declarative JSON inputs consumed by Linux `perf`'s PMU event/metric table generation and lookup path rather than executable Ceph client logic.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/hsx-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/hsx-metrics.json

## Purpose

`hsx-metrics.json` defines 162 derived metric records for the Haswell-X/Haswell-EP x86 PMU model used by `perf stat -M`, metric groups, and top-down microarchitecture analysis. It turns raw architectural, model-specific, uncore, C-state, and synthetic perf events into human-oriented ratios, percentages, bandwidth values, frequencies, latencies, and top-down bottleneck categories.

The file is not runtime code. Its effective API is the perf PMU metric JSON schema: each array element may provide `MetricName`, `MetricExpr`, `BriefDescription`, `PublicDescription`, `MetricGroup`, `MetricgroupNoGroup`, `MetricConstraint`, `MetricThreshold`, and `ScaleUnit`. During the perf build, PMU event tooling parses these fields into generated metric tables for the `haswellx` architecture directory.

## Important schema entries and metric families

The highest-level metrics include package/core C-state residency (`C2_Pkg_Residency`, `C3_Core_Residency`, `C6_Pkg_Residency`, `C7_Core_Residency`), CPI/frequency/utilization (`cpi`, `cpu_operating_frequency`, `cpu_utilization`, `UNCORE_FREQ`, `uncore_frequency`), cache/TLB miss-per-instruction metrics, memory and I/O bandwidth metrics, NUMA locality metrics, SMI counters, and the full TMA hierarchy.

Top-down level 1 metrics are represented by `tma_frontend_bound`, `tma_bad_speculation`, `tma_retiring`, and `tma_backend_bound`. They depend on raw events such as `IDQ_UOPS_NOT_DELIVERED.CORE`, `UOPS_RETIRED.RETIRE_SLOTS`, `UOPS_ISSUED.ANY`, `BR_MISP_RETIRED.ALL_BRANCHES`, and synthetic helper metrics like `tma_info_thread_slots`. Lower levels break down frontend issues, speculation, backend memory/core bounds, DRAM/local/remote memory, port utilization, assists, machine clears, lock latency, store forwarding, split loads/stores, TLB behavior, and instruction mix.

Uncore formulas are important integration points. Examples include `memory_bandwidth_total = (UNC_M_CAS_COUNT.RD + UNC_M_CAS_COUNT.WR) * 64 / 1e6 / duration_time`, `qpi_data_transmit_bw = UNC_Q_TxL_FLITS_G0.DATA * 8 / 1e6 / duration_time`, and LLC miss latency expressions using `cbox@UNC_C_TOR_OCCUPANCY...@`, `cbox@UNC_C_TOR_INSERTS...@`, `UNC_C_CLOCKTICKS`, `#num_cores`, and `#num_packages`.

## Control flow and evaluation model

There is no imperative control flow in the JSON. Perf's generated metric engine treats `MetricExpr` as an expression graph. Raw event aliases, constants, runtime variables such as `duration_time`, topology variables such as `#num_cores`, `#num_packages`, and `#SMT_on`, and references to other metric names are resolved while a metric group is scheduled and evaluated.

Some expressions contain conditional forms, for example `if #SMT_on` and `if tma_info_thread_ipc > 1.8 else ...`, plus `min(...)` and arithmetic over multiple raw events. This makes dependency ordering and grouping significant: helper metrics such as `tma_info_thread_slots`, `tma_info_thread_ipc`, `tma_info_system_time`, and uncore frequencies feed many visible metrics.

## State and persistence behavior

The file persists static performance model metadata in the source tree. It does not store measured counter values, machine state, or user configuration. State at runtime lives in perf's event scheduler, counters, topology detection, and metric expression evaluator. `MetricConstraint: NO_GROUP_EVENTS` appears on metrics that cannot safely be scheduled as a normal grouped event set, which affects how perf multiplexes and validates counters during collection.

## Dependencies and integration points

Metrics depend on event aliases defined in neighboring Haswell-X JSON files, common x86 PMU event files, and uncore PMUs exposed by the kernel. Important dependencies include core events from `pipeline.json`, memory/offcore events from `memory.json`, OS/lock events from `other.json`, and group names described in `metricgroups.json`.

The `MetricGroup` field integrates metrics with user-facing group selectors. It includes legacy group names such as `Summary`, `Power`, `Mem`, `MemoryBW`, `Offcore`, `Pipeline`, `TopdownL1` through `TopdownL6`, and TMA-specific groups such as `tma_L1_group`, `tma_backend_bound_group`, `tma_issueBW`, and `tma_issueSyncxn`. `MetricgroupNoGroup` is used to expose top-down group placement while avoiding automatic grouping for selected entries.

## Risks and maintenance notes

Metric correctness is tightly coupled to event encodings and Haswell-X microarchitecture details. If a raw event alias is renamed or removed in another JSON file, dependent `MetricExpr` strings fail late in perf metric parsing or at runtime. Uncore formulas are especially topology-sensitive because they use socket/core variables and PMU-specific aliases.

Expression complexity is a risk. Several TMA formulas nest conditionals, `min(...)`, SMT-sensitive paths, and helper metrics. Small syntax errors in escaped event names, filter syntax, or parentheses can break metric generation. Thresholds are advisory but user-visible; stale thresholds can mislead performance triage even when event collection works.

Multiplexing and grouping are also risk areas. `tma_info_system_mux` explicitly measures multiplexing accuracy, while `NO_GROUP_EVENTS` warns that some formulas should avoid strict grouped scheduling. Tests should verify both JSON validity and actual `perf stat -M` scheduling on Haswell-X-compatible systems or fixtures.

## Test signals

Useful validation includes JSON parsing with `jq`, perf's PMU event table generation, metric expression parser tests, and command-level smoke tests such as `perf list metric`, `perf stat -M TopdownL1`, `perf stat -M memory_bandwidth_total`, and `perf stat -M tma_info_system_mux` on matching hardware. Cross-file tests should confirm every event alias referenced by `MetricExpr` is resolvable and every `MetricGroup` name has an expected description in `metricgroups.json` or is intentionally implicit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/hsx-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/memory.json

## Purpose

`memory.json` defines 67 Haswell-X core PMU events related to transactional memory, memory ordering, load latency sampling, misaligned memory references, and offcore LLC miss response classification. These entries provide raw event aliases used directly by `perf record/stat` and indirectly by higher-level metrics in `hsx-metrics.json`.

The file is declarative PMU metadata. Its API surface is the perf event JSON schema: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and optional `MSRIndex`, `MSRValue`, `PEBS`, `Data_LA`, `Errata`, `BriefDescription`, and `PublicDescription`.

## Important event families

Transactional memory events cover HLE and RTM lifecycle and abort categories: `HLE_RETIRED.START`, `HLE_RETIRED.COMMIT`, `HLE_RETIRED.ABORTED`, `HLE_RETIRED.ABORTED_MISC1` through `MISC5`, and the analogous `RTM_RETIRED.*` set. `TX_EXEC.MISC1` through `MISC5` and `TX_MEM.*` record transactional abort causes such as capacity write, conflict, HLE elision buffer mismatch/not-empty/unsupported-alignment, store to elided lock, and full elision buffer.

Load latency sampling is represented by `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_4`, `_8`, `_16`, `_32`, `_64`, `_128`, `_256`, and `_512`. These entries use counter 3, `Data_LA: 1`, PEBS level `2`, `MSRIndex: 0x3F6`, and different `MSRValue` thresholds. They are intended for precise latency sampling rather than ordinary aggregate counting.

Offcore response events use event codes `0xB7, 0xBB` with `MSRIndex: 0x1a6,0x1a7` and request/response filter `MSRValue` masks. The file defines aliases for code reads, data reads, all reads, all requests, RFOs, demand reads/RFOs, and L2/LLC prefetches, subdivided by LLC miss response classes such as `ANY_RESPONSE`, `LOCAL_DRAM`, `REMOTE_DRAM`, `REMOTE_HITM`, and `REMOTE_HIT_FORWARD`.

Other memory events include `MACHINE_CLEARS.MEMORY_ORDERING` and `MISALIGN_MEM_REF.LOADS`/`STORES`.

## Control flow and evaluation model

There is no file-local execution flow. Perf maps each `EventName` to an event selector made from `EventCode`, `UMask`, counter constraints, optional PEBS and data-address sampling flags, and optional model-specific register programming. When a user asks for an offcore event, perf must program the core event select plus the appropriate offcore response MSR filter.

The load-latency threshold events share the same core event encoding and differ mostly by latency threshold MSR value. The offcore aliases share the same PMU event codes and differ by filter masks. This makes the schema compact but means the correctness of `MSRValue` is central to the event semantics.

## State and persistence behavior

The JSON stores static event definitions only. Runtime state is the PMU programming performed by perf and the kernel: general-purpose counter allocation, PEBS buffer setup, data linear address capture, and MSR filter programming. `SampleAfterValue` values provide default sampling periods and affect profile granularity when used by perf.

## Dependencies and integration points

The file integrates with perf's PMU event generator, x86 core PMU event parser, PEBS support, offcore response MSR support, and metric formulas in `hsx-metrics.json`. Metrics for memory latency, DRAM/local/remote memory, data sharing, false sharing, and NUMA locality rely on these aliases or related offcore definitions.

The file also depends on Haswell-X errata handling and kernel support. Entries mark errata such as `HSD65`, `HSD76`, `HSD25`, and `HSM26`; users and tests need to interpret affected measurements carefully.

## Risks and maintenance notes

Offcore events are high risk because event code, umask, MSR index, and MSR filter masks must agree. A wrong `MSRValue` can silently count the wrong request or response class. Events using two possible offcore MSRs (`0x1a6,0x1a7`) may also interact with grouping and counter allocation limits.

PEBS/data-address events are sensitive to hardware support and kernel implementation. The latency events require counter 3 and precise sampling setup, so they can fail or be silently unavailable on mismatched systems. Transactional memory events may be unavailable or misleading on systems where TSX/HLE/RTM are disabled by microcode, BIOS policy, or security mitigations.

## Test signals

Validation should include JSON parsing, perf event table generation, `perf list` visibility for representative `HLE_RETIRED`, `RTM_RETIRED`, `TX_MEM`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, and `OFFCORE_RESPONSE.*` aliases, and hardware smoke tests for offcore MSR programming. Good command-level checks include `perf stat -e OFFCORE_RESPONSE.ALL_DATA_RD.LLC_MISS.LOCAL_DRAM` and PEBS sampling checks such as `perf record -e MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128` on Haswell-X hardware where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/metricgroups.json

## Purpose

`metricgroups.json` maps 124 metric group names to user-facing descriptions for the Haswell-X PMU metrics. It documents the grouping vocabulary referenced from `hsx-metrics.json` and shown by perf metric listing and selection interfaces.

Unlike the event files, this JSON is an object, not an array. Each property name is a group identifier and each value is a description string. The effective API is the perf metric group description schema.

## Important group families

The file contains legacy and broad analysis groups such as `Summary`, `Power`, `Pipeline`, `Frontend`, `Backend`, `BadSpec`, `MemoryBound`, `MemoryBW`, `MemoryLat`, `MemoryTLB`, `Offcore`, `CacheHits`, `CacheMisses`, `Branches`, `PortsUtil`, `SMT`, `OS`, `Server`, `SoC`, `HPC`, and `PGO`.

It also defines top-down hierarchy groups: `TopdownL1` through `TopdownL6` and corresponding `tma_L1_group` through `tma_L6_group`. Category-specific TMA groups include examples such as `tma_backend_bound_group`, `tma_frontend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, `tma_mem_latency_group`, `tma_ports_utilization_group`, `tma_retiring_group`, `tma_store_bound_group`, and `tma_store_op_utilization_group`.

Issue-oriented TMA groups such as `tma_issueBW`, `tma_issueFB`, `tma_issueL1`, `tma_issueLat`, `tma_issueMC`, `tma_issueMS`, `tma_issueRFO`, `tma_issueSyncxn`, and `tma_issueTLB` let related diagnosis metrics be surfaced together.

## Control flow and lookup model

There is no imperative control flow. Perf loads or compiles this mapping and uses it when displaying group descriptions or resolving metric group names. The control path is a lookup from a metric's `MetricGroup` token to a description string.

Most values say they come from the Top-down Microarchitecture Analysis Metrics spreadsheet. A smaller set gives specific descriptions for top-down levels and TMA category/issue groups. The distinction matters for user documentation, not counter programming.

## State and persistence behavior

The file persists only static group metadata. It does not affect measured counter state directly. It affects user-facing discovery and organization of metrics, which can influence which metric expressions perf schedules together.

## Dependencies and integration points

The main dependency is cross-file consistency with `hsx-metrics.json`: every group token referenced by metric records should either have a description here or be intentionally handled as a built-in/implicit group. This file does not depend on `memory.json`, `other.json`, or `pipeline.json` directly, but those event files provide the raw counters behind metrics assigned to these groups.

Perf tooling must parse this file as an object; treating it like the array-shaped event files is an error. That shape difference is a useful test signal for parsers.

## Risks and maintenance notes

Stale or missing group descriptions do not usually break counter collection, but they degrade `perf list`/metric discovery and can confuse users selecting metric groups. Naming drift is the main risk: if `hsx-metrics.json` adds or renames a `MetricGroup` token without updating this file, group documentation becomes incomplete.

Group names use multiple naming conventions, including legacy CamelCase, underscore variants such as `Memory_BW`, and TMA names with `_group` suffixes. Normalizing names without preserving compatibility could break user workflows and metric selection.

## Test signals

Tests should confirm valid JSON object shape, uniqueness of keys, non-empty string descriptions, and cross-reference coverage from `hsx-metrics.json` `MetricGroup` tokens. Perf-level validation should include `perf list metricgroups` or equivalent listing behavior and selection of representative groups such as `TopdownL1`, `MemoryBW`, `tma_L3_group`, and `tma_issueBW`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/other.json

## Purpose

`other.json` defines four Haswell-X PMU events that do not fit the larger memory or pipeline categories: privilege-level cycle accounting and split/uncacheable lock duration. These aliases support OS/kernel-mode analysis and lock contention diagnostics.

The file is a JSON array of event records using the perf PMU event schema: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, optional `CounterMask`, `EdgeDetect`, `BriefDescription`, and `PublicDescription`.

## Important events

`CPL_CYCLES.RING0` counts unhalted core cycles while the thread is in ring 0. `CPL_CYCLES.RING123` counts unhalted cycles while the thread is outside ring 0, covering rings 1, 2, and 3. Both use event code `0x5C`, counters `0,1,2,3`, and different umasks.

`CPL_CYCLES.RING0_TRANS` counts intervals between processor halts while in ring 0. It adds `CounterMask: 1` and `EdgeDetect: 1` to the same `0x5C`/`0x1` base encoding and has a lower sample period.

`LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION` counts cycles in which L1D and L2 are locked because of an uncacheable lock or split lock. It uses event code `0x63`, umask `0x1`, and general counters `0,1,2,3`.

## Control flow and evaluation model

No local control flow exists. Perf converts the event records into encodings and schedules them on general-purpose counters. The ring events are separated by umask; the transition event uses edge-detection and counter-mask semantics to count transitions rather than raw cycles.

## State and persistence behavior

The file stores static aliases only. Runtime state is the PMU counter configuration and sampling state maintained by perf and the kernel. `SampleAfterValue` controls default sampling periods when these aliases are used for profiling.

## Dependencies and integration points

These aliases feed OS and lock-related metrics in `hsx-metrics.json`, including kernel utilization/CPI and lock-latency analysis. Their group descriptions are represented by metric groups such as `OS`, `LockCont`, and related TMA issue groups in `metricgroups.json`.

They integrate with the same Haswell-X PMU table generation path as `memory.json` and `pipeline.json`, but have no direct dependency on offcore MSRs or PEBS.

## Risks and maintenance notes

The primary risks are semantic. Privilege-level accounting depends on accurate CPL attribution and may be affected by virtualization or host/guest counting policy. The ring 0 transition event relies on edge-detect/cmask behavior; a parser or generator bug in those fields would change the event from transition counting to ordinary cycle counting.

Split-lock/uncacheable-lock cycles can be rare, workload-dependent, and platform-policy-sensitive. Measurements may be affected by split-lock detection or mitigation settings outside perf.

## Test signals

Validation should include JSON parsing, `perf list` visibility of all four aliases, and event encoding checks for `CounterMask` and `EdgeDetect` on `CPL_CYCLES.RING0_TRANS`. Runtime smoke tests can use `perf stat -e CPL_CYCLES.RING0,CPL_CYCLES.RING123` and a lock-heavy workload for `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION` on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/pipeline.json

## Purpose

`pipeline.json` defines 130 Haswell-X core PMU events for instruction retirement, branches and mispredictions, cycles, frontend and backend stalls, machine clears, move elimination, load blocking, loop stream detector activity, resource stalls, reservation station behavior, uop issue/execute/retire accounting, and execution port usage. These aliases are the core raw inputs for top-down analysis in `hsx-metrics.json`.

The file uses the standard perf PMU event JSON array schema. Records include `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and optional fields such as `CounterMask`, `Invert`, `AnyThread`, `EdgeDetect`, `PEBS`, `Errata`, `BriefDescription`, and `PublicDescription`.

## Important event families

Branch events include executed and retired branch counts (`BR_INST_EXEC.*`, `BR_INST_RETIRED.*`) plus misprediction counts (`BR_MISP_EXEC.*`, `BR_MISP_RETIRED.*`). These feed bad speculation, branch resteer, and branch misprediction metrics.

Cycle and instruction events include fixed/general counter aliases such as `CPU_CLK_UNHALTED.THREAD`, `CPU_CLK_UNHALTED.THREAD_P`, `CPU_CLK_THREAD_UNHALTED.ONE_THREAD_ACTIVE`, `CPU_CLK_UNHALTED.REF_TSC`, `CPU_CLK_UNHALTED.REF_XCLK`, `INST_RETIRED.ANY`, `INST_RETIRED.ANY_P`, and `INST_RETIRED.PREC_DIST`. These are foundational for CPI, IPC, frequency, utilization, and multiplexing metrics.

Pipeline stall families include `CYCLE_ACTIVITY.CYCLES_L1D_PENDING`, `CYCLES_L2_PENDING`, `CYCLES_LDM_PENDING`, `CYCLES_NO_EXECUTE`, and matching `STALLS_*` events; `RESOURCE_STALLS.ANY`, `ROB`, `RS`, and `SB`; `ILD_STALL.IQ_FULL` and `ILD_STALL.LCP`; `LD_BLOCKS.NO_SR`, `LD_BLOCKS.STORE_FORWARD`, and `LD_BLOCKS_PARTIAL.ADDRESS_ALIAS`.

Uop accounting is extensive: `UOPS_ISSUED.*`, `UOPS_EXECUTED.*`, `UOPS_EXECUTED_PORT.PORT_0` through `PORT_7` and `_CORE` variants, `UOPS_DISPATCHED_PORT.PORT_0` through `PORT_7`, and `UOPS_RETIRED.ALL`, `RETIRE_SLOTS`, `STALL_CYCLES`, `CORE_STALL_CYCLES`, and `TOTAL_CYCLES`. These drive TMA retiring, backend, core-bound, port-utilization, and stalls calculations.

Other important families include `ARITH.DIVIDER_UOPS`, `LSD.CYCLES_4_UOPS`, `LSD.CYCLES_ACTIVE`, `LSD.UOPS`, `MACHINE_CLEARS.COUNT`, `CYCLES`, `MASKMOV`, `SMC`, `MOVE_ELIMINATION.*`, `OTHER_ASSISTS.ANY_WB_ASSIST`, `ROB_MISC_EVENTS.LBR_INSERTS`, and `RS_EVENTS.EMPTY_*`.

## Control flow and evaluation model

There is no imperative control flow in the file. Perf parses each event alias into PMU event selector fields and schedules requested events on fixed or programmable counters. Fields such as `CounterMask`, `Invert`, `AnyThread`, `EdgeDetect`, and `PEBS` alter the low-level event selection and sampling behavior.

Some aliases intentionally describe cycle-qualified counts rather than simple event occurrences. For example, `CYCLE_ACTIVITY.CYCLES_NO_EXECUTE` uses `CounterMask: 4`, and `UOPS_RETIRED.TOTAL_CYCLES` uses `CounterMask: 16` with `Invert: 1`. These encodings are consumed directly by metric formulas and must preserve their exact semantics.

## State and persistence behavior

The file persists static event metadata. Runtime state is counter allocation, fixed-counter availability, any-thread counting mode, PEBS configuration, sampling period, and multiplexing handled by perf and the kernel PMU driver. `SampleAfterValue` values provide defaults for profiling and do not represent accumulated state in the source tree.

## Dependencies and integration points

This is the main raw-event dependency for `hsx-metrics.json` top-down formulas. Examples include `IDQ_UOPS_NOT_DELIVERED.CORE` as a frontend-bound input, `UOPS_RETIRED.RETIRE_SLOTS` for retiring, `UOPS_ISSUED.ANY` and branch misprediction events for bad speculation, cycle activity and resource stalls for memory/core bound, and port events for port utilization.

It integrates with `metricgroups.json` indirectly through the metrics that consume these event names. It also depends on perf's x86 PMU generator understanding fixed counters, programmable counters, PEBS flags, errata fields, and event modifiers.

## Risks and maintenance notes

This file has high blast radius because many TMA and summary metrics rely on exact event names and semantics. Renaming an event alias breaks metric expressions. Changing `CounterMask`, `Invert`, `AnyThread`, or fixed-counter metadata can silently change measurements even if JSON parsing succeeds.

Errata annotations such as `HSD11`, `HSD135`, and `HSD140` indicate known hardware caveats. Tests and documentation should avoid treating affected events as universally precise. Fixed-counter aliases and `_ANY` variants require careful scheduling because they may count per-thread or any-thread cycles differently.

The event list includes many related names with similar encodings, such as `UOPS_EXECUTED_PORT.*` and `UOPS_DISPATCHED_PORT.*`; maintenance mistakes are easy to miss without cross-checking against Intel event tables.

## Test signals

Validation should include JSON parsing, perf PMU table generation, `perf list` visibility for representative branch, cycle, stall, uop, and port aliases, and expression resolution for top-down metrics in `hsx-metrics.json`. Hardware smoke tests should exercise `perf stat -e cycles,instructions,UOPS_RETIRED.RETIRE_SLOTS,BR_MISP_RETIRED.ALL_BRANCHES` and `perf stat -M TopdownL1` on matching Haswell-X systems. Parser tests should specifically assert preservation of `CounterMask`, `Invert`, `AnyThread`, fixed-counter names, PEBS flags, and errata metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/pipeline.json -->
