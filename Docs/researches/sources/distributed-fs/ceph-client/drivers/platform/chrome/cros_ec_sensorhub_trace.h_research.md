# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sensorhub_trace.h

## Purpose
`cros_ec_sensorhub_trace.h` defines ftrace tracepoints for Chrome EC sensorhub FIFO timestamp reconstruction and sample delivery diagnostics.

## Important APIs, Types, and Functions
- `TRACE_EVENT(cros_ec_sensorhub_timestamp)` records EC sample timestamp, EC FIFO timestamp, AP FIFO IRQ timestamp, calculated current timestamp, current AP time, and delta.
- `TRACE_EVENT(cros_ec_sensorhub_data)` records sensor number and timing fields for emitted samples.
- `TRACE_EVENT(cros_ec_sensorhub_filter)` records timestamp filter deltas, median slope/error, history length, and current offsets.

## Control Flow
`cros_ec_sensorhub_ring.c` defines `CREATE_TRACE_POINTS` before including this header, so these tracepoint definitions instantiate events there. Other includes can use the header guard/multi-read pattern normally. The trace include path/file macros at the bottom are required by the kernel tracepoint generator.

## State and Persistence
The header defines tracepoint schemas, not runtime state. Trace buffers are managed by ftrace/perf infrastructure when enabled.

## Dependencies and Integration Points
It depends on Linux tracepoint infrastructure and sensorhub platform data for `struct cros_ec_sensors_ts_filter_state`. It integrates directly with the timestamp filter and sample-processing paths in `cros_ec_sensorhub_ring.c`.

## Risks and Edge Cases
Tracepoint field types must match caller argument types; mismatches can corrupt trace output or fail compilation. The header uses `TRACE_SYSTEM cros_ec`, shared with other Chrome EC tracepoints, so event names must remain unique. Format strings use signed 64-bit output for nanosecond timestamps and deltas.

## Test Signals
Compilation with tracepoints enabled is the main static signal. Runtime trace output is a diagnostic signal for timestamp jitter, future timestamps, and filter behavior.
