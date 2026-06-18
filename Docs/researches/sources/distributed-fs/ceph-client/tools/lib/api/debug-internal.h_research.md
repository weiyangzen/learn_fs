<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/debug-internal.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/debug-internal.h

## Purpose
`debug-internal.h` is the private libapi logging facade. It lets internal libapi code emit warn/info/debug messages through callback pointers configured by the public debug API.

## Important APIs, types, and functions
It includes `debug.h`, declares the global callback variables `__pr_warn`, `__pr_info`, and `__pr_debug`, and defines `pr_warn()`, `pr_info()`, and `pr_debug()` through the `__pr(func, fmt, ...)` macro. The macro prefixes messages with `libapi: ` and suppresses output when the callback pointer is `NULL`.

## Control flow
Each logging macro checks the selected function pointer before calling it. The callback is expected to behave like `printf`, accepting a format string and variadic arguments.

## State and persistence behavior
The header exposes mutable process-global function pointers defined in `debug.c`. Those settings persist for the lifetime of the process or until `libapi_set_print()` replaces them.

## Dependencies and integration points
This file is internal to `tools/lib/api`. Public consumers should use `debug.h` and `libapi_set_print()`, while libapi implementation files can include this header for prefixed logging.

## Risks and edge cases
The callback pointers are global and unsynchronized, so concurrent changes from multiple threads can race with logging. Format-string type safety depends entirely on compiler checks at call sites and callback compatibility.

## Test signals
Build with warnings enabled to catch format issues. Runtime tests can set callbacks to capture strings and verify prefixes, NULL suppression, and warn/info/debug routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/debug-internal.h -->
