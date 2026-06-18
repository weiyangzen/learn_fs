<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/core.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/core.h

## Purpose
This public header defines libperf's core symbol-export macro, print levels, logging callback type, and initialization entry point.

## Important APIs, Types, and Functions
- `LIBPERF_API` defaults to `extern __attribute__((visibility("default")))`, marking installed library symbols for export.
- `enum libperf_print_level` defines `ERR`, `WARN`, `INFO`, `DEBUG`, `DEBUG2`, and `DEBUG3`.
- `libperf_print_fn_t` is a printf-style callback taking a level, format string, and `va_list`.
- `libperf_init(libperf_print_fn_t fn)` installs the caller's print function.

## Control Flow and State
This header only declares the public setup contract. Runtime state lives in libperf implementation files: the installed callback is used by `libperf_print` and `pr_*` wrappers from `internal.h`.

## Dependencies and Integration Points
It depends on `<stdarg.h>` and is included by almost every public libperf header. Tests install local callbacks with `libperf_init` before exercising maps, evsels, and evlists.

## Risks and Test Signals
Changing enum ordering or callback signature is ABI-visible. Consumers that pass `NULL` or callbacks with incompatible formatting behavior can lose diagnostics. Tests validate initialization implicitly by routing libperf messages through local `vfprintf` callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/perf/core.h -->
