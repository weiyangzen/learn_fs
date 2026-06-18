# Research: subset-b-006694 Jaketown PMU Event Metadata

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/memory.json

## Purpose

This file is a Jaketown/Sandy Bridge-EP perf PMU event table for memory-facing core events. It contains 35 JSON event records that are consumed by `tools/perf/pmu-events/jevents.py` and compiled into perf's generated PMU event tables. The events cover memory ordering machine clears, PEBS load latency thresholds, precise store sampling, misaligned memory references, and offcore response selectors for LLC misses by request type and response source.

The file is source data rather than executable code. Its correctness determines whether `perf list`, `perf stat`, and `perf record -e <event>` expose usable Intel Jaketown memory events with the right raw event encodings and special MSR programming.

## Important APIs, Types, And Data Contracts

Each array element follows the perf JSON event schema handled by `JsonEvent` in `tools/perf/pmu-events/jevents.py`. Important fields used here are `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, `PEBS`, `MSRIndex`, and `MSRValue`.

`EventName` is converted to lower case by the generator and becomes the symbolic perf event name. `EventCode` and `UMask` are converted into raw `event=` and `umask=` config terms. `SampleAfterValue` becomes `period=`, which affects default sampling period. `PEBS` augments descriptions as precise events and constrains sampling expectations. `MSRIndex` plus `MSRValue` are resolved through `lookup_msr()` and appended to the generated config for events that need auxiliary MSR selectors.

The most important event families are:

- `MEM_TRANS_RETIRED`: 9 entries, all on counter 3, including load latency thresholds from `GT_4` through `GT_512` and `PRECISE_STORE`.
- `OFFCORE_RESPONSE`: 23 entries, all using event code pair `0xB7, 0xBB` with MSR selectors `0x1a6,0x1a7`.
- `MISALIGN_MEM_REF`: 2 entries for split load/store uops.
- `MACHINE_CLEARS`: 1 memory-ordering machine-clear event.

## Control Flow And Generation Behavior

At build time `jevents.py` walks the model directory, reads non-`metricgroups.json` files, parses each JSON object, and builds generated C tables. For this file, the topic is inferred from the filename `memory.json`, so events are categorized under the memory topic for listing output.

For normal events, `JsonEvent` emits an `event=<EventCode>` plus optional `umask=<UMask>` and `period=<SampleAfterValue>` string. For offcore response and load latency records, `MSRIndex` and `MSRValue` add model-specific MSR programming to the generated event string. For entries with comma-separated event codes and MSR indices, `jevents.py` uses the first event code for the base event encoding while the raw MSR string is preserved through the MSR lookup path, so malformed comma lists are a high-risk area.

## State And Persistence

The JSON file has no runtime state. It is persistent build input. Its contents are compiled into generated perf PMU event C data, then loaded at runtime based on CPU model mapping. Runtime state lives in perf's PMU/event parser and kernel PMU programming, not in this file.

Events with `MSRIndex`/`MSRValue` imply hardware state programming when selected by perf: offcore response events program offcore response MSRs, and load-latency events program the PEBS load latency threshold MSR. Counter placement is also persistent metadata: load latency and precise store events are restricted to counter 3, while most offcore events allow counters 0-3.

## Dependencies And Integration Points

Primary dependencies are the perf PMU event generator, the Jaketown mapfile/model selection, and Intel PMU hardware semantics for Sandy Bridge-EP. Integration points include `jevents.py`, generated `pmu-events.c`, `perf list`, `perf stat`, `perf record`, and the kernel perf x86 PMU implementation that interprets offcore MSR constraints and PEBS support.

This file complements `pipeline.json`, `other.json`, and `uncore-cache.json`: it covers core-side memory behavior, while `uncore-cache.json` covers package-level cache/home-agent behavior and `pipeline.json` covers broader execution pipeline counters.

## Risks And Edge Cases

Offcore response entries depend on exact `MSRValue` bitmasks. A single wrong bit changes the selected request/response class while still producing a syntactically valid event. Several descriptions have spacing and grammar issues, but those are lower risk than encoding errors.

PEBS and counter constraints matter. The load-latency events are counter-3-only and precise; scheduling them with incompatible events can fail or multiplex unexpectedly. `MEM_TRANS_RETIRED.PRECISE_STORE` has no MSR threshold, unlike the load-latency variants, so tools should not infer all `MEM_TRANS_RETIRED` records use `MSRIndex`.

The comma-separated `EventCode` and `MSRIndex` values on offcore events are generator-sensitive. Tests should ensure the generated event strings still select the intended offcore registers for `0xB7`/`0xBB` aliases.

## Test Signals

Useful validation includes `jq empty memory.json`, generator tests that rebuild `pmu-events.c`, and `perf list memory` on a build containing Jaketown tables. Spot-check generated entries for `mem_trans_retired.load_latency_gt_128`, `mem_trans_retired.precise_store`, and `offcore_response.demand_data_rd.llc_miss.remote_dram`.

Runtime test signals on compatible hardware include successful event scheduling, PEBS availability for load latency/store sampling, and offcore events producing nonzero counts under LLC-miss workloads. Regression tests should also compare `EventCode`, `UMask`, `MSRIndex`, and `MSRValue` against Intel's Jaketown event reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/metricgroups.json

## Purpose

This file maps metric group names to user-facing descriptions for the Jaketown PMU event/metric model. Unlike the event JSON files, it is an object rather than an array. It does not define counters or raw events; it gives perf descriptions for groups such as `Backend`, `MemoryBound`, `TopdownL1`, `tma_frontend_bound_group`, and issue-oriented groups like `tma_issueTLB`.

The data supports `perf list metricgroups`, metric browsing, and generated lookup helpers that explain metric groups. It is a metadata index for Intel Top-down Microarchitecture Analysis groupings and derived TMA categories.

## Important APIs, Types, And Data Contracts

`jevents.py` treats any file named `metricgroups.json` specially. Instead of parsing event records, it loads the JSON object, interns each key and description into the generated big C string table, and stores the pair in `_metricgroups`. `print_metricgroups()` later emits a sorted C array and a `describe_metricgroup(const char *group)` binary-search helper.

The keys are the public group identifiers. Descriptions are plain strings. There are no `EventName`, `MetricExpr`, `MetricGroup`, or event-encoding fields in this file. The generator asserts each group name has length greater than one, so empty or one-character names would fail generation.

The file includes both older/top-level names (`Backend`, `Frontend`, `Mem`, `Pipeline`, `HPC`, `Summary`) and newer generated TMA group names (`tma_L1_group` through `tma_L6_group`, category groups, and issue groups). Most legacy entries share the description "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet"; topdown levels and TMA categories have more specific text.

## Control Flow And Generation Behavior

During the `pmu-events` tree walk, `add_events_table_entries()` returns early for `metricgroups.json`. The file's object entries are collected globally instead of becoming event table rows. At output time, the generated `metricgroups` C array is sorted by group name and searched by `describe_metricgroup()`.

Runtime consumers do not parse this JSON directly. They call generated PMU event APIs through perf's metric and list code. `builtin-list.c` uses metric group information when rendering grouped metric output, and metric parsing/stat code uses generated metric metadata when resolving requested groups.

## State And Persistence

This file has no mutable state. The persistent state is the checked-in JSON mapping and its generated C representation. Because descriptions are compiled into a string table, changes require regenerating/rebuilding perf PMU events before users see them.

The mapping is global within the generated output; duplicate names would overwrite in the Python `_metricgroups` dictionary before printing. In this file all keys are unique.

## Dependencies And Integration Points

Dependencies include `jevents.py`, generated `pmu-events.c`, perf's metric group lookup routines, `perf list --details`, and metric group filtering in `builtin-list.c`. The names should align with `MetricGroup` values emitted by architecture-specific metric generators such as `intel_metrics.py`; stale names here can leave metrics with less helpful descriptions or unreachable documentation.

The file integrates conceptually with the sibling event files by giving names to analysis buckets that use events from `pipeline.json`, `memory.json`, and uncore files. It is not Jaketown hardware programming data by itself.

## Risks And Edge Cases

The main risk is drift between metric definitions and group descriptions. A group can be listed here even if no current metric references it, and a metric can reference a group missing here, which leaves the group less discoverable.

Case and punctuation are significant. `MachineClears` and `Machine_Clears` both appear, as do `TopdownL1` and `tma_L1_group` naming styles. Normalizing names casually would break lookup compatibility.

Since this file is object-shaped while sibling PMU event files are array-shaped, generic tooling must special-case it the same way the perf generator does. Treating it as an event array would produce invalid research, invalid schema validation, or broken generated tables.

## Test Signals

Validation should include `jq type metricgroups.json` returning `object`, generator rebuild coverage for `describe_metricgroup()`, and `perf list metricgroups` output showing representative entries. Tests should query both legacy and TMA names, for example `TopdownL1`, `MemoryBound`, `tma_backend_bound_group`, and `tma_issueTLB`.

Schema tests should ensure every key and value is a non-empty string and should cross-check metric `MetricGroup` names against this file when generated Jaketown metrics are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/other.json

## Purpose

This file defines five miscellaneous Jaketown core PMU events that do not fit the larger memory, pipeline, cache, floating point, or frontend/backend topic files. The covered event families are `CPL_CYCLES`, `HW_PRE_REQ`, and `LOCK_CYCLES`.

The events expose privilege-level cycle accounting, ring-transition intervals, L1D hardware prefetch misses, and split/uncacheable lock duration. This is build-time data for perf's event table, not executable logic.

## Important APIs, Types, And Data Contracts

The file is a JSON array consumed by `jevents.py` through the standard `JsonEvent` path. It uses `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `CounterMask`, `EdgeDetect`, and `BriefDescription`.

