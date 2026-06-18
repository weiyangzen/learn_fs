<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/debug.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/debug.h

## Purpose
`debug.h` is the public logging configuration API for libapi. It lets embedding tools customize how libapi warnings, informational messages, and debug messages are printed.

## Important APIs, types, and functions
`typedef int (*libapi_print_fn_t)(const char *, ...);` defines callback shape. `libapi_set_print(libapi_print_fn_t warn, libapi_print_fn_t info, libapi_print_fn_t debug)` installs callbacks for each logging channel.

## Control flow
The header has no executable logic. Consumers include it and call `libapi_set_print()` during initialization if default stderr logging is not desired.

## State and persistence behavior
State is owned by `debug.c` as global callback pointers. The header documents no ownership because callbacks are plain function pointers.

## Dependencies and integration points
It is installed as part of libapi headers and is included by `debug-internal.h`. Tools linking libapi can use it without including private headers.

## Risks and edge cases
The callback type is variadic; mismatched implementations are not strongly type-checked beyond the first argument. There is no thread-safety contract for changing callbacks after other threads start using libapi.

## Test signals
Compile a consumer against the installed header and link with `libapi.a`. Runtime tests are covered by `debug.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/debug.h -->
