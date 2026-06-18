# sources/distributed-fs/ceph-client/tools/perf/util/mem-events.h

## Purpose

`mem-events.h` declares perf memory-event selection, formatting, cache-to-cache statistics, and memory-stat bucket APIs.

## Important APIs, Types, and Functions

`struct perf_mem_event` describes one PMU memory event template with support, load-latency, optional auxiliary config, tag, event-name format, and sysfs event name. Enums define load/store/load-store slots and memory stat types/buckets. `struct c2c_stats` stores counters for locks, stores, loads, cache hits, HITM, peer hits, DRAM locality, blocking, missing maps, and parse failures. The header declares PMU initialization/list/parse/record APIs, data-source formatting APIs, c2c decode/add APIs, and stat index/name APIs.

## Control Flow

No local runtime flow exists. Callers typically initialize PMU memory events, parse user selections, generate record arguments, then format and aggregate memory samples during reporting.

## State and Persistence Behavior

The header exposes global `perf_mem_events__loads_ldlat`, `perf_mem_events[]`, and `perf_mem_record[]`. Those globals are command-level state and affect later record-argument generation.

## Dependencies and Integration Points

It depends on Linux types and perf `evsel`, `mem_info`, and `perf_pmu` declarations. It is used by perf mem, perf c2c, perf script, hist sorting, and memory sample resolution code.

## Risks and Edge Cases

Bucket enums and `MEM_STAT_PRINT_LEN` must stay aligned with display code. Adding a new memory level or data-source field requires updates in both index and name functions. Global selection state means independent command phases must reset or initialize it intentionally.

## Test Signals

Compile tests should cover users of every declared API. Functional tests should validate each enum bucket maps to a display name and that c2c counters remain large enough for expected workloads.
