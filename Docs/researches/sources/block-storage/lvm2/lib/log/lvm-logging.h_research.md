# File Research: sources/block-storage/lvm2/lib/log/lvm-logging.h

Purpose: declares LVM2's core logging interface, log initialization/finalization hooks, stream/syslog/journal configuration, error-message storage accessors, and reporting-context state used to route logs into structured reports.

Read coverage: complete file read, 139 lines.

Key responsibilities:
- Declares `print_log()` and `print_log_libdm()` with printf-format checking and wraps them through `LOG_LINE*` macros that inject source file and line.
- Exposes initialization for custom file descriptors, standard streams, custom log callback functions, indentation, message prefixes, debug fields, log files, syslog, journald fields, suspended-device logging, and abort-on-internal-error behavior.
- Provides lifecycle calls such as `fin_log()`, `reset_log_duplicated()`, `fin_syslog()`, and `unlink_log_file()`.
- Defines stored errno/message helpers used after command failures: `reset_lvm_errno()`, `stored_errno()`, `stored_errmsg()`, and `stored_errmsg_with_clear()`.
- Defines suppression controls for general logging and syslog.
- Defines `log_report_t` plus report context/object enums for emitting command, PV, VG, LV, label, orphan, and pre-command log records through `dm_report`.

Dependencies:
- Includes `lib/misc/lvm-file.h`, `lib/log/log.h`, and uses `struct dm_report`, `struct id`, `FILE`, and `uint32_t`.
- Implemented by the logging subsystem and consumed broadly by command, metadata, activation, and daemon code.

Risk and edge cases:
- The printf-format attributes protect callers only if function signatures remain aligned with the macros.
- Report state is global process state; callers that temporarily set report context/object fields must restore state to avoid misattributing later log messages.
- `log_suppress()` distinguishes suppression to stdout/stderr from suppression everywhere, so callers need the right level for quiet or machine-readable modes.
