<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/debug.c -->
# sources/distributed-fs/ceph-client/tools/lib/api/debug.c

## Purpose
`debug.c` implements libapi's configurable print callbacks. It provides default warning and info output to stderr and lets embedding tools redirect or silence messages.

## Important APIs, types, and functions
`__base_pr()` is a static variadic wrapper around `vfprintf(stderr, ...)`. The global callback variables `__pr_warn`, `__pr_info`, and `__pr_debug` back the internal macros from `debug-internal.h`; warn and info default to `__base_pr`, while debug defaults to `NULL`. `libapi_set_print()` assigns new callback pointers for all three channels.

## Control flow
Callers configure logging with `libapi_set_print(warn, info, debug)`. Later internal `pr_*` macros call the selected function if non-NULL. There is no validation or fallback when callbacks are NULL.

## State and persistence behavior
The three callback variables are process-global mutable state. Settings persist until overwritten and affect all libapi users in the same process.

## Dependencies and integration points
It depends on the public `debug.h` typedef and private `debug-internal.h` declarations. It is archived into `libapi.a` and used by filesystem helpers for warnings such as mount discovery issues.

## Risks and edge cases
Callback mutation is not thread-safe. A callback with incompatible variadic behavior can crash callers. Because debug defaults to NULL, debug messages disappear unless explicitly enabled.

## Test signals
Tests should verify default warn/info write to stderr, debug is silent by default, setting NULL suppresses a channel, and custom callbacks receive the `libapi:` prefix from internal macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/debug.c -->
