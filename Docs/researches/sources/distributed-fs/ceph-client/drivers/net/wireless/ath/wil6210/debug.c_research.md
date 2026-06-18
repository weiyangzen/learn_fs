# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/debug.c

## Purpose
`debug.c` centralizes `wil6210` logging wrappers so driver messages are emitted both to the netdevice log and to tracing when enabled.

## Important APIs, Types, and Functions
- `__wil_err()` emits error messages through `netdev_err()` and `trace_wil6210_log_err()`.
- `__wil_err_ratelimited()` wraps the same error path with `net_ratelimit()`.
- `wil_dbg_ratelimited()` rate-limits debug messages through `netdev_dbg()` and `trace_wil6210_log_dbg()`.
- `__wil_info()` emits info messages through `netdev_info()` and trace info.
- `wil_dbg_trace()` emits debug tracepoints without printing to netdev.
- All helpers use `struct va_format` to share a variadic format with both sinks.

## Control Flow
Each function builds a `va_list`, assigns it to `va_format`, emits to the appropriate netdev and/or trace sink, and then calls `va_end()`. The rate-limited variants return early if `net_ratelimit()` denies the message.

## State and Persistence Behavior
There is no persistent state. The functions read `wil->main_ndev` for logging context and emit transient kernel log/trace records.

## Dependencies and Integration Points
It depends on `wil6210.h` logging declarations/macros and `trace.h` tracepoint definitions. Other driver files use these wrappers instead of directly calling netdev logging.

## Risks and Test Signals
Risks include using a NULL or freed `main_ndev`, trace format lifetime mistakes, and suppressed diagnostics from global rate limiting during failure storms. Test signals are compile coverage with tracing enabled/disabled, visible netdev messages, tracepoint capture, and no warnings from variadic formatting paths.
