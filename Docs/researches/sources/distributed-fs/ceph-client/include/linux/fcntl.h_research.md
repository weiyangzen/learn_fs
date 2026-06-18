# sources/distributed-fs/ceph-client/include/linux/fcntl.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fcntl.h` provides kernel-side validation masks and lock-command classification helpers for open/openat2/fcntl handling. The source was read as a complete 48-line file for this report.

## Important APIs, Types, and Functions

Key macros are `VALID_OPEN_FLAGS`, `VALID_RESOLVE_FLAGS`, `OPEN_HOW_SIZE_VER0`, `OPEN_HOW_SIZE_LATEST`, `force_o_largefile`, `IS_GETLK32`, `IS_SETLK32`, `IS_SETLKW32`, `IS_GETLK64`, `IS_SETLK64`, `IS_SETLKW64`, and aggregate `IS_GETLK`, `IS_SETLK`, `IS_SETLKW`.

## Control Flow

Open and openat2 syscall code validates userspace flags against these masks, applies large-file defaults, and dispatches fcntl lock commands through 32-bit or native command paths based on word size.

## State and Persistence Behavior

No state is stored in this header. It affects validation before file objects, dentries, and locks are created or modified.

## Dependencies and Integration Points

It includes `linux/stat.h` and UAPI fcntl definitions. It integrates with VFS open path resolution, openat2 ABI sizing, file locking, and compat handling.

## Risks and Edge Cases

Adding flags without updating masks rejects valid userspace requests; overly broad masks can bypass intended path-resolution restrictions. Lock command mapping differs between 32-bit and 64-bit builds.

## Test Signals

open/openat2 selftests for flag validation, path resolution constraints, 32-bit compat fcntl lock tests, and large-file behavior tests.
