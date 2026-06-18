# sources/distributed-fs/ceph-client/include/trace/events/fsi_master_i2cr.h

Purpose: I2C-responder FSI master tracing for command/status/log words and I2C transport errors.

Important APIs/types/functions: Declares trace-event macros/classes `trace:i2cr_i2c_error`, `trace:i2cr_read`, `trace:i2cr_status`, `trace:i2cr_status_error`, `trace:i2cr_write`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:unsigned short`, `bus:int`, `command:unsigned char`, `data:unsigned char`, `error:uint64_t`, `log:uint64_t`, `rc:int`, `status:uint64_t`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The tracepoints record I2C command/address/data flow, status/log reads, decoded error words, and return codes from I2C operations. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Only trace-buffer snapshots are kept; live persistence belongs to the I2C adapter, responder device, and FSI master state. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: I2C bus number/address reuse and compact status words can obscure which responder failed unless every error path emits consistent data. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Test responder read/write/status operations with NACK, timeout, and status-error injection while checking bus/address/command fields. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/fsi_master_i2cr`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
