# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/pseudo_lock_trace.h

## Purpose

This header defines tracepoints used by resctrl pseudo-lock measurement code. It gives users and tests visibility into memory access latency and cache residency measurements.

## Important APIs, Types, And Functions

Trace events are `pseudo_lock_mem_latency`, `pseudo_lock_l2`, and `pseudo_lock_l3`. The first records a 32-bit latency sample. The L2 and L3 events record 64-bit hit/reference and miss counts. The header sets `TRACE_SYSTEM resctrl`, `TRACE_INCLUDE_PATH .`, and `TRACE_INCLUDE_FILE pseudo_lock_trace` for recursive trace generation.

## Control Flow

There is no ordinary control flow. `pseudo_lock.c` defines `CREATE_TRACE_POINTS` before including this header, causing tracepoint definitions to be emitted; other includes can use declarations.

## State, Dependencies, And Integration

Tracepoint state is managed by the kernel tracing subsystem. Dependencies include `linux/tracepoint.h` and the Makefile include-path setting. Integration is with tracefs/perf tracing and pseudo-lock measurement functions.

## Risks And Test Signals

Field or format changes affect tracing tools. Include-path mistakes break builds. Test by enabling `CONFIG_RESCTRL_FS_PSEUDO_LOCK`, building with tracing, creating measurements, and verifying events appear under `tracefs/events/resctrl/`.
