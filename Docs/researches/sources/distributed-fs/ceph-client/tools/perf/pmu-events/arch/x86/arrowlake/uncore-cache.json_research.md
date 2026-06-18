# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-cache.json

## Purpose

This file defines Arrow Lake uncore cache events for the HAC CBO PMU. It contains two TOR allocation counters: `UNC_HAC_CBO_TOR_ALLOCATION.ALL` and `UNC_HAC_CBO_TOR_ALLOCATION.DRD`. They expose cache-coherent queue allocation activity, including all TOR entries and data-read allocations.

## Important APIs, Types, And Data

The records use the perf JSON event schema with `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. `Unit` is `HAC_CBO`, which `jevents.py` maps to an uncore PMU name by lowercasing and prefixing with `uncore_`. `PerPkg` marks these as package-level uncore counters rather than per-CPU thread counters.

## Control Flow

`jevents.py` reads both JSON entries, lowercases the event names, converts `EventCode` and nonzero `UMask` into perf event strings, and places them in the Arrow Lake generated PMU table for the `uncore_hac_cbo` PMU. Runtime perf commands match the generated alias against kernel uncore PMU devices.

## State And Persistence Behavior

The file stores static hardware-event metadata only. Counter values are produced by the uncore PMU at measurement time. Because these counters are per package, aggregation behavior depends on perf's PMU discovery and package selection rather than any mutable state in this JSON.

## Dependencies And Integration Points

Integration points include the Arrow Lake x86 mapfile row, `jevents.py` unit-to-PMU conversion, uncore PMU discovery in perf, generated `pmu-events.c`, and user-facing `perf list` output. The event semantics depend on the kernel exposing a compatible HAC CBO uncore PMU.

## Risks And Edge Cases

The small file has little internal complexity, but PMU naming is sensitive: a mismatch between `HAC_CBO` and the kernel uncore PMU name would make aliases undiscoverable. `PerPkg` mistakes can cause confusing aggregation. The descriptions distinguish all TOR entries from coherent data reads; swapping masks would make cache traffic analysis misleading.

## Test Signals

Validate with `jq empty`, x86 PMU event generation, `perf test pmu-events`, and `perf list` on a system or fixture exposing `uncore_hac_cbo`. Generated event strings should contain `event=0x35,umask=0x8` for `.all` and `event=0x35,umask=0x1` for `.drd`.
