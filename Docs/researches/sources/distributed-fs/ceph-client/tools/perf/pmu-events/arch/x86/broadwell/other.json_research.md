# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/other.json

## Purpose

`other.json` defines four Broadwell core PMU events that do not fit the neighboring memory, pipeline, virtual-memory, or uncore categories. The events expose privilege-level cycle accounting and split-lock/uncacheable-lock stall duration.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects using the standard perf PMU event schema. It contains `CPL_CYCLES.RING0`, `CPL_CYCLES.RING0_TRANS`, `CPL_CYCLES.RING123`, and `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`. The cycle events use event code `0x5C` with umasks `0x1` and `0x2`; the transition event uses `CounterMask: 1` and `EdgeDetect: 1`; the lock-duration event uses event code `0x63` and umask `0x1`.

## Control Flow and Data Flow

The data flow matches other perf event catalogs: JSON is parsed during perf's PMU table generation, users select event names through perf, and the generated encoding is passed through the kernel PMU driver to Broadwell counters. The ring-transition event uses edge-detect semantics so hardware increments on transitions instead of counting every eligible cycle.

## State and Persistence Behavior

This file is static metadata. It does not store runtime privilege transitions or lock events. `SampleAfterValue` provides default sampling periods for generated perf metadata.

## Dependencies and Integration Points

The file depends on Broadwell core PMU semantics for current privilege level cycles and lock-cycle detection. It integrates with perf list/stat/record through generated PMU event tables and with operating-system profiling workflows that distinguish kernel cycles, user cycles, ring transitions, and expensive split-lock or uncacheable locked operations.

## Risks and Edge Cases

Ring-level accounting can be misinterpreted in virtualized or unusual privilege environments where rings 1 and 2 are uncommon or remapped. `CPL_CYCLES.RING0_TRANS` is not a cycle count; it counts transitions, so comparing it directly to `RING0` or `RING123` is a units bug. The split-lock event describes a severe performance hazard, but support and behavior can vary with platform lock-detection policy.

## Test Signals

Smoke tests should verify the four event names appear in `perf list` and can be accepted by `perf stat` on Broadwell. A targeted kernel-heavy workload should move `CPL_CYCLES.RING0`; user-only loops should mostly move `CPL_CYCLES.RING123`; split-lock tests, where safe and permitted, should trigger `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`.
