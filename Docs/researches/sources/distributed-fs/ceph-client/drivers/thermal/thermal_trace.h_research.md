# sources/distributed-fs/ceph-client/drivers/thermal/thermal_trace.h

## Purpose
`thermal_trace.h` defines ftrace tracepoints for generic thermal-zone temperature updates, trip events, cooling-device updates, and CPU/devfreq power cooling activity.

## Important APIs, Types, and Functions
Trace events include `thermal_temperature`, `cdev_update`, `thermal_zone_trip`, `thermal_power_cpu_get_power_simple`, `thermal_power_cpu_limit`, `thermal_power_devfreq_get_power`, and `thermal_power_devfreq_limit`. It maps trip enum values to symbolic names with `TRACE_DEFINE_ENUM` and `show_tzt_type`.

## Control Flow
The file is declarative tracepoint metadata. Runtime callers invoke generated `trace_*` functions, which collect fields such as zone type/id, current/previous temperature, trip id/type, cdev target, CPU masks, frequencies, loads, and power values.

## State and Persistence Behavior
Tracepoints do not persist state in this file; they emit records to ftrace/perf buffers when enabled. Generated code is included through `trace/define_trace.h`.

## Dependencies and Integration Points
It depends on `linux/tracepoint.h`, `linux/thermal.h`, optional CPU thermal and devfreq thermal configs, and `thermal_core.h`. Thermal helpers and governors use these tracepoints for observability.

## Risks and Edge Cases
Trace ABI field names are consumed by tooling. CPU/devfreq events must remain behind the right config guards to avoid type visibility issues. Load calculation avoids divide-by-zero when total time is zero.

## Test Signals
Build with CPU/devfreq thermal enabled/disabled, enable trace events under tracing, drive thermal updates and cooling limits, and validate expected field values in trace output.