`CPL_CYCLES.RING0` and `CPL_CYCLES.RING123` count unhalted cycles by current privilege level. `CPL_CYCLES.RING0_TRANS` adds `CounterMask: "1"` and `EdgeDetect: "1"` to count intervals/transitions rather than raw cycles. `HW_PRE_REQ.DL1_MISS` counts L1D hardware prefetch requests that miss. `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION` counts cycles where L1/L2 are locked by UC or split-lock behavior.

`CounterMask` and `EdgeDetect` are translated by the generator to `cmask=` and `edge=` config terms. These modifiers are semantically important for the transition event.

## Control Flow And Generation Behavior

The perf PMU event generator infers the topic `other` from the filename, then emits one generated event row per array element. The events become discoverable through `perf list other` and selectable by their lower-cased names.

There is no control flow inside the file. Runtime behavior is the standard perf event path: user selection resolves the generated event name, perf programs the event select/umask plus modifiers, and the kernel reads counts from the allowed programmable counters.

## State And Persistence

The file is static persistent metadata. Runtime state is limited to hardware counter values while perf sessions are active. All five entries allow counters `0,1,2,3`, so they are more schedulable than events restricted to a fixed counter or counter 3.

The transition event's edge-detect state is implemented by hardware PMU configuration derived from the JSON fields.

