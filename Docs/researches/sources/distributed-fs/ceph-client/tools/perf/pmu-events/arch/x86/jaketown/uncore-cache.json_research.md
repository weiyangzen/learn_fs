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
