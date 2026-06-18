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
