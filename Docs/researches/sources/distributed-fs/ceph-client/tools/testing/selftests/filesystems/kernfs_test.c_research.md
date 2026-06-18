# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/kernfs_test.c

## Purpose

`kernfs_test.c` validates xattr behavior on kernfs-backed sysfs files.

## Important APIs, Types, and Functions

It contains two kselftest tests using `listxattr` and `getxattr` against `/sys/kernel`. It includes `_GNU_SOURCE`, sane userspace types, `sys/xattr.h`, and the kselftest harness.

## Control Flow, State, and Persistence

`kernfs_listxattr` calls `listxattr("/sys/kernel", NULL, 0)` and expects `ENOTSUP`. `kernfs_getxattr` calls `getxattr("/sys/kernel", "user.test", NULL, 0)` and expects `ENOTSUP`. No state is modified.

## Dependencies, Integration Points, Risks, and Test Signals

The test depends on sysfs mounted at `/sys` and kernfs returning unsupported xattr errors for this path. It integrates with kernfs/sysfs VFS xattr semantics. Risks are environments without sysfs or changed errno behavior for unsupported xattrs. Passing signals are both calls failing with `-1` and `errno == ENOTSUP`.
