# sources/distributed-fs/ceph-client/include/trace/events/gpio.h

Purpose: Generic GPIO tracing for direction changes and value get/set operations.

Important APIs/types/functions: Declares trace-event macros/classes `trace:gpio_direction`, `trace:gpio_value`. Defines or exports symbolic enums/helpers none. Representative payload fields include `err:int`, `get:int`, `gpio:unsigned`, `in:int`, `value:int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. GPIO core users emit direction and value events with GPIO number, input/output or get/set direction, value, and error code. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The tracepoint owns no GPIO state; it records samples from gpiolib transitions and line values. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Legacy global GPIO numbers may be ambiguous on systems with many chips, and high-frequency value tracing can be noisy. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Toggle GPIO direction and values through gpiod/gpiolib paths, including failing requests, and verify event ordering and error reporting. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/gpio`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
