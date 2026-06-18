# sources/distributed-fs/ceph-client/include/trace/events/mmc.h

Purpose: MMC core request tracing for command/data/stop request start and completion.

Important APIs/types/functions: Declares trace-event macros/classes `trace:mmc_request_done`, `trace:mmc_request_start`. Defines or exports symbolic enums/helpers none. Representative payload fields include `blk_addr:unsigned int`, `blksz:unsigned int`, `blocks:unsigned int`, `bytes_xfered:unsigned int`, `can_retune:unsigned int`, `cmd_arg:u32`, `cmd_err:int`, `cmd_flags:unsigned int`, `cmd_opcode:u32`, `cmd_resp:u32`, `cmd_retries:unsigned int`, `data_err:int`, `data_flags:unsigned int`, `doing_retune:unsigned int`, `hold_retune:int`, `mrq:struct mmc_request *`, `name`, `need_retune:int`, `retune_now:unsigned int`, `retune_period:unsigned int`, `sbc_arg:u32`, `sbc_err:int`, `sbc_flags:unsigned int`, `sbc_opcode:u32`, `sbc_resp:u32`, `sbc_retries:unsigned int`, `stop_arg:u32`, `stop_err:int`, ... plus 5 more.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Request start/done events record host name, command opcode/arg/flags/retries/error, data block counts/sizes/flags/errors, stop command, and SBC info. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: MMC host/card/request state persists in the MMC core and driver; trace entries snapshot request structures at start and completion. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/blkdev.h>`, `#include <linux/mmc/core.h>`, `#include <linux/mmc/host.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Requests can include optional data/stop/SBC pieces; traces must handle NULL members and completion mutation correctly. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run reads, writes, erase, tuning/error-retry, and command-only requests on MMC/SD/eMMC devices and compare start/done fields. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mmc`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
