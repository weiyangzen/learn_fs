# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logger.h

## Purpose
`logger.h` defines VDO logging priorities, module prefixing, public logging functions, and convenience macros used throughout VDO/UDS code.

## Important APIs, Types, and Functions
The header maps `VDO_LOG_*` constants to kernel log levels, declares `vdo_log_level`, `vdo_get_log_level()`, embedded/error/string/backtrace functions, and macros such as `vdo_log_error_strerror()`, `vdo_log_warning()`, `vdo_log_info()`, and `vdo_log_ratelimit()`.

## Control Flow
Macros wrap calls to implementation functions with the standard `VDO_LOGGING_MODULE_NAME`. `vdo_log_ratelimit()` creates a static ratelimit state at each call site and invokes the supplied log function only when allowed.

## State and Persistence Behavior
The only exposed state is the global runtime log level. No persistent state is defined.

## Dependencies and Integration Points
The header includes kernel log level, module, ratelimit, and device-mapper definitions. It is a common dependency of VDO modules and assertion helpers.

## Risks and Edge Cases
Because logging macros preserve caller errno only by convention in implementation, callers should avoid relying on side effects. Rate-limit state is per macro expansion site. Module prefixing depends on device-mapper `DM_NAME`.

## Test Signals
Compile-time format checking via `__printf` attributes, rate-limited logging coverage, and integration logs from error paths are key signals.
