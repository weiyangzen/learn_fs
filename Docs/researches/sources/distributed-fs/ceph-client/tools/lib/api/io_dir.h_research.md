<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/io_dir.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/io_dir.h

## Purpose
`io_dir.h` is a header-only low-level directory reader built on the `getdents64` syscall. It avoids stdio `DIR *` overhead for tools that need compact directory iteration.

## Important APIs, types, and functions
It defines `perf_getdents64()`, `struct io_dirent64`, and `struct io_dir`. Inline helpers are `io_dir__init()`, `io_dir__rewinddir()`, `io_dir__readdir()`, and `io_dir__is_dir()`. Architecture-specific `SYS_getdents64` fallback numbers are provided when libc headers do not define the syscall number.

## Control flow
Callers open a directory fd, initialize `struct io_dir`, and repeatedly call `io_dir__readdir()`. When the internal fixed buffer is exhausted, the helper calls `getdents64` again. `io_dir__is_dir()` trusts `d_type` unless it is `DT_UNKNOWN`, in which case it calls `fstatat()`.

## State and persistence behavior
Runtime state is the directory fd, available bytes, next pointer, and a four-entry buffer embedded in `struct io_dir`. There is no persistent state. Rewind uses `lseek(fd, 0, SEEK_SET)` and clears buffered bytes.

## Dependencies and integration points
It depends on raw Linux directory entry layout, syscall numbers, `fstatat`, `lseek`, and `<linux/limits.h>`. It is used by performance-sensitive tools code that can tolerate Linux-specific APIs.

## Risks and edge cases
The embedded buffer can hold only a few dirents and assumes returned records fit in it. Fallback syscall numbers are architecture-sensitive and can age. `io_dir__readdir()` does not validate `d_reclen`, so malformed syscall output would corrupt iteration. It is Linux-only.

## Test signals
Iterate real directories with many entries, names near `NAME_MAX`, unknown `d_type` filesystems, rewind behavior, and memory-sanitizer builds that exercise the explicit zeroing path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/io_dir.h -->
