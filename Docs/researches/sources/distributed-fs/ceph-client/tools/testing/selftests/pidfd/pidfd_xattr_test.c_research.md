# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_xattr_test.c

## Purpose
Checks pidfs extended-attribute behavior on pidfds, including multiple xattrs and persistence across task exit while a pidfd remains open.

## Important APIs, Types, and Functions
Defines `FIXTURE(pidfs_xattr)` with a child pid and pidfd. Tests call `fsetxattr()`, `fgetxattr()`, `flistxattr()`, and compare values stored under user xattr names.

## Control Flow
Setup creates a child in new user and pid namespaces. `set_get_list_xattr_multiple` writes multiple user xattrs, reads them back, and verifies the list buffer contains expected names. `set_get_list_xattr_persistent` writes an xattr, waits for child exit, then reads it again through the still-open pidfd.

## State and Persistence
The only persisted state is xattr data attached to the pidfs file object for the lifetime of the pidfd. The test confirms that data survives target process exit until descriptor cleanup.

## Dependencies and Integration Points
Depends on pidfs xattr support, Linux xattr syscalls, `create_child()`, and `kselftest_harness.h`. It integrates pidfs with generic VFS xattr APIs.

## Risks and Test Signals
Risks include xattr ordering/list formatting assumptions, namespace restrictions, and kernels/filesystems without pidfs xattr support. Failure signals are syscall errors, mismatched values, missing list entries, or loss of xattrs after reaping.
