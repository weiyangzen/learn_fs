<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/log.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/log.c research

Purpose: provides the debug logging backend for `CONFIG_BATMAN_ADV_DEBUG` builds by emitting formatted messages to the batman-adv tracepoint.

Important APIs and functions: `batadv_debug_log()` takes `bat_priv` and a printf-style format, wraps the variadic arguments in `struct va_format`, calls `trace_batadv_dbg()`, and returns 0.

Control flow and state behavior: there is no buffering or persistent storage in this file. Filtering and rate limiting happen in macros from `log.h` before this function is called. The tracepoint consumer decides where messages are observed.

Dependencies and integration: includes `trace.h` and `log.h`. It is reached by `batadv_dbg()`, `batadv_info()`, and `batadv_err()` when debug logging is enabled and the relevant log level bit is set.

Risks: because it forwards a live `va_list` through `va_format`, tracepoint formatting must happen during the function call. The function always returns success, so callers cannot detect trace backend failures.

Test signals: debug build compilation, dynamic tracepoint enablement, log level filtering via `log.h`, formatted messages with MAC/IP specifiers, and ensuring no calls are emitted when debug is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/log.c -->
