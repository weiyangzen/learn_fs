# sources/distributed-fs/ceph-client/include/trace/events/lock.h

Purpose: Lockdep/lock tracing for acquire, acquired, release, contention begin, and contention end events.

Important APIs/types/functions: Declares trace-event macros/classes `class:lock`, `event:lock_acquired`, `event:lock_contended`, `event:lock_release`, `trace:contention_begin`, `trace:contention_end`, `trace:lock_acquire`. Defines or exports symbolic enums/helpers none. Representative payload fields include `flags:unsigned int`, `lock_addr:void *`, `lockdep_addr:void *`, `name`, `ret:int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The events record lockdep map names/classes, subclass/try/read/check flags, caller ip, wait context, and contention timing/flags. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Lock state is owned by lockdep and primitives; trace entries sample lock operation metadata. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/sched.h>`, `#include <linux/tracepoint.h>`, `#include <linux/lockdep.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Tracing lock operations is high-volume and reentrancy-sensitive; class/name pointers must remain valid. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run lockdep tests and contention microbenchmarks to validate acquire/release pairing and contention duration fields. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/lock`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
