# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-debug.c

## Purpose
Implements iwlwifi logging wrappers that route warning/info/critical/error/debug messages to the kernel device log and iwlwifi tracepoints.

## Important APIs, Types, and Functions
Exports `__iwl_warn`, `__iwl_info`, `__iwl_crit`, `__iwl_err`, and conditionally `__iwl_dbg`. `__iwl_err()` supports regular, RFKILL-prefixed, trace-only, and ratelimited modes. `__iwl_dbg()` checks debug masks and trace support.

## Control Flow
Variadic wrappers package messages in `struct va_format`. Errors optionally print to `dev_err()` depending on mode and ratelimit, then always emit the tracepoint. Debug prints go to `dev_printk(KERN_DEBUG)` only when `CONFIG_IWLWIFI_DEBUG` and level match, then emit debug tracepoint.

## State and Persistence Behavior
No persistent state except reading `iwlwifi_mod_params.debug_level` indirectly. Output persists in kernel logs or tracing buffers.

## Dependencies and Integration Points
Depends on Linux device logging, `net_ratelimit()`, exported symbol namespace helpers, and tracepoints from `iwl-devtrace.h`.

## Risks
Varargs are consumed twice in error paths using `va_copy`; mistakes here would corrupt log output. Trace-only errors intentionally skip device log output but still trace.

## Test Signals
Regular/RFKILL/ratelimited/trace-only errors, debug enabled/disabled builds, device tracing enabled/disabled builds, newline macro enforcement at call sites, and tracepoint message capture are useful signals.
