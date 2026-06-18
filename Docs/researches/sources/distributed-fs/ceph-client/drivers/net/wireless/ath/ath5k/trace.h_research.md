# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/trace.h

Purpose: Defines optional ath5k ftrace tracepoints for RX, TX enqueue, and TX completion events, with no-op inline fallbacks when tracing is disabled.

Important APIs and events: `TRACE_EVENT(ath5k_rx)` records driver private pointer, skb address, and a dynamic copy of the received frame. `TRACE_EVENT(ath5k_tx)` records private pointer, skb address, queue number, and a dynamic copy of the transmitted frame. `TRACE_EVENT(ath5k_tx_complete)` records private pointer, skb address, queue number, status, RSSI, and antenna. When `CONFIG_ATH5K_TRACER` is not enabled, `TRACE_EVENT` is redefined to static inline `trace_*` stubs.

Control flow: Including code calls generated `trace_ath5k_*()` helpers at datapath points. If tracing is enabled, tracepoint infrastructure captures metadata and optional frame bytes; otherwise calls compile away to no-op inline functions. The bottom include of `<trace/define_trace.h>` materializes tracepoints when the header is included by the trace definition translation unit.

State and persistence: No driver state is owned. Trace buffers are managed by the kernel tracing subsystem and are transient. The dynamic arrays copy skb payload bytes at trace time.

Dependencies and integration points: Depends on `<linux/tracepoint.h>`, `struct sk_buff`, ath5k TX queue/status types, `TRACE_SYSTEM ath5k`, and build configuration `CONFIG_ATH5K_TRACER`. It integrates with trace-cmd/perf/ftrace and ath5k RX/TX datapath instrumentation.

Risks: Capturing full frame bytes can expose packet contents and add overhead when tracepoints are enabled. The fallback macro must keep call signatures compatible with enabled tracepoints. `TRACE_INCLUDE_PATH .` assumes trace build include paths are set correctly.

Test signals: Build with and without `CONFIG_ATH5K_TRACER`, enable each tracepoint under ftrace, verify RX/TX/TX-complete records include expected queue/status metadata, confirm no unresolved trace symbols in disabled builds, and measure datapath overhead when tracepoints are active.
