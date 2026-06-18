# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/other.json

## Purpose

This file defines four Haswell core PMU events outside the main memory, pipeline, cache, frontend, and TLB categories. They cover privilege-level cycle accounting and split/uncacheable lock duration: `CPL_CYCLES.RING0`, `CPL_CYCLES.RING0_TRANS`, `CPL_CYCLES.RING123`, and `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`.

## Important APIs, Types, And Data

Each record uses the standard event schema with `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and for `LOCK_CYCLES...` a longer `PublicDescription`. All entries are default core-PMU aliases. `CPL_CYCLES` uses event `0x5C` with masks for ring 0 and non-ring-0 cycles; `LOCK_CYCLES` uses event `0x63`, mask `0x1`.

## Control Flow

`jevents.py` ingests the entries with the other Haswell arrays, converts selector and mask fields into generated perf alias configs, and emits them into the Haswell core event table. Runtime perf uses the aliases for direct event requests and as possible ingredients in OS/kernel-utilization analysis.

## State And Persistence Behavior

The file persists static alias metadata and sample periods. Privilege-cycle counts and lock-duration counts are hardware/runtime state measured during a perf session. No local mutable state exists in the JSON.

## Dependencies And Integration Points

The entries integrate with Haswell model matching, perf alias generation, privilege filter usage (`:k`, `:u`) in metrics, and lock-contention diagnostics. `CPL_CYCLES` is related to system/kernel metrics in `hsw-metrics.json`, while `LOCK_CYCLES...` supports split-lock and uncacheable-lock investigation.

## Risks And Edge Cases

The privilege-level naming can be misread: `RING123` is non-ring-0 rather than all user-only cycles under every perf filter combination. `RING0_TRANS` counts intervals between halts while in ring 0, not cycles. Lock-cycle events may be rare and workload-sensitive, and split-lock behavior can be affected by kernel mitigation or platform configuration.

## Test Signals

Validate JSON and generated aliases. Runtime checks include kernel-heavy versus user-heavy workloads for `CPL_CYCLES.*`, a lock-stress or split-lock test where available for `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`, and `perf list` verification that the descriptions are visible under Haswell core events.
