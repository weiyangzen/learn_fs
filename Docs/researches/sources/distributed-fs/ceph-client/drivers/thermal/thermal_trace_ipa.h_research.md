# sources/distributed-fs/ceph-client/drivers/thermal/thermal_trace_ipa.h

## Purpose
`thermal_trace_ipa.h` defines tracepoints for the intelligent power allocator governor, capturing aggregate power allocation, per-actor grants, and PID controller terms.

## Important APIs, Types, and Functions
Trace events are `thermal_power_allocator`, `thermal_power_actor`, and `thermal_power_allocator_pid`. They record zone id, requested and granted power, actor counts, available power range, current temperature, delta temperature, PID error, integral, p/i/d terms, and output.

## Control Flow
The header declares trace metadata only. The power allocator governor emits generated `trace_thermal_power_*` calls during control-loop computation and actor allocation.

## State and Persistence Behavior
No persistent state is owned. Records appear in trace buffers only while tracing is active.

## Dependencies and Integration Points
It depends on tracepoint infrastructure and `thermal_core.h`; it is included by the power allocator governor to expose tuning and debugging signals.

## Risks and Edge Cases
Field type choices are ABI-visible to trace tooling. PID values use signed 64-bit fields for intermediate terms, which helps avoid truncation in diagnostics.

## Test Signals
Build the power allocator governor, enable `thermal_power_allocator*` trace events, force governor updates, and check aggregate power, actor grants, and PID terms for consistency.
