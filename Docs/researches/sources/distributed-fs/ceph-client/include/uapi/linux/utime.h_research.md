# sources/distributed-fs/ceph-client/include/uapi/linux/utime.h

## Purpose
Provides the legacy userspace `struct utimbuf` definition used by `utime(2)`-style file timestamp updates.

## Important APIs, Types, And Constants
The single ABI type is `struct utimbuf`, with `actime` and `modtime` fields of type `__kernel_old_time_t`. It includes `<linux/types.h>` and intentionally uses the old kernel time type rather than `time64` types for compatibility with the historical syscall interface.

## Control Flow, State, And Persistence
No code executes here. User programs pass the struct to timestamp-setting syscalls; the filesystem persists the resulting access and modification times in inode metadata. The header itself does not define validation, conversion, or timezone behavior.

## Dependencies And Integration Points
Used by libc/kernel UAPI consumers that need the raw Linux layout for `utime`. Filesystems, VFS timestamp conversion, and architecture syscall wrappers are the runtime integration points.

## Risks And Test Signals
The main risk is time-width compatibility, especially on 32-bit ABIs where `__kernel_old_time_t` can truncate modern timestamps. Test signals include ABI size/layout checks, syscall tests around epoch boundaries, negative values where supported, and filesystem round trips verifying `atime` and `mtime`.
