# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_debugfs.c

Purpose: debugfs support for ChromeOS EC internals, including console log streaming, panicinfo blob, USB-PD status, EC uptime, last resume result, and suspend timeout tuning.

Important APIs, types, and functions: `struct cros_ec_debugfs` stores EC pointer, debugfs dir, circular log buffer, preallocated console read command, delayed work, panicinfo blob, and panic notifier. `cros_ec_console_log_work()` snapshots and drains EC console logs. `cros_ec_create_console_log()` gates creation on console-read v1 support. `cros_ec_get_panicinfo()` fetches panic data. `cros_ec_pdinfo_read()` queries PD port status. `cros_ec_uptime_is_supported()` and `cros_ec_uptime_read()` expose uptime conditionally.

Control flow: probe creates a debugfs directory named for the EC, fetches panicinfo once, creates console log polling if supported, creates `pdinfo`, optional `uptime`, `last_resume_result`, and writable `suspend_timeout_ms`, then registers a panic notifier. Console work sends `EC_CMD_CONSOLE_SNAPSHOT`, repeatedly issues `EC_CMD_CONSOLE_READ` recent reads, appends data to a fixed circular buffer, wakes readers, and reschedules itself. Panic notifier forces an immediate log poll and flushes it. Suspend cancels log polling; resume schedules it again. Remove removes debugfs and cancels work.

State and persistence: log buffer is in memory and lossy when full. Panicinfo is a snapshot at probe. `suspend_timeout_ms` writes modify the core EC device value used by host sleep v1 commands. `last_resume_result` is updated by core resume handling.

Dependencies and integration points: depends on debugfs, delayed work, EC protocol commands, panic notifier from core EC, PD command definitions, and platform `cros-ec-dev` data.

Risks and edge cases: debugfs is diagnostic and not stable ABI. The circular log can drop data if EC output exceeds polling capacity. Remove unregisters debugfs but does not visibly unregister the panic notifier, so lifetime depends on platform-device teardown ordering and devm state; this is worth review. `pdinfo` stops at first failed port query, which is normal for absent ports but hides later sparse ports.

Test signals: debugfs file creation based on feature support, blocking/nonblocking console reads and poll, log flush on EC panic notifier, uptime feature detection, writable suspend timeout changing suspend command parameters, and suspend/resume cancel/reschedule behavior.