## Dependencies And Integration Points

Dependencies include `jevents.py`, the x86 PMU event generator, generated C PMU tables, and perf's event parser. The hardware dependency is Intel Jaketown PMU support for event codes `0x5C`, `0x4E`, and `0x63`.

The file integrates with broader profiling workflows by filling gaps: privilege-cycle data helps separate kernel/user execution, prefetch misses complement memory/cache analysis, and lock cycles can diagnose split-lock or UC access behavior.

## Risks And Edge Cases

The terse file can be overlooked in schema or documentation updates. The most sensitive record is `CPL_CYCLES.RING0_TRANS`; removing `CounterMask` or `EdgeDetect` would silently convert interval counting into a different measurement.

Privilege-level counters depend on accurate hardware CPL classification and may be affected by virtualization or kernel/hypervisor restrictions. Lock-cycle counts can be rare or workload-specific, so zero counts do not necessarily indicate a broken event.

## Test Signals

Static tests should run `jq empty other.json` and verify all five entries include non-empty `EventName`, `EventCode`, and `Counter` fields. Generated output should include lower-case names such as `cpl_cycles.ring0_trans` with `cmask=1,edge=1`.

Runtime validation on compatible hardware can compare `CPL_CYCLES.RING0` and `CPL_CYCLES.RING123` under kernel-heavy and user-heavy workloads. A microbenchmark that triggers split locks or UC accesses can validate `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`, though such tests may need elevated privileges or platform-specific setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/pipeline.json

