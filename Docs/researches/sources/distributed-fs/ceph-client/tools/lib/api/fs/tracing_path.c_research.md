<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/tracing_path.c -->
# sources/distributed-fs/ceph-client/tools/lib/api/fs/tracing_path.c

## Purpose
`tracing_path.c` centralizes discovery and path construction for Linux ftrace/tracepoint event files. It prefers tracefs and falls back to debugfs tracing, matching older and newer kernel layouts.

## Important APIs, types, and functions
State is held in static `char tracing_path[PATH_MAX]`, initially `/sys/kernel/tracing`. Public functions include `tracing_path_mount()`, `tracing_path_set()`, `get_tracing_file()`, `put_tracing_file()`, `get_events_file()`, `put_events_file()`, `tracing_events__opendir()`, `tracing_events__scandir_alphasort()`, and `tracing_path__strerror_open_tp()`. Private helpers mount tracefs/debugfs and set `tracing_path`.

## Control flow
`tracing_path_mount()` first calls `tracefs__mount()` and uses the mountpoint directly if available. If not, it calls `debugfs__mount()` and appends `tracing/`. Path constructors allocate strings with `asprintf()`. Directory helpers open or scan the `events` directory. The strerror helper formats actionable messages for missing tracepoints, missing tracing filesystems, permission failures, and generic errors.

## State and persistence behavior
The static `tracing_path` buffer is process-global and mutable. `tracing_path_set()` allows callers to override it. Allocated path strings are caller-owned and freed by the matching `put_*()` helpers.

## Dependencies and integration points
It depends on `fs.h` mount helpers, GNU `asprintf`, `<dirent.h>`, Linux `str_error_r()`, and tracefs/debugfs filesystem availability. It is used by perf-style tools that enumerate or open tracepoint event files.

## Risks and edge cases
`get_tracing_file()` concatenates `tracing_path_mount()` and `name` without inserting a slash; callers must pass names with the expected leading slash or rely on the stored path ending in slash for debugfs. Some helpers call `put_events_file()` on strings allocated by `get_tracing_file()`, which is equivalent today but semantically confusing. The global path is unsynchronized.

## Test signals
Test with tracefs mounted, only debugfs tracing available, neither available, and permission-denied event files. Verify generated paths for names with and without leading slashes, event directory scans, and formatted error messages for ENOENT/EACCES.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/tracing_path.c -->
