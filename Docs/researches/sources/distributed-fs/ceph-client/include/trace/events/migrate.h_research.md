# sources/distributed-fs/ceph-client/include/trace/events/migrate.h

Purpose: Page migration tracepoints for migration batches, migration start, and migration PTE install/remove.

Important APIs/types/functions: Declares trace-event macros/classes `class:migration_pte`, `event:remove_migration_pte`, `event:set_migration_pte`, `trace:mm_migrate_pages`, `trace:mm_migrate_pages_start`. Defines or exports symbolic enums/helpers `a`. Representative payload fields include `addr:unsigned long`, `failed:unsigned long`, `large_folio_split:unsigned long`, `mode:enum migrate_mode`, `order:int`, `pte:unsigned long`, `reason:int`, `succeeded:unsigned long`, `thp_failed:unsigned long`, `thp_split:unsigned long`, `thp_succeeded:unsigned long`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record mode/reason/result counts, migration start parameters, and migration PTE old/new PFNs for install/remove operations. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Migration state persists in page tables and page structs; trace entries snapshot migration decisions and PTE transitions. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: PFN exposure and result enum drift are risks; migration can be concurrent with reclaim/compaction/NUMA balancing. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run NUMA balancing, compaction, memory hotplug, and mbind/move_pages migration cases and validate result counts and PTE traces. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/migrate`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
