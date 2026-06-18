# sources/distributed-fs/ceph-client/include/trace/events/i2c.h

Purpose: I2C master transfer tracing for write/read request payloads, read replies, and transfer results.

Important APIs/types/functions: Declares trace-event macros/classes `trace:i2c_read`, `trace:i2c_reply`, `trace:i2c_result`, `trace:i2c_write`. Defines or exports symbolic enums/helpers none. Representative payload fields include `adapter_nr:int`, `addr:__u16`, `buf:__u8`, `flags:__u16`, `len:__u16`, `msg_nr:__u16`, `nr_msgs:__u16`, `ret:__s16`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. TRACE_EVENT_FN hooks register/unregister trace callbacks around adapter transfers, copying message buffers for write/read/reply and logging final result counts/errors. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The tracepoint snapshots adapter number, message address/flags/length, buffer bytes, and return code; I2C core and adapter own transaction state. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/i2c.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Buffer capture can expose device data and must handle zero-length or invalid buffers safely; callback enablement affects overhead. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run combined write/read transfers, SMBus-like messages, NACK/timeouts, and trace enable/disable cycles with buffer content validation. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/i2c`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
