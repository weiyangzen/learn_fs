# sources/distributed-fs/ceph-client/rust/kernel/fs/file.rs

## Purpose
`fs/file.rs` provides Rust wrappers for open kernel files and file descriptor reservation. It models `struct file` reference ownership, distinguishes locally safe file references from thread-safe ones, exposes open flags, and provides RAII cleanup for reserved fd slots.

## Important APIs, Types, and Functions
`Offset` aliases `loff_t`. `flags` exports open and file mode constants. `File` is the thread-safe wrapper around `struct file`; `LocalFile` models a file that may have same-thread `fdget_pos` state. Both implement `AlwaysRefCounted` through `get_file`/`fput`. `LocalFile::fget`, `LocalFile::from_raw_file`, `LocalFile::assume_no_fdget_pos`, `cred`, and `flags` are the main accessors. `File::from_raw_file` creates a shared thread-safe reference. `FileDescriptorReservation` wraps `get_unused_fd_flags`, `fd_install`, and `put_unused_fd`. `BadFdError` maps only to `EBADF`.

## Control Flow
`fget` calls C `fget`, turns null into `BadFdError`, and transfers the acquired reference into `ARef<LocalFile>`. Callers that know no unsafe `fdget_pos` path is active can convert `ARef<LocalFile>` to `ARef<File>` with `assume_no_fdget_pos`. `File` derefs to `LocalFile` to share methods. Descriptor reservation first claims an unused fd, then either `fd_install` consumes both reservation and file reference via `forget`, or `Drop` releases the unused slot.

## State and Persistence
State is entirely kernel object state: file reference counts, flags, credentials, and fd table reservations. `FileDescriptorReservation` is task-local by `NotThreadSafe` because fd reservation must be committed or released on the same current task.

## Dependencies and Integration Points
The file integrates with VFS `fget`, `get_file`, `fput`, `get_unused_fd_flags`, `fd_install`, `put_unused_fd`, credentials, `ARef`, `Opaque`, and device/ioctl code that accepts file descriptors. It is foundational for Rust drivers exposing or consuming file-backed resources.

## Risks
The safety boundary around `fdget_pos` is subtle. Incorrectly converting `LocalFile` to `File` can allow data races on `f_pos`. Raw construction requires the caller to keep the C refcount positive. `flags()` uses volatile read as a READ_ONCE stand-in; future memory-ordering helpers may be needed.

## Test Signals
Test invalid fd returns `BadFdError`, valid fd refcount lifecycle, `cred()` stability, flag reads, reservation drop releasing unused fd, `fd_install` consuming the reservation, and compile-time non-`Send` behavior for `FileDescriptorReservation`.
