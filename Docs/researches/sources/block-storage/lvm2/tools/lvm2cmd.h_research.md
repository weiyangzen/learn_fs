# File Research: sources/block-storage/lvm2/tools/lvm2cmd.h

## Purpose
Public C API header for embedding/running LVM2 commands through `liblvm2cmd`.

## API Surface
- Defines `lvm2_log_fn_t`, a callback receiving log level, source file, line, errno/class, and message.
- Logging constants:
  - `LVM2_LOG_SUPPRESS`
  - `LVM2_LOG_FATAL`
  - `LVM2_LOG_ERROR`
  - `LVM2_LOG_PRINT`
  - `LVM2_LOG_VERBOSE`
  - `LVM2_LOG_VERY_VERBOSE`
  - `LVM2_LOG_DEBUG`
- Return constants map to internal command statuses:
  - success, no such command, invalid parameters, init failed, processing failed.
- Public functions:
  - `lvm2_log_fn()`
  - `lvm2_init()`
  - `lvm2_init_threaded()`
  - `lvm2_disable_dmeventd_monitoring()`
  - `lvm2_log_level()`
  - `lvm2_run()`
  - `lvm2_exit()`

## Important Details
- Supports C++ callers via `extern "C"`.
- `lvm2_run()` accepts a nullable handle for one-off command execution.
- The header documents that the built-in log level defaults to `LVM2_LOG_PRINT`.

## Dependencies
No internal headers are exposed; this is the external ABI-facing interface.
