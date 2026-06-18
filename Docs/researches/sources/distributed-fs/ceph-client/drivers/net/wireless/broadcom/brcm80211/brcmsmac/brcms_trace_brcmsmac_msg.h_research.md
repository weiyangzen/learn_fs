# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_brcmsmac_msg.h

Purpose: defines tracepoints for brcmsmac log messages and debug messages.

Important APIs and tracepoints: `DECLARE_EVENT_CLASS(brcms_msg_event)` captures formatted `va_format` messages. `DEFINE_EVENT` creates `brcms_info`, `brcms_warn`, `brcms_err`, and `brcms_crit`. `TRACE_EVENT(brcms_dbg)` records debug level, function name, and formatted message. GCC diagnostics suppress format-suggestion warnings around trace macros.

Control flow: logging wrappers in `debug.c` emit normal device logs and then these tracepoints. When tracing is configured, `define_trace.h` materializes them.

State and persistence: no persistent state; trace buffers hold formatted message copies while tracing is active.

Dependencies and integration: depends on Linux tracepoint `__vstring` support and `struct va_format`. Integrated with brcms debug macros.

Risks and test signals: formatted varargs must remain valid for trace assignment inside the call. Test info/warn/err/crit and debug paths with tracing enabled and disabled, including dynamic debug levels.
