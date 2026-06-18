# sources/distributed-fs/ceph-client/include/trace/events/fsi.h

Purpose: Generic FSI bus tracing for master read/write operations, results, breaks, scans, slave discovery, and device creation.

Important APIs/types/functions: Declares trace-event macros/classes `trace:fsi_dev_init`, `trace:fsi_master_break`, `trace:fsi_master_read`, `trace:fsi_master_rw_result`, `trace:fsi_master_scan`, `trace:fsi_master_unregister`, `trace:fsi_master_write`, `trace:fsi_slave_init`, `trace:fsi_slave_invalid_cfam`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:__u32`, `cfam_id:__u32`, `chip_id:int`, `data:__u32`, `id:int`, `idx:int`, `link:int`, `master_idx:int`, `master_n_links:int`, `n_links:int`, `ret:int`, `scan:bool`, `size:__u32`, `size:size_t`, `type:int`, `unit:int`, `version:int`, `write:bool`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Callers bracket master I/O and bus management with read/write/result/break/scan/unregister/slave/device events so failures can be correlated by master index, link, address, size, and return code. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace records contain ephemeral bus topology and transaction fields such as master index, link, CFAM id, engine type, unit, version, data, and error code. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Because FSI is low-level service-processor plumbing, missing traces around error returns or endian conversion makes field failures hard to isolate. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run scan/discovery plus read/write error injection on FSI masters and check result events line up with transfer arguments and return codes. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/fsi`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
