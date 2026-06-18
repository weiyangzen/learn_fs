# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trace-id.h

## Purpose

`coresight-trace-id.h` declares the public CoreSight trace ID allocation API and documents the allocator contract for CPU and system trace sources.

## Important APIs, Types, and Functions

The header defines reserved ID boundaries with `CORESIGHT_TRACE_ID_RES_0`, `CORESIGHT_TRACE_ID_RES_TOP`, and `IS_VALID_CS_TRACE_ID`. It declares CPU allocation/read/release APIs, map-specific variants, system and static system allocation APIs, system release, and perf session start/stop notifications.

## Control Flow

Callers obtain a CPU ID with `coresight_trace_id_get_cpu_id*`, emit or program it, and release it with `put` unless perf session semantics defer release. Fast readers use `coresight_trace_id_read_cpu_id*` when allocation cannot change. System sources call `coresight_trace_id_get_system_id` or request a static ID, then later release it.

## State and Persistence Behavior

State is owned by the implementation file and by optional `coresight_trace_id_map` instances supplied by callers. The API contract states that perf sessions retain CPU mappings until the final session stops.

## Dependencies and Integration Points

The header depends on bitops/types and `struct coresight_trace_id_map` from CoreSight public headers. It is included by CoreSight sources, links needing ATIDs, and perf ETM code.

## Risks and Edge Cases

Callers must not program ID 0 or IDs at/above `0x70`. Lockless reads are only safe under the documented perf stability condition. Every successful system allocation needs a matching put.

## Test Signals

Compile users against all declared APIs, and runtime-check invalid ID rejection, map-specific behavior, static allocation, and perf session lifetime semantics.
