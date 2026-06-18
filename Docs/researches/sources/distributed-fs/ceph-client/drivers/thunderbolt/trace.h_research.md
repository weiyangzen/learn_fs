# sources/distributed-fs/ceph-client/drivers/thunderbolt/trace.h

## Purpose

`trace.h` defines Thunderbolt tracepoints for control-channel packets. It formats transmitted packets, received packets, and asynchronous event packets with domain index, package type, route, message-specific header fields, raw dword data, and receive-drop status. The header follows the kernel tracepoint pattern where helper definitions are guarded but `trace/define_trace.h` inclusion remains outside the include guard.

## Important APIs, Types, and Functions

The tracepoint surface consists of event class `tb_raw`, concrete events `tb_tx` and `tb_event`, and `TRACE_EVENT(tb_rx)`. Helper macros `tb_cfg_type_name()` and `show_type_name()` map package type constants such as `TB_CFG_PKG_READ`, `WRITE`, `ERROR`, `EVENT`, `ICM_EVENT`, `ICM_CMD`, and `ICM_RESP` to symbolic names. Inline formatting helpers `show_data_read_write()`, `show_data_error()`, `show_data_event()`, `show_route()`, and `show_data()` interpret raw `u32` payloads as Thunderbolt config packet structures from `tb_msgs.h`.

## Control Flow

At trace runtime, callers pass a domain index, type byte, data pointer, and byte size. `TP_fast_assign` stores the index/type, converts byte size to dword count, and copies the payload into a dynamic trace array. `TP_printk` then prints the symbolic type and delegates raw payload formatting to `show_data()`. That helper emits packet-specific fields for read/write, error, event, and ICM packets, then appends the raw dword array. `tb_rx` follows the same path and adds a `dropped` field to indicate packets not matched to a request.

## State and Persistence Behavior

Tracepoints do not own persistent driver state. They copy packet data into the ftrace ring buffer when enabled. Formatting state is transient in `struct trace_seq`. Trace output persistence is controlled by kernel tracing infrastructure, not this header.

## Dependencies and Integration Points

The header depends on Linux tracepoint APIs, `trace_seq`, `tb_msgs.h` packet layouts, and `tb_cfg_get_route()`. `ctl.c` calls `trace_tb_tx()` when sending, `trace_tb_event()` for event packets, and `trace_tb_rx()` when receiving. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` are set so kernel trace generation can find this header from the Thunderbolt driver directory.

## Risks and Edge Cases

The dynamic array length uses `size / 4`, while `memcpy()` copies `size` bytes. Callers must pass sizes that are valid multiples of four and backed by enough memory for the casted packet structures used by formatting helpers. Unknown package types still call `show_route()`, so malformed short packets could be unsafe if traced from a bad caller. ICM packets force `route=0`, which is an inference based on current message semantics. Trace output is diagnostic only, but wrong formatting can mislead debugging of control-channel failures.

## Test Signals

Compile coverage with tracing enabled is the basic signal. Runtime signals include enabling `thunderbolt:tb_tx`, `thunderbolt:tb_rx`, and `thunderbolt:tb_event` under ftrace, checking READ/WRITE/ERROR/EVENT/ICM formatting against known packets, and fuzz or fault-injection tests in the control layer to ensure dropped/unknown packets do not break tracing.
