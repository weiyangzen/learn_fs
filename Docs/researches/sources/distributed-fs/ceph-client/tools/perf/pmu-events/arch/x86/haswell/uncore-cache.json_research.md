# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/uncore-cache.json

## Purpose

This file defines 26 Haswell uncore cache/CBOX events. It exposes LLC/CBOX cache-lookup classifications by request source and MESI state, plus external snoop response classifications for hit, hitm, miss, eviction, external, and cross-core cases.

## Important APIs, Types, And Data

The entries use `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and descriptions. `Unit` is `CBOX`, `PerPkg` is set, and counters are generally `0,1`, indicating package-level uncore CBOX programmable counters. `UNC_CBO_CACHE_LOOKUP` has 16 aliases spanning `ANY`, `READ`, `WRITE`, and `EXTSNP` crossed with MESI-style state masks. `UNC_CBO_XSNP_RESPONSE` has 9 aliases for HIT/HITM/MISS by eviction, external, and xcore response sources.

## Control Flow

During generation, `jevents.py` maps the `CBOX` unit to an uncore PMU table, converts event and umask fields to perf configs, and carries `PerPkg` metadata into generated entries. Runtime perf resolves these aliases against kernel-exposed uncore CBOX PMUs and programs package-scope counters rather than per-thread core counters.

## State And Persistence Behavior

The JSON stores static uncore alias metadata. Actual LLC lookup counts and snoop responses are maintained by uncore hardware during measurement. Package aggregation is driven by perf and kernel PMU topology, not by mutable state in this file.

## Dependencies And Integration Points

The file integrates with Haswell model selection, uncore PMU discovery, generated event tables, `perf list`, `perf stat`, and metrics that estimate data sharing, false sharing, L3 behavior, and memory traffic. It depends on the kernel naming and availability of CBOX PMUs matching perf's generated unit mapping.

## Risks And Edge Cases

Uncore PMU naming and package topology are the largest integration risks. Systems may expose multiple CBOX instances, so aggregation can differ from a single core event. MESI and snoop-response masks are easy to mix up; wrong masks would make cache-sharing diagnosis misleading. `PerPkg` events should not be interpreted as per-thread counts.

## Test Signals

Validate JSON and x86 generation. On compatible hardware or fixtures, `perf list` should show `unc_cbo_cache_lookup.*` and `unc_cbo_xsnp_response.*` under CBOX-style uncore PMUs. Runtime checks should compare lookup counts under read-heavy, write-heavy, and cross-core sharing workloads.
