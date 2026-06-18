<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/tracing_path.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/fs/tracing_path.h

## Purpose
`tracing_path.h` declares libapi helpers for locating tracefs/debugfs tracing files and formatting tracepoint-open errors.

## Important APIs, types, and functions
It declares directory helpers `tracing_events__opendir()` and `tracing_events__scandir_alphasort()`, mount/path helpers `tracing_path_set()` and `tracing_path_mount()`, allocated string constructors `get_tracing_file()` and `get_events_file()` with matching free helpers, `zput_events_file(ptr)`, and `tracing_path__strerror_open_tp()`.

## Control flow
Callers obtain a mount path or allocated file path, operate on it, and free it. The error helper converts errno values and tracepoint names into user-facing diagnostic strings.

## State and persistence behavior
The implementation owns a global tracing path; callers own allocated strings returned by `get_*_file()`.

## Dependencies and integration points
It includes `<linux/types.h>` and `<dirent.h>`, and is installed under `include/api/fs`. It is intended for perf-like tools that interact with trace events.

## Risks and edge cases
`zput_events_file()` uses `free()` but this header does not include `<stdlib.h>` directly, so include order can matter. Ownership is conventional rather than type-enforced.

## Test signals
Compile consumers using only the installed header plus standard includes, and run implementation tests from `tracing_path.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/tracing_path.h -->
