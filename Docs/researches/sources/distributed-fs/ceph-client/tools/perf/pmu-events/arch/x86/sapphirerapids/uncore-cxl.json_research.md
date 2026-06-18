# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-cxl.json

## Purpose

This 56-entry catalog defines Intel Sapphire Rapids uncore CXL PMU events for perf. It describes package-level counters for the CXL cache/memory block (`CXLCM`) and the CXL datapath block (`CXLDP`), covering clock ticks, transmit and receive flit classifications, packing-buffer occupancy and allocations, AGF allocations, link-layer maintenance flits, and CRC errors. The file lets `perf list` and `perf stat` expose named aliases for CXL.io/CXL.cache/CXL.mem-adjacent traffic without requiring users to program raw event codes and unit masks manually.

## Important APIs, Types, and Data

Each JSON object is an event descriptor consumed by perf's PMU event generation pipeline. The important fields are `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and optional `Experimental`. `jevents.py` reads these fields into generated `pmu-events.c` tables: it lowercases `EventName`, maps `Unit` names to PMU names, stores the event encoding, keeps `PerPkg`, and carries descriptions into perf aliases.

The file has 49 `CXLCM` events and 7 `CXLDP` events. All entries set `PerPkg: 1`, so the intended aggregation domain is package-level uncore hardware rather than per-thread or per-core counting. Two clock tick events are non-experimental: `UNC_CXLCM_CLOCKTICKS` on counters `0,1,2,3,4,5,6,7` and `UNC_CXLDP_CLOCKTICKS` on counters `0,1,2,3`. The other 54 entries are marked `Experimental: 1`.

`CXLCM` entries are split by counter lane. Receive-side events use counters `4,5,6,7` and include `RxC_AGF_INSERTS`, `RxC_FLITS`, `RxC_MISC`, `RxC_PACK_BUF_FULL`, `RxC_PACK_BUF_INSERTS`, and `RxC_PACK_BUF_NE`. Transmit-side events use counters `0,1,2,3` and include `TxC_FLITS` plus `TxC_PACK_BUF_INSERTS`. `CXLDP` entries use counters `0,1,2,3` and include `TxC_AGF_INSERTS` classes for `U2C`, `M2S`, data, request, and response traffic.

## Control Flow

There is no imperative control flow in this file. Build-time control flow comes from perf's PMU event tooling: the JSON array is parsed by `tools/perf/pmu-events/jevents.py`, converted into generated C tables, and compiled into perf. Runtime control flow starts when a user selects an alias such as `uncore_cxlcm/event=.../` through `perf stat` or by its named event. Perf matches the generated event's PMU name against discovered sysfs PMUs, installs the encoded `EventCode` and `UMask` into the uncore counter format, and reads package-level counts.

The event group names encode traffic direction and hardware queue location. `RxC_FLITS` and `TxC_FLITS` count received or packed flits by validity and header bits such as `VALID`, `PROT`, `CTRL`, `NO_HDR`, `AK_HDR`, `BE_HDR`, and `SZ_HDR`. `PACK_BUF_INSERTS`, `PACK_BUF_NE`, and `PACK_BUF_FULL` track pressure in packing buffers. `AGF_INSERTS` track allocations into aggregation or flow queues, while `RxC_MISC` tracks link maintenance and error events including `LLCRD`, `RETRY`, `INIT`, and `CRC_ERRORS`.

## State and Persistence Behavior

The persistent state is the static mapping from CXL event aliases to raw uncore event encodings and legal counter sets. Runtime measurements are ephemeral perf counts; they last only for the active perf session and are shared by package-level hardware. Because every event is `PerPkg`, consumers should expect aggregation across the socket/package rather than attribution to a single CPU, task, or Ceph thread.

Counter-set restrictions are part of the behavioral contract. Receive-side `CXLCM` events are limited to counters `4-7`, transmit-side `CXLCM` events are limited to counters `0-3`, and `CXLDP` events are limited to counters `0-3`. Scheduling incompatible events into the same limited counter bank can fail or multiplex, affecting count accuracy. Experimental events may also change naming or semantics across kernel/perf updates.

## Dependencies and Integration Points

This data depends on Sapphire Rapids kernel PMU support exposing matching uncore CXL PMUs through sysfs. In perf, it integrates with `jevents.py`, generated `pmu-events.c`, `struct perf_pmu` alias tables, `perf list`, and `perf stat` uncore event programming. The `Unit` names are the bridge between this source file and runtime PMU matching: `CXLCM` and `CXLDP` become uncore PMU aliases that must match discovered hardware PMU names, typically through perf's uncore wildcard and suffix-insensitive matching.

For the larger source tree, these events are diagnostic rather than Ceph-specific logic. They can help analyze Ceph or distributed-storage workloads on Sapphire Rapids systems with CXL memory or attached devices by distinguishing CXL flit traffic, queue pressure, retry/init behavior, CRC errors, and datapath allocations from core-side CPU, cache, or memory-controller counters.

## Risks

Most events are experimental, so downstream scripts should avoid assuming stable names or exact semantics without checking the target perf/kernel version. Package-level uncore counts are noisy when other workloads share the same socket. Counter-bank restrictions make event grouping fragile: a group mixing too many receive-side or transmit-side CXL events may be unschedulable or multiplexed. The brief descriptions contain several confusing labels, including swapped-looking cache request/response text and `Rxx` wording, so users should treat the `EventName`, `EventCode`, and `UMask` as authoritative and confirm interpretations against Intel PMU documentation when precision matters.

Hardware availability is another risk. Systems without Sapphire Rapids CXL PMUs, disabled CXL features, unsupported firmware, or kernels lacking these uncore devices will not expose usable aliases even though the JSON exists in the source tree. CRC, retry, and init counts may be sparse under healthy operation, so zero values are not proof that an event is misconfigured.

## Test Signals

Static validation should parse the file as JSON, verify all 56 entries include `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`, and confirm that all records are `PerPkg: 1`. Generation tests should run the perf PMU event build path and verify that `UNC_CXLCM_*` and `UNC_CXLDP_*` aliases appear in generated tables without duplicate-name or invalid-field errors.

Runtime validation should start with `perf list` on Sapphire Rapids hardware and confirm that the CXL uncore aliases are visible only when the matching PMUs exist. Smoke tests should compare clock tick events against elapsed time, generate CXL traffic where possible, and check that `TxC_FLITS.VALID`, `RxC_FLITS.VALID`, packing-buffer insert/not-empty/full events, and `CXLDP_TxC_AGF_INSERTS.*` move in plausible directions. Error-path tests are harder, but link retry, init, and CRC counters should remain near zero on healthy hardware and be monitored for nonzero deltas during stress or fault-injection runs.
