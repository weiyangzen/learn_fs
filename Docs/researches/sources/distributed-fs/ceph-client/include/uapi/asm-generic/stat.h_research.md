# sources/distributed-fs/ceph-client/include/uapi/asm-generic/stat.h

## Purpose
Defines generic `struct stat` and conditional `struct stat64` layouts for file metadata syscalls.

## Important APIs, Types, And Functions
Exports `STAT_HAVE_NSEC`, `struct stat`, and `struct stat64` when `__BITS_PER_LONG != 64` or `__ARCH_WANT_STAT64`. Fields cover device, inode, mode, link count, uid/gid, rdev, size, block size, blocks, and nanosecond timestamps.

## Control Flow
Preprocessor selection includes `stat64` only for 32-bit or opt-in architectures. There are no functions.

## State, Persistence, And Dependencies
The structs are copied across syscall boundaries and encode persistent filesystem metadata snapshots. It depends on `<asm/bitsperlong.h>`.

## Integration Points
Used by `stat`, `fstat`, `newfstatat`, `stat64`, libc metadata APIs, and filesystem implementations including Ceph client paths that fill generic inode metadata.

## Risks
Layout, signedness, padding, and timestamp field width are ABI. Time fields based on `long` or `int` interact with 32-bit time limits. New architectures should avoid inheriting old layout mistakes.

## Test Signals
ABI size/offset checks, stat syscall round trips on regular files/devices/symlinks, nanosecond timestamp verification, large inode and large file tests, and 32-bit compat stat64 tests.
