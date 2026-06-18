# sources/distributed-fs/ceph-client/include/trace/events/kyber.h

Purpose: Kyber I/O scheduler tracing for latency measurement, token depth adjustment, and throttling.

Important APIs/types/functions: Declares trace-event macros/classes `trace:kyber_adjust`, `trace:kyber_latency`, `trace:kyber_throttled`. Defines or exports symbolic enums/helpers none. Representative payload fields include `denominator:u8`, `depth:unsigned int`, `dev:dev_t`, `domain:char`, `numerator:u8`, `percentile:u8`, `samples:unsigned int`, `type:char`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record block device names, scheduling domain, latency target/actual, queue depth adjustments, and throttled requests. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Scheduler state persists in kyber queues/domains; traces sample latency controller decisions. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/blkdev.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Device name/domain mismatch or timing unit errors can lead to wrong scheduler tuning conclusions. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run mixed read/write latency workloads under Kyber and verify latency, adjustment, and throttling events. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/kyber`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
