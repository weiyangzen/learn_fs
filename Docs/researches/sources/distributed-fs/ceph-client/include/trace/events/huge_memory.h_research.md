# sources/distributed-fs/ceph-client/include/trace/events/huge_memory.h

Purpose: Transparent huge page and khugepaged tracing for PMD scans, page collapse, file collapse, isolation, swapin, and scan summaries.

Important APIs/types/functions: Declares trace-event macros/classes `trace:mm_collapse_huge_page`, `trace:mm_collapse_huge_page_isolate`, `trace:mm_collapse_huge_page_swapin`, `trace:mm_khugepaged_collapse_file`, `trace:mm_khugepaged_scan`, `trace:mm_khugepaged_scan_file`, `trace:mm_khugepaged_scan_pmd`. Defines or exports symbolic enums/helpers `a`. Representative payload fields include `addr:unsigned long`, `filename`, `full_scan_finished:bool`, `hpfn:unsigned long`, `index:pgoff_t`, `is_shmem:bool`, `isolated:int`, `mm:struct mm_struct *`, `none_or_zero:int`, `nr:int`, `pfn:unsigned long`, `present:int`, `progress:unsigned int`, `referenced:int`, `result:int`, `ret:int`, `status:int`, `swap:int`, `swapped_in:int`, `unmapped:int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events follow khugepaged as it scans VMAs/files, isolates candidate pages, swaps in missing pages, attempts collapse, and records result enums. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace entries capture mm/vma addresses, pfn/isolate counts, writable flags, file indexes, HPAGE_PMD order, node, and result codes; VM state lives elsewhere. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include  <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Result enums must stay synchronized with THP code, and traces can sample rapidly changing memory layout under mmap/page-table locks. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run THP collapse tests for anonymous and file-backed memory, including failure reasons, swapin, and isolation counts. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/huge_memory`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
