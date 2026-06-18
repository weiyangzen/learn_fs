<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/fs.c -->
# sources/distributed-fs/ceph-client/tools/lib/api/fs/fs.c

## Purpose
`fs.c` is libapi's filesystem discovery and simple file-value I/O layer. It finds and optionally mounts common pseudo-filesystems used by tools (`sysfs`, `procfs`, `debugfs`, `tracefs`, `hugetlbfs`, and bpffs), then offers helpers for reading and writing numeric/string values under those mounts.

## Important APIs, types, and functions
`struct fs` records a filesystem name, known mountpoint list, cached path, mount mutex, and magic number. The `FS()` macro generates `name__mountpoint()`, `name__mount()`, and `name__configured()` for each supported filesystem. Helpers include `fs__read_mounts()`, `fs__valid_mount()`, `fs__check_mounts()`, `fs__env_override()`, `fs__mount()`, `filename__read_int()`, `filename__read_ull()`, `filename__read_xll()`, `filename__read_str()`, `filename__write_int()`, `procfs__read_str()`, `sysctl__read_int()`, `sysfs__read_*()`, and `sysfs__write_int()`.

## Control flow
On first `*_mountpoint()` call, `pthread_once()` runs initialization: environment override (`NAME_PATH`), known mountpoint statfs checks, then `/proc/mounts` scan. `*_mount()` returns the cached mountpoint or attempts `mount(NULL, mountpoint, fs->name, 0, NULL)` under a mutex. Read helpers resolve a mountpoint, format a path, open/read/parse, and close.

## State and persistence behavior
Each filesystem has a static `struct fs` and a cached heap `path` that persists for the process lifetime. Initialization is once-only; mount changes after first lookup are not observed. Read/write helpers do not cache values.

## Dependencies and integration points
It uses Linux magic constants, `statfs`, `/proc/mounts`, environment variables such as `SYSFS_PATH`, `mount(2)`, pthread once/mutex primitives, local buffered `io.h`, and `debug-internal.h`. It underpins `cpu.c`, tracing path helpers, and many tools that need sysfs/procfs/debugfs paths.

## Risks and edge cases
`mount_overload()` uses `snprintf(upper_name, name_len, ...)`, which cannot write the full `PERF_<name>_ENVIRONMENT` string and limits the environment override path. `filename__write_int()` writes the full 64-byte buffer instead of the formatted string length, which can send trailing NULs/spaces to sysfs-like files. Numeric reads use `atoi()`/`strtoull()` without rigorous error-end validation. Once-only caching can become stale after remounts.

## Test signals
Use temporary mount namespaces or environment overrides to test mount discovery order, magic validation, and mount fallback. Mock files should cover integer, hex, bool, long string, missing path, oversized path, and write behavior. Threaded tests should call mount helpers concurrently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/fs.c -->
