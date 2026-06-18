# sources/distributed-fs/ceph-client/include/trace/events/mmap.h

Purpose: MM mmap tracepoints for unmapped-area search results and exit_mmap teardown.

Important APIs/types/functions: Declares trace-event macros/classes `trace:exit_mmap`, `trace:vm_unmapped_area`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:unsigned long`, `align_mask:unsigned long`, `align_offset:unsigned long`, `flags:unsigned long`, `high_limit:unsigned long`, `length:unsigned long`, `low_limit:unsigned long`, `mm:struct mm_struct *`, `mt:struct maple_tree *`, `total_vm:unsigned long`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record unmapped area info/result fields and mm teardown state as address-space mappings are selected and destroyed. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: VMA/mm state persists in memory-management structures; trace entries snapshot addresses, lengths, flags, pgoff, and mm counters. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Address traces expose process layout and must be interpreted with ASLR and concurrent VMA changes in mind. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run mmap/munmap/brk and process-exit workloads, including top-down/bottom-up allocation failures, and validate ranges. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mmap`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
