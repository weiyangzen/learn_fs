# sources/distributed-fs/ceph-client/include/trace/events/mmap_lock.h

Purpose: mmap_lock tracepoints for lock acquisition attempts and returned status with memcg context.

Important APIs/types/functions: Declares trace-event macros/classes `class:mmap_lock`, `event:name`, `trace:mmap_lock_acquire_returned`. Defines or exports symbolic enums/helpers none. Representative payload fields include `memcg_id:u64`, `mm:struct mm_struct *`, `success:bool`, `write:bool`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Shared lock classes record mm pointer, write/read mode, caller ip, memcg path, and acquisition result. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The rwsem/mmap_lock owns state; trace entries sample contention/acquisition metadata. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/memcontrol.h>`, `#include <linux/tracepoint.h>`, `#include <linux/types.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Lock tracing can be high-volume and caller IP symbolization must be accurate to identify contention sites. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run mmap_lock contention tests with reads/writes and verify acquire/release/result sequences. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mmap_lock`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