## Purpose

This file is the main Jaketown core pipeline PMU event table. It contains 127 event records for execution, retirement, branch behavior, allocation/issue/dispatch, stall cycles, load blocking, resource pressure, clock cycles, and fixed counters. It supplies the raw hardware events behind many top-down and low-level performance investigations on Sandy Bridge-EP.

The file is static PMU metadata. It does not implement pipeline analysis itself; it exposes the event encodings that perf and generated metric formulas can use.

## Important APIs, Types, And Data Contracts

The JSON array uses the standard perf PMU event schema: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, plus modifiers such as `CounterMask`, `EdgeDetect`, `Invert`, `AnyThread`, and `PEBS`.

Major event families and counts are:

- Branch execution and retirement: `BR_INST_EXEC` 13, `BR_INST_RETIRED` 8, `BR_MISP_EXEC` 11, `BR_MISP_RETIRED` 6.
- Clock and instruction retirement: `CPU_CLK_THREAD_UNHALTED` 3, `CPU_CLK_UNHALTED` 8, `INST_RETIRED` 3.
- Pipeline activity and stalls: `CYCLE_ACTIVITY` 5, `ILD_STALL` 2, `INT_MISC` 4, `RESOURCE_STALLS` 8, `RESOURCE_STALLS2` 4, `RS_EVENTS` 2.
- Load and memory pipeline blocking: `LD_BLOCKS` 4, `LD_BLOCKS_PARTIAL` 2, `LOAD_HIT_PRE` 2.
- Uop flow: `UOPS_DISPATCHED` 2, `UOPS_DISPATCHED_PORT` 12, `UOPS_EXECUTED` 5, `UOPS_ISSUED` 3, `UOPS_RETIRED` 5.
- Other execution details: `AGU_BYPASS_CANCEL`, `ARITH`, `LSD`, `MACHINE_CLEARS`, `PARTIAL_RAT_STALLS`, `ROB_MISC_EVENTS`, and `OTHER_ASSISTS`.

Fixed-counter records such as `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF_TSC` use `Counter: "Fixed counter N"` instead of an `EventCode`-only programmable-counter contract. PEBS flags appear on several retired branch/uop/instruction events.

## Control Flow And Generation Behavior

`jevents.py` reads this file during the Jaketown leaf directory pass, infers topic `pipeline`, and constructs generated event rows. It lowercases event names, converts event encodings and modifiers into perf config strings, and appends precision notes to descriptions when `PEBS` is set.

Modifier fields are especially important in this file. `AnyThread` becomes `any=`, `CounterMask` becomes `cmask=`, `EdgeDetect` becomes `edge=`, and `Invert` becomes `inv=`. These fields distinguish raw event counts from cycle-threshold, transition, or inverted stall-cycle events. For example, `RS_EVENTS.EMPTY_END` uses edge detection plus inversion, and `UOPS_EXECUTED.CORE_CYCLES_NONE` uses inversion to count cycles with no uops.

At runtime, perf event selection follows the generated table. The kernel PMU programs programmable or fixed counters, applies PEBS where available, and enforces counter constraints.

## State And Persistence

