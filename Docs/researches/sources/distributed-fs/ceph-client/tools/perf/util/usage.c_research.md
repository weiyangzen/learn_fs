# sources/distributed-fs/ceph-client/tools/perf/util/usage.c

## Purpose

`usage.c` provides perf's generic usage strings and a basic usage reporting hook.

## Important APIs, Types, and Functions

It defines `perf_usage_string`, `perf_more_info_string`, static `usage_builtin()`, a static `usage_routine` pointer initialized to that builtin, and public `usage(const char *err)`.

## Control Flow and State

`usage()` calls the current usage routine, which prints `Usage: <err>` to stderr and exits with status 129. The routine pointer is kept static to avoid writes through globals in dlopened shared objects.

## Dependencies and Integration Points

It depends on stdio/stdlib and is included through `util.h`. CLI command parsing calls `usage()` on fatal syntax errors.

## Risks and Test Signals

Risks are limited: `usage()` is noreturn and unsuitable for recoverable errors. Tests should verify output and exit status for invalid command invocations.
