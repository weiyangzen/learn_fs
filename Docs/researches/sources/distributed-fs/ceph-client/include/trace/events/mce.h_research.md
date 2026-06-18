# sources/distributed-fs/ceph-client/include/trace/events/mce.h

Purpose: Machine Check Exception record tracing for x86 MCE hardware error reports.

Important APIs/types/functions: Declares trace-event macros/classes `trace:mce_record`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:u64`, `apicid:u32`, `bank:u8`, `cpu:u32`, `cpuid:u32`, `cpuvendor:u8`, `cs:u8`, `ip:u64`, `ipid:u64`, `mcgcap:u64`, `mcgstatus:u64`, `microcode:u32`, `misc:u64`, `ppin:u64`, `socketid:u32`, `status:u64`, `synd:u64`, `tsc:u64`, `v_data:u8`, `walltime:u64`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. A single event records machine-check fields such as CPU, bank, status, address, misc, syndrome, ip, time, walltime, and severity/context data. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: MCE records may also be logged by architecture code; this tracepoint snapshots the struct mce passed to it. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/ktime.h>`, `#include <linux/tracepoint.h>`, `#include <asm/mce.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Hardware error data is critical and architecture-specific; truncation or format drift can break postmortem analysis. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Inject corrected/uncorrected MCEs where supported and compare trace records with mcelog/rasdaemon output. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mce`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
