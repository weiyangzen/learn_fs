# sources/distributed-fs/ceph-client/include/trace/events/fsi_master_ast_cf.h

Purpose: AST ColdFire-assisted FSI master tracing for coprocessor commands, SRAM requests/responses, CRC failures, busy polling, and address optimization.

Important APIs/types/functions: Declares trace-event macros/classes `trace:fsi_master_acf_cmd_abs_addr`, `trace:fsi_master_acf_cmd_rel_addr`, `trace:fsi_master_acf_cmd_same_addr`, `trace:fsi_master_acf_copro_command`, `trace:fsi_master_acf_copro_response`, `trace:fsi_master_acf_crc_rsp_error`, `trace:fsi_master_acf_poll_response_busy`, `trace:fsi_master_acf_send_request`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:u32`, `bits:u8`, `busy_count:int`, `crc_ok:bool`, `master_idx:int`, `msg:uint64_t`, `op:uint32_t`, `rbits:u8`, `rcrc:u8`, `rdata:u32`, `rel_addr:u32`, `retries:int`, `rtag:u8`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Command events follow request submission, coprocessor response, CRC validation, busy-loop retries, and absolute/relative/same-address command construction. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace entries snapshot command words, response words, CRC bits, retry counts, relative addresses, and master index without storing state outside tracing buffers. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: FSI command bit packing is dense; mismatched bit lengths, CRC interpretation, or relative-address traces can send debugging toward the wrong transaction. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Validate read/write, BUSY retry, CRC error, and absolute/relative/same-address cases with firmware/hardware tests and compare traces to wire-format commands. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/fsi_master_ast_cf`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
