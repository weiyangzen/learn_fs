# sources/distributed-fs/ceph-client/include/trace/events/fsi_master_gpio.h

Purpose: GPIO bit-banged FSI master tracing for bit input/output, break clocks, CRC/busy handling, and address command forms.

Important APIs/types/functions: Declares trace-event macros/classes `trace:fsi_master_gpio_break`, `trace:fsi_master_gpio_clock_zeros`, `trace:fsi_master_gpio_cmd_abs_addr`, `trace:fsi_master_gpio_cmd_rel_addr`, `trace:fsi_master_gpio_cmd_same_addr`, `trace:fsi_master_gpio_crc_cmd_error`, `trace:fsi_master_gpio_crc_rsp_error`, `trace:fsi_master_gpio_in`, `trace:fsi_master_gpio_out`, `trace:fsi_master_gpio_poll_response_busy`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:u32`, `bits:int`, `busy:int`, `clocks:int`, `master_idx:int`, `msg:uint64_t`, `rel_addr:u32`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events are emitted while shifting FSI bits through GPIOs, sending breaks, polling responses, reporting CRC command/response errors, and selecting absolute/relative/same-address encodings. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: State is external GPIO pin state and FSI protocol state; trace payloads store bit counts, messages, addresses, busy counts, and master index samples. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: High-volume bit tracing can perturb timing, and off-by-one bit counts or reversed bit order make protocol traces deceptive. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run bit-banged read/write/break operations with CRC and busy retries, then compare trace messages against expected FSI frame encoding. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/fsi_master_gpio`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
