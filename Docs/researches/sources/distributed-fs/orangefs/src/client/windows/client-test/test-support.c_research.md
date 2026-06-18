# sources/distributed-fs/orangefs/src/client/windows/client-test/test-support.c

Purpose: Implements small support routines for the OrangeFS Windows client test programs: path generation, zero-byte file creation, and standardized result/performance reporting.

Important APIs/functions: `quickcat()` allocates and concatenates two strings. `randdir()` and `randfile()` normalize a root path with `SLASH_CHAR`/`SLASH_STR`, append randomized names, and return caller-owned strings. `quick_create()` creates an empty file via `fopen(..., "w")`. `report_error()`, `report_result()`, and `report_perf()` route formatted messages to console and/or a report file according to `global_options.report_flags`.

Control flow: Reporting is synchronous and simple. `report_result()` compares `actual_code` to `expected_code` using the requested operator, constructs a line with test name, subtest, expectation, expected code, actual code, and `OK`/`NOT_OK`, then writes to enabled sinks.

State/persistence: No durable state besides files created by `quick_create()` and output appended through `freport`. All generated path strings are heap-allocated and must be freed by callers.

Dependencies/integration: Includes `test-support.h` for constants and `timer.h` though this file does not call timer functions. Integrates with the broader client-test framework through the shared `global_options` struct.

Risks: `quickcat()` does not check `malloc()` before `sprintf()`. Random name formatting uses fixed 16-byte buffers and unseeded/global `rand()`. `report_result()` lacks a default case if `code_operation` is invalid, leaving `comp` undefined. `_snprintf()` truncation handling falls back to a fixed overflow message.

Test signals: Exercise all report flags, each comparison operator, report file flushing, null roots in `randdir()`/`randfile()`, and creation failure paths.
