# File Research: sources/block-storage/kvdo/vdo/logger.h

Logging API and convenience macros for UDS/VDO kernel code.

Key responsibilities:
- Defines UDS log priority constants compatible with syslog ordering.
- Defines `UDS_LOGGING_MODULE_NAME` from `THIS_MODULE->name` or `"vdo"`.
- Provides a `uds_log_ratelimit()` wrapper macro.
- Declares log-level get/set and priority conversion helpers.
- Declares varargs logging functions and strerror logging helpers.
- Defines level-specific macros: debug, info, notice, warning, error, fatal, and corresponding strerror variants.
- Declares `uds_log_backtrace()` and `uds_pause_for_logger()`.

Dependencies:
- Linux module and ratelimit headers.

Notable risks:
- The strerror macros include trailing semicolons in macro definitions; they are intended for statement use.
- The rate-limit macro creates one static ratelimit state per call site.
