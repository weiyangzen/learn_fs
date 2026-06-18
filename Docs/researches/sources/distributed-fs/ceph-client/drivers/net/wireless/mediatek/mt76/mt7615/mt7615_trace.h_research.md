# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mt7615_trace.h

Purpose: Defines mt7615-specific Linux tracepoints, currently a reusable device/token event class and the `mac_tx_free` event.

Important APIs and types: `DECLARE_EVENT_CLASS(dev_token)` records the wiphy name and a TX token. `DEFINE_EVENT(dev_token, mac_tx_free, ...)` instantiates the trace event. Macros `DEV_ENTRY`, `DEV_ASSIGN`, `TOKEN_ENTRY`, and related print macros keep tracepoint field definitions consistent.

Control flow and integration: Included by `trace.c` with `CREATE_TRACE_POINTS` to emit tracepoint definitions and included by other code for declarations. Runtime users can enable the `mt7615:mac_tx_free` tracepoint through ftrace/perf to observe token completion behavior.

State and persistence: No persistent state. Each trace event snapshots the wiphy name and token at emission time.

Dependencies: Linux tracepoint infrastructure and `mt7615.h` for `struct mt7615_dev` and `mt76_hw()`. `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` are set for kernel trace generation.

Risks: Trace headers are sensitive to include guards and `TRACE_HEADER_MULTI_READ`; wrong names or paths break generated trace code. `strscpy()` bounds the wiphy name to 32 bytes, so trace names can truncate.

Test signals: Kernel build with tracepoints enabled, presence of generated trace events under tracing, and successful event emission during TX token free paths.
