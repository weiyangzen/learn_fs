# sources/distributed-fs/ceph-client/net/mac80211/trace_msg.h

## Purpose
This header declares the optional `mac80211_msg` tracepoint system used to capture formatted mac80211 debug/info/error messages as trace events when `CONFIG_MAC80211_MESSAGE_TRACING` is enabled.

## Important APIs, types, and functions
- `DECLARE_EVENT_CLASS(mac80211_msg_event)` defines a single `struct va_format *` based event class with a dynamic formatted string field.
- `mac80211_info`, `mac80211_dbg`, and `mac80211_err` are concrete events derived from the class.
- `__vstring()` and `__assign_vstr()` store the formatted message in the trace record.

## Control flow
When message tracing is configured, the header defines trace declarations under `TRACE_SYSTEM mac80211_msg`. `trace.c` includes it with `CREATE_TRACE_POINTS` to instantiate events. The wrappers in `trace.c` call `trace_mac80211_info()`, `trace_mac80211_dbg()`, or `trace_mac80211_err()` after preparing a `va_format`.

## State and persistence
The header defines event schema only. Each event snapshots one formatted message string into the tracing ring buffer. No mac80211 state is changed, and no message history is persisted outside the tracing subsystem.

## Dependencies and integration points
It depends on Linux tracepoint infrastructure, public mac80211 types, and `ieee80211_i.h`. It integrates with `debug.h` message macros through the wrapper functions implemented in `trace.c`. The final `TRACE_INCLUDE_FILE trace_msg` block is required so the trace generator can find this header when building trace definitions.

## Risks and edge cases
The trace event formats variadic strings, so invalid format strings or mismatched arguments in callers affect both printk and tracing paths. Enabling message tracing increases overhead and can expose operational messages in trace buffers. Because the whole header is under `CONFIG_MAC80211_MESSAGE_TRACING`, callers must be guarded by the corresponding debug wrapper definitions.

## Test signals
Build success with `CONFIG_MAC80211_MESSAGE_TRACING=y` verifies trace declaration and instantiation. Runtime signal is the presence of `mac80211_msg/mac80211_info`, `mac80211_msg/mac80211_dbg`, and `mac80211_msg/mac80211_err` events and matching formatted messages when mac80211 debug wrappers run.
