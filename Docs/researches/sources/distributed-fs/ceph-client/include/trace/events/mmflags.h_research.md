# sources/distributed-fs/ceph-client/include/trace/events/mmflags.h

Purpose: Shared memory-management trace formatting helpers for GFP flags, page flags, VMA flags, compaction status, migrate types, and related enums.

Important APIs/types/functions: Declares trace-event macros/classes none. Defines or exports symbolic enums/helpers `___GFP_##a##_BIT`, `___GFP_LAST_BIT`, `___GFP_UNUSED_BIT`, `a`. Representative payload fields include none.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. This header does not declare trace events; it defines TRACE_DEFINE_ENUM entries and __def_gfpflag_names, show_gfp_flags, show_vma_flags, show_page_flags, and related symbolic helper macros consumed by other trace headers. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: It owns no runtime state; its persistent contract is compile-time symbolic mapping from bit values/enums to trace output strings. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/node.h>`, `#include <linux/mmzone.h>`, `#include <linux/compaction.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: If new flags are added without updating these helpers, memory traces become incomplete or misleading; configuration-specific flags need guarded definitions. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Build with varied MM configs and inspect kmem/compaction/migration trace output for correct flag decoding. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mmflags`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
