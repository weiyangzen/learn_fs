# sources/distributed-fs/ceph-client/include/trace/events/intel_ifs.h

Purpose: Intel In-Field Scan tracing for scan status and SBAF status reporting.

Important APIs/types/functions: Declares trace-event macros/classes `trace:ifs_sbaf`, `trace:ifs_status`. Defines or exports symbolic enums/helpers none. Representative payload fields include `batch:int`, `bundle:u16`, `pgm:u16`, `start:u16`, `status:u64`, `stop:u16`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The events record CPU/package context, batch/test ids, status chunks, control/error fields, and ktime for IFS diagnostics. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Hardware scan status persists in model-specific registers; tracing snapshots the decoded values at status points. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/ktime.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Incorrect package/CPU association or status decoding can misclassify silicon self-test failures. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run IFS status and SBAF reporting paths on supported hardware or mocked MSR reads and validate status fields. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/intel_ifs`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
