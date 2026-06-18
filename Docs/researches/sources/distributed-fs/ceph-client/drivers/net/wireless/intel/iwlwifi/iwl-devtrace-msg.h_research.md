# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-msg.h

## Purpose
Declares tracepoints for iwlwifi formatted log messages.

## Important APIs, Types, and Functions
Defines event class `iwlwifi_msg_event` and events `iwlwifi_err`, `iwlwifi_warn`, `iwlwifi_info`, `iwlwifi_crit`, plus `iwlwifi_dbg` with debug level and function name.

## Control Flow
Logging wrappers pass `struct va_format` to the tracepoints. The trace event stores formatted text using `__vstring`/`__assign_vstr`.

## State and Persistence Behavior
Messages persist only in trace buffers. No driver state changes.

## Dependencies and Integration Points
Used by `iwl-debug.c` and included through `iwl-devtrace.h`.

## Risks
Varargs formatting must happen while the `va_list` remains valid. Trace volume can be high with broad debug masks.

## Test Signals
Error/warn/info/crit/debug trace capture, debug function-name capture, long message truncation behavior through trace infrastructure, and tracing-disabled builds are relevant.
