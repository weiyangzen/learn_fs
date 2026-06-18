# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debug.c

## Purpose
`debug.c` centralizes ath11k logging wrappers and debug hex dumps. It routes informational, warning, error, and conditional debug messages to device logging and tracepoints.

## Important APIs, Types, And Functions
Exported always-on wrappers are `ath11k_info()`, `ath11k_err()`, and `ath11k_warn()`. Under `CONFIG_ATH11K_DEBUG`, `__ath11k_dbg()` and `ath11k_dbg_dump()` are exported. The wrappers use `struct va_format` so the same formatted message can be sent to `dev_*` logging and `trace_ath11k_log_*` tracepoints.

## Control Flow
Info/error/warn functions build a varargs format and emit to `dev_info`, `dev_err`, or rate-limited `dev_warn`, then trace. Debug logging checks `ath11k_debug_mask` before printing to the device, but it always sends matching tracepoint data when `__ath11k_dbg()` is invoked. `ath11k_dbg_dump()` prints 16-byte hex lines when the mask is enabled and also traces the full dump buffer with null-safe strings.

## State And Persistence
The only external state is the module-global `ath11k_debug_mask` defined in `core.c`. Logs are transient kernel log/trace data; no driver-private persistent state is stored.

## Dependencies And Integration Points
The file depends on `core.h`, `debug.h`, tracepoint definitions, Linux device logging, and hex dump helpers. It is used across nearly all ath11k modules for consistent diagnostics.

## Risks And Test Signals
Risk is mostly diagnostic overhead and format correctness. Warnings are rate-limited, so repeated failures may be hidden in stress logs. Debug dumps can be large when enabled. Test signals include build coverage with and without `CONFIG_ATH11K_DEBUG`, tracepoint enablement, dynamic `debug_mask` changes, and ensuring no NULL `ab`/`dev` callers reach these wrappers.
