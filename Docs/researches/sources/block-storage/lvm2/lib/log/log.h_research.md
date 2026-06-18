# File Research: sources/block-storage/lvm2/lib/log/log.h

## Purpose
Defines LVM's logging levels, debug classes, journal/debug field flags, user-facing logging macros, system-call logging macros, and common error-return convenience macros.

## Main Contents
- Defines internal log levels from fatal through debug, plus stderr-forcing, once-only, and report-bypass bits.
- Defines `INTERNAL_ERROR` prefix used by fatal internal-error handling.
- Defines debug output/file field masks for time, command, file/line, and message fields.
- Defines journald option bits for command, output, and debug logging.
- Defines debug classes for memory, devices, activation, allocation, metadata, cache, locking, lvmpolld, dbus, and I/O.
- Maps common macros such as `log_error`, `log_warn`, `log_print`, `log_verbose`, `log_debug_*`, and `stack` onto lower-level `LOG_LINE`/`LOG_LINE_WITH_ERRNO` primitives.
- Defines system-call error helpers that include `strerror(errno)`.
- Defines convenience macros such as `return_0`, `return_NULL`, `goto_out`, and `goto_bad` that log a debug backtrace before control transfer.

## Dependencies
Includes only errno/string headers directly, but expects lower-level logging primitives and mode helpers to be available through broader LVM logging includes.

## Risk Notes
The visible behavior of many LVM commands is shaped by these macros: `log_print` is warning-level without forced stderr, `log_warn` forces stderr, and `stack` is just a debug message. Changing level mappings affects terminal output, reports, syslog, journald, and tests that inspect command output.
