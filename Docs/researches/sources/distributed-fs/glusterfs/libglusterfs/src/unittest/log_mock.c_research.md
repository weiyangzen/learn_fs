# sources/distributed-fs/glusterfs/libglusterfs/src/unittest/log_mock.c

## Purpose

`log_mock.c` provides no-op cmocka-friendly replacements for Gluster logging entry points so unit tests can link code that logs without initializing the full logging subsystem or emitting output.

## Important APIs, Types, and Functions

The mock functions are `_gf_log()`, `_gf_log_callingfn()`, `_gf_log_nomem()`, `_gf_msg_nomem()`, and `gf_log_globals_init()`. The logging functions accept the same metadata and varargs shapes as real logging functions and return zero; initialization is an empty function.

## Control Flow and Data Flow

All logging calls return immediately and discard domain, file, function, line, level, format, size, and varargs. No formatting is performed and no messages are recorded.

## State and Persistence Behavior

There is no state and no persisted log output. The mock suppresses logging side effects entirely.

## Dependencies and Integration Points

The file depends on Gluster logging and xlator declarations plus cmocka includes for the unit-test build environment. It integrates with tests that focus on non-logging behavior but need to satisfy linker references to logging symbols.

## Risks and Edge Cases

Because messages are discarded, tests using this mock cannot assert log content, formatting, rate limiting, or log-level behavior. Varargs are not consumed beyond function call ABI handling, so format-string bugs in code under test may remain hidden. Returning success for all logging paths can mask failures in code that reacts to logging initialization problems.

## Test Signals

The main signal is successful linkage and silent execution of code paths that call logging. Tests that need logging assertions should use a different mock that records calls and arguments.
