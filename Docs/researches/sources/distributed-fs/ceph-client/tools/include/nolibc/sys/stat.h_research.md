# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/stat.h

## Purpose
Provides file-status wrappers for nolibc using modern `statx` where possible.

## APIs, Types, and Functions
Defines `_sys_statx`, `statx`, `fstatat`, `stat`, `fstat`, and `lstat`, converting `struct statx` results into nolibc `struct stat` for legacy APIs.

## Control Flow, State, and Persistence
The wrappers query kernel metadata, translate errors, and populate caller buffers. Conversion maps device, inode, mode, link count, uid/gid, size, block size, block count, and timestamps. No persistent userspace state is held.

## Dependencies and Integration
Depends on `../types.h`, `../sys.h`, Linux stat UAPI, and fd/path syscall support. It integrates with directory walkers, file tools, and stdio/file tests.

## Risks and Test Signals
Risks include incomplete stat field conversion, timestamp width, symlink-following flags, and kernels lacking `statx`. Test signals are stat/fstat/lstat comparisons against libc, symlink behavior, device/inode fields, timestamp checks, and old-kernel fallback coverage if available.
