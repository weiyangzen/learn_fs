# sources/distributed-fs/ceph-client/include/trace/events/mlxsw.h

Purpose: mlxsw Spectrum ACL TCAM tracing for ATCAM spill, vregion rehash, migration, migration completion, and rollback failure.

Important APIs/types/functions: Declares trace-event macros/classes `trace:mlxsw_sp_acl_atcam_entry_add_ctcam_spill`, `trace:mlxsw_sp_acl_tcam_vregion_migrate`, `trace:mlxsw_sp_acl_tcam_vregion_migrate_end`, `trace:mlxsw_sp_acl_tcam_vregion_rehash`, `trace:mlxsw_sp_acl_tcam_vregion_rehash_rollback_failed`. Defines or exports symbolic enums/helpers none. Representative payload fields include `aregion:const void *`, `mlxsw_sp:const void *`, `vregion:const void *`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events expose region/vregion identifiers, region sizes, hints, chunk counts, and error conditions during TCAM rehash/migration. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: mlxsw ACL state persists in driver TCAM structures and hardware; traces snapshot control-plane transitions. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: TCAM resource traces are hardware-specific; missing rollback failures can hide ACL programming inconsistencies. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Program ACL sets that force spill, rehash, migrate, and rollback-failure paths on mlxsw test hardware or mocks. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mlxsw`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
