# sources/distributed-fs/ceph-client/tools/include/nolibc/std.h

## Purpose
Defines common POSIX-ish scalar typedefs for nolibc.

## APIs, Types, and Functions
Provides `dev_t`, `ino_t`, `mode_t`, `pid_t`, `uid_t`, `gid_t`, `nlink_t`, `off_t`, `blksize_t`, `blkcnt_t`, and `time_t` based on fixed-width and kernel time types.

## Control Flow, State, and Persistence
There is no control flow or runtime state. The header fixes userspace ABI type widths used by stat, filesystem, process, and time wrappers.

## Dependencies and Integration
Depends on `stdint.h` and Linux time type definitions. It integrates with `types.h`, `sys/stat.h`, `fcntl.h`, `time.h`, and many syscall wrappers.

## Risks and Test Signals
Risks are ABI mismatches on unusual architectures, especially `time_t` and file offset width, and divergence from system libc typedefs. Test signals are sizeof/alignment assertions, stat/time wrapper builds, and 32-bit architecture coverage.
