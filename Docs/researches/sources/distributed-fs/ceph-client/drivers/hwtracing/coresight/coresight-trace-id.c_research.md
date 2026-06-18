# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trace-id.c

## Purpose

`coresight-trace-id.c` implements the CoreSight trace ID allocator. It assigns architecturally valid trace IDs to CPUs and system trace sources, preserves CPU IDs across overlapping perf sessions, supports static requested IDs, and exports map-based variants for non-default sink maps.

## Important APIs, Types, and Functions

The default state is `id_map_default`, backed by per-CPU atomic IDs and a raw spinlock. Internal helpers include `_coresight_trace_id_read_cpu_id`, `coresight_trace_id_find_odd_id`, `coresight_trace_id_alloc_new_id`, `coresight_trace_id_free`, `coresight_trace_id_release_all`, and map-specific CPU/system get/put helpers. Exported APIs include CPU get/read/put, map variants, system get/static-get/put, and perf session start/stop notifications.

## Control Flow

CPU allocation first returns an existing per-CPU ID if present. Otherwise it tries the legacy CPU trace ID, then any available valid ID. System allocation prefers odd IDs to reduce collision with legacy CPU values. Static system allocation requires the requested valid ID to be free. Perf start increments `perf_cs_etm_session_active`; perf stop decrements it and releases all IDs only when the last session stops, preserving stable CPU-to-ID mapping across concurrent perf events.

## State and Persistence Behavior

The allocator persists a bitmap of used IDs and per-CPU atomic assignments. IDs are reserved between `get` and `put`, while perf sessions intentionally defer CPU ID release until all sessions complete. `coresight_trace_id_release_all` clears both bitmap and CPU atomics under lock.

## Dependencies and Integration Points

The file depends on CoreSight PMU trace ID map definitions, CPU masks, atomics, bitmaps, and raw spinlocks. It is consumed by ETM/ETE CPU sources, TPDA, Trace NoC, dummy/static sources, and any system component requiring a CoreSight trace ID.

## Risks and Edge Cases

`coresight_trace_id_read_cpu_id*` is intentionally lockless for perf contexts, so callers must use it only when IDs are known stable. Put operations warn on invalid or unused IDs. Static allocation returns `-EBUSY` for valid but occupied IDs and `-EINVAL` for invalid requested IDs. A missing perf stop would retain IDs indefinitely.

## Test Signals

Tests should cover legacy CPU preference, odd system allocation, exhaustion, static ID conflicts, invalid puts, perf start/stop release semantics, lockless reads during active sessions, and map-specific isolation from the default allocator.
