# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/permassert.c

## Purpose
`permassert.c` implements VDO permanent assertion failure logging. Unlike a kernel BUG, assertions return a VDO/UDS error code after logging diagnostic context and a stack trace.

## Important APIs, Types, and Functions
The single public function is `vdo_assertion_failed(const char *expression_string, const char *file_name, int line_number, const char *format, ...)`.

## Control Flow
On assertion failure, the function formats the caller-supplied message inside a standard assertion prefix/suffix with expression, file, and line, logs it at error priority via `vdo_log_embedded_message()`, emits a backtrace, ends the varargs, and returns `UDS_ASSERTION_FAILED`.

## State and Persistence Behavior
No state is stored. The only side effect is kernel logging.

## Dependencies and Integration Points
It depends on `errors.h` for the assertion error code and `logger.h` for logging/backtrace. The macros in `permassert.h` route failed assertions here throughout VDO/UDS.

## Risks and Edge Cases
Assertions are not fatal by themselves; callers must return or handle the error where `VDO_ASSERT()` is used. `VDO_ASSERT_LOG_ONLY()` callers intentionally continue after logging, which can expose later failures if used for invariants that should stop flow.

## Test Signals
Inject failed assertions and verify return code, formatted expression/file/line, message content, and backtrace logging. Compile-time format checking comes from the header attributes.
