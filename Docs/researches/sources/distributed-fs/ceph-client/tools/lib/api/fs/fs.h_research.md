<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/fs.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/fs/fs.h

## Purpose
`fs.h` is the public libapi interface for pseudo-filesystem mount discovery and simple sysfs/procfs file I/O. It hides common path construction and parsing for tool code.

## Important APIs, types, and functions
The `FS(name)` macro declares `name__mountpoint()`, `name__mount()`, and `name__configured()` for `sysfs`, `procfs`, `debugfs`, `tracefs`, `hugetlbfs`, and `bpf_fs`. The header also declares `cgroupfs_find_mountpoint()`, filename-level read/write helpers, `procfs__read_str()`, `sysctl__read_int()`, and typed `sysfs__read_*()`/`sysfs__write_int()` helpers. It defines `PATH_MAX` as 4096 if libc did not.

## Control flow
The header itself has no execution. The declared mountpoint functions perform lazy discovery in `fs.c`; read helpers return zero on success or negative/error values depending on the path.

## State and persistence behavior
State is internal to the implementation, mostly cached mount paths. Callers own buffers returned by `filename__read_str()`, `procfs__read_str()`, and `sysfs__read_str()` and must free them.

## Dependencies and integration points
It includes `<stdbool.h>` and `<unistd.h>` and is installed as `include/api/fs/fs.h`. It is used by libapi CPU/tracing helpers and external tools.

## Risks and edge cases
Return conventions are not fully uniform: some helpers return `-errno`, others return `-1`. Callers must not assume all failures map directly to errno. The header does not annotate ownership for returned strings.

## Test signals
Compile installed-header users and exercise the implementation tests for `fs.c` and `cgroup.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/fs.h -->