This file has no mutable state. Its durable state is the checked-in PMU event schema. Runtime state consists of hardware counters and sampling buffers during perf sessions.

Several records encode scheduling constraints as state-like metadata: fixed-counter-only events cannot be freely assigned to generic PMCs, counter-specific events such as `CYCLE_ACTIVITY.CYCLES_L1D_PENDING` use counter 2, and PEBS events require precise sampling support. `AnyThread` entries aggregate at physical-core scope rather than logical-thread scope.

## Dependencies And Integration Points

Dependencies include the perf PMU event generator, generated x86 PMU tables, Intel Jaketown raw PMU semantics, and perf user interfaces. The file is a key integration point for top-down analysis and ratios generated elsewhere: retirement slots, branch mispredicts, uop dispatch/issue/retire, frontend stalls, and backend resource stalls all come from this table.

It complements `memory.json` for memory-ordering and offcore events. Some families overlap by name, such as `MACHINE_CLEARS`, but with different subevents and analysis purposes.

## Risks And Edge Cases

Pipeline events are easy to misuse because similar names can mean speculative execution, retired execution, cycles, or occurrences. `BR_INST_EXEC` and `BR_INST_RETIRED` are not interchangeable. `UOPS_RETIRED.ALL`, `UOPS_RETIRED.RETIRE_SLOTS`, and inverted stall-cycle forms measure different quantities.

Counter masks and inversion are high-risk encoding fields. Dropping `cmask`, `edge`, or `inv` yields syntactically valid but semantically wrong events. Fixed counter descriptions mention dedicated counters; if generated scheduling metadata ignores that, perf may fail to open the event or report confusing multiplexing.

Some descriptions are truncated or contain typographical errors, for example the first `AGU_BYPASS_CANCEL.COUNT` description ends mid-sentence. Documentation cleanup must avoid changing event encodings.

## Test Signals

Static validation should include JSON syntax, schema checks for required event fields, and generated-table inspection for representative modifiers: `arith.fpu_div` with `edge=1,cmask=1`, `rs_events.empty_end` with `edge=1,inv=1`, `cpu_clk_unhalted.thread_any` with `any=1`, and PEBS metadata for retired branch/uop events.

Runtime smoke tests on compatible hardware can run `perf stat` with `inst_retired.any`, `cpu_clk_unhalted.thread`, `br_misp_retired.all_branches`, `uops_retired.retire_slots`, and `resource_stalls.any`. More focused tests should compare branch-heavy, divide-heavy, and memory-stall microbenchmarks to ensure the expected event families move in the expected direction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-cache.json

## Purpose

This file defines package-scoped Jaketown uncore cache and Home Agent PMU events. It contains 205 event records split across `CBOX` and `HA` units. The CBOX records describe LLC slices, ring stops, ingress/egress queues, TOR state, and CBo ring traffic. The HA records describe Home Agent requests, directory behavior, memory-controller credits, ring egress, Direct2Core, TAD region requests, and QPI/iMC interactions.

The file is build-time event metadata for perf. It lets users ask perf for uncore events by symbolic name rather than manually programming uncore unit event codes and unit masks.

## Important APIs, Types, And Data Contracts

