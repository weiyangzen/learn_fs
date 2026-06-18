# sources/distributed-fs/ceph-client/include/trace/events/i2c_slave.h

Purpose: I2C slave callback tracing for read/write requested, processed, received, and stop events.

Important APIs/types/functions: Declares trace-event macros/classes `trace:i2c_slave`. Defines or exports symbolic enums/helpers `I2C_SLAVE_READ_PROCESSED`, `I2C_SLAVE_READ_REQUESTED`, `I2C_SLAVE_STOP`, `I2C_SLAVE_WRITE_RECEIVED`, `I2C_SLAVE_WRITE_REQUESTED`. Representative payload fields include `adapter_nr:int`, `addr:__u16`, `buf:__u8`, `event:enum i2c_slave_event`, `len:__u16`, `ret:int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The single event maps slave event enums to strings and records adapter number, slave address, event type, and value byte. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Slave driver state persists elsewhere; trace entries capture callback invocations and byte values. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/i2c.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Event ordering is protocol-sensitive and byte values may be stale or undefined for some slave events if used incorrectly. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Exercise slave read/write/stop callbacks against a test master and verify enum names and byte values. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/i2c_slave`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
