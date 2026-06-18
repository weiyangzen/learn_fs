# sources/distributed-fs/ceph-client/include/trace/events/hwmon.h

Purpose: Hardware monitoring sysfs attribute tracing for numeric and string attribute show/store paths.

Important APIs/types/functions: Declares trace-event macros/classes `class:hwmon_attr_class`, `event:hwmon_attr_show`, `event:hwmon_attr_store`, `trace:hwmon_attr_show_string`. Defines or exports symbolic enums/helpers none. Representative payload fields include `attr_name`, `index:int`, `label`, `val:long long`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Shared attribute classes record device name, attribute name, index/channel, value, and return code; a separate string show event records text values. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace events snapshot hwmon attribute I/O; hwmon device drivers own sensor state. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Sensor labels can contain user-visible strings, and trace coverage depends on drivers routing through hwmon core helpers. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Read/write hwmon sysfs attributes across numeric and string sensors and verify values and errors in trace output. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/hwmon`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
