# File Research: sources/block-storage/lvm2/lib/log/log.c

## Purpose
Implements LVM2's central logging engine. It routes formatted messages to stderr/stdout, optional command reports, optional custom file descriptors, optional log files, syslog, systemd journal, stored error buffers, and optional external library log callbacks.

## Main Responsibilities
- Maintains global logging configuration for syslog, file logging, journal fields, indentation, suppression, message prefix, debug field selection, and internal-error abort behavior.
- Supports custom output, error, and report streams from caller-provided file descriptors with line buffering.
- Reopens standard streams safely and updates custom stream references when standard `FILE *` objects change.
- Opens debug log files, including environment-controlled epoch suffixes based on PID and `/proc/self/stat` start time.
- Supports line-limited log files through `LVM_LOG_FILE_MAX_LINES` and conditional unlinking through `LVM_EXPECTED_EXIT_STATUS`.
- Stores the first LVM error number and an optional accumulated error-message buffer up to 512 KiB.
- Deduplicates `log_error_once` messages by hashing formatted message text.
- Converts log report context/object enums to names and writes command log rows through report infrastructure.
- Formats and emits log messages in `_vprint_log`, applying verbosity, debug classes, report routing, external callback routing, journald/syslog routing, and fatal internal-error abort handling.
- Sends command records to journald when configured.
- Converts journal option strings into bit flags.

## Important Control Flow
`_vprint_log` first checks whether internal errors should be fatal based on `DM_ABORT_ON_INTERNAL_ERRORS` or config. It formats the message early when needed for stored errors, reporting, external callbacks, or deduplication. Report logging temporarily clears `_log_report.report` to avoid recursion through logging.

Visible terminal output depends on `verbose_level`, stderr forcing, warning-vs-print semantics, debug class filters, and optional debug output field masks. Log-file output is separately gated by `debug_level`, debug class filters, and critical-section suspension rules. Syslog and journald receive messages only when configured and not suppressed by critical-section rules unless `log_while_suspended` is set.

`print_log_libdm` redirects normal libdm warning-level output to the report stream and bypasses report integration for common non-error output.

## Dependencies
Depends on LVM command/log helper functions, device headers for custom fd structures, memlock critical-section state, report command-log output, file helpers, syslog, optional systemd journal support, and `/proc/self/stat` parsing for log epoch file names.

## Risk Notes
- Logging is global mutable state; concurrent or nested use must avoid report recursion and unexpected stream replacement.
- Stored error messages can grow to 512 KiB and are manually reallocated; reset ownership matters.
- `log_once` deduplication keys on formatted message text, so variable data prevents deduplication.
- Fatal internal-error behavior can be enabled by environment and calls `abort` after logging.
- Critical sections suppress file/syslog output unless explicitly configured, which avoids unsafe logging while suspended.
