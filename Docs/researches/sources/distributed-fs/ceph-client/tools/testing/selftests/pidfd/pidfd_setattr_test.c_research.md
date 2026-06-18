# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_setattr_test.c

## Purpose
Verifies pidfs/pidfd file descriptors reject file metadata and execution operations that must not be supported on task handles.

## Important APIs, Types, and Functions
Defines `FIXTURE(pidfs_setattr)` with `child_pid` and `child_pidfd`; setup uses `create_child()` with `CLONE_NEWUSER | CLONE_NEWPID`; tests call `fchown()`, `fchmod()`, and `execveat(..., AT_EMPTY_PATH)`.

## Control Flow
The fixture creates a short-lived child and pidfd, each test performs one forbidden operation on the pidfd, and teardown waits for the child and closes the pidfd.

## State and Persistence
State is limited to the fixture child and pidfd. The test intentionally does not persist metadata because the expected behavior is rejection before any pidfs inode mutation.

## Dependencies and Integration Points
Uses `pidfd.h` syscall wrappers and `kselftest_harness.h` fixtures. It exercises the pidfs VFS operation table through generic libc/VFS APIs rather than pidfd-specific ioctls.

## Risks and Test Signals
Expected errno values are part of the contract: `EOPNOTSUPP` for chown/chmod and `EACCES` for exec. A regression could expose task handles as mutable/executable filesystem objects or produce incompatible errno values.
