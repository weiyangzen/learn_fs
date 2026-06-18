# sources/cloud-native/fuse-overlayfs/src/sys/io.rs

## Purpose
`sys/io.rs` wraps low-level fd I/O syscalls used by FUSE read/write paths, sync operations, truncation, sparse/extent operations, file cloning, copy ranges, and filesystem ioctls.

## Important APIs, Types, And Functions
The module exports `pread`, `pwrite`, `read`, `write`, `sendfile`, `copy_file_range`, `fsync`, `fdatasync`, `ftruncate`, `lseek`, `ficlone`, and `ioctl_long`.

## Control Flow
Each wrapper invokes one libc syscall using raw fd and Rust-managed buffers or integer parameters, then returns either the byte count/result or `FsError::last()`.

## State And Persistence
Persistent effects are file content writes, file length changes, sync-to-storage requests, copied extents, cloned extents, and ioctl-set filesystem flags/version values. The module itself keeps no state.

## Dependencies And Integration Points
`overlay.rs` uses `pread`/`pwrite` for FUSE `read`/`write`, sync wrappers for `fsync`/`fsyncdir`, `ftruncate` for setattr/truncate, `lseek` for FUSE lseek, `copy_file_range` for server-side copies, and `ioctl_long` for `FS_IOC_*FLAGS`/`VERSION`. Copy-up code can use `ficlone`/`sendfile` paths elsewhere in the crate.

## Risks
Partial reads/writes/copies must be handled by callers. `copy_file_range`, `sendfile`, and `FICLONE` are filesystem/kernel dependent. `ioctl_long` assumes c_long-sized in/out values and is not a generic ioctl abstraction. Offset casts must remain within kernel-supported ranges.

## Test Signals
Unit tests cover pread/pwrite round trips, fsync, ftruncate, lseek, best-effort copy_file_range, and read/write. Integration tests cover FUSE I/O, fallocate, sparse and mmap workflows, and setattr truncation.
