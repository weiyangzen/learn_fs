# sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_trace.h

Purpose: tracepoint definitions for the Qualcomm GLINK native protocol. It gives ftrace/perf users structured visibility into command exchange, channel IDs, intent flow, data chunks, read notifications, and signal changes.

Important APIs, types, and functions: the file defines `TRACE_SYSTEM qcom_glink` and multiple `TRACE_EVENT()` blocks: `qcom_glink_cmd_version`, `qcom_glink_cmd_version_ack`, `qcom_glink_cmd_open`, `qcom_glink_cmd_close`, `qcom_glink_cmd_open_ack`, `qcom_glink_cmd_intent`, `qcom_glink_cmd_rx_done`, `qcom_glink_cmd_rx_intent_req`, `qcom_glink_cmd_rx_intent_req_ack`, `qcom_glink_cmd_tx_data`, `qcom_glink_cmd_close_ack`, `qcom_glink_cmd_read_notif`, and `qcom_glink_cmd_signal`. For most events, `_tx` and `_rx` convenience macros append a direction boolean.

Control flow: this header is included by the GLINK native implementation with trace generation enabled. Each tracepoint captures immutable event fields via `TP_fast_assign()` and formats them via `TP_printk()`. `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` make the header self-contained for trace event generation.

State and persistence: no runtime state is owned by this file. Trace data is transient in the kernel tracing buffers and enabled only when selected tracepoints are active.

Dependencies and integration points: depends on Linux tracepoint infrastructure and `qcom_glink_native.h` for protocol-related types. It is an observability integration point for GLINK transports such as RPM and SMEM and for the GLINK core state machine.

Risks: tracepoint field schemas become user-visible ABI-like diagnostics; renaming fields or changing types can break tracing scripts. String capture uses `__string()`/`__assign_str()`, so callers must pass valid NUL-terminated remote and channel names. High-rate data events can add overhead when enabled.

Test signals: compile with tracing enabled, inspect `/sys/kernel/tracing/events/qcom_glink/*`, enable each event during GLINK channel open/data/close traffic, and verify tx/rx macros report correct direction, IDs, intent IDs, chunk sizes, and signals.