The array uses the standard perf PMU event schema plus uncore-specific fields. Key fields are `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and `PublicDescription`.

`Unit` is essential. `jevents.py` maps JSON units to PMU names with `unit_to_pmu()`, so `CBOX` and `HA` records become uncore PMU events rather than core events. `PerPkg: "1"` marks package-level aggregation semantics. `Counter` identifies valid uncore counters, often `0,1` for CBOX lookup/queue events, `2,3` for ring-used events, counter `0` for occupancy events, or `0,1,2,3` for many HA events.

The file has 97 `CBOX` events and 108 `HA` events. CBOX families include `UNC_C_LLC_LOOKUP`, `UNC_C_LLC_VICTIMS`, `UNC_C_RING_*`, `UNC_C_RxR_*`, `UNC_C_TOR_INSERTS`, `UNC_C_TOR_OCCUPANCY`, and `UNC_C_TxR_*`. HA families include `UNC_H_REQUESTS`, `UNC_H_DIRECTORY_*`, `UNC_H_IMC_*`, `UNC_H_RPQ_*`, `UNC_H_WPQ_*`, `UNC_H_RING_*`, `UNC_H_TAD_REQUESTS_*`, `UNC_H_TRACKER_INSERTS`, and `UNC_H_TxR_*`.

## Control Flow And Generation Behavior

During event generation, `jevents.py` parses each record, converts `Unit` to the generated PMU name, lowercases `EventName`, and emits config strings from `EventCode` and `UMask`. The inferred topic is `uncore-cache`, but the runtime PMU target is driven primarily by the `Unit` field.

There is no procedural control flow in the file. Runtime flow is: perf resolves the generated uncore event, opens the appropriate uncore PMU instance, applies package/unit scope, programs the unit event/umask on valid counters, and reads counts from each exposed uncore box. For package systems with multiple CBoxes or HAs, perf's uncore PMU layer handles instance enumeration and aggregation.

## State And Persistence

The file is static persistent metadata. Runtime state is hardware uncore counter configuration and counter values. The `PerPkg` field means counts are package-scoped, which affects aggregation and interpretation in multi-socket systems.

Occupancy events such as `UNC_C_RxR_OCCUPANCY.*` and `UNC_C_TOR_OCCUPANCY.*` accumulate queue entries per cycle rather than simple occurrences. They are state-derived measurements and often require division by insertion counts or clockticks to infer average occupancy or latency. Ring-used and credit-empty events are cycle-state measurements.

## Dependencies And Integration Points

Dependencies include perf's generated PMU event tables, x86 uncore PMU support for Jaketown, sysfs-exposed uncore PMU instances, and Intel hardware documentation for CBOX and HA semantics. `jevents.py` handles `Unit` and `PerPkg`, while perf's runtime PMU layer decides which uncore boxes can be opened on the current CPU.

The file integrates with memory and NUMA analysis workflows. CBOX TOR/LLC/ring events can be correlated with core `OFFCORE_RESPONSE` events from `memory.json`. HA request, directory, and iMC credit events help explain memory-controller and interconnect bottlenecks not visible from core counters alone.

## Risks And Edge Cases

Uncore event semantics are heavily filtered. Some descriptions explicitly require external box filter programming, such as TOR opcode/NID filters and LLC lookup state filters. The JSON records provide base event/umask values but not every required box-filter value; users may need additional raw filter terms to get meaningful counts.

Counter restrictions are strict. Occupancy events often require counter 0, while ring-used events may require counters 2 or 3. If perf schedules incompatible uncore events together, it may fail or multiplex in ways that change interpretation.

Package aggregation can hide per-box imbalance. A high-level package count may mask one saturated CBOX, HA, channel, or ring direction. Multi-socket systems add another layer of aggregation risk.

There are text-quality issues in descriptions and at least one apparent naming/documentation mismatch in the TAD group: `UNC_H_TAD_REQUESTS_G1.REGION11` appears even though the public description says group 1 covers regions 8 to 10. Such issues warrant checking against Intel's original uncore event reference before changing encodings.

## Test Signals

Static validation should include `jq empty uncore-cache.json`, schema checks that every record has `Unit` and `PerPkg`, and generated-table inspection for representative CBOX and HA names. The unit distribution should remain 97 CBOX and 108 HA events unless an intentional table update occurs.

Runtime validation requires compatible Jaketown uncore PMUs. Smoke tests should use events such as `unc_c_clockticks`, `unc_c_llc_lookup.data_read`, `unc_c_tor_inserts.miss_all`, `unc_h_clockticks`, `unc_h_requests.reads`, and `unc_h_imc_writes.all`. Memory bandwidth, NUMA remote-access, and cache-thrashing workloads should produce directional changes in HA request/credit and CBOX TOR/LLC events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-cache.json -->
